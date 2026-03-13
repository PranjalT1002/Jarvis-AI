import os
from mss import mss
import requests
from bs4 import BeautifulSoup
import ollama


def take_screenshot():
    """Captures the primary monitor and saves to a temp file, returns path."""
    temp_img = os.path.join(os.environ["TEMP"], "jarvis_vision.png")
    with mss() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        # Save to disk
        from PIL import Image

        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.thumbnail((1024, 1024))  # Resize to save vram
        img.save(temp_img)
    return temp_img


def read_screen(query="What is on my screen?"):
    """Takes a screenshot and sends it to local llava model."""
    img_path = take_screenshot()

    try:
        response = ollama.chat(
            model="llava",
            messages=[{"role": "user", "content": query, "images": [img_path]}],
        )
        # Clean up
        if os.path.exists(img_path):
            os.remove(img_path)

        return response["message"]["content"]
    except Exception as e:
        if os.path.exists(img_path):
            os.remove(img_path)
        err_msg = str(e)
        return f"I could not analyze the screen. The error is: {err_msg[:60]}"


def search_and_summarize(query):
    """Searches Wikipedia or does a highly basic DuckDuckGo scrape to keep it text-only and anonymous."""

    # Simple DuckDuckGo HTML parsing (No JS)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"

    try:
        req = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(req.text, "html.parser")

        # Grab top 3 results text
        results = soup.find_all("a", class_="result__snippet", limit=3)
        snippets = [res.text for res in results]

        if not snippets:
            return "I could not find any relevant information on the local web."

        context = " \\n".join(snippets)

        # Summarize locally using llama3.2:3b
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": "You are Jarvis. Summarize the following internet search results into a concise, spoken answer (2-3 sentences max). Do not mention that these are search results.",
                },
                {
                    "role": "user",
                    "content": f"Search Query: {query}\\nResults: {context}",
                },
            ],
        )

        return response["message"]["content"]

    except Exception:
        return "I failed to connect to the external web, Sir."
