import requests
from core import memory


def get_weather(location=""):
    # Uses wttr.in format 3 (text only)
    # If no location is provided, it attempts to guess based on IP.
    try:
        url = f"https://wttr.in/{location}?format=3"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        return "Weather service is currently unavailable."
    except Exception:
        return "I could not connect to the weather service."


def handle_productivity_query(query):
    query = query.lower()

    # --- Weather ---
    if "weather" in query:
        # crude location extraction: "weather in london" -> "london"
        words = query.split()
        location = ""
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                location = " ".join(words[idx + 1 :])
        return get_weather(location)

    # --- Notes ---
    if "take a note" in query or "add a note" in query or "remember this" in query:
        return "I am ready. What would you like me to note down, Sir?"

    if "read my notes" in query or "what are my notes" in query:
        notes = memory.get_notes()
        if not notes:
            return "You do not have any saved notes, Sir."

        response = "Here are your notes: "
        for n in notes:
            response += f"Note {n[0]}: {n[1]}. "
        return response

    if "delete note" in query:
        # Extract number
        words = query.split()
        for w in words:
            if w.isdigit():
                memory.delete_note(int(w))
                return f"Deleted note number {w}."
        return "Which note number would you like me to delete?"

    # --- Reminders ---
    # Simplified reminder check triggers.
    # Proper parsing of time from voice is complex, we will hook this up
    # loosely to LLM summarization later or simple keywords here.
    if "remind me to" in query:
        # A full NLP implementation for time extraction is heavy.
        # We will let the Brain prompt the user for the exact interval if needed,
        # or implement a fast basic one here:
        return "<JarvisInternal> Needs Reminder Parsing"

    return None
