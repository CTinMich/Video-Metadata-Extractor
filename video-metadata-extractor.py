#!/usr/bin/env python3

"""
Script for extracting metadata from video files and generating an Excel report.

Author: Christopher Thomas
Version: 1.0
Date: 2024-12-09

Description:
This script processes video files from specified directories, extracts metadata
using ffprobe, and generates an Excel report. It reports information such as
resolution, audio/video codecs, video bitrate (in kbps), HDR/SDR status,
container type, video frame rate, and more. It also reports all audio tracks
with their codecs, languages, and track numbers.
"""

import os
import glob
import subprocess
import json
from openpyxl import Workbook


def get_metadata(path):
    """Run ffprobe to extract metadata from the file."""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=format_name,bit_rate,duration:stream=index,codec_name,codec_type,profile,width,height,r_frame_rate,bit_rate,color_space,color_transfer,tags',
            '-of', 'json', path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error reading metadata for {path}: {e}")
        return None


def size_in_gb(path):
    """Convert file size to GB."""
    return round(os.path.getsize(path) / (1024 ** 3), 3)


def parse_framerate(rate):
    """Convert frame rate from fraction to fps."""
    try:
        num, denom = map(int, rate.split('/'))
        return f"{num / denom:.3f} fps"
    except:
        return None


def detect_hdr(color, transfer):
    """Guess if the video is HDR or SDR."""
    hdr_keywords = ['bt2020', 'smpte2084', 'arib-std-b67']
    if color or transfer:
        if any(word in (color or '').lower() for word in hdr_keywords):
            return 'HDR'
        if any(word in (transfer or '').lower() for word in hdr_keywords):
            return 'HDR'
    return 'SDR'


def create_report(paths, output_path):
    """Main function to process files and write to Excel."""
    wb = Workbook()
    ws = wb.active

    # Set headers
    ws.append(
        ['Path', 'Size (GB)', 'Resolution', 'Audio Tracks', 'Video Codec', 'Profile', 'Bitrate (kbps)', 'Container',
         'Frame Rate', 'HDR/SDR'])

    # Process paths
    for path in paths:
        print(f"Looking in: {path}")
        for file in glob.iglob(os.path.join(path, '**'), recursive=True):
            if os.path.isfile(file):
                print(f"Working on: {file}")
                meta = get_metadata(file)

                # Defaults
                res = None
                vid_codec = None
                profile = None
                bitrate = None
                framerate = None
                hdr = 'SDR'
                audio_tracks = []

                if meta:
                    fmt = meta.get('format', {})
                    bitrate = fmt.get('bit_rate')
                    if bitrate:
                        bitrate = round(int(bitrate) / 1000, 2)

                    for stream in meta.get('streams', []):
                        if stream.get('codec_type') == 'video':
                            res = f"{stream.get('width')}x{stream.get('height')}"
                            vid_codec = stream.get('codec_name')
                            profile = stream.get('profile')
                            framerate = parse_framerate(stream.get('r_frame_rate'))
                            hdr = detect_hdr(stream.get('color_space'), stream.get('color_transfer'))
                        elif stream.get('codec_type') == 'audio':
                            track_num = stream.get('index')
                            codec = stream.get('codec_name')
                            lang = stream.get('tags', {}).get('language', 'Unknown').upper()
                            audio_tracks.append(f"Track {track_num}/{codec}/{lang}")

                # Add row
                ws.append([
                    file,
                    size_in_gb(file),
                    res,
                    '; '.join(audio_tracks) if audio_tracks else None,
                    vid_codec,
                    profile,
                    bitrate,
                    fmt.get('format_name'),
                    framerate,
                    hdr
                ])

    # Save the Excel report
    if not output_path.endswith('.xlsx'):
        output_path = os.path.join(output_path, "video_metadata.xlsx")
    try:
        wb.save(output_path)
        print(f"Done. Saved report to {output_path}")
    except Exception as e:
        print(f"Error saving report: {e}")


if __name__ == "__main__":
    """
    Main entry point of the script.

    Update the 'dirs' list with directories to scan for video files.
    Update the 'output_path' variable with the desired path for the Excel report.
    Example:
        dirs = ["/path/to/videos", "/another/path/to/videos"]
        output_path = "/path/to/save/report"
    """
    dirs = []  # Add your video directory paths here.
    output_path = ""  # Specify where the Excel report should be saved.

    if not dirs:
        print("Please add your video directory paths to the 'dirs' list in the script.")
    elif not output_path:
        print("Please specify the output path for the Excel report in the 'output_path' variable.")
    else:
        create_report(dirs, output_path)
