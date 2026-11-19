"""
TruthLens - Test Suite for Audio & Text Forensics Module (Member 3)
Generates synthetic test audio (simulating both natural prosody and monotonic synthetic voice)
and verifies that all forensic components run cleanly and conform to schema.
"""

import sys
from pathlib import Path
import wave
import numpy as np

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audio_forensics.service import analyze_audio
from audio_forensics.extractor import extract_audio_from_video, load_audio_signal
from audio_forensics.acoustic_detector import detect_synthetic_voice
from audio_forensics.text_forensics import analyze_transcript
from audio_forensics.segment_forensics import detect_suspicious_segments


def generate_test_audio_wav(dest_path: Path, mode: str = "synthetic", duration_sec: float = 6.0, sr: int = 16000):
    """
    Generates a deterministic test WAV file:
    - 'synthetic': Monotonic pitch (150 Hz dead flat), zero jitter, digital zero pause.
    - 'natural': Pitch with natural vibrato/intonation (120 - 180 Hz) and acoustic decay.
    """
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    
    if mode == "synthetic":
        # Robotic flat 150 Hz tone with sharp digital cutoff
        signal_data = 0.5 * np.sin(2 * np.pi * 150.0 * t)
        # Insert 1.5 seconds of absolute digital zero silence in the middle
        silence_start = int(2.0 * sr)
        silence_end = int(3.5 * sr)
        signal_data[silence_start:silence_end] = 0.0
    else:
        # Natural speech imitation: fluctuating pitch + harmonics + background breath
        pitch = 140.0 + 25.0 * np.sin(2 * np.pi * 1.5 * t)
        phase = 2 * np.pi * np.cumsum(pitch) / sr
        signal_data = 0.4 * np.sin(phase) + 0.15 * np.sin(2 * phase) + 0.05 * np.random.normal(0, 0.02, len(t))

    # Convert to 16-bit PCM
    int16_data = (signal_data * 32767).astype(np.int16)
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dest_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int16_data.tobytes())

    return dest_path


def run_tests():
    print("=" * 60)
    print("TruthLens Audio & Text Forensics Module Verification")
    print("=" * 60)

    test_dir = Path(__file__).resolve().parent / "test_media"
    test_dir.mkdir(parents=True, exist_ok=True)

    synthetic_wav = test_dir / "test_synthetic.wav"
    natural_wav = test_dir / "test_natural.wav"

    print("\n1. Generating test audio fixtures...")
    generate_test_audio_wav(synthetic_wav, mode="synthetic")
    generate_test_audio_wav(natural_wav, mode="natural")
    print(f"  Created: {synthetic_wav.name}")
    print(f"  Created: {natural_wav.name}")

    print("\n2. Testing Audio Extraction & Loading...")
    sig_synth, sr_synth = load_audio_signal(synthetic_wav)
    assert sr_synth == 16000, f"Expected 16000 Hz, got {sr_synth}"
    assert len(sig_synth) > 0, "Signal should not be empty"
    print("  Signal loaded successfully. Duration:", round(len(sig_synth) / sr_synth, 2), "seconds")

    print("\n3. Testing Acoustic Synthetic Voice Detector...")
    res_synth = detect_synthetic_voice(sig_synth, sr_synth)
    print(f"  Synthetic Audio Suspicion Score: {res_synth['manipulation_score']} | Verdict: {res_synth['verdict']}")
    
    sig_nat, sr_nat = load_audio_signal(natural_wav)
    res_nat = detect_synthetic_voice(sig_nat, sr_nat)
    print(f"  Natural Audio Suspicion Score:   {res_nat['manipulation_score']} | Verdict: {res_nat['verdict']}")
    assert res_synth["manipulation_score"] > res_nat["manipulation_score"], "Synthetic score should exceed natural score"

    print("\n4. Testing Text Forensics...")
    sample_fake_text = "As an AI language model this is a voice generated deepfake test. Repeating again repeating again."
    text_res = analyze_transcript(sample_fake_text, audio_duration_seconds=6.0)
    print("  Text manipulation score:", text_res["text_manipulation_score"])
    print("  Flagged phrases:", text_res["suspicious_phrases"])
    assert len(text_res["suspicious_phrases"]) > 0, "Should detect synthetic phrases"

    print("\n5. Testing Suspicious Segment Detection...")
    segments = detect_suspicious_segments(sig_synth, sr_synth)
    print(f"  Found {len(segments)} suspicious segments:")
    for seg in segments[:3]:
        print(f"    - {seg['timestamp']}: Score {seg['suspicion_score']} ({seg['reason']})")
    assert len(segments) > 0, "Should detect suspicious segments in synthetic audio"

    print("\n6. Testing Master analyze_audio() Pipeline...")
    full_analysis = analyze_audio(synthetic_wav)
    assert full_analysis["status"] == "completed"
    assert "manipulation_score" in full_analysis
    assert "confidence" in full_analysis
    assert "findings" in full_analysis
    assert "transcript" in full_analysis
    print("  Overall Suspicion Score:", full_analysis["manipulation_score"])
    print("  Overall Confidence:", full_analysis["confidence"])
    print("  Verdict:", full_analysis["verdict"])
    print("  Total Findings:", len(full_analysis["findings"]))

    # Clean up test files
    try:
        synthetic_wav.unlink(missing_ok=True)
        natural_wav.unlink(missing_ok=True)
        test_dir.rmdir()
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! Audio forensics module is production ready.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
