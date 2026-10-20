#!/usr/bin/env python3
"""
split_shots.py  --  Shot Splitter (GUI)

Detects shot / scene boundaries in a movie (PySceneDetect) and splits it into
one .mp4 file per shot (ffmpeg).

Run it and a window opens where you can:
  * read what the tool does and what every setting means
  * pick the input movie and the output folder
  * tune detection (detector, sensitivity, minimum shot length, export mode)
  * follow progress with a loading bar, an ETA and a live event log

Requirements:
    pip install scenedetect opencv-python --break-system-packages
        (or: pip install "scenedetect[opencv]")
    ffmpeg must be installed and available on your PATH
    (Windows: https://ffmpeg.org/download.html, Mac: brew install ffmpeg,
     Linux: sudo apt install ffmpeg)
    tkinter (usually bundled with Python; on Linux: sudo apt install python3-tk)

Usage:
    python split_shots.py
        -> opens the window
    python split_shots.py "/path/to/movie.mp4" --threshold 20 --detector adaptive
        -> opens the window with the movie and settings pre-filled
"""

import argparse
import os
import platform
import queue
import shutil
import subprocess
import sys
import threading
import time
from collections import deque
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector

try:  # scenedetect >= 0.7
    from scenedetect import split_video_ffmpeg
except ImportError:  # scenedetect 0.6
    from scenedetect.video_splitter import split_video_ffmpeg


# --------------------------------------------------------------------------- #
#  Small helpers
# --------------------------------------------------------------------------- #

def fmt_clock(seconds: float) -> str:
    """12.3 -> '0:12', 3725 -> '1:02:05'  (for elapsed / ETA labels)."""
    if seconds is None or seconds != seconds or seconds < 0:
        return "--:--"
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_tc(seconds: float) -> str:
    """Timecode like 00:01:23.450."""
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def tc_seconds(value, fps: float) -> float:
    """Seconds from a FrameTimecode (0.6/0.7) or a plain frame number."""
    if hasattr(value, "get_seconds"):
        return float(value.get_seconds())
    return float(value) / fps


def tc_frames(value) -> int:
    if hasattr(value, "get_frames"):
        return int(value.get_frames())
    if hasattr(value, "frame_num"):
        return int(value.frame_num)
    return int(value)


def open_folder(path: Path) -> None:
    try:
        if platform.system() == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as exc:  # pragma: no cover
        messagebox.showerror("Could not open folder", str(exc))


# --------------------------------------------------------------------------- #
#  Worker thread: detection + splitting. Talks to the UI only through a queue.
# --------------------------------------------------------------------------- #
#   ("log", level, text)       level: info | ok | warn | err | cut
#   ("phase", index, label)    index: 0 = detect, 1 = split
#   ("progress", fraction)     0..1 inside the current phase (None = unknown)
#   ("done", n_shots, out_dir)
#   ("cancelled",)
#   ("error", text)

