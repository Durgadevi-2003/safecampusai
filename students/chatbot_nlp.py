import random
import spacy
from nltk.corpus import wordnet
import re

# Load small English model
nlp = spacy.load("en_core_web_sm")

# Define emotional categories & responses
RESPONSES = {
    "stress": [
        "It’s okay to feel stressed, {name}. Try a few deep breaths 🌿",
        "Stress happens to everyone, {name}. Maybe take a short break 💪",
    ],
    "anxiety": [
        "Anxiety can feel heavy, {name}. Try slow breathing — inhale 4s, exhale 4s 🧘",
        "Writing down your thoughts might help clear your mind ✍️",
    ],
    "sadness": [
        "I’m really sorry you’re feeling sad, {name}. You’re not alone 💙",
        "It’s okay to feel down sometimes — try talking to someone you trust 💬",
    ],
    "motivation": [
        "You’ve got this, {name}! Every small step matters 🌟",
        "Progress is progress, no matter how small. Keep going 💪",
    ],
    "sleep": [
        "Good rest helps a lot, {name}. Maybe try relaxing music 😴",
        "Avoid screens 30 minutes before bed and take a few deep breaths 💫",
    ],
    "exercise": [
        "Even a short walk can boost your mood, {name} 🚶‍♀️",
        "Stretching or light yoga can really help your mind and body 🌞",
    ],
    "crisis": [
        "Hey {name}, it sounds serious. Please contact your counselor or a trusted teacher immediately 🚨",
        "You’re not alone, {name}. Help is available — reach out right now 💖",
    ],
    "default": [
        "Hi {name}, I’m here for you. How are you feeling today? 💬",
        "You can share anything with me — this is a safe space 💖",
    ],
}

# Detect intent using keywords or NLP
def get_intent(text):
    text = text.lower()
    doc = nlp(text)

    crisis_words = ["die", "kill", "suicide", "overdose", "hopeless", "end it"]
    if any(word in text for word in crisis_words):
        return "crisis"

    emotion_map = {
        "stress": ["stress", "tired", "pressure", "burnout"],
        "anxiety": ["anxious", "nervous", "worried", "panic"],
        "sadness": ["sad", "cry", "lonely", "depressed"],
        "motivation": ["lazy", "no energy", "can't focus", "unmotivated"],
        "sleep": ["sleep", "insomnia", "tired", "awake"],
        "exercise": ["walk", "run", "exercise", "workout"],
    }

    for category, words in emotion_map.items():
        for w in words:
            if re.search(rf"\b{w}\b", text):
                return category

    # If nothing matches, fallback to NLP token intent
    for token in doc:
        for key in RESPONSES.keys():
            if key in token.text:
                return key

    return "default"

# 🧠 Final customized mental health reply
def mental_health_reply(user_input, student_name="Student"):
    intent = get_intent(user_input)
    reply = random.choice(RESPONSES[intent])
    return reply.format(name=student_name)
