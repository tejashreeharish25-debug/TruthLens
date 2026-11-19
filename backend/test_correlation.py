
from analysis.correlation import correlate_results


def test_correlate_results():
    image = {
        "status": "completed",
        "manipulation_score": 0.85,
        "findings": ["Possible facial artifacts"]
    }

    video = {
        "status": "completed",
        "manipulation_score": 0.78,
        "findings": ["Frame inconsistency"]
    }

    audio = {
        "status": "completed",
        "manipulation_score": 0.20,
        "findings": ["No strong synthetic voice indicators"]
    }

    result = correlate_results(
        image=image,
        video=video,
        audio=audio
    )

    assert result["analysis_type"] == "cross_modal_correlation"
    assert result["available_modalities"] == ["image", "video", "audio"]
    assert result["unavailable_modalities"] == ["text"]
    assert result["suspicious_modalities"] == ["image", "video"]
    assert result["agreement"] == "multiple_modalities_flagged"
    assert len(result["findings"]) == 3
