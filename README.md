
# Video Metadata Extractor

A Python script that uses `ffprobe` to extract metadata from video files and generates an Excel report with details like resolution, audio/video codecs, frame rate, HDR status, and more.

## Features
- Extracts detailed metadata for video files, including audio track information (track numbers, codecs, languages).
- Outputs an Excel file with structured metadata.
- Supports multiple directories for scanning.

## Requirements
- Python 3.x
- `ffmpeg` installed and accessible via `ffprobe`.
- `openpyxl` library for Excel file creation.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/video-metadata-extractor.git
   ```
2. Navigate to the repository directory:
   ```bash
   cd video-metadata-extractor
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Update the `dirs` variable in the script with your directory paths.
2. Run the script:
   ```bash
   python3 video_metadata_extractor.py
   ```
3. The Excel report will be saved as `video_metadata.xlsx` in the current directory.

## Example Output
The generated Excel file contains columns like:
- Full file path
- File size in GB
- Resolution (e.g., `1920x1080`)
- Audio tracks (with track numbers, codecs, and languages)
- Video codec
- Video profile
- Bitrate (in kbps)
- Container type
- Frame rate (e.g., `23.976 fps`)
- HDR/SDR status

## Contributing
Feel free to fork the repository and submit pull requests. Issues and feature requests are welcome!

## License
This project is licensed under the [MIT License](LICENSE).
