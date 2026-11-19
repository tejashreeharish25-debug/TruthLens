import io
from PIL import Image, ExifTags


def analyze_image(image_bytes):
    findings = []

    try:
        image = Image.open(io.BytesIO(image_bytes))

        findings.append("Image successfully loaded")
        findings.append(f"Image format: {image.format}")
        findings.append(f"Image dimensions: {image.width} x {image.height}")
        findings.append(f"Color mode: {image.mode}")

        # Check EXIF metadata
        exif_data = image.getexif()

        if exif_data:
            findings.append("EXIF metadata is present")
        else:
            findings.append("No EXIF metadata found")

        result = {
            "modality": "image",
            "status": "completed",
            "manipulation_score": None,
            "confidence": None,
            "findings": findings,
            "image_info": {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "color_mode": image.mode,
                "file_size_bytes": len(image_bytes)
            }
        }

        return result

    except Exception as e:
        return {
            "modality": "image",
            "status": "error",
            "manipulation_score": None,
            "confidence": None,
            "findings": [f"Image analysis failed: {str(e)}"]
        }