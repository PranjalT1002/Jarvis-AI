# 🎙️ JARVIS: Local Desktop Assistant
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Llama_3.2-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A sophisticated, multi-threaded AI assistant inspired by Iron Man's JARVIS. This project integrates a local neural core for privacy and speed, featuring a futuristic HUD and real-time system monitoring.

## ✨ Key Features
- **🧠 Local Intelligence:** Powered by **Ollama (Llama 3.2)**. No cloud APIs required—fully private conversation.
- **🎙️ Fast Transcription:** Implements **Faster-Whisper** for near-instant speech-to-text processing.
- **🖥️ Futuristic HUD:** A transparent, custom-painted dashboard built with **PyQt6** and **QPainter**.
- **📊 System Diagnostics:** Real-time monitoring of CPU and RAM usage directly on the HUD.
- **🔊 High-Quality Voice:** Utilizes **Piper TTS** for a natural-sounding local voice engine.
- **🛠️ Integrated Tools:** Voice-activated app launching, Google searching, and system time/date queries.

## 🚀 Setup
1. Install [Ollama](https://ollama.com/) and run `ollama pull llama3.2:3b`.
2. Place `piper.exe` and voice models in `C:\Jarvis\`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run `python main.py`.

## ⌨️ Hotkeys
- `Ctrl + Shift + J + O`: Talk
- `Ctrl + Shift + J + C`: Cancel
