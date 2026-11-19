
from datetime import datetime, timezone


def correlate_results(image=None, video=None, audio=None, text=None):
    """
    Compare findings from different media detectors.
    This module combines evidence; it does not independently
    detect deepfakes.
    """

    results = {
        "image": image,
        "video": video,
        "audio": audio,
        "text": text
    }

    available = {}
    unavailable = []

    for modality, result in results.items():
        if result is None:
            unavailable.append(modality)
        elif result.get("status") != "completed":
            unavailable.append(modality)
        else:
            available[modality] = result

    findings = []

    for modality, result in available.items():
        for indicator in result.get("findings", []):
            findings.append({
                "modality": modality,
                "indicator": indicator
            })

    suspicious = []

    for modality, result in available.items():
        score = result.get("manipulation_score")

        if isinstance(score, (int, float)) and 0 <= score <= 1:
            if score >= 0.70:
                suspicious.append(modality)

    if len(suspicious) >= 2:
        agreement = "multiple_modalities_flagged"
        explanation = (
            "Multiple media detectors reported elevated "
            "manipulation indicators. Further investigation "
            "is recommended."
        )
    elif len(suspicious) == 1:
        agreement = "single_modality_flagged"
        explanation = (
            "One media detector reported elevated manipulation "
            "indicators. Other evidence should be reviewed."
        )
    else:
        agreement = "no_multiple_flags"
        explanation = (
            "No multiple-modality agreement was established. "
            "This does not prove the media is authentic."
        )

    return {
        "analysis_type": "cross_modal_correlation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "available_modalities": list(available.keys()),
        "unavailable_modalities": unavailable,
        "suspicious_modalities": suspicious,
        "agreement": agreement,
        "findings": findings,
        "explanation": explanation
    }
