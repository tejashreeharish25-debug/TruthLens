
import json
from pathlib import Path
from video_analysis import analyze_video

# Folder containing sample videos
sample_folder = Path("sample_videos")

supported_formats = [".mp4", ".avi", ".mov", ".mkv"]

if not sample_folder.exists():
    print("sample_videos folder not found")

else:
    video_files = [
        file for file in sample_folder.iterdir()
        if file.suffix.lower() in supported_formats
    ]

    if not video_files:
        print("No sample video found in sample_videos folder")

    else:
        sample_video = video_files[0]

        print("Testing video:", sample_video.name)

        video_bytes = sample_video.read_bytes()

        result = analyze_video(
            video_bytes,
            filename=sample_video.name
        )

        print("\nVideo Analysis Result:")
        print(json.dumps(result, indent=4))
