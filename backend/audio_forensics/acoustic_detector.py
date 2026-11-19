"""
TruthLens - Acoustic & Synthetic Voice Forensics Detector
Analyzes acoustic features: pitch contour, vocal micro-perturbations (jitter/shimmer),
spectral flatness, high-frequency cutoff, and pause distribution to detect AI speech artifacts.
"""

import numpy as np
from scipy import signal


def _extract_pitch_contour(audio: np.ndarray, sr: int, frame_size: int = 1024, hop_size: int = 512) -> np.ndarray:
    """
    Extracts fundamental frequency (F0) contour using autocorrelation over sliding frames.
    Focuses on normal human speech range (75 Hz - 400 Hz).
    """
    min_lag = int(sr / 400.0)  # Max pitch: 400 Hz
    max_lag = int(sr / 75.0)   # Min pitch: 75 Hz
    
    n_frames = (len(audio) - frame_size) // hop_size
    if n_frames <= 0:
        return np.array([])

    f0_estimates = []

    for i in range(n_frames):
        start = i * hop_size
        frame = audio[start : start + frame_size] * np.hanning(frame_size)

        # Check frame energy (ignore near-silent frames)
        energy = np.sum(frame ** 2)
        if energy < 1e-4:
            continue

        # Autocorrelation via FFT for speed
        n_fft = 2 ** int(np.ceil(np.log2(2 * frame_size - 1)))
        fft_val = np.fft.rfft(frame, n=n_fft)
        corr = np.fft.irfft(fft_val * np.conj(fft_val))[:frame_size]

        if max_lag < len(corr) and min_lag < max_lag:
            search_window = corr[min_lag:max_lag]
            peak_lag = np.argmax(search_window) + min_lag
            peak_val = corr[peak_lag]

            # Voicing threshold check
            if corr[0] > 0 and (peak_val / corr[0]) > 0.35:
                f0 = sr / float(peak_lag)
                f0_estimates.append(f0)

    return np.array(f0_estimates)


def _compute_jitter_shimmer(audio: np.ndarray, sr: int) -> tuple[float, float]:
    """
    Estimates cycle-to-cycle frequency variation (Jitter) and amplitude variation (Shimmer).
    Natural human voice typically has Jitter ~ 0.5% - 2.5%, Shimmer ~ 2% - 6%.
    Neural TTS often exhibits unnaturally suppressed jitter (<0.3%) or vocoder instability (>4%).
    """
    frame_size = int(sr * 0.03)  # 30ms frames
    hop_size = int(sr * 0.015)   # 15ms hop
    n_frames = (len(audio) - frame_size) // hop_size
    
    if n_frames < 4:
        return 0.0, 0.0

    peak_amplitudes = []
    periods = []

    for i in range(n_frames):
        start = i * hop_size
        frame = audio[start : start + frame_size]
        amp = np.max(np.abs(frame))
        if amp > 0.02:
            peak_amplitudes.append(amp)
            # Find dominant zero-crossing or peak interval
            zc = np.where(np.diff(np.signbit(frame)))[0]
            if len(zc) >= 2:
                avg_period = np.mean(np.diff(zc)) * 2
                periods.append(avg_period)

    if len(periods) > 5 and len(peak_amplitudes) > 5:
        periods = np.array(periods)
        peak_amplitudes = np.array(peak_amplitudes)
        jitter = float(np.mean(np.abs(np.diff(periods))) / (np.mean(periods) + 1e-6)) * 100.0
        shimmer = float(np.mean(np.abs(np.diff(peak_amplitudes))) / (np.mean(peak_amplitudes) + 1e-6)) * 100.0
        return round(jitter, 3), round(shimmer, 3)

    return 0.0, 0.0


