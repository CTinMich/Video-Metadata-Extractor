#!/usr/bin/python3

# Simple script to get metadata from videos and save it in Excel.
# This isn't fancy, but it works for what I need.

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
    return round(os.path.getsize(path) / (1024**3), 3)

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

def create_report(paths):
    """Main function to process files and write to Excel."""
    wb = Workbook()
    ws = wb.active

    # Set headers
    ws.append(['Path', 'Size (GB)', 'Resolution', 'Audio Tracks', 'Video Codec', 'Profile', 'Bitrate (kbps)', 'Container', 'Frame Rate', 'HDR/SDR'])

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

    wb.save('video_metadata.xlsx')
    print("Done. Saved as video_metadata.xlsx.")

if __name__ == "__main__":
    # Directories to scan
    dirs = ['/home/pi/usbhdd/Media/Movies', '/home/pi/usbhdd/Media/Movies02']
    create_report(dirs)
