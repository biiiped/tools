#!/usr/bin/env python3
"""
stitch_videos.py

Asks you for a folder, finds every video file in it, and stitches them
together (in name order) into a single .mp4 saved right next to the folder.

Requirements:
    - Python 3.8+
    - ffmpeg installed and available on your PATH
      (Windows: https://ffmpeg.org/download.html, then add to PATH
       macOS:   brew install ffmpeg
       Linux:   sudo apt install ffmpeg)
    - tkinter (usually included with Python) for the folder-picker popup.
      If tkinter isn't available, the script just asks you to type/paste
      the folder path instead.

Usage:
    python stitch_videos.py
"""

import os
import re
import subprocess
import sys
import tempfile

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v",
    ".flv", ".wmv", ".mpg", ".mpeg", ".3gp", ".ts",
}


def natural_key(s: str):
    """Sort 'clip2' before 'clip10' instead of alphabetically."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def ask_for_folder() -> str:
    """Try a native folder-picker dialog; fall back to typed input."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select the folder of videos to stitch")
        root.destroy()
        if folder:
            return folder
    except Exception:
        pass

    # Fallback: plain console prompt
    folder = input("Enter the path to the folder containing your videos: ").strip().strip('"')
    return folder


def find_videos(folder: str):
    files = [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
        and os.path.isfile(os.path.join(folder, f))
    ]
    files.sort(key=natural_key)
    return [os.path.join(folder, f) for f in files]


def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit(
            "ERROR: ffmpeg was not found on your PATH.\n"
            "Install it first (see the comment at the top of this script)."
        )


def has_audio_stream(video: str) -> bool:
    """Return True if the file has at least one audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0",
        video,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return bool(result.stdout.strip())


def stitch(videos, output_path, log_dir):
    """
    Concatenate videos by re-encoding them to a common format first.
    This is slower than a raw stream copy, but it works even when the
    clips have different resolutions/codecs/frame rates, which is the
    usual reason a naive concat fails.
    """
    with tempfile.TemporaryDirectory() as tmp:
        normalized = []
        for i, video in enumerate(videos):
            out = os.path.join(tmp, f"norm_{i:04d}.ts")
            print(f"[{i + 1}/{len(videos)}] Normalizing: {os.path.basename(video)}")

            video_filter = (
                "scale=1920:1080:force_original_aspect_ratio=decrease,"
                "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1"
            )

            if has_audio_stream(video):
                cmd = [
                    "ffmpeg", "-y", "-i", video,
                    "-vf", video_filter,
                    "-r", "30",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
                    "-f", "mpegts",
                    out,
                ]
            else:
                # No audio track in the source: synthesize silence so every
                # normalized clip has a matching audio stream for concat.
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-shortest",
                    "-vf", video_filter,
                    "-r", "30",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
                    "-f", "mpegts",
                    out,
                ]

            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode != 0:
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(
                    log_dir, f"error_{i:04d}_{os.path.basename(video)}.log"
                )
                with open(log_path, "wb") as f:
                    f.write(result.stderr)
                print(f"  WARNING: failed to process this file, skipping it.")
                print(f"  Full ffmpeg log saved to: {log_path}")
                tail = result.stderr.decode(errors="ignore").strip().splitlines()[-5:]
                for line in tail:
                    print(f"    {line}")
                continue
            normalized.append(out)

        if not normalized:
            sys.exit("ERROR: no video could be processed successfully.")

        print("Concatenating everything into the final file...")
        concat_input = "concat:" + "|".join(normalized)
        cmd = [
            "ffmpeg", "-y", "-i", concat_input,
            "-c:v", "copy", "-c:a", "copy", "-bsf:a", "aac_adtstoasc",
            output_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode != 0:
            sys.exit(
                "ERROR: final concatenation step failed.\n"
                + result.stderr.decode(errors="ignore")[-1500:]
            )


def main():
    check_ffmpeg()

    folder = ask_for_folder()
    if not folder or not os.path.isdir(folder):
        sys.exit(f"'{folder}' is not a valid folder.")
    folder = os.path.abspath(folder)

    videos = find_videos(folder)
    if not videos:
        sys.exit(f"No video files found in: {folder}")

    print(f"Found {len(videos)} video(s):")
    for v in videos:
        print(f"  - {os.path.basename(v)}")

    # Output mp4 goes beside the folder (i.e. in its parent directory),
    # named after the folder itself.
    parent_dir = os.path.dirname(folder)
    folder_name = os.path.basename(folder)
    output_path = os.path.join(parent_dir, f"{folder_name}_stitched.mp4")
    log_dir = os.path.join(parent_dir, f"{folder_name}_stitch_errors")

    stitch(videos, output_path, log_dir)

    print(f"\nDone! Stitched video saved to:\n{output_path}")


if __name__ == "__main__":
    main()