
import cv2
import tempfile
import os


def analyze_video(video_bytes, filename="uploaded_video"):
    findings = []
    temp_path = None
    video = None

    try:
        # Save video temporarily for OpenCV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(video_bytes)
            temp_path = temp_file.name

        # Open video
        video = cv2.VideoCapture(temp_path)

        if not video.isOpened():
            return {
                "modality": "video",
                "status": "error",
                "manipulation_score": None,
                "confidence": None,
                "findings": ["Unable to open video file"]
            }

        # Read video properties
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        duration_seconds = frame_count / fps if fps > 0 else 0

        findings.append("Video successfully opened")
        findings.append(f"Video dimensions: {width} x {height}")
        findings.append(f"Frame rate: {fps:.2f} FPS")
        findings.append(f"Total frames: {frame_count}")
        findings.append(f"Duration: {duration_seconds:.2f} seconds")

        # Select up to 5 sample frames
        sample_count = min(5, frame_count)
        sampled_frames = []

        for i in range(sample_count):
            frame_index = int(
                i * (frame_count - 1) / max(sample_count - 1, 1)
            )

            video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = video.read()

            if success:
                timestamp = frame_index / fps if fps > 0 else 0

                sampled_frames.append({
                    "frame_number": frame_index,
                    "timestamp_seconds": round(timestamp, 2)
                })

        findings.append(
            f"Sampled {len(sampled_frames)} frames for inspection"
        )

        # JSON-compatible result
        result = {
            "modality": "video",
            "status": "completed",
            "manipulation_score": None,
            "confidence": None,
            "findings": findings,
            "video_info": {
                "filename": filename,
                "width": width,
                "height": height,
                "fps": round(fps, 2),
                "total_frames": frame_count,
                "duration_seconds": round(duration_seconds, 2),
                "sampled_frames": sampled_frames,
                "file_size_bytes": len(video_bytes)
            }
        }

        return result

    except Exception as e:
        return {
            "modality": "video",
            "status": "error",
            "manipulation_score": None,
            "confidence": None,
            "findings": [f"Video analysis failed: {str(e)}"]
        }

    finally:
        if video is not None:
            video.release()

        if temp_path is not None and os.path.exists(temp_path):
            os.remove(temp_path)
