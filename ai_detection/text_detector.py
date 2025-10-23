# import re
# from students.models import DrugAlert, Student  # ✅ Correct import

# DRUG_KEYWORDS = [
#     "drug", "weed", "marijuana", "cocaine", "heroin", "pill", "tablet", "inject",
#     "addict", "addiction", "sniff", "joint", "high", "overdose", "overdosed",
#     "overdosing", "meth", "crack", "narcotic", "opium", "substance", "needle"
# ]

# def detect_drug_text(text, student=None):
#     text_lower = text.lower()
#     detected_words = [w for w in DRUG_KEYWORDS if re.search(rf"{w}", text_lower)]
#     risk_score = min(100, len(detected_words) * 15)

#     if risk_score == 0:
#         label = "Safe"
#     elif risk_score < 40:
#         label = "Suspicious"
#     else:
#         label = "Drug-related"

#     # ✅ Only save to DB if student is provided and risk is nonzero
#     if student and risk_score > 0:
#         DrugAlert.objects.create(
#             student=student,
#             text=text,
#             label=label,
#             score=risk_score,
#             detected_words=detected_words
#         )

#     return {
#         "label": label,
#         "score": risk_score,
#         "detected_words": detected_words
#     }

#new 

# ai_detection/text_detector.py
import re
from students.models import DrugAlert

DRUG_KEYWORDS = [
    "drug", "weed", "marijuana", "cocaine", "heroin", "pill", "tablet",
    "inject", "addict", "addiction", "sniff", "joint", "high",
    "overdose", "overdosed", "meth", "crack", "narcotic", "opium",
    "substance", "needle"
]

def detect_drug_text(text, student=None):
    text_lower = text.lower()
    detected_words = [w for w in DRUG_KEYWORDS if re.search(rf"{w}", text_lower)]
    risk_score = min(100, len(detected_words) * 15)

    if risk_score == 0:
        label = "Safe"
    elif risk_score < 40:
        label = "Suspicious"
    else:
        label = "Drug-related"

    # ✅ Save to DB if risky
    if student and risk_score > 0:
        DrugAlert.objects.create(
            student=student,
            text=text,
            label=label,
            score=risk_score,
            detected_words=", ".join(detected_words)
        )

    return {
        "label": label,
        "score": risk_score,
        "detected_words": detected_words
    }