class SplitJob(threading.Thread):
    def __init__(self, movie, out_dir, detector, threshold, min_len, copy_mode, q):
        super().__init__(daemon=True)
        self.movie = Path(movie)
        self.out_dir = Path(out_dir)
        self.detector = detector
        self.threshold = threshold
        self.min_len = min_len
        self.copy_mode = copy_mode
        self.q = q
        self._cancel = threading.Event()
        self._sm = None

    # -- control ------------------------------------------------------------
    def cancel(self):
        self._cancel.set()
        if self._sm is not None:
            try:
                self._sm.stop()
            except Exception:
                pass

    def log(self, text, level="info"):
        self.q.put(("log", level, text))

    # -- main ---------------------------------------------------------------
    def run(self):
        try:
            self._run()
        except Exception as exc:
            self.q.put(("error", f"{type(exc).__name__}: {exc}"))

    def _run(self):
        job = self

        # ---------------- open video ----------------
        video = open_video(str(self.movie))
        fps = float(video.frame_rate)
        try:
            total = tc_frames(video.duration)
        except Exception:
            total = 0
        try:
            w, h = video.frame_size
            size = f"{w}x{h}"
        except Exception:
            size = "unknown size"
        self.log(f"Opened '{self.movie.name}'  ({size}, {fps:.3f} fps, "
                 f"{fmt_tc(total / fps) if total else 'unknown duration'})")

        # ---------------- phase 1: detect ----------------
        self.q.put(("phase", 0, "Detecting shots"))
        self.q.put(("progress", 0.0 if total else None))
        min_len_frames = max(1, int(self.min_len * fps))
        base = AdaptiveDetector if self.detector == "adaptive" else ContentDetector
        state = {"last": 0.0, "cuts": 0}

        class TrackedDetector(base):
            """Same detector, but reports progress + every cut it finds."""

            def process_frame(self, *args, **kwargs):
                cuts = super().process_frame(*args, **kwargs)
                now = time.monotonic()
                if total and now - state["last"] > 0.1:
                    state["last"] = now
                    job.q.put(("progress", min(1.0, tc_frames(args[0]) / total)))
                for c in cuts or []:
                    state["cuts"] += 1
                    job.log(f"Cut #{state['cuts']} at {fmt_tc(tc_seconds(c, fps))}", "cut")
                return cuts

        if self.detector == "adaptive":
            detector = TrackedDetector(min_scene_len=min_len_frames)
            self.log(f"Detector: adaptive (min shot length {self.min_len:.1f}s)")
        else:
            detector = TrackedDetector(threshold=self.threshold, min_scene_len=min_len_frames)
            self.log(f"Detector: content (threshold {self.threshold:g}, "
                     f"min shot length {self.min_len:.1f}s)")

        self._sm = SceneManager()
        self._sm.add_detector(detector)
        self._sm.detect_scenes(video, show_progress=False)
        scenes = self._sm.get_scene_list()

        if self._cancel.is_set():
            self.q.put(("cancelled",))
            return

        self.q.put(("progress", 1.0))
        if not scenes:
            self.log("No shots detected. Try a lower sensitivity threshold "
                     "or the adaptive detector.", "warn")
            self.q.put(("done", 0, self.out_dir))
            return
        self.log(f"Detection finished: {len(scenes)} shots found.", "ok")

        # ---------------- phase 2: split ----------------
        self.q.put(("phase", 1, "Splitting into files"))
        self.q.put(("progress", 0.0))
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"Writing to: {self.out_dir}")

        if self.copy_mode:
            ffmpeg_args = "-c:v copy -c:a copy -sn"
        else:
            ffmpeg_args = "-map 0:v:0 -map 0:a? -c:v libx264 -preset veryfast -crf 22 -c:a aac"

        durations = [max(0.001, tc_seconds(e, fps) - tc_seconds(s, fps)) for s, e in scenes]
        total_dur = sum(durations)
        done_dur = 0.0
        width = max(4, len(str(len(scenes))))

        for i, (scene, dur) in enumerate(zip(scenes, durations), 1):
            if self._cancel.is_set():
                self.q.put(("cancelled",))
                return
            start_s, end_s = tc_seconds(scene[0], fps), tc_seconds(scene[1], fps)
            rc = split_video_ffmpeg(
                str(self.movie),
                [scene],
                output_dir=str(self.out_dir),
                output_file_template=f"$VIDEO_NAME-Shot-{i:0{width}d}.mp4",
                video_name=self.movie.stem,
                arg_override=ffmpeg_args,
                show_progress=False,
            )
            if rc not in (0, None):
                raise RuntimeError(f"ffmpeg failed on shot {i} (exit code {rc})")
            done_dur += dur
            self.q.put(("progress", done_dur / total_dur))
            self.log(f"Shot {i}/{len(scenes)}  {fmt_tc(start_s)} -> {fmt_tc(end_s)}  "
                     f"({dur:.2f}s)", "ok")

        self.q.put(("done", len(scenes), self.out_dir))


# --------------------------------------------------------------------------- #
#  GUI
# --------------------------------------------------------------------------- #

BG = "#13151b"
PANEL = "#1c1f28"
PANEL2 = "#262a36"
BORDER = "#323747"
FG = "#e8eaf0"
MUTED = "#8d94a6"
ACCENT = "#6c8cff"
ACCENT_D = "#5575e6"
OK = "#4ade80"
WARN = "#fbbf24"
ERR = "#f87171"
CUT = "#c4a1ff"

