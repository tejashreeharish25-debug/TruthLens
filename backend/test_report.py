
from pathlib import Path

from analysis.correlation import correlate_results
from analysis.confidence import calculate_confidence
from reports.report_generator import create_pdf_report


def test_pdf_report_generation(tmp_path, monkeypatch):
    image = {
        "status": "completed",
        "manipulation_score": 0.85,
        "confidence": 0.90,
        "findings": ["Possible facial artifacts"]
    }

    video = {
        "status": "completed",
        "manipulation_score": 0.78,
        "confidence": 0.85,
        "findings": ["Frame inconsistency"]
    }

    audio = {
        "status": "completed",
        "manipulation_score": 0.20,
        "confidence": 0.80,
        "findings": ["No strong synthetic voice indicators"]
    }

    correlation = correlate_results(
        image=image,
        video=video,
        audio=audio
    )

    confidence = calculate_confidence({
        "image": image,
        "video": video,
        "audio": audio,
        "text": None
    })

    report_path = create_pdf_report(correlation, confidence)

    assert report_path is not None

    report_file = Path(report_path)
    assert report_file.exists()
    assert report_file.stat().st_size > 0
