
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from image_analysis import analyze_image
from video_analysis import analyze_video
from audio_forensics.service import analyze_audio
from analysis.correlation import correlate_results
from analysis.confidence import calculate_confidence
from reports.report_generator import create_pdf_report


app = FastAPI(
    title="TruthLens API",
    description="Multimodal Digital Forensics and Deepfake Detection System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {
    "image": {".jpg", ".jpeg", ".png", ".webp"},
    "video": {".mp4", ".avi", ".mov", ".mkv"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg"}
}


def get_uploaded_file(filename, media_type):
    """Validate and locate a previously uploaded file."""

    if not isinstance(filename, str) or Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = UPLOAD_DIR / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    extension = file_path.suffix.lower()

    if extension not in ALLOWED_TYPES[media_type]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported {media_type} file format"
        )

    return file_path


@app.get("/")
def home():
    return {
        "message": "Welcome to TruthLens!",
        "status": "Backend running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": "TruthLens"
    }


@app.post("/upload/{media_type}")
async def upload_file(media_type: str, file: UploadFile = File(...)):
    if media_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid media type")

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_TYPES[media_type]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported {media_type} file format"
        )

    filename = f"{uuid4().hex}{extension}"
    save_path = UPLOAD_DIR / filename

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        save_path.write_bytes(contents)

        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "media_type": media_type,
            "status": "uploaded"
        }

    finally:
        await file.close()


@app.post("/analyze/audio")
async def analyze_audio_upload(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    allowed_audio_video = ALLOWED_TYPES["audio"] | ALLOWED_TYPES["video"]

    if extension not in allowed_audio_video:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio or video format"
        )

    filename = f"{uuid4().hex}{extension}"
    save_path = UPLOAD_DIR / filename

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        save_path.write_bytes(contents)
        result = analyze_audio(save_path)

        return {
            "message": "Audio analysis completed",
            "filename": filename,
            "forensics": result
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        await file.close()


@app.post("/analyze")
async def analyze_media(payload: dict = Body(...)):
    try:
        image_result = None
        video_result = None
        audio_result = None
        text_result = None

        # IMAGE ANALYSIS
        image_filename = payload.get("image")

        if image_filename:
            image_path = get_uploaded_file(image_filename, "image")
            image_result = analyze_image(image_path.read_bytes())

        # VIDEO ANALYSIS
        video_filename = payload.get("video")

        if video_filename:
            video_path = get_uploaded_file(video_filename, "video")
            video_result = analyze_video(
                video_path.read_bytes(),
                filename=video_filename
            )

        # AUDIO ANALYSIS
        audio_filename = payload.get("audio")

        if audio_filename:
            audio_path = get_uploaded_file(audio_filename, "audio")
            audio_result = analyze_audio(audio_path)

        # OPTIONAL TEXT / TRANSCRIPT CONTEXT
        supplied_text = payload.get("text")

        if supplied_text is not None:
            if not isinstance(supplied_text, str):
                raise HTTPException(
                    status_code=400,
                    detail="Text input must be a string"
                )

            text_result = {
                "modality": "text",
                "status": "completed",
                "manipulation_score": None,
                "confidence": None,
                "findings": [
                    "Text supplied as contextual evidence",
                    f"Text length: {len(supplied_text)} characters"
                ]
            }

        # CROSS-MODAL CORRELATION
        correlation = correlate_results(
            image=image_result,
            video=video_result,
            audio=audio_result,
            text=text_result
        )

        # CONFIDENCE SUMMARY
        confidence = calculate_confidence({
            "image": image_result,
            "video": video_result,
            "audio": audio_result,
            "text": text_result
        })

        # GENERATE PDF REPORT
        pdf_path = create_pdf_report(correlation, confidence)

        return {
            "message": "Analysis completed successfully",
            "image": image_result,
            "video": video_result,
            "audio": audio_result,
            "text": text_result,
            "correlation": correlation,
            "confidence": confidence,
            "report_path": str(pdf_path)
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/report/download")
def download_latest_report():
    report_path = REPORT_DIR / "truthlens_report.pdf"

    if not report_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="No report is available yet. Run an analysis first."
        )

    return FileResponse(
        path=report_path,
        media_type="application/pdf",
        filename="truthlens_report.pdf"
    )