def _compute_spectral_features(audio: np.ndarray, sr: int) -> dict:
    """
    Computes spectral flatness, high-frequency energy ratio, and cutoff frequency.
    Many TTS engines (FastSpeech, VITS, HiFi-GAN) exhibit unnatural high-frequency attenuation
    or artificial phase noise in the 7 kHz - 10 kHz band.
    """
    if len(audio) < 1024:
        return {"spectral_flatness": 0.0, "high_freq_ratio": 0.0, "has_cutoff": False}

    frequencies, times, spec = signal.spectrogram(
        audio,
        fs=sr,
        nperseg=1024,
        noverlap=512,
        mode="magnitude"
    )

    # Power spectrum
    power_spec = spec ** 2 + 1e-12

    # Spectral flatness (geometric mean / arithmetic mean)
    geo_mean = np.exp(np.mean(np.log(power_spec), axis=0))
    arith_mean = np.mean(power_spec, axis=0)
    flatness = float(np.mean(geo_mean / arith_mean))

    # High frequency energy ratio (> 6500 Hz vs Total)
    high_freq_mask = frequencies > 6500
    high_freq_energy = np.sum(power_spec[high_freq_mask, :])
    total_energy = np.sum(power_spec)
    high_freq_ratio = float(high_freq_energy / (total_energy + 1e-12))

    # Detect steep brickwall cutoff (common in 16kHz resampled TTS models)
    energy_by_freq = np.mean(power_spec, axis=1)
    has_cutoff = False
    if len(frequencies) > 10:
        top_quarter = energy_by_freq[int(len(energy_by_freq) * 0.75):]
        has_cutoff = bool(np.mean(top_quarter) < 1e-6 and total_energy > 1.0)

    return {
        "spectral_flatness": round(flatness, 4),
        "high_freq_ratio": round(high_freq_ratio, 4),
        "has_cutoff": has_cutoff
    }


def _analyze_pause_distribution(audio: np.ndarray, sr: int) -> dict:
    """
    Analyzes pause and silence behavior.
    Synthetic audio frequently contains mathematical absolute zeros (digital silence),
    or unnaturally uniform pause durations.
    """
    frame_ms = 20
    frame_len = int(sr * (frame_ms / 1000.0))
    n_frames = len(audio) // frame_len
    if n_frames < 5:
        return {"dead_silence_count": 0, "total_pause_ratio": 0.0, "robotic_pauses": False}

    reshaped = audio[: n_frames * frame_len].reshape(n_frames, frame_len)
    frame_energies = np.sqrt(np.mean(reshaped ** 2, axis=1))

    # Absolute digital zero frames (amplitude < 1e-7)
    dead_silence_frames = np.sum(frame_energies < 1e-6)
    
    # Silence threshold for normal background
    silent_frames = np.sum(frame_energies < 0.005)
    total_pause_ratio = float(silent_frames / n_frames)

    # Check for abrupt digital silences without natural acoustic decay
    robotic_pauses = bool(dead_silence_frames > (0.05 * n_frames))

    return {
        "dead_silence_frames": int(dead_silence_frames),
        "total_pause_ratio": round(total_pause_ratio, 3),
        "robotic_pauses": robotic_pauses
    }


