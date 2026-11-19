
from analysis.correlation import correlate_results

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

print(result)
