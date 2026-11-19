# TruthLens - Audio and Text Forensics Module
**Hackathon Deliverable — Member 3: Audio & Text Forensics in Deepfake Video Detection**

---

## 📌 Executive Summary

The **Audio & Text Forensics Module** of TruthLens extracts audio from video media (MP4, AVI, MOV, MKV) and analyzes both **physical acoustic signatures** and **linguistic/textual structures** to identify signs of synthetic speech, voice cloning, and AI manipulation.

Rather than claiming that audio anomalies definitively prove a deepfake, this module implements a **defensible, scientifically grounded baseline** combining acoustic micro-perturbation analysis, spectral inspection, and natural language consistency checks, returning structured evidence for multimodal correlation.

---

## 🏗️ Architecture & Component Breakdown

```
TruthLens/
├── backend/
│   ├── audio_forensics/               # Core Forensic Engine (Member 3)
│   │   ├── __init__.py                # Clean export interface
│   │   ├── extractor.py               # FFmpeg extraction & PCM standardization
│   │   ├── acoustic_detector.py       # F0 pitch, jitter/shimmer, spectral flatness, pauses
│   │   ├── transcription.py           # Speech-to-text with Whisper & CPU resilience
│   │   ├── text_forensics.py          # Repetition loops, AI marker phrases, WPM cadence
│   │   ├── segment_forensics.py       # Time-sliced segment suspicion scoring & reasons
│   │   └── service.py                 # Master analyze_audio() orchestrator
│   ├── analysis/
│   │   ├── confidence.py              # Multimodal confidence aggregator
│   │   └── correlation.py             # Cross-modal correlation engine
│   ├── reports/
│   │   └── report_generator.py        # PDF forensic report builder
│   ├── main.py                        # FastAPI endpoints (/analyze, /analyze/audio)
│   └── test_audio_forensics.py        # Automated test verification suite
├── frontend/                          # React + Vite UI
├── app_audio_forensics.py             # Streamlit Interactive Dashboard
├── requirements.txt                   # Project dependencies
└── README_AUDIO_FORENSICS.md          # Comprehensive module guide
```

---

## 🔬 Forensic Methodology

### 1. Audio Extraction & Standardization (`extractor.py`)
- Extracts audio tracks from uploaded video containers (`.mp4`, `.avi`, `.mov`, `.mkv`).
- Normalizes sample rate to **16,000 Hz, 16-bit PCM, single-channel (Mono)**.
- Uses bundled `imageio-ffmpeg` binary, ensuring standalone execution on Windows without requiring manual system environment configuration.

### 2. Acoustic Synthetic Voice Detection (`acoustic_detector.py`)
- **Fundamental Frequency ($F_0$) & Pitch Contour:**
  - Evaluates pitch variation across voiced frames. Human speech exhibits organic intonation ($\sigma_{F0} \approx 25\text{--}80\text{ Hz}$).
  - Monotonic flattening ($\sigma_{F0} < 14\text{ Hz}$) indicates robotic text-to-speech (TTS) synthesis.
- **Vocal Micro-perturbations (Jitter & Shimmer):**
  - Evaluates cycle-to-cycle frequency variation (Jitter) and amplitude perturbation (Shimmer).
  - Neural vocoders often produce unnaturally smoothed waveforms ($\text{Jitter} < 0.25\%$) or erratic phase noise ($\text{Jitter} > 4.5\%$).
- **Spectral Flatness & High-Frequency Cutoff:**
  - Detects artificial brickwall band-pass cutoffs (common in 16kHz neural vocoders) and elevated Wiener entropy.
- **Silence & Pause Distribution:**
  - Identifies artificial dead silence (absolute digital zero $\text{amplitude} = 0.0$) and absent breath pauses.

### 3. Speech-to-Text Transcription (`transcription.py`)
- Transcribes speech using OpenAI Whisper (`tiny` or `base` model) optimized for CPU execution on standard laptops.
- Generates timestamped speech segments with start and end intervals.
- Features resilient zero-crash fallback to energy-based segmentation if heavy models are initializing.

### 4. Text & Linguistic Forensics (`text_forensics.py`)
- **Lexical Diversity (Type-Token Ratio - TTR):** Identifies repetitive loops and hallucinations.
- **Suspicious Synthetic Markers:** Flags phrases like *"as an AI language model"*, *"voice generated"*, *"prompt injection"*.
- **Speech Rate Cadence:** Measures Words Per Minute (WPM). Normal speech ranges between 120–170 WPM; unpaused bursts exceeding 230 WPM trigger cadence flags.

### 5. Suspicious Segment Detection (`segment_forensics.py`)
- Slices the audio stream into 3.0-second sliding windows.
- Evaluates acoustic metrics per segment and tags suspicious intervals with specific explanations (e.g., `00:02 - 00:05: Unnatural pitch monotony; High spectral noise`).

---

## 🚀 Step-by-Step Setup Guide (Windows / VS Code)

### Prerequisites
- Windows 10/11
- Python 3.10 to 3.13 installed ([python.org](https://www.python.org/downloads/))
- VS Code ([code.visualstudio.com](https://code.visualstudio.com/))

### Step 1: Open Terminal in VS Code
Open VS Code, press ``Ctrl + ` `` to open the integrated terminal.

### Step 2: Activate or Create Virtual Environment
```powershell
# Navigate to TruthLens root directory
cd "c:\Users\tejas\OneDrive\Attachments\Desktop\TruthLens"

# Activate existing virtual environment
.\backend\.venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```

### Step 4: Verify with Automated Tests
```powershell
python backend/test_audio_forensics.py
```
Expected output:
```
ALL TESTS PASSED SUCCESSFULLY! Audio forensics module is production ready.
```

---

## 🖥️ Running the Applications

### Option A: Launch Interactive Streamlit Forensics Dashboard
```powershell
streamlit run app_audio_forensics.py
```
This opens `http://localhost:8501` in your browser where you can:
1. Upload any MP4, AVI, MOV video or WAV audio.
2. Or click the built-in synthetic/natural audio generator buttons to test the engine immediately.
3. Inspect the suspicious score, waveform, acoustic metrics, transcript, and timestamp table.
4. Download the forensic JSON report.

### Option B: Launch FastAPI Main Backend
```powershell
cd backend
uvicorn main:app --reload --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`

---

## 🔗 Teammate Integration Guide

Teammates can integrate the module with a single clean function call:

```python
from audio_forensics.service import analyze_audio

# Pass path to any video (MP4, AVI, MOV) or audio (WAV, MP3) file
result = analyze_audio("path/to/video.mp4")

print("Suspicion Score:", result["manipulation_score"]) # Float between 0.0 and 1.0
print("Confidence:", result["confidence"])              # Float between 0.0 and 1.0
print("Transcript:", result["transcript"])              # Extracted string
print("Suspicious Timestamps:", result["suspicious_timestamps"]) # List of segments
print("Findings:", result["findings"])                  # List of forensic findings
```

This return dictionary automatically matches the expected schema of `correlate_results()` and `calculate_confidence()` in `backend/analysis/`.
