
from analysis.confidence import calculate_confidence

results = {
    "image": {
        "status": "completed",
        "confidence": 0.90
    },
    "video": {
        "status": "completed",
        "confidence": 0.85
    },
    "audio": {
        "status": "completed",
        "confidence": 0.80
    },
    "text": None
}

result = calculate_confidence(results)

print("\nCONFIDENCE ANALYSIS RESULT:")
print(result)
