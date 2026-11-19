
from io import BytesIO
from PIL import Image

from image_analysis import analyze_image


def create_test_image():
    buffer = BytesIO()

    image = Image.new("RGB", (100, 80), color="blue")
    image.save(buffer, format="PNG")

    return buffer.getvalue()


def test_analyze_image_success():
    image_bytes = create_test_image()

    result = analyze_image(image_bytes)

    assert result["modality"] == "image"
    assert result["status"] == "completed"
    assert result["image_info"]["width"] == 100
    assert result["image_info"]["height"] == 80
    assert result["image_info"]["format"] == "PNG"
    assert result["image_info"]["file_size_bytes"] == len(image_bytes)
    assert "Image successfully loaded" in result["findings"]


def test_analyze_image_invalid_file():
    result = analyze_image(b"this is not a valid image")

    assert result["modality"] == "image"
    assert result["status"] == "error"
    assert any(
        "Image analysis failed" in finding
        for finding in result["findings"]
    )
