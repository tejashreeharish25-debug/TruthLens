"""
TruthLens - Multimodal Digital Forensics & Deepfake Video Detection
Member 3: Audio and Text Forensics Interactive Streamlit Application
"""

import sys
import os
import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# Add backend directory to sys.path so audio_forensics package is discoverable
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from audio_forensics.service import analyze_audio
from audio_forensics.extractor import load_audio_signal

# Page Configuration
st.set_page_config(
    page_title="TruthLens - Audio & Text Forensics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5, #7E57C2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #8892B0;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E222D;
        border: 1px solid #2E3440;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .badge-safe {
        background-color: #1b5e20;
        color: #a5d6a7;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
    }
    .badge-warn {
        background-color: #f57f17;
        color: #fff9c4;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
    }
    .badge-danger {
        background-color: #b71c1c;
        color: #ffcdd2;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown('<div class="main-header">TruthLens // Audio & Text Forensics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multimodal Deepfake Detection • Synthetic Voice & Linguistic Analysis Module (Member 3)</div>', unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/sound-wave.png", width=64)
    st.subheader("Forensic Settings")
    
    sensitivity = st.slider("Anomaly Sensitivity", min_value=0.3, max_value=0.9, value=0.6, step=0.05)
    sample_rate_target = st.selectbox("Audio Target Resampling", [16000, 22050, 44100], index=0)
    
    st.markdown("---")
    st.subheader("System Status")
    st.success("✅ Extraction Engine: FFmpeg / PCM-16")
    st.success("✅ Acoustic Forensics: F0 / Jitter / Spectral")
    st.info("ℹ️ Speech Recognition: Whisper / CPU Resilient")
    st.markdown("---")
    st.markdown("**Hackathon Project:** TruthLens  \n**Module:** Audio & Text Forensics (Member 3)")

# File Upload Section
upload_tab1, upload_tab2 = st.tabs(["📁 Upload Video / Audio", "🧪 Test with Synthetic & Natural Audio Sample"])

file_to_analyze = None
temp_file_path = None

with upload_tab1:
    uploaded_file = st.file_uploader(
        "Upload Video (MP4, AVI, MOV, MKV) or Audio (WAV, MP3)",
        type=["mp4", "avi", "mov", "mkv", "wav", "mp3", "m4a", "ogg"],
        help="Audio is automatically extracted, standardized to 16kHz mono, and forensically analyzed."
    )
    if uploaded_file is not None:
        file_suffix = Path(uploaded_file.name).suffix.lower()
        temp_dir = Path(tempfile.gettempdir()) / "truthlens_uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_dir / uploaded_file.name
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_to_analyze = temp_file_path

with upload_tab2:
    st.write("Generate a simulated sample directly inside the app to evaluate the forensic engine:")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("Generate Synthetic Voice Demo Audio (Monotonic F0 & Zero Pauses)"):
            t_dir = Path(tempfile.gettempdir()) / "truthlens_uploads"
            t_dir.mkdir(parents=True, exist_ok=True)
            demo_path = t_dir / "demo_synthetic_sample.wav"
            
            # Deterministic synthetic audio creation
            sr = 16000
            t = np.linspace(0, 5.0, sr * 5, endpoint=False)
            sig = 0.5 * np.sin(2 * np.pi * 150.0 * t)
            sig[int(sr * 1.5):int(sr * 2.8)] = 0.0  # digital zero gap
            int16_sig = (sig * 32767).astype(np.int16)
            import wave
            with wave.open(str(demo_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(int16_sig.tobytes())
            file_to_analyze = demo_path
            st.session_state["demo_sample"] = demo_path
            st.success("Generated `demo_synthetic_sample.wav`")

    with col_demo2:
        if st.button("Generate Natural Human Speech Simulation (Pitch Fluctuations)"):
            t_dir = Path(tempfile.gettempdir()) / "truthlens_uploads"
            t_dir.mkdir(parents=True, exist_ok=True)
            demo_path = t_dir / "demo_natural_sample.wav"
            
            sr = 16000
            t = np.linspace(0, 5.0, sr * 5, endpoint=False)
            pitch = 145.0 + 30.0 * np.sin(2 * np.pi * 1.5 * t)
            phase = 2 * np.pi * np.cumsum(pitch) / sr
            sig = 0.4 * np.sin(phase) + 0.15 * np.sin(2 * phase) + 0.04 * np.random.normal(0, 0.02, len(t))
            int16_sig = (sig * 32767).astype(np.int16)
            import wave
            with wave.open(str(demo_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(int16_sig.tobytes())
            file_to_analyze = demo_path
            st.session_state["demo_sample"] = demo_path
            st.success("Generated `demo_natural_sample.wav`")

if "demo_sample" in st.session_state and file_to_analyze is None:
    file_to_analyze = st.session_state["demo_sample"]

# Media Previews
if file_to_analyze and Path(file_to_analyze).exists():
    st.markdown("---")
    col_prev1, col_prev2 = st.columns([1, 1])
    ext = Path(file_to_analyze).suffix.lower()
    
    with col_prev1:
        st.subheader("Media Playback")
        if ext in [".mp4", ".mov", ".avi", ".mkv"]:
            st.video(str(file_to_analyze))
        else:
            st.audio(str(file_to_analyze))

    with col_prev2:
        st.subheader("File Information")
        st.write(f"**Filename:** `{Path(file_to_analyze).name}`")
        st.write(f"**File Size:** `{os.path.getsize(file_to_analyze) / 1024:.1f} KB`")
        st.write(f"**Format:** `{ext.upper()}`")
        st.write("**Analysis Engine:** TruthLens Audio Forensics Engine v1.0")

    # Execution Trigger
    st.markdown("---")
    if st.button("🔍 Run Audio & Text Forensic Analysis", type="primary", use_container_width=True):
        with st.spinner("Executing forensic pipeline: extracting audio, computing acoustic features, running speech-to-text..."):
            try:
                results = analyze_audio(file_to_analyze)
                st.session_state["analysis_results"] = results
                st.success("Forensic analysis completed successfully!")
            except Exception as err:
                st.error(f"Analysis failed: {err}")

# Display Results
if "analysis_results" in st.session_state:
    res = st.session_state["analysis_results"]
    score = res["manipulation_score"]
    confidence = res["confidence"]
    verdict = res["verdict"]

    st.markdown("### 📊 Forensic Verdict & Suspicion Overview")
    
    # Verdict Banner
    if score >= 0.70:
        badge = f'<span class="badge-danger">🚨 {verdict.upper()} ({int(score * 100)}%)</span>'
    elif score >= 0.40:
        badge = f'<span class="badge-warn">⚠️ {verdict.upper()} ({int(score * 100)}%)</span>'
    else:
        badge = f'<span class="badge-safe">✅ {verdict.upper()} ({int(score * 100)}%)</span>'
    
    st.markdown(f"**Verdict:** {badge}", unsafe_allow_html=True)
    st.info(f"**Forensic Explanation:** {res['explanation']}")

    # Metrics Summary Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric(
            label="Synthetic Suspicion Score",
            value=f"{int(score * 100)}%",
            delta=f"{score:.2f} / 1.0",
            delta_color="inverse"
        )
    with m_col2:
        st.metric(
            label="Detector Confidence",
            value=f"{int(confidence * 100)}%",
            help="Statistical reliability of acoustic signal length and quality"
        )
    with m_col3:
        wpm = res.get("text_forensics", {}).get("words_per_minute", 0)
        st.metric(
            label="Speech Rate",
            value=f"{wpm} WPM",
            help="Normal human conversational speech is typically 120-170 WPM"
        )
    with m_col4:
        pitch_f0 = res.get("acoustic_analysis", {}).get("pitch_statistics", {}).get("mean_f0_hz", 0)
        st.metric(
            label="Mean Pitch (F0)",
            value=f"{pitch_f0} Hz"
        )

    # Detailed Tabs
    tab_acoustic, tab_timeline, tab_transcript, tab_report = st.tabs([
        "🎙️ Acoustic & Synthetic Voice Indicators",
        "⏱️ Suspicious Audio Timestamps",
        "📝 Speech-to-Text & Linguistic Forensics",
        "📄 Multimodal Integration Report"
    ])

    # Tab 1: Acoustic Analysis
    with tab_acoustic:
        st.subheader("Physical & Psychoacoustic Voice Indicators")
        
        # Audio waveform preview
        if "extracted_audio_path" in res and Path(res["extracted_audio_path"]).exists():
            sig, sr = load_audio_signal(res["extracted_audio_path"])
            # Subsample for fast charting
            step = max(1, len(sig) // 1000)
            downsampled = sig[::step]
            time_axis = np.linspace(0, len(sig) / sr, len(downsampled))
            chart_df = pd.DataFrame({"Time (s)": time_axis, "Normalized Amplitude": downsampled})
            st.line_chart(chart_df, x="Time (s)", y="Normalized Amplitude", height=180)

        ac_features = res.get("acoustic_analysis", {}).get("acoustic_features", {})
        pitch_stats = res.get("acoustic_analysis", {}).get("pitch_statistics", {})
        
        c_ac1, c_ac2 = st.columns(2)
        with c_ac1:
            st.write("#### Pitch Intonation & Jitter")
            st.write(f"- **Fundamental Frequency (F0 Mean):** `{pitch_stats.get('mean_f0_hz', 0)} Hz`")
            st.write(f"- **Pitch Variation (F0 Std Dev):** `{pitch_stats.get('std_f0_hz', 0)} Hz` (Monotony threshold: < 14 Hz)")
            st.write(f"- **Frequency Jitter:** `{ac_features.get('jitter_percent', 0)}%` (Normal: 0.5% - 2.5%)")
            st.write(f"- **Amplitude Shimmer:** `{ac_features.get('shimmer_percent', 0)}%` (Normal: 2.0% - 6.0%)")

        with c_ac2:
            st.write("#### Spectral Properties & Silence Distribution")
            st.write(f"- **Spectral Flatness (Wiener Entropy):** `{ac_features.get('spectral_flatness', 0)}`")
            st.write(f"- **High-Frequency Rolloff Cutoff:** `{'Detected (TTS filter artifact)' if ac_features.get('has_cutoff') else 'Natural decay'}`")
            st.write(f"- **Digital Zero Silence Frames:** `{ac_features.get('dead_silence_frames', 0)}`")
            st.write(f"- **Total Pause Ratio:** `{int(ac_features.get('pause_ratio', 0) * 100)}%`")

        st.markdown("#### Key Acoustic Forensic Findings")
        for finding in res.get("acoustic_analysis", {}).get("findings", []):
            st.markdown(f"- 🔎 {finding}")

    # Tab 2: Suspicious Timestamps
    with tab_timeline:
        st.subheader("Suspicious Audio Segment Timestamps")
        suspicious = res.get("suspicious_timestamps", [])
        
        if suspicious:
            st.warning(f"Detected {len(suspicious)} segment(s) exhibiting synthetic speech anomalies:")
            df_suspicious = pd.DataFrame(suspicious)
            df_display = df_suspicious[["timestamp", "suspicion_score", "reason"]].rename(
                columns={
                    "timestamp": "Timestamp Interval",
                    "suspicion_score": "Suspicion Score (0-1)",
                    "reason": "Forensic Reason / Anomaly"
                }
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No individual time segments exceeded the suspicion threshold. Voice continuity appears natural.")

    # Tab 3: Speech-to-Text & Text Forensics
    with tab_transcript:
        st.subheader("Speech-to-Text Transcript")
        transcript_text = res.get("transcript", "")
        if transcript_text:
            st.text_area("Extracted Transcript (Whisper Engine)", value=transcript_text, height=120)
        else:
            st.info("No verbal speech transcribed from audio.")

        st.subheader("Linguistic & Consistency Forensics")
        txt_forensics = res.get("text_forensics", {})
        
        col_tx1, col_tx2 = st.columns(2)
        with col_tx1:
            st.write(f"- **Lexical Diversity (Type-Token Ratio):** `{txt_forensics.get('lexical_diversity', 0)}`")
            st.write(f"- **Total Word Count:** `{txt_forensics.get('total_words', 0)} words`")
            st.write(f"- **Speech Cadence:** `{txt_forensics.get('words_per_minute', 0)} WPM`")

        with col_tx2:
            st.write(f"- **Text Manipulation Score:** `{txt_forensics.get('text_manipulation_score', 0)}`")
            st.write(f"- **Flagged AI Marker Phrases:** `{txt_forensics.get('suspicious_phrases', [])}`")
            st.write(f"- **Repeated Loop Patterns:** `{txt_forensics.get('repeated_patterns', [])}`")

        st.markdown("#### Text Forensic Findings")
        for finding in txt_forensics.get("findings", []):
            st.markdown(f"- 📝 {finding}")

    # Tab 4: Multimodal Integration Report
    with tab_report:
        st.subheader("TruthLens Backend Integration Payload")
        st.caption("Clean Python dictionary returned by `analyze_audio()` ready to integrate into `correlate_results()`:")
        
        # Format payload compatible with backend/main.py and correlate_results()
        integration_payload = {
            "status": res["status"],
            "manipulation_score": res["manipulation_score"],
            "confidence": res["confidence"],
            "findings": res["findings"],
            "transcript": res["transcript"],
            "verdict": res["verdict"],
            "suspicious_timestamps": res["suspicious_timestamps"]
        }
        
        st.json(integration_payload)
        
        # Download button
        json_report = json.dumps(res, indent=2)
        st.download_button(
            label="📥 Download Complete Forensic JSON Report",
            data=json_report,
            file_name=f"truthlens_audio_forensics_{Path(file_to_analyze).stem}.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("---")
st.caption("TruthLens Deepfake Video Detection System • Hackathon Deliverable — Member 3 (Audio and Text Forensics)")
