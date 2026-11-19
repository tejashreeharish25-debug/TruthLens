import json
from pathlib import Path
from image_analysis import analyze_image

# Find sample images
sample_folder = Path("sample_images")

supported_formats = [".jpg", ".jpeg", ".png", ".webp"]

if not sample_folder.exists():
    print("sample_images folder not found")

else:
    image_files = [
        file for file in sample_folder.iterdir()
        if file.suffix.lower() in supported_formats
    ]

    if not image_files:
        print("No sample image found in sample_images folder")

    else:
        sample_image = image_files[0]

        print("Testing image:", sample_image.name)

        image_bytes = sample_image.read_bytes()

        result = analyze_image(image_bytes)

        print("\nImage Analysis Result:")
        print(json.dumps(result, indent=4))