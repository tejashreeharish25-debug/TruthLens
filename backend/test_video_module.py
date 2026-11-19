
import cv2
import numpy as np

from video_analysis import analyze_video


def create_test_video():
    output_path = "test_sample_video.mp4"

    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        5.0,
        (100, 80)
    )

    if not writer.isOpened():
        raise RuntimeError("Could not create test video")

    try:
        for i in range(5):
            frame = np.zeros((80, 100, 3), dtype=np.uint8)
            frame[:] = (i * 30, 100, 150)
            writer.write(frame)
    finally:
        writer.release()

    with open(output_path, "rb") as file:
        video_bytes = file.read()

    import os
    os.remove(output_path)

    return video_bytes


def test_analyze_video_success():
    video_bytes = create_test_video()

    result = analyze_video(
        video_bytes,
        filename="test_video.mp4"
    )

    assert result["modality"] == "video"
    assert result["status"] == "completed"
    assert result["video_info"]["filename"] == "test_video.mp4"
    assert result["video_info"]["width"] == 100
    assert result["video_info"]["height"] == 80
    assert result["video_info"]["total_frames"] == 5
    assert len(result["video_info"]["sampled_frames"]) > 0


def test_analyze_video_invalid_file():
    result = analyze_video(b"not a valid video")

    assert result["modality"] == "video"
    assert result["status"] == "error"
    assert len(result["findings"]) > 0
