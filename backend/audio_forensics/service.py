"""
TruthLens - Audio & Text Forensics Core Service
Unified interface coordinating audio extraction, acoustic deepfake detection,
transcription, text forensics, and suspicious segment identification.
"""

from pathlib import Path
from .extractor import extract_audio_from_video, load_audio_signal
from .acoustic_detector import detect_synthetic_voice
from .transcription import transcribe_audio
from .text_forensics import analyze_transcript
from .segment_forensics import detect_suspicious_segments


def analyze_audio(video_or_audio_path: str | Path) -> dict:
    """
    Main forensic entrypoint. Analyzes an uploaded video or audio file.
    
    Args:
        video_or_audio_path: Path to video (MP4, AVI, MOV) or audio (WAV, MP3) file.
        
    Returns:
        dict: Standardized multimodal result dictionary:
            - status: "completed"
            - manipulation_score: Combined synthetic suspicion score (0.0 - 1.0)
            - confidence: Detector confidence (0.0 - 1.0)
            - findings: List of key forensic indicators
            - transcript: Extracted speech transcript
            - suspicious_timestamps: List of timestamp intervals with reasons
            - acoustic_analysis: Complete acoustic breakdown
            - text_forensics: Speech-to-text consistency and linguistic markers
            - extracted_audio_path: Path to standardized WAV file
            - verdict: Summary classification
            - explanation: Detailed forensic interpretation
    """
    input_path = Path(video_or_audio_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Media file not found: {input_path}")

    # 1. Audio Extraction and Standardization (16kHz mono WAV)
    extracted_wav = extract_audio_from_video(input_path)
    audio_signal, sample_rate = load_audio_signal(extracted_wav)
    duration_sec = len(audio_signal) / float(sample_rate)

    # 2. Synthetic Voice Acoustic Analysis
    acoustic_results = detect_synthetic_voice(audio_signal, sample_rate)

    # 3. Speech-to-Text Transcription
    transcription_results = transcribe_audio(extracted_wav)
    transcript = transcription_results.get("transcript", "")

    # 4. Text & Speech Consistency Forensics
    text_results = analyze_transcript(
        transcript=transcript,
        audio_duration_seconds=duration_sec
    )

    # 5. Segment-level Suspicious Timestamp Detection
    suspicious_segments = detect_suspicious_segments(
        audio=audio_signal,
        sr=sample_rate,
        segment_duration_sec=3.0,
        hop_duration_sec=2.0
    )

    # 6. Combined Manipulation & Confidence Scoring
    # Weight: 70% acoustic physical cues, 30% text linguistic markers
    acoustic_score = acoustic_results.get("manipulation_score", 0.10)
    text_score = text_results.get("text_manipulation_score", 0.10)
    combined_score = round(0.70 * acoustic_score + 0.30 * text_score, 3)

    detector_confidence = acoustic_results.get("confidence", 0.80)

    # Aggregate key findings for TruthLens cross-modal correlation
    findings = []
    findings.extend(acoustic_results.get("findings", []))
    findings.extend(text_results.get("findings", []))

    if suspicious_segments:
        findings.append(f"Identified {len(suspicious_segments)} suspicious audio timestamp segments.")

    # High-level verdict
    if combined_score >= 0.70:
        verdict = "High Synthetic Voice Suspicion"
        summary = (
            "Elevated acoustic and/or linguistic manipulation indicators detected. "
            "Evidence suggests potential AI voice cloning or synthetic speech generation."
        )
    elif combined_score >= 0.40:
        verdict = "Moderate Suspicion / Inconclusive"
        summary = (
            "Some acoustic and textual irregularities present. Recommend manual forensic review."
        )
    else:
        verdict = "Low Suspicion (Authentic Indicators)"
        summary = (
            "Acoustic prosody, vocal micro-perturbations, and linguistic structure are consistent "
            "with natural human speech."
        )

    return {
        "status": "completed",
        "manipulation_score": combined_score,
        "confidence": detector_confidence,
        "verdict": verdict,
        "explanation": summary,
        "findings": findings,
        "transcript": transcript,
        "speech_segments": transcription_results.get("segments", []),
        "suspicious_timestamps": suspicious_segments,
        "acoustic_analysis": acoustic_results,
        "text_forensics": text_results,
        "duration_seconds": round(duration_sec, 2),
        "sample_rate": sample_rate,
        "extracted_audio_path": str(extracted_wav)
    }
