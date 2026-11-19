
from analysis.correlation import correlate_results
from analysis.confidence import calculate_confidence
from reports.report_generator import create_pdf_report

# Sample detector results for testing
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

# Run correlation
correlation = correlate_results(
    image=image,
    video=video,
    audio=audio
)

# Run confidence analysis
confidence = calculate_confidence({
    "image": image,
    "video": video,
    "audio": audio,
    "text": None
})

# Generate PDF
pdf_path = create_pdf_report(correlation, confidence)

print("PDF REPORT GENERATED SUCCESSFULLY!")
print("Saved at:", pdf_path)
