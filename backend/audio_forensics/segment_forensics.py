"""
TruthLens - Segment-level Audio Forensics Module
Slices audio into time windows, evaluates micro-acoustic properties per slice,
and flags suspicious timestamps with actionable forensic explanations.
"""

import numpy as np
from .acoustic_detector import _extract_pitch_contour, _compute_spectral_features


def format_timestamp(seconds: float) -> str:
    """Formats seconds into MM:SS string."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def detect_suspicious_segments(
    audio: np.ndarray,
    sr: int,
    segment_duration_sec: float = 3.0,
    hop_duration_sec: float = 2.0
) -> list[dict]:
    """
    Divides audio into sliding segments and flags those with synthetic anomalies.
    
    Args:
        audio: 1D normalized audio signal.
        sr: Sample rate.
        segment_duration_sec: Duration of each analysis segment (default 3.0s).
        hop_duration_sec: Step size between segments (default 2.0s).
        
    Returns:
        List of dicts representing suspicious segments:
            - start_time (float)
            - end_time (float)
            - timestamp (str: "MM:SS - MM:SS")
            - suspicion_score (float 0.0 - 1.0)
            - reason (str)
    """
    total_samples = len(audio)
    duration = total_samples / float(sr)
    seg_samples = int(segment_duration_sec * sr)
    hop_samples = int(hop_duration_sec * sr)

    if total_samples < seg_samples:
        seg_samples = total_samples
        hop_samples = total_samples

    suspicious_segments = []
    start_samp = 0

    while start_samp < total_samples:
        end_samp = min(start_samp + seg_samples, total_samples)
        segment = audio[start_samp:end_samp]
        
        if len(segment) < int(sr * 0.5):
            break

        start_time = start_samp / float(sr)
        end_time = end_samp / float(sr)
        time_label = f"{format_timestamp(start_time)} - {format_timestamp(end_time)}"

        rms = float(np.sqrt(np.mean(segment ** 2)))
        reasons = []
        score = 0.10

        # 1. Near dead silence or abrupt digital cut
        if rms < 0.001:
            zero_count = np.sum(np.abs(segment) < 1e-7)
            if zero_count > (len(segment) * 0.5):
                score += 0.45
                reasons.append("Abrupt digital silence / missing room acoustics")
        else:
            # 2. Check local pitch stability in segment
            f0 = _extract_pitch_contour(segment, sr)
            if len(f0) >= 4:
                std_f0 = float(np.std(f0))
                if std_f0 < 8.0:
                    score += 0.40
                    reasons.append(f"Unnatural pitch monotony ({std_f0:.1f} Hz variance)")
                elif std_f0 > 70.0:
                    score += 0.30
                    reasons.append(f"Erratic pitch fluctuations ({std_f0:.1f} Hz variance)")

            # 3. Spectral anomaly in segment
            spec = _compute_spectral_features(segment, sr)
            if spec.get("has_cutoff"):
                score += 0.25
                reasons.append("Steep high-frequency vocoder cutoff")
            if spec.get("spectral_flatness", 0) > 0.45:
                score += 0.20
                reasons.append("High spectral noise / metallic phase distortion")

        bounded_score = min(score, 0.95)

        # Flag if suspicion is elevated (>= 0.45)
        if bounded_score >= 0.45 or reasons:
            primary_reason = "; ".join(reasons) if reasons else "Elevated acoustic variance"
            suspicious_segments.append({
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "timestamp": time_label,
                "suspicion_score": round(bounded_score, 2),
                "reason": primary_reason
            })

        if hop_samples <= 0 or end_samp >= total_samples:
            break
        start_samp += hop_samples

    return suspicious_segments
