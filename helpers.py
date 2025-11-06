def get_suggestions(text: str):
    """
    Simple rule-based suggestions for the demo app.
    Keep suggestions non-clinical and supportive.
    """
    text_lower = text.lower()
    suggestions = []
    if any(w in text_lower for w in ["sad", "depressed", "down", "hopeless"]):
        suggestions.append("Try a 5-minute grounding exercise (name 5 things you can see).")
        suggestions.append("Consider reaching out to one trusted person and telling them you need support.")
    if any(w in text_lower for w in ["anx", "anxiety", "panic", "worried", "nervous"]):
        suggestions.append("Do 4-4-4 breathing for 1-2 minutes: inhale 4s, hold 4s, exhale 4s.")
        suggestions.append("If you're having a panic episode and feel unsafe, contact emergency services.")
    if "sleep" in text_lower:
        suggestions.append("Try a wind-down routine: no screens 1 hour before bed, dim lights, read a book.")
    if "work" in text_lower or "stress" in text_lower:
        suggestions.append("Break tasks into 15-25 minute focused sessions (Pomodoro-style) and take short breaks.")
    if not suggestions:
        suggestions = [
            "Try a short breathing or grounding exercise for 2-5 minutes.",
            "Write down one small step you can take in the next hour to feel a bit better."
        ]
    suggestions.append("If these feelings are persistent or worsening, consider contacting a mental health professional.")
    return suggestions

def calming_breathing_text():
    return (
        "1. Sit comfortably with both feet on the floor.\n"
        "2. Close your eyes if that feels safe.\n"
        "\n"
        "**Cycle (repeat 5 times):**\n"
        "- Breathe in slowly for 4 seconds.\n"
        "- Hold for 4 seconds.\n"
        "- Breathe out slowly for 6 seconds.\n"
        "\n"
        "When finished, open your eyes and notice how your body feels."
    )
