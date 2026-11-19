
from analysis.confidence import calculate_confidence


def test_calculate_confidence():
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

    assert result["average_detector_confidence"] == 0.85
    assert result["analysed_modalities"] == [
        "image", "video", "audio"
    ]
    assert result["unavailable_modalities"] == ["text"]
    assert result["evidence_coverage"] == "3/4 modalities"
