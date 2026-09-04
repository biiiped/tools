#!/usr/bin/env python3
"""
split_shots.py

Run this script and a file-explorer window will pop up asking you to pick
a movie. It will then:
  1. Detect shot/scene boundaries in it (using PySceneDetect).
  2. Create a folder next to the movie (named "<movie_name>_shots").
  3. Split the movie into one .mp4 file per shot inside that folder.

Requirements:
    pip install scenedetect[opencv] --break-system-packages
    ffmpeg must be installed and available on your PATH
    (Windows: https://ffmpeg.org/download.html, Mac: brew install ffmpeg,
     Linux: sudo apt install ffmpeg)
    tkinter (usually bundled with Python; on Linux you may need:
     sudo apt install python3-tk)

Usage:
    python split_shots.py
        -> opens a file picker, then processes the chosen movie
    python split_shots.py --threshold 20 --detector adaptive
        -> same, but with custom detection settings
    python split_shots.py "/path/to/movie.mp4"
        -> skips the file picker if you pass a path directly
"""

import argparse
import shutil
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector
from scenedetect.video_splitter import split_video_ffmpeg


def pick_movie_file() -> str:
    """Open a native file-explorer dialog and return the chosen movie path."""
    root = tk.Tk()
    root.withdraw()          # hide the empty root window
    root.attributes("-topmost", True)  # bring the dialog to the front

    path = filedialog.askopenfilename(
        title="Select a movie to split into shots",
        filetypes=[
            ("Video files", "*.mp4 *.mov *.mkv *.avi *.m4v *.webm *.wmv"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return path


def detect_shots(video_path: str, detector_name: str, threshold: float, min_scene_len: float):
    video = open_video(video_path)
    scene_manager = SceneManager()

    # min_scene_len is given in seconds; PySceneDetect wants frames or a
    # FrameTimecode, so we let it interpret a float as seconds via base_timecode.
    min_len_frames = max(1, int(min_scene_len * video.frame_rate))

    if detector_name == "adaptive":
        detector = AdaptiveDetector(min_scene_len=min_len_frames)
    else:
        detector = ContentDetector(threshold=threshold, min_scene_len=min_len_frames)

    scene_manager.add_detector(detector)
    scene_manager.detect_scenes(video, show_progress=True)
    return scene_manager.get_scene_list()


def main():
    parser = argparse.ArgumentParser(description="Split a movie into one mp4 per shot.")
    parser.add_argument(
        "movie",
        nargs="?",
        default=None,
        help="Path to the movie file. If omitted, a file-explorer dialog opens to pick one.",
    )
    parser.add_argument(
        "--detector",
        choices=["content", "adaptive"],
        default="content",
        help="Detection algorithm. 'content' = classic cut detection (default). "
             "'adaptive' = better for fast pans/camera motion.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=27.0,
        help="Sensitivity for the 'content' detector. Lower = more cuts detected. Default 27.0.",
    )
    parser.add_argument(
        "--min-length",
        type=float,
        default=0.6,
        dest="min_length",
        help="Minimum shot length in seconds, to avoid tiny false-positive cuts. Default 0.6.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional custom output folder. Defaults to '<movie_name>_shots' next to the movie.",
    )
    args = parser.parse_args()

    movie_arg = args.movie
    if not movie_arg:
        movie_arg = pick_movie_file()
        if not movie_arg:
            sys.exit("No file selected. Exiting.")

    movie_path = Path(movie_arg).expanduser().resolve()
    if not movie_path.is_file():
        sys.exit(f"Error: file not found: {movie_path}")

    if shutil.which("ffmpeg") is None:
        sys.exit(
            "Error: ffmpeg was not found on your PATH.\n"
            "Install it first (e.g. 'brew install ffmpeg' or "
            "'sudo apt install ffmpeg' or download from ffmpeg.org)."
        )

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else movie_path.parent / f"{movie_path.stem}_shots"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing '{movie_path.name}' for shot boundaries...")
    scene_list = detect_shots(
        str(movie_path),
        detector_name=args.detector,
        threshold=args.threshold,
        min_scene_len=args.min_length,
    )

    if not scene_list:
        sys.exit("No shots detected. Try lowering --threshold or using --detector adaptive.")

    print(f"Detected {len(scene_list)} shots. Splitting into '{output_dir}'...")

    # This produces files like: <movie_stem>-Scene-001.mp4, -Scene-002.mp4, ...
    split_video_ffmpeg(
        str(movie_path),
        scene_list,
        output_dir=str(output_dir),
        show_progress=True,
    )

    print(f"Done. {len(scene_list)} shot files written to: {output_dir}")

    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Done",
            f"{len(scene_list)} shots extracted.\n\nSaved to:\n{output_dir}",
        )
        root.destroy()
    except tk.TclError:
        pass  # no display available (e.g. headless server) — console message is enough


if __name__ == "__main__":
    main()