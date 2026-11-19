"""
TruthLens - Audio and Text Forensics Package (Member 3)
"""

from .service import analyze_audio
from .extractor import extract_audio_from_video, load_audio_signal
from .acoustic_detector import detect_synthetic_voice
from .transcription import transcribe_audio
from .text_forensics import analyze_transcript
from .segment_forensics import detect_suspicious_segments

__all__ = [
    "analyze_audio",
    "extract_audio_from_video",
    "load_audio_signal",
    "detect_synthetic_voice",
    "transcribe_audio",
    "analyze_transcript",
    "detect_suspicious_segments",
]
