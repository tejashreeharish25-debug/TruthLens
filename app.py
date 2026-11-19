"""
TruthLens — Unified Multimodal Deepfake Detection Dashboard
============================================================
Single Streamlit app integrating:
  • Image Forensics  (Member 1 — image_analysis.py)
  • Video Forensics  (Member 2 — video_analysis.py)
  • Audio & Text Forensics (Member 3 — audio_forensics/)

Run:
    backend\\.venv\\Scripts\\python.exe -m streamlit run app.py --server.port 8501
"""

import sys
import os
import json
import tempfile
import io

import streamlit as st
import pandas as pd

# ── make backend importable ──────────────────────────────────────────────────
BACKEND = os.path.join(os.path.dirname(__file__), "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

# ── lazy imports (only fail if that module is broken) ────────────────────────
def _import_image():
    from image_analysis import analyze_image
    return analyze_image

def _import_video():
    from video_analysis import analyze_video
    return analyze_video

def _import_audio():
    from audio_forensics.service import analyze_audio
    return analyze_audio

def _import_pdf():
    from reports.report_generator import create_pdf_report
    return create_pdf_report

def _import_correlation():
    from analysis.correlation import correlate_results
    return correlate_results

def _import_confidence():
    from analysis.confidence import calculate_confidence
    return calculate_confidence

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TruthLens — AI Deepfake Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark theme overrides */
    .stApp { background: #080d18; color: #ffffff; }
    .block-container { padding-top: 2rem; }

    /* Score badge */
    .score-badge {
        display: inline-block;
        font-size: 2.4rem;
        font-weight: 800;
        padding: 0.4rem 1.4rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    .score-safe   { background: #0d3324; color: #2ecc71; border: 1px solid #2ecc71; }
    .score-warn   { background: #2d2200; color: #f39c12; border: 1px solid #f39c12; }
    .score-danger { background: #2d0d0d; color: #e74c3c; border: 1px solid #e74c3c; }

    /* Section cards */
    .result-card {
        background: rgba(20,34,57,0.75);
        border: 1px solid #263b59;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }

    /* Metric label override */
    [data-testid="stMetricLabel"] { color: #9cabc0 !important; }
    [data-testid="stMetricValue"] { color: #36a8ff !important; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def score_badge(score: float | None, label: str = "Manipulation Score") -> str:
    if score is None:
        return f"<span class='score-badge score-warn'>N/A</span>"
    pct = int(score * 100)
    cls = "score-safe" if score < 0.4 else ("score-warn" if score < 0.7 else "score-danger")
    return f"<span class='score-badge {cls}'>{pct}%</span>"

def verdict(score: float | None) -> str:
    if score is None:
        return "⚠️ Inconclusive"
    if score < 0.40:
        return "✅ Likely Authentic"
    if score < 0.70:
        return "⚠️ Suspicious — Review Carefully"
    return "🚨 High Deepfake Probability"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 TruthLens")
    st.caption("AI-Powered Deepfake Detection")
    st.divider()
    mode = st.radio(
        "Analysis Mode",
        ["🖼️ Image", "🎬 Video", "🎙️ Audio / Speech", "📊 Full Report"],
        index=0
    )
    st.divider()
    st.caption("**TruthLens v1.0** — Hackathon Build")
    st.caption("Backend: FastAPI :8000")
    st.caption("Dashboard: Streamlit :8501")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 1.5rem 0 0.5rem;'>
  <h1 style='font-size:2.8rem; font-weight:800; letter-spacing:-2px;'>
    Truth<span style='color:#36a8ff;'>Lens</span>
  </h1>
  <p style='color:#9cabc0; font-size:1rem;'>
    Multimodal AI Forensics · Detect Deepfakes · Verify Media
  </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ════════════════════════════════════════════════════════════════════════════
# MODE: IMAGE
# ════════════════════════════════════════════════════════════════════════════
if mode == "🖼️ Image":
    st.subheader("🖼️ Image Forensics")
    st.caption("Upload an image to detect manipulation, check EXIF metadata, and assess authenticity.")

    uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded, caption=f"📎 {uploaded.name}", use_container_width=True)

        with col2:
            with st.spinner("🔬 Analyzing image…"):
                try:
                    analyze_image = _import_image()
                    img_bytes = uploaded.read()
                    result = analyze_image(img_bytes)
                except Exception as e:
                    st.error(f"Image module error: {e}")
                    result = None

            if result:
                score = result.get("manipulation_score")
                st.markdown(f"**Manipulation Score** {score_badge(score)}", unsafe_allow_html=True)
                st.markdown(f"**Verdict:** {verdict(score)}")
                st.divider()

                info = result.get("image_info", {})
                c1, c2, c3 = st.columns(3)
                c1.metric("Width", f"{info.get('width','?')} px")
                c2.metric("Height", f"{info.get('height','?')} px")
                c3.metric("Format", info.get("format") or info.get("color_mode","?"))

                st.markdown("**📋 Findings**")
                for f in result.get("findings", []):
                    st.markdown(f"- {f}")

                with st.expander("🗂️ Raw JSON"):
                    st.json(result)

# ════════════════════════════════════════════════════════════════════════════
# MODE: VIDEO
# ════════════════════════════════════════════════════════════════════════════
elif mode == "🎬 Video":
    st.subheader("🎬 Video Forensics")
    st.caption("Upload a video to inspect frame properties, detect anomalies, and check for manipulation.")

    uploaded = st.file_uploader("Upload Video", type=["mp4", "avi", "mov", "mkv"])

    if uploaded:
        st.video(uploaded)

        with st.spinner("🔬 Analyzing video frames…"):
            try:
                analyze_video = _import_video()
                vid_bytes = uploaded.read()
                result = analyze_video(vid_bytes, filename=uploaded.name)
            except Exception as e:
                st.error(f"Video module error: {e}")
                result = None

        if result:
            score = result.get("manipulation_score")
            st.markdown(f"**Manipulation Score** {score_badge(score)}", unsafe_allow_html=True)
            st.markdown(f"**Verdict:** {verdict(score)}")
            st.divider()

            info = result.get("video_info", {})
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Resolution", f"{info.get('width','?')}×{info.get('height','?')}")
            c2.metric("FPS", info.get("fps", "?"))
            c3.metric("Duration", f"{info.get('duration_seconds','?')}s")
            c4.metric("Frames", info.get("total_frames", "?"))

            st.markdown("**📋 Findings**")
            for f in result.get("findings", []):
                st.markdown(f"- {f}")

            frames = info.get("sampled_frames", [])
            if frames:
                st.markdown("**🎞️ Sampled Frames**")
                st.dataframe(pd.DataFrame(frames), use_container_width=True)

            with st.expander("🗂️ Raw JSON"):
                st.json(result)

# ════════════════════════════════════════════════════════════════════════════
# MODE: AUDIO / SPEECH
# ════════════════════════════════════════════════════════════════════════════
elif mode == "🎙️ Audio / Speech":
    st.subheader("🎙️ Audio & Text Forensics")
    st.caption("Upload a video or audio file to transcribe speech, detect synthetic voice, and flag anomalies.")

    uploaded = st.file_uploader(
        "Upload Video or Audio",
        type=["mp4", "avi", "mov", "mkv", "mp3", "wav", "m4a", "ogg"]
    )

    if uploaded:
        # Save to temp file for the audio pipeline
        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        # Playback
        uploaded.seek(0)
        st.audio(uploaded)

        with st.spinner("🔬 Running audio forensics (this may take 20–60s for Whisper)…"):
            try:
                analyze_audio = _import_audio()
                result = analyze_audio(tmp_path)
            except Exception as e:
                st.error(f"Audio forensics error: {e}")
                result = None
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        if result:
            score = result.get("manipulation_score", result.get("suspicion_score"))
            conf  = result.get("confidence", 0.0)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Synthetic Voice Score** {score_badge(score)}", unsafe_allow_html=True)
                st.markdown(f"**Verdict:** {verdict(score)}")
            with col2:
                st.metric("Confidence", f"{int((conf or 0)*100)}%")
                st.metric("Status", result.get("status", "completed"))

            st.divider()

            # ── Acoustic Metrics ──────────────────────────────────────────
            acoustic = result.get("acoustic_features", {})
            if acoustic:
                st.markdown("#### 🎵 Acoustic Metrics")
                acols = st.columns(4)
                acols[0].metric("Jitter",    f"{acoustic.get('jitter',0):.4f}")
                acols[1].metric("Shimmer",   f"{acoustic.get('shimmer',0):.4f}")
                acols[2].metric("Spec. Flatness", f"{acoustic.get('spectral_flatness',0):.4f}")
                acols[3].metric("Silence %", f"{acoustic.get('silence_ratio',0)*100:.1f}%")

            # ── Transcript ────────────────────────────────────────────────
            transcript = result.get("transcript", "")
            if transcript:
                st.markdown("#### 📝 Transcript")
                st.info(transcript or "_No speech detected_")

            # ── Text Forensics ────────────────────────────────────────────
            text_info = result.get("text_forensics", {})
            if text_info:
                st.markdown("#### 📖 Linguistic Analysis")
                tc1, tc2, tc3 = st.columns(3)
                tc1.metric("Lexical Diversity", f"{text_info.get('lexical_diversity',0):.2f}")
                tc2.metric("Words/Min", f"{text_info.get('words_per_minute',0):.0f}")
                tc3.metric("AI Markers Found", len(text_info.get("ai_markers_found", [])))
                markers = text_info.get("ai_markers_found", [])
                if markers:
                    st.warning(f"🤖 AI Marker Phrases: `{'`, `'.join(markers)}`")

            # ── Suspicious Timestamps ─────────────────────────────────────
            segments = result.get("suspicious_segments", [])
            if segments:
                st.markdown("#### ⚠️ Suspicious Segments")
                seg_df = pd.DataFrame(segments)
                st.dataframe(seg_df, use_container_width=True)
            else:
                st.success("✅ No suspicious timestamps detected.")

            # ── Downloads ─────────────────────────────────────────────────
            st.divider()
            d1, d2 = st.columns(2)
            with d1:
                json_str = json.dumps(result, indent=2)
                st.download_button("⬇️ Download JSON Report", json_str, "audio_forensics.json", "application/json")
            with d2:
                try:
                    create_pdf = _import_pdf()
                    corr_fn = _import_correlation()
                    conf_fn = _import_confidence()
                    corr = corr_fn(image=None, video=None, audio=result, text=None)
                    conf = conf_fn({"audio": result})
                    pdf_path = create_pdf(corr, conf)
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button("⬇️ Download PDF Report", f.read(), "truthlens_report.pdf", "application/pdf")
                except Exception:
                    pass

            with st.expander("🗂️ Raw JSON"):
                st.json(result)

# ════════════════════════════════════════════════════════════════════════════
# MODE: FULL REPORT (Multi-modal)
# ════════════════════════════════════════════════════════════════════════════
elif mode == "📊 Full Report":
    st.subheader("📊 Full Multi-Modal Analysis")
    st.caption("Upload a video file. TruthLens will run ALL modules — image frame, video, and audio forensics — and produce a unified report.")

    uploaded = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov", "mkv"])

    if uploaded:
        st.video(uploaded)

        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        results = {}

        with st.spinner("Step 1/3 — Video forensics…"):
            try:
                analyze_video = _import_video()
                with open(tmp_path, "rb") as vf:
                    video_bytes = vf.read()
                results["video"] = analyze_video(video_bytes, filename=uploaded.name)
            except Exception as e:
                results["video"] = {"status": "error", "findings": [str(e)]}

        with st.spinner("Step 2/3 — Audio & speech forensics (Whisper)…"):
            try:
                analyze_audio = _import_audio()
                results["audio"] = analyze_audio(tmp_path)
            except Exception as e:
                results["audio"] = {"status": "error", "findings": [str(e)]}

        with st.spinner("Step 3/3 — Correlating signals…"):
            try:
                corr_fn = _import_correlation()
                conf_fn = _import_confidence()
                correlation = corr_fn(
                    image=None,
                    video=results.get("video"),
                    audio=results.get("audio"),
                    text=None
                )
                confidence = conf_fn({
                    "video": results.get("video"),
                    "audio": results.get("audio")
                })
            except Exception as e:
                correlation = {"error": str(e)}
                confidence = {}

        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        st.divider()
        st.markdown("### 🧠 TruthLens Unified Verdict")

        # Overall score
        overall = confidence.get("overall_score") or confidence.get("score")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Overall Deepfake Score** {score_badge(overall)}", unsafe_allow_html=True)
            st.markdown(f"**Verdict:** {verdict(overall)}")
        with col2:
            conf_lvl = confidence.get("confidence_level", "")
            st.metric("Confidence Level", conf_lvl or "—")
            st.metric("Modalities Analyzed", "Video + Audio")

        st.divider()

        # Per-module summaries
        tab1, tab2, tab3 = st.tabs(["🎬 Video", "🎙️ Audio", "📄 JSON"])

        with tab1:
            vr = results.get("video", {})
            st.markdown(f"**Status:** {vr.get('status','?')}")
            for f in vr.get("findings", []):
                st.markdown(f"- {f}")

        with tab2:
            ar = results.get("audio", {})
            a_score = ar.get("manipulation_score", ar.get("suspicion_score"))
            st.markdown(f"**Synthetic Voice Score:** {score_badge(a_score)}", unsafe_allow_html=True)
            transcript = ar.get("transcript", "")
            if transcript:
                st.info(transcript)
            segs = ar.get("suspicious_segments", [])
            if segs:
                st.warning(f"⚠️ {len(segs)} suspicious audio segment(s) detected")
                st.dataframe(pd.DataFrame(segs), use_container_width=True)

        with tab3:
            st.json({"video": results.get("video"), "audio": results.get("audio"),
                     "correlation": correlation, "confidence": confidence})

        # PDF download
        try:
            create_pdf = _import_pdf()
            pdf_path = create_pdf(correlation, confidence)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pf:
                    st.download_button("⬇️ Download Full PDF Report", pf.read(), "truthlens_full_report.pdf", "application/pdf")
        except Exception:
            pass
