"""
TruthLens - Speech-to-Text Transcription Module
Extracts verbatim speech transcripts with start/end segment timestamps using Whisper.
Includes defensive CPU-friendly fallbacks to ensure zero failure on constrained environments.
"""

from pathlib import Path
import numpy as np


_WHISPER_MODEL = None


def _get_whisper_model(model_name: str = "tiny"):
    """
    Lazy loader for OpenAI Whisper model.
    Defaults to 'tiny' for fast execution on standard Windows laptops without requiring a GPU.
    """
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            import whisper
            _WHISPER_MODEL = whisper.load_model(model_name)
        except Exception:
            _WHISPER_MODEL = False
    return _WHISPER_MODEL


def transcribe_audio(
    audio_path: str | Path,
    model_name: str = "tiny"
) -> dict:
    """
    Transcribes audio into timestamped speech segments and full text.
    
    Args:
        audio_path: Path to the WAV audio file.
        model_name: Whisper model size ('tiny', 'base', 'small').
        
    Returns:
        dict:
            - transcript: Full transcribed text string
            - segments: List of [{"id": int, "start": float, "end": float, "text": str}]
            - engine: "whisper" or "heuristic_segmenter"
            - language: Detected language
    """
    file_path = Path(audio_path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    model = _get_whisper_model(model_name)

    # 1. Primary path: OpenAI Whisper
    if model:
        try:
            result = model.transcribe(
                str(file_path),
                fp16=False,            # CPU-compatible
                language=None          # Auto-detect language
            )
            segments = []
            for seg in result.get("segments", []):
                segments.append({
                    "id": seg.get("id", 0),
                    "start": round(seg.get("start", 0.0), 2),
                    "end": round(seg.get("end", 0.0), 2),
                    "text": seg.get("text", "").strip()
                })

            return {
                "transcript": result.get("text", "").strip(),
                "segments": segments,
                "language": result.get("language", "en"),
                "engine": f"whisper-{model_name}"
            }
        except Exception as e:
            # If whisper run encountered a runtime error, fall through to fallback
            print(f"Whisper runtime notice: {e}, using acoustic fallback segmenter.")

    # 2. Resilient Fallback: Energy-based speech segmenter
    # Guarantees the application never crashes even before large torch models are downloaded
    from .extractor import load_audio_signal
    audio, sr = load_audio_signal(file_path)
    duration = len(audio) / float(sr)

    # Break into natural 3-second speech intervals
    interval = 3.0
    segments = []
    seg_id = 0
    t = 0.0
    while t < duration:
        end_t = min(t + interval, duration)
        start_samp = int(t * sr)
        end_samp = int(end_t * sr)
        chunk = audio[start_samp:end_samp]
        rms = float(np.sqrt(np.mean(chunk ** 2))) if len(chunk) > 0 else 0.0
        
        status_label = "[Voiced speech activity detected]" if rms > 0.01 else "[Low energy / Pause]"
        segments.append({
            "id": seg_id,
            "start": round(t, 2),
            "end": round(end_t, 2),
            "text": status_label
        })
        seg_id += 1
        t += interval

    full_text = " ".join([s["text"] for s in segments if "Voiced" in s["text"]])
    if not full_text:
        full_text = "[No speech activity identified]"

    return {
        "transcript": full_text,
        "segments": segments,
        "language": "en",
        "engine": "energy-segmenter-fallback"
    }
