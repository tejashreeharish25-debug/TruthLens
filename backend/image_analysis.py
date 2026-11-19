
import io
from functools import lru_cache

from PIL import Image
from transformers import pipeline


MODEL_ID = "capcheck/ai-image-detection"


@lru_cache(maxsize=1)
def get_detector():
    return pipeline(
        "image-classification",
        model=MODEL_ID,
        device=-1
    )


def analyze_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()

        image_format = image.format
        width, height = image.size
        color_mode = image.mode

        exif_data = image.getexif()

        # Run AI image detection
        detector = get_detector()
        predictions = detector(image.convert("RGB"))

        fake_score = next(
            item["score"]
            for item in predictions
            if item["label"].upper() == "FAKE"
        )

        real_score = next(
            item["score"]
            for item in predictions
            if item["label"].upper() == "REAL"
        )

        verdict = "AI-generated" if fake_score >= real_score else "Real"

        findings = [
            "Image successfully loaded",
            f"Image format: {image_format}",
            f"Image dimensions: {width} x {height}",
            f"Color mode: {color_mode}",
            "EXIF metadata is present" if exif_data else "No EXIF metadata found",
            f"AI-generated score: {fake_score * 100:.2f}%",
            f"Model classification: {verdict}"
        ]

        return {
            "modality": "image",
            "status": "completed",
            "manipulation_score": round(fake_score, 3),
            "confidence": round(max(fake_score, real_score), 3),
            "ai_generated_score": round(fake_score, 3),
            "real_score": round(real_score, 3),
            "verdict": verdict,
            "findings": findings,
            "image_info": {
                "width": width,
                "height": height,
                "format": image_format,
                "color_mode": color_mode,
                "file_size_bytes": len(image_bytes)
            }
        }

    except Exception as e:
        return {
            "modality": "image",
            "status": "error",
            "manipulation_score": None,
            "confidence": None,
            "findings": [f"Image analysis failed: {str(e)}"]
        }
