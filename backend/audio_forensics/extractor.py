"""
TruthLens - Audio Extraction Module
Extracts high-fidelity audio from video files (MP4, AVI, MOV, MKV)
and standardizes to 16 kHz mono 16-bit PCM WAV for forensic analysis.
"""

from pathlib import Path
import subprocess
import shutil
import wave
import numpy as np


def _find_ffmpeg_executable() -> str:
    """Locate the ffmpeg executable from PATH or bundled imageio-ffmpeg."""
    # Check if ffmpeg is in PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg

    # Try imageio_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass

    raise RuntimeError(
        "FFmpeg is not available. Please install imageio-ffmpeg or ensure ffmpeg is in PATH."
    )


def extract_audio_from_video(
    video_path: str | Path,
    output_wav_path: str | Path | None = None,
    target_sample_rate: int = 16000
) -> Path:
    """
    Extracts audio from video or converts input audio to standardized WAV.
    
    Args:
        video_path: Path to the input video (or audio) file.
        output_wav_path: Optional destination path. If None, creates a .wav in the same directory.
        target_sample_rate: Standard analysis sample rate (default: 16000 Hz, 16-bit mono).
        
    Returns:
        Path to the extracted WAV file.
    """
    input_path = Path(video_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_wav_path is None:
        dest_dir = input_path.parent / "extracted_audio"
        dest_dir.mkdir(parents=True, exist_ok=True)
        out_path = dest_dir / f"{input_path.stem}_audio.wav"
    else:
        out_path = Path(output_wav_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = _find_ffmpeg_executable()

    # FFmpeg command: convert input to 16kHz, mono (ac 1), 16-bit PCM WAV (pcm_s16le)
    cmd = [
        ffmpeg_bin,
        "-y",               # Overwrite output without asking
        "-i", str(input_path),
        "-vn",              # Disable video stream
        "-acodec", "pcm_s16le",
        "-ar", str(target_sample_rate),
        "-ac", "1",         # Convert to single channel (mono)
        str(out_path)
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        # Fallback to moviepy if ffmpeg direct call had an issue
        try:
            from moviepy import AudioFileClip
            clip = AudioFileClip(str(input_path))
            clip.write_audiofile(
                str(out_path),
                fps=target_sample_rate,
                nbytes=2,
                codec='pcm_s16le',
                ffmpeg_params=["-ac", "1"],
                logger=None
            )
            clip.close()
        except Exception as fallback_err:
            raise RuntimeError(
                f"Audio extraction failed for {input_path.name}: {result.stderr or fallback_err}"
            )

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Audio extraction produced an empty or missing file: {out_path}")

    return out_path


def load_audio_signal(wav_path: str | Path) -> tuple[np.ndarray, int]:
    """
    Reads a WAV file and returns normalized floating point signal (-1.0 to 1.0) and sample rate.
    Uses standard library wave module and numpy for zero-dependency speed and reliability.
    """
    file_path = Path(wav_path).resolve()
    with wave.open(str(file_path), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    # Convert bytes to numpy array according to sample width
    if sampwidth == 2:  # 16-bit PCM
        audio = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:  # 32-bit PCM
        audio = np.frombuffer(raw_bytes, dtype=np.int32).astype(np.float32) / 2147483648.0
    elif sampwidth == 1:  # 8-bit unsigned
        audio = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth * 8}-bit")

    # If multi-channel, downmix to mono
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)

    return audio, framerate
