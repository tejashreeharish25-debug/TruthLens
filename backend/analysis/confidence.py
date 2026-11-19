
def calculate_confidence(results):
    """
    Summarize detector confidence and evidence coverage.
    This is not a calibrated probability that media is fake.
    """

    valid_results = []
    unavailable = []

    for modality, result in results.items():
        if result is None or result.get("status") != "completed":
            unavailable.append(modality)
            continue

        confidence = result.get("confidence")

        if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
            valid_results.append({
                "modality": modality,
                "confidence": confidence
            })

    if valid_results:
        average_confidence = sum(
            item["confidence"] for item in valid_results
        ) / len(valid_results)
    else:
        average_confidence = None

    return {
        "analysis_type": "confidence_summary",
        "average_detector_confidence": (
            round(average_confidence, 3)
            if average_confidence is not None else None
        ),
        "analysed_modalities": [
            item["modality"] for item in valid_results
        ],
        "unavailable_modalities": unavailable,
        "evidence_coverage": (
            f"{len(valid_results)}/4 modalities"
        ),
        "warning": (
            "Detector confidence is not the probability that "
            "the media is fake or authentic."
        )
    }
