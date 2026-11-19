
import wave
import numpy as np
import pytest
from pathlib import Path

from audio_forensics.service import analyze_audio
from audio_forensics.extractor import load_audio_signal
from audio_forensics.acoustic_detector import detect_synthetic_voice
from audio_forensics.text_forensics import analyze_transcript
from audio_forensics.segment_forensics import detect_suspicious_segments


def generate_test_audio_wav(
    dest_path: Path,
    mode: str = "synthetic",
    duration_sec: float = 6.0,
    sr: int = 16000
):
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)

    if mode == "synthetic":
        signal_data = 0.5 * np.sin(2 * np.pi * 150.0 * t)
        silence_start = int(2.0 * sr)
        silence_end = int(3.5 * sr)
        signal_data[silence_start:silence_end] = 0.0
    else:
        pitch = 140.0 + 25.0 * np.sin(2 * np.pi * 1.5 * t)
        phase = 2 * np.pi * np.cumsum(pitch) / sr
        rng = np.random.default_rng(42)
        signal_data = (
            0.4 * np.sin(phase)
            + 0.15 * np.sin(2 * phase)
            + 0.05 * rng.normal(0, 0.02, len(t))
        )

    int16_data = (signal_data * 32767).astype(np.int16)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dest_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int16_data.tobytes())

    return dest_path


@pytest.fixture
def audio_files(tmp_path):
    synthetic = generate_test_audio_wav(
        tmp_path / "test_synthetic.wav", mode="synthetic"
    )
    natural = generate_test_audio_wav(
        tmp_path / "test_natural.wav", mode="natural"
    )
    return synthetic, natural


def test_load_audio_signal(audio_files):
    synthetic, _ = audio_files

    signal, sample_rate = load_audio_signal(synthetic)

    assert sample_rate == 16000
    assert len(signal) > 0


def test_synthetic_voice_detector(audio_files):
    synthetic, natural = audio_files

    synthetic_signal, synthetic_sr = load_audio_signal(synthetic)
    natural_signal, natural_sr = load_audio_signal(natural)

    synthetic_result = detect_synthetic_voice(
        synthetic_signal, synthetic_sr
    )
    natural_result = detect_synthetic_voice(
        natural_signal, natural_sr
    )

    assert "manipulation_score" in synthetic_result
    assert "verdict" in synthetic_result
    assert synthetic_result["manipulation_score"] > natural_result["manipulation_score"]


def test_text_forensics():
    sample_text = (
        "As an AI language model this is a voice generated "
        "deepfake test. Repeating again repeating again."
    )

    result = analyze_transcript(
        sample_text, audio_duration_seconds=6.0
    )

    assert "text_manipulation_score" in result
    assert len(result["suspicious_phrases"]) > 0


def test_suspicious_segment_detection(audio_files):
    synthetic, _ = audio_files
    signal, sample_rate = load_audio_signal(synthetic)

    segments = detect_suspicious_segments(signal, sample_rate)

    assert isinstance(segments, list)
    assert len(segments) > 0


def test_analyze_audio_pipeline(audio_files):
    synthetic, _ = audio_files

    result = analyze_audio(synthetic)

    assert result["status"] == "completed"
    assert "manipulation_score" in result
    assert "confidence" in result
    assert "findings" in result
    assert "transcript" in result
    assert "verdict" in result