def detect_synthetic_voice(audio: np.ndarray, sr: int) -> dict:
    """
    Full acoustic synthetic voice forensics detector.
    
    Returns:
        dict containing:
            - manipulation_score (0.0 to 1.0)
            - confidence (0.0 to 1.0)
            - pitch_statistics (mean, std, range)
            - acoustic_features (jitter, shimmer, spectral flatness, pauses)
            - findings (list of human-readable forensic observations)
            - explanation
    """
    findings = []
    suspicion_points = 0.0
    total_weights = 1.0

    # 1. Pitch contour analysis
    f0_series = _extract_pitch_contour(audio, sr)
    if len(f0_series) > 8:
        pitch_mean = float(np.mean(f0_series))
        pitch_std = float(np.std(f0_series))
        pitch_range = float(np.ptp(f0_series))

        # Check for robotic pitch monotony (TTS monotonic speech)
        if pitch_std < 14.0:
            suspicion_points += 0.35
            findings.append(
                f"Abnormally low pitch variance (Std: {pitch_std:.1f} Hz). Suggests synthetic voice monotony."
            )
        elif pitch_std > 85.0:
            suspicion_points += 0.20
            findings.append(
                f"Unnatural pitch fluctuations (Std: {pitch_std:.1f} Hz). Potential vocoder pitch distortion."
            )
        else:
            findings.append(
                f"Pitch intonation within standard human range (Mean: {pitch_mean:.1f} Hz, Std: {pitch_std:.1f} Hz)."
            )
    else:
        pitch_mean, pitch_std, pitch_range = 0.0, 0.0, 0.0
        findings.append("Insufficient voiced frames to compute pitch contour.")

    # 2. Vocal micro-perturbations (Jitter & Shimmer)
    jitter, shimmer = _compute_jitter_shimmer(audio, sr)
    if jitter > 0:
        if jitter < 0.25:
            suspicion_points += 0.25
            findings.append(
                f"Unnaturally low vocal jitter ({jitter}%). Typical of mathematical neural vocoder synthesis."
            )
        elif jitter > 4.5:
            suspicion_points += 0.20
            findings.append(
                f"Elevated frequency jitter ({jitter}%). Possible voice conversion artifacts."
            )

        if shimmer < 1.0:
            suspicion_points += 0.15
            findings.append(
                f"Artificially consistent vocal amplitude shimmer ({shimmer}%)."
            )

    # 3. Spectral analysis
    spectral = _compute_spectral_features(audio, sr)
    if spectral["has_cutoff"]:
        suspicion_points += 0.20
        findings.append("Sharp high-frequency cutoff detected, common in 16kHz neural vocoder pipelines.")
    
    if spectral["spectral_flatness"] > 0.40:
        suspicion_points += 0.15
        findings.append("Elevated spectral flatness indicating synthetic hiss or phase vocoder artifacts.")

    # 4. Silence & pause analysis
    pauses = _analyze_pause_distribution(audio, sr)
    if pauses["robotic_pauses"]:
        suspicion_points += 0.25
        findings.append(
            f"Detected {pauses['dead_silence_frames']} frames of unnatural zero-energy digital silence."
        )

    # Bound manipulation score between 0.05 and 0.95
    manipulation_score = min(max(suspicion_points, 0.08), 0.95)

    # Calculate forensic confidence based on audio length and available signal
    duration_sec = len(audio) / float(sr)
    if duration_sec < 2.0:
        confidence = 0.50
        findings.append("Warning: Short audio snippet (< 2s) limits acoustic forensic confidence.")
    elif duration_sec < 5.0:
        confidence = 0.75
    else:
        confidence = 0.88

    # Summary interpretation
    if manipulation_score >= 0.70:
        verdict = "High Synthetic Voice Suspicion"
        explanation = (
            "Multiple acoustic anomalies detected (pitch monotony/artifacts, unnatural micro-tremor, "
            "or digital silence) characteristic of AI-generated or cloned voice."
        )
    elif manipulation_score >= 0.40:
        verdict = "Moderate Suspicion / Inconclusive"
        explanation = (
            "Some acoustic irregularities observed. Could be influenced by audio compression, "
            "microphone noise, or mild voice processing."
        )
    else:
        verdict = "Likely Natural Speech"
        explanation = (
            "Acoustic features display natural human vocal variations, prosodic pitch contour, "
            "and organic background decay."
        )

    return {
        "manipulation_score": round(manipulation_score, 3),
        "confidence": round(confidence, 2),
        "verdict": verdict,
        "explanation": explanation,
        "findings": findings,
        "pitch_statistics": {
            "mean_f0_hz": round(pitch_mean, 1),
            "std_f0_hz": round(pitch_std, 1),
            "range_f0_hz": round(pitch_range, 1)
        },
        "acoustic_features": {
            "jitter_percent": jitter,
            "shimmer_percent": shimmer,
            "spectral_flatness": spectral["spectral_flatness"],
            "high_freq_ratio": spectral["high_freq_ratio"],
            "has_cutoff": spectral["has_cutoff"],
            "dead_silence_frames": pauses["dead_silence_frames"],
            "pause_ratio": pauses["total_pause_ratio"]
        }
    }
