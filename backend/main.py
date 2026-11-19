
from fastapi import Body
from fastapi.responses import FileResponse
from analysis.correlation import correlate_results
from analysis.confidence import calculate_confidence
from reports.report_generator import create_pdf_report
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from uuid import uuid4
import shutil

# Create application
app = FastAPI(
    title="TruthLens API",
    description="Multimodal Digital Forensics and Deepfake Detection System",
    version="1.0.0"
)

# Enable frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Supported media formats
ALLOWED_TYPES = {
    "image": {".jpg", ".jpeg", ".png", ".webp"},
    "video": {".mp4", ".avi", ".mov", ".mkv"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg"}
}


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
def upload_file(
    media_type: str,
    file: UploadFile = File(...)
):
    if media_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Media type must be image, video or audio"
        )

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_TYPES[media_type]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format"
        )

    safe_filename = f"{uuid4().hex}{extension}"
    save_path = UPLOAD_DIR / safe_filename

    try:
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(
            status_code=500,
            detail="File upload failed"
        )
    finally:
        file.file.close()

    return {
        "message": "File uploaded successfully",
        "filename": safe_filename,
        "media_type": media_type,
        "status": "uploaded"
    }

@app.post("/analyze")
async def analyze_media(payload: dict = Body(...)):
    try:
        image = payload.get("image")
        video = payload.get("video")
        audio = payload.get("audio")
        text = payload.get("text")

        # Cross-modal correlation
        correlation = correlate_results(
            image=image,
            video=video,
            audio=audio,
            text=text
        )

        # Confidence analysis
        confidence = calculate_confidence({
            "image": image,
            "video": video,
            "audio": audio,
            "text": text
        })

        # Generate PDF
        pdf_path = create_pdf_report(
            correlation,
            confidence
        )

        return {
            "message": "Analysis completed successfully",
            "correlation": correlation,
            "confidence": confidence,
            "report_path": pdf_path
        }

    except Exception as error:
        return {
            "error": str(error)
        }