STEPS = [
    ("1", "Detect", "PySceneDetect scans every frame and flags sudden visual changes as shot boundaries."),
    ("2", "Split", "ffmpeg cuts the movie at each boundary and writes one .mp4 per shot."),
    ("3", "Review", "Files are named  <movie>-Shot-0001.mp4,  -0002.mp4 ...  in the output folder."),
]


class App(tk.Tk):
    def __init__(self, preset):
        super().__init__()
        self.title("Shot Splitter")
        self.configure(bg=BG)
        self.minsize(860, 840)
        self.geometry("940x960")

        self.q: queue.Queue = queue.Queue()
        self.job: SplitJob | None = None
        self.out_is_manual = False
        self.last_out_dir: Path | None = None

        # progress bookkeeping
        self.phase = -1
        self.phase_frac = 0.0
        self.t_start = 0.0
        self.samples: deque = deque(maxlen=60)

        self._build_style()
        self._build_ui()
        self._apply_preset(preset)
        self._refresh_ffmpeg_status()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(50, self._poll)
        self.after(250, self._tick_clock)

    # ------------------------------------------------------------------ style
    def _build_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        self.option_add("*TCombobox*Listbox.background", PANEL2)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

        s.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=PANEL)
        s.configure("TLabel", background=PANEL, foreground=FG)
        s.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Bg.TLabel", background=BG, foreground=FG)
        s.configure("BgMuted.TLabel", background=BG, foreground=MUTED)
        s.configure("Title.TLabel", background=BG, foreground=FG, font=("Segoe UI", 22, "bold"))
        s.configure("CardTitle.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 11, "bold"))
        s.configure("Big.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 12, "bold"))
        s.configure("Mono.TLabel", background=PANEL, foreground=MUTED, font=("Consolas", 10))

        s.configure("TEntry", fieldbackground=PANEL2, foreground=FG, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER, insertcolor=FG, padding=6)
        s.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)],
              darkcolor=[("focus", ACCENT)])
        s.configure("TCombobox", fieldbackground=PANEL2, background=PANEL2, foreground=FG,
                    arrowcolor=FG, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    padding=5)
        s.map("TCombobox", fieldbackground=[("readonly", PANEL2)],
              foreground=[("readonly", FG)], bordercolor=[("focus", ACCENT)])

        s.configure("TButton", background=PANEL2, foreground=FG, bordercolor=BORDER,
                    focuscolor=PANEL2, padding=(14, 7))
        s.map("TButton", background=[("active", BORDER), ("disabled", PANEL)],
              foreground=[("disabled", MUTED)])
        s.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", bordercolor=ACCENT,
                    font=("Segoe UI", 11, "bold"), padding=(22, 10))
        s.map("Accent.TButton", background=[("active", ACCENT_D), ("disabled", PANEL2)],
              foreground=[("disabled", MUTED)], bordercolor=[("disabled", PANEL2)])

        s.configure("TRadiobutton", background=PANEL, foreground=FG, focuscolor=PANEL,
                    indicatorcolor=PANEL2)
        s.map("TRadiobutton", background=[("active", PANEL)],
              indicatorcolor=[("selected", ACCENT)])
        s.configure("Horizontal.TScale", background=PANEL, troughcolor=PANEL2,
                    bordercolor=BORDER, lightcolor=ACCENT, darkcolor=ACCENT)

        s.configure("Accent.Horizontal.TProgressbar", troughcolor=PANEL2, background=ACCENT,
                    bordercolor=PANEL, lightcolor=ACCENT, darkcolor=ACCENT, thickness=18)
        s.configure("Done.Horizontal.TProgressbar", troughcolor=PANEL2, background=OK,
                    bordercolor=PANEL, lightcolor=OK, darkcolor=OK, thickness=18)
        s.configure("Vertical.TScrollbar", background=PANEL2, troughcolor=PANEL,
                    bordercolor=PANEL, arrowcolor=MUTED)

    # --------------------------------------------------------------------- UI
    def _card(self, parent, title=None):
        outer = tk.Frame(parent, bg=BORDER)
        inner = ttk.Frame(outer, style="Card.TFrame", padding=(14, 10))
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        if title:
            ttk.Label(inner, text=title, style="CardTitle.TLabel").grid(
                row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))
        return outer, inner

    def _build_ui(self):
        root = ttk.Frame(self, padding=(22, 14, 22, 10))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(5, weight=1)   # event log row stretches

        # ---------------- header ----------------
        head = ttk.Frame(root)
        head.grid(row=0, column=0, sticky="ew")
        ttk.Label(head, text="\u2702  Shot Splitter", style="Title.TLabel").pack(anchor="w")
        self.intro = ttk.Label(
            head, style="BgMuted.TLabel", justify="left",
            text="Turn one long movie into many short clips. The tool finds every cut "
                 "(where one shot ends and the next begins) and saves each shot as its own "
                 ".mp4 file, so you can review, tag or re-use shots individually.")
        self.intro.pack(anchor="w", pady=(4, 0), fill="x")
        head.bind("<Configure>", lambda e: self.intro.configure(wraplength=max(300, e.width - 10)))

        # ---------------- how it works ----------------
        steps = ttk.Frame(root)
        steps.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        for c in range(3):
            steps.columnconfigure(c, weight=1, uniform="steps")
        self.step_badges = []
        self.step_descs = []
        for c, (num, name, desc) in enumerate(STEPS):
            outer, inner = self._card(steps)
            outer.grid(row=0, column=c, sticky="nsew", padx=(0 if c == 0 else 6, 0 if c == 2 else 6))
            badge = tk.Label(inner, text=num, bg=PANEL2, fg=ACCENT, width=2,
                             font=("Segoe UI", 11, "bold"))
            inner.columnconfigure(1, weight=1)
            badge.grid(row=0, column=0, sticky="nw", padx=(0, 10))
            ttk.Label(inner, text=name, style="CardTitle.TLabel").grid(row=0, column=1, sticky="w")
            d = ttk.Label(inner, text=desc, style="Muted.TLabel", justify="left")
            d.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
            inner.bind("<Configure>", lambda e, d=d: d.configure(wraplength=max(120, e.width - 36)))
            self.step_badges.append(badge)
            self.step_descs.append(d)

        # ---------------- files ----------------
        outer, files = self._card(root, "Files")
        outer.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        files.columnconfigure(1, weight=1)

        self.var_in = tk.StringVar()
        self.var_out = tk.StringVar()
        ttk.Label(files, text="Input movie").grid(row=1, column=0, sticky="w", padx=(0, 12))
        self.ent_in = ttk.Entry(files, textvariable=self.var_in)
        self.ent_in.grid(row=1, column=1, sticky="ew")
        self.btn_in = ttk.Button(files, text="Browse\u2026", command=self._browse_in)
        self.btn_in.grid(row=1, column=2, padx=(8, 0))

        ttk.Label(files, text="Output folder").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(10, 0))
        self.ent_out = ttk.Entry(files, textvariable=self.var_out)
        self.ent_out.grid(row=2, column=1, sticky="ew", pady=(10, 0))
        self.btn_out = ttk.Button(files, text="Browse\u2026", command=self._browse_out)
        self.btn_out.grid(row=2, column=2, padx=(8, 0), pady=(10, 0))
        ttk.Label(files, style="Muted.TLabel",
                  text="Left empty, a folder named \u201c<movie>_shots\u201d is created next to the movie."
                  ).grid(row=3, column=1, sticky="w", pady=(4, 0))
        self.var_out.trace_add("write", self._on_out_edit)
        self._setting_out = False

        # ---------------- settings ----------------
        outer, st = self._card(root, "Detection settings")
        outer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        st.columnconfigure(1, weight=1)

        self.var_det = tk.StringVar(value="content")
        ttk.Label(st, text="Detector").grid(row=1, column=0, sticky="w", padx=(0, 12))
        det_box = ttk.Frame(st, style="Card.TFrame")
        det_box.grid(row=1, column=1, columnspan=2, sticky="w")
        ttk.Radiobutton(det_box, text="Content  (classic hard cuts)", value="content",
                        variable=self.var_det, command=self._on_detector).pack(side="left")
        ttk.Radiobutton(det_box, text="Adaptive  (fast pans / camera motion)", value="adaptive",
                        variable=self.var_det, command=self._on_detector).pack(side="left", padx=(16, 0))

        self.var_thr = tk.DoubleVar(value=27.0)
        ttk.Label(st, text="Sensitivity").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(8, 0))
        self.scl_thr = ttk.Scale(st, from_=5, to=60, variable=self.var_thr,
                                 command=lambda v: self._on_scale(self.var_thr, self.lbl_thr, 0, "{:g}"))
        self.scl_thr.grid(row=2, column=1, sticky="ew", pady=(8, 0))
        self.lbl_thr = ttk.Label(st, text="27", style="Big.TLabel", width=5, anchor="e")
        self.lbl_thr.grid(row=2, column=2, padx=(8, 0), pady=(8, 0))
        self.hint_thr = ttk.Label(st, style="Muted.TLabel",
                                  text="Lower = more cuts detected (also more false positives). "
                                       "Higher = only obvious cuts. Default 27.")
        self.hint_thr.grid(row=3, column=1, sticky="w")

        self.var_min = tk.DoubleVar(value=0.6)
        ttk.Label(st, text="Min. shot length").grid(row=4, column=0, sticky="w", padx=(0, 12), pady=(8, 0))
        self.scl_min = ttk.Scale(st, from_=0.1, to=5.0, variable=self.var_min,
                                 command=lambda v: self._on_scale(self.var_min, self.lbl_min, 1, "{:.1f} s"))
        self.scl_min.grid(row=4, column=1, sticky="ew", pady=(8, 0))
        self.lbl_min = ttk.Label(st, text="0.6 s", style="Big.TLabel", width=5, anchor="e")
        self.lbl_min.grid(row=4, column=2, padx=(8, 0), pady=(8, 0))
        ttk.Label(st, style="Muted.TLabel",
                  text="Shots shorter than this are merged into their neighbour "
                       "(avoids tiny false-positive cuts)."
                  ).grid(row=5, column=1, sticky="w")

        self.var_mode = tk.StringVar(value="encode")
        ttk.Label(st, text="Export mode").grid(row=6, column=0, sticky="w", padx=(0, 12), pady=(8, 0))
        mode_box = ttk.Frame(st, style="Card.TFrame")
        mode_box.grid(row=6, column=1, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Radiobutton(mode_box, text="Re-encode  (frame-accurate, slower)", value="encode",
                        variable=self.var_mode).pack(side="left")
        ttk.Radiobutton(mode_box, text="Stream copy  (very fast, may start on nearest keyframe)",
                        value="copy", variable=self.var_mode).pack(side="left", padx=(16, 0))

        # ---------------- run controls + progress ----------------
        outer, run = self._card(root, "Progress")
        outer.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        run.columnconfigure(0, weight=1)

        self.lbl_phase = ttk.Label(run, text="Ready", style="Big.TLabel")
        self.lbl_phase.grid(row=1, column=0, sticky="w")
        self.lbl_pct = ttk.Label(run, text="0 %", style="Big.TLabel")
        self.lbl_pct.grid(row=1, column=1, sticky="e")

        self.bar = ttk.Progressbar(run, style="Accent.Horizontal.TProgressbar",
                                   orient="horizontal", mode="determinate", maximum=100)
        self.bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 6))

        stats = ttk.Frame(run, style="Card.TFrame")
        stats.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.lbl_elapsed = ttk.Label(stats, text="Elapsed  0:00", style="Mono.TLabel")
        self.lbl_elapsed.pack(side="left")
        self.lbl_eta = ttk.Label(stats, text="ETA  --:--", style="Mono.TLabel")
        self.lbl_eta.pack(side="left", padx=(24, 0))
        self.lbl_shots = ttk.Label(stats, text="Shots  0", style="Mono.TLabel")
        self.lbl_shots.pack(side="left", padx=(24, 0))

        btns = ttk.Frame(run, style="Card.TFrame")
        btns.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.btn_start = ttk.Button(btns, text="\u25B6  Split movie", style="Accent.TButton",
                                    command=self._start)
        self.btn_start.pack(side="left")
        self.btn_cancel = ttk.Button(btns, text="Cancel", command=self._cancel, state="disabled")
        self.btn_cancel.pack(side="left", padx=(10, 0))
        self.btn_open = ttk.Button(btns, text="Open output folder", command=self._open_out,
                                   state="disabled")
        self.btn_open.pack(side="right")

        # ---------------- event log ----------------
        outer, lg = self._card(root, "Events")
        outer.grid(row=5, column=0, sticky="nsew", pady=(8, 0))
        lg.rowconfigure(1, weight=1)
        lg.columnconfigure(0, weight=1)
        self.txt = tk.Text(lg, height=4, bg=PANEL2, fg=FG, bd=0, highlightthickness=0,
                           font=("Consolas", 10), wrap="word", state="disabled",
                           padx=10, pady=8, insertbackground=FG)
        self.txt.grid(row=1, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lg, orient="vertical", command=self.txt.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self.txt.configure(yscrollcommand=sb.set)
        self.txt.tag_configure("ts", foreground=MUTED)
        self.txt.tag_configure("info", foreground=FG)
        self.txt.tag_configure("ok", foreground=OK)
        self.txt.tag_configure("warn", foreground=WARN)
        self.txt.tag_configure("err", foreground=ERR)
        self.txt.tag_configure("cut", foreground=CUT)

        # ---------------- footer ----------------
        self.lbl_ff = ttk.Label(root, text="", style="BgMuted.TLabel")
        self.lbl_ff.grid(row=6, column=0, sticky="w", pady=(8, 0))

    # ------------------------------------------------------------- UI helpers
    def _log(self, text, level="info"):
        self.txt.configure(state="normal")
        self.txt.insert("end", time.strftime("%H:%M:%S  "), "ts")
        self.txt.insert("end", text + "\n", level)
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _on_scale(self, var, label, digits, fmt):
        v = round(var.get(), digits)
        var.set(v)
        label.configure(text=fmt.format(v))

    def _on_detector(self):
        adaptive = self.var_det.get() == "adaptive"
        self.scl_thr.state(["disabled"] if adaptive else ["!disabled"])
        self.hint_thr.configure(
            text="Not used by the adaptive detector (it tunes itself to the footage)." if adaptive
            else "Lower = more cuts detected (also more false positives). "
                 "Higher = only obvious cuts. Default 27.")

    def _on_out_edit(self, *_):
        if not self._setting_out:
            self.out_is_manual = bool(self.var_out.get().strip())

    def _set_out(self, text):
        self._setting_out = True
        self.var_out.set(text)
        self._setting_out = False

    def _browse_in(self):
        path = filedialog.askopenfilename(
            parent=self, title="Select a movie to split into shots",
            filetypes=[("Video files", "*.mp4 *.mov *.mkv *.avi *.m4v *.webm *.wmv"),
                       ("All files", "*.*")])
        if path:
            self.var_in.set(path)
            if not self.out_is_manual:
                self._set_out(str(Path(path).parent / f"{Path(path).stem}_shots"))

    def _browse_out(self):
        initial = Path(self.var_in.get()).parent if self.var_in.get() else Path.home()
        path = filedialog.askdirectory(parent=self, title="Select output folder",
                                       initialdir=str(initial))
        if path:
            self.var_out.set(path)

    def _open_out(self):
        if self.last_out_dir and self.last_out_dir.exists():
            open_folder(self.last_out_dir)

    def _refresh_ffmpeg_status(self):
        if shutil.which("ffmpeg"):
            self.lbl_ff.configure(text="\u25CF ffmpeg found", foreground=OK)
        else:
            self.lbl_ff.configure(
                text="\u25CF ffmpeg NOT found on PATH \u2013 install it first "
                     "(brew install ffmpeg / sudo apt install ffmpeg / ffmpeg.org)",
                foreground=ERR)

    def _apply_preset(self, p):
        self.var_det.set(p.detector)
        self.var_thr.set(p.threshold)
        self.var_min.set(p.min_length)
        self._on_scale(self.var_thr, self.lbl_thr, 0, "{:g}")
        self._on_scale(self.var_min, self.lbl_min, 1, "{:.1f} s")
        self._on_detector()
        if p.output_dir:
            self.var_out.set(p.output_dir)
        if p.movie:
            self.var_in.set(str(Path(p.movie).expanduser()))
            if not p.output_dir:
                mp = Path(p.movie).expanduser()
                self._set_out(str(mp.parent / f"{mp.stem}_shots"))

    def _set_running(self, running: bool):
        state = "disabled" if running else "normal"
        for w in (self.ent_in, self.ent_out, self.btn_in, self.btn_out):
            w.configure(state=state)
        self.btn_start.configure(state="disabled" if running else "normal")
        self.btn_cancel.configure(state="normal" if running else "disabled")
        if running:
            self.btn_open.configure(state="disabled")

    def _mark_steps(self, active: int, finished=False):
        for i, b in enumerate(self.step_badges):
            if finished or i < active:
                b.configure(bg=OK, fg="#0b1b10")
            elif i == active:
                b.configure(bg=ACCENT, fg="#ffffff")
            else:
                b.configure(bg=PANEL2, fg=ACCENT)

    # -------------------------------------------------------------- run / stop
    def _start(self):
        movie = self.var_in.get().strip()
        if not movie:
            self._browse_in()
            movie = self.var_in.get().strip()
            if not movie:
                return
        mp = Path(movie).expanduser()
        if not mp.is_file():
            messagebox.showerror("File not found", f"Cannot find:\n{mp}", parent=self)
            return
        if shutil.which("ffmpeg") is None:
            self._refresh_ffmpeg_status()
            messagebox.showerror("ffmpeg missing",
                                 "ffmpeg was not found on your PATH.\nInstall it first.", parent=self)
            return
        out = self.var_out.get().strip()
        out_dir = Path(out).expanduser() if out else mp.parent / f"{mp.stem}_shots"
        self._set_out(str(out_dir))
        self.last_out_dir = out_dir

        # reset progress UI
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.configure(state="disabled")
        self.bar.configure(style="Accent.Horizontal.TProgressbar", mode="determinate", value=0)
        self.lbl_pct.configure(text="0 %")
        self.lbl_eta.configure(text="ETA  --:--")
        self.lbl_shots.configure(text="Shots  0")
        self.samples.clear()
        self.phase, self.phase_frac = 0, 0.0
        self.t_start = time.monotonic()
        self._mark_steps(0)
        self._set_running(True)

        self.job = SplitJob(
            mp, out_dir, self.var_det.get(), float(self.var_thr.get()),
            float(self.var_min.get()), self.var_mode.get() == "copy", self.q)
        self.job.start()

    def _cancel(self):
        if self.job:
            self.btn_cancel.configure(state="disabled")
            self.lbl_phase.configure(text="Cancelling\u2026")
            self._log("Cancelling\u2026", "warn")
            self.job.cancel()

    def _on_close(self):
        if self.job and self.job.is_alive():
            if not messagebox.askyesno("Quit", "A job is still running. Cancel it and quit?",
                                       parent=self):
                return
            self.job.cancel()
        self.destroy()

    # ------------------------------------------------------ progress / events
    def _overall(self) -> float:
        """0..1 over both phases (detect = first half, split = second half)."""
        if self.phase < 0:
            return 0.0
        return min(1.0, (self.phase + self.phase_frac) / 2.0)

    def _poll(self):
        try:
            while True:
                msg = self.q.get_nowait()
                kind = msg[0]
                if kind == "log":
                    self._log(msg[2], msg[1])
                    if msg[1] == "cut":
                        n = msg[2].split("#")[1].split()[0]
                        self.lbl_shots.configure(text=f"Shots  {int(n) + 1}")
                elif kind == "phase":
                    self.phase, self.phase_frac = msg[1], 0.0
                    self.samples.clear()
                    self.lbl_phase.configure(text=f"Step {msg[1] + 1}/2 \u00B7 {msg[2]}")
                    self._mark_steps(msg[1])
                elif kind == "progress":
                    if msg[1] is None:
                        self.bar.configure(mode="indeterminate")
                        self.bar.start(15)
                    else:
                        if str(self.bar.cget("mode")) == "indeterminate":
                            self.bar.stop()
                            self.bar.configure(mode="determinate")
                        self.phase_frac = msg[1]
                        self.samples.append((time.monotonic(), self._overall()))
                        self._render_progress()
                elif kind == "done":
                    self._finish(msg[1], msg[2])
                elif kind == "cancelled":
                    self._end("Cancelled", WARN)
                    self._log("Cancelled by user.", "warn")
                elif kind == "error":
                    self._end("Failed", ERR)
                    self._log(msg[1], "err")
                    messagebox.showerror("Error", msg[1], parent=self)
        except queue.Empty:
            pass
        self.after(50, self._poll)

    def _render_progress(self):
        pct = self._overall() * 100
        self.bar.configure(value=pct)
        self.lbl_pct.configure(text=f"{pct:.0f} %")
        self.lbl_eta.configure(text=f"ETA  {fmt_clock(self._eta())}")

    def _eta(self):
        """Remaining time from the recent speed of the overall progress."""
        if len(self.samples) < 5:
            return None
        t0, f0 = self.samples[0]
        t1, f1 = self.samples[-1]
        if t1 - t0 < 1.0 or f1 <= f0:
            return None
        rate = (f1 - f0) / (t1 - t0)
        # Note: the two phases run at different speeds, so ETA is re-estimated
        # at the start of each phase (the sample window is cleared).
        return (1.0 - f1) / rate

    def _tick_clock(self):
        if self.job and self.job.is_alive():
            self.lbl_elapsed.configure(text=f"Elapsed  {fmt_clock(time.monotonic() - self.t_start)}")
            self.lbl_eta.configure(text=f"ETA  {fmt_clock(self._eta())}")
        self.after(250, self._tick_clock)

    def _end(self, label, color):
        self.bar.stop()
        self.lbl_phase.configure(text=label, foreground=color)
        self.lbl_eta.configure(text="ETA  --:--")
        self._set_running(False)
        self.after(3000, lambda: self.lbl_phase.configure(foreground=FG))

    def _finish(self, n_shots, out_dir):
        elapsed = time.monotonic() - self.t_start
        self.bar.stop()
        self.bar.configure(mode="determinate", value=100,
                           style="Done.Horizontal.TProgressbar" if n_shots else
                           "Accent.Horizontal.TProgressbar")
        self.lbl_pct.configure(text="100 %" if n_shots else "0 %")
        self.lbl_eta.configure(text="ETA  0:00")
        self.lbl_elapsed.configure(text=f"Elapsed  {fmt_clock(elapsed)}")
        self.lbl_shots.configure(text=f"Shots  {n_shots}")
        self._mark_steps(2, finished=bool(n_shots))
        self._set_running(False)
        if n_shots:
            self.lbl_phase.configure(text=f"\u2713 Done \u2013 {n_shots} shots", foreground=OK)
            self._log(f"Done. {n_shots} shot files written to {out_dir} "
                      f"in {fmt_clock(elapsed)}.", "ok")
            self.btn_open.configure(state="normal")
        else:
            self.lbl_phase.configure(text="No shots detected", foreground=WARN)


# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Split a movie into one mp4 per shot (GUI).")
    parser.add_argument("movie", nargs="?", default=None,
                        help="Optional: pre-fill the input movie in the window.")
    parser.add_argument("--detector", choices=["content", "adaptive"], default="content",
                        help="Detection algorithm. 'content' = classic cut detection (default). "
                             "'adaptive' = better for fast pans/camera motion.")
    parser.add_argument("--threshold", type=float, default=27.0,
                        help="Sensitivity for the 'content' detector. Lower = more cuts. Default 27.")
    parser.add_argument("--min-length", type=float, default=0.6, dest="min_length",
                        help="Minimum shot length in seconds. Default 0.6.")
    parser.add_argument("--output-dir", default=None,
                        help="Optional custom output folder (default: '<movie_name>_shots').")
    args = parser.parse_args()

    app = App(args)
    app.mainloop()


if __name__ == "__main__":
    main()