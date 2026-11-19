"""
TruthLens - Text & Speech-Text Consistency Forensics Module
Analyzes transcript consistency, unusual word/phrase repetitions, unnatural cadence,
lexical diversity, and AI conversational markers.
"""

import re
from collections import Counter


# Common AI text generation or disclaimer markers
AI_MARKER_PATTERNS = [
    r"\bas an ai\b",
    r"\blanguage model\b",
    r"\bvoice generated\b",
    r"\bsynthetic speech\b",
    r"\btext to speech\b",
    r"\belevenlabs\b",
    r"\bdeepfake\b",
    r"\btest 1 2 3\b",
    r"\bprompt injection\b"
]


def analyze_transcript(
    transcript: str,
    audio_duration_seconds: float = 0.0
) -> dict:
    """
    Forensic analysis of the recognized transcript and consistency with speech audio.
    
    Args:
        transcript: Extracted text transcript from speech recognition.
        audio_duration_seconds: Total duration of the audio in seconds.
        
    Returns:
        dict:
            - text_manipulation_score (0.0 to 1.0)
            - lexical_diversity (TTR)
            - words_per_minute (WPM)
            - suspicious_words (list)
            - suspicious_phrases (list)
            - repeated_patterns (list)
            - findings (list of explanations)
    """
    cleaned = transcript.strip().lower()
    words = re.findall(r"\b[a-zA-Z']+\b", cleaned)
    total_words = len(words)

    findings = []
    suspicious_words = []
    suspicious_phrases = []
    repeated_patterns = []
    score = 0.0

    if total_words == 0:
        return {
            "text_manipulation_score": 0.0,
            "lexical_diversity": 0.0,
            "words_per_minute": 0.0,
            "suspicious_words": [],
            "suspicious_phrases": [],
            "repeated_patterns": [],
            "findings": ["No verbal lexical content detected in transcript."]
        }

    # 1. Lexical Diversity (Type-Token Ratio)
    unique_words = set(words)
    ttr = len(unique_words) / float(total_words)

    if total_words > 15 and ttr < 0.35:
        score += 0.30
        findings.append(
            f"Unusually low vocabulary diversity (TTR: {ttr:.2f}). Repetitive looping typical of AI hallucination."
        )

    # 2. Repeated Consecutive Words or Phrases (Looping artifacts)
    word_counts = Counter(words)
    for word, count in word_counts.items():
        if count >= 4 and len(word) > 2 and (count / total_words) > 0.20:
            suspicious_words.append(word)
            repeated_patterns.append(f"Word '{word}' repeated {count} times ({int((count/total_words)*100)}% of text)")
            score += 0.20

    # Check 2-gram and 3-gram repetitions
    if total_words >= 6:
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        bigram_counts = Counter(bigrams)
        for bg, bg_cnt in bigram_counts.items():
            if bg_cnt >= 3:
                repeated_patterns.append(f"Phrase '{bg}' repeated {bg_cnt} times")
                score += 0.25

    # 3. Known Synthetic Voice / Prompt Markers
    for pattern in AI_MARKER_PATTERNS:
        match = re.search(pattern, cleaned)
        if match:
            matched_phrase = match.group(0)
            suspicious_phrases.append(matched_phrase)
            score += 0.45
            findings.append(f"Detected explicit synthetic voice marker phrase: '{matched_phrase}'.")

    # 4. Words Per Minute (Cadence & Pace Consistency)
    wpm = 0.0
    if audio_duration_seconds > 0:
        wpm = round((total_words / audio_duration_seconds) * 60.0, 1)
        if wpm > 230:
            score += 0.25
            findings.append(
                f"Abnormally rapid speech rate ({wpm} WPM). Unnatural without physiological breathing pauses."
            )
        elif wpm < 60 and total_words > 8:
            score += 0.15
            findings.append(
                f"Sluggish or artificially stretched speech pace ({wpm} WPM)."
            )
        else:
            findings.append(f"Speech cadence within expected pace ({wpm} WPM).")

    text_score = min(max(score, 0.05), 0.90)

    if not findings:
        findings.append("Transcript appears structurally natural with balanced vocabulary.")

    return {
        "text_manipulation_score": round(text_score, 3),
        "lexical_diversity": round(ttr, 3),
        "words_per_minute": wpm,
        "total_words": total_words,
        "suspicious_words": list(set(suspicious_words)),
        "suspicious_phrases": suspicious_phrases,
        "repeated_patterns": repeated_patterns,
        "findings": findings
    }
