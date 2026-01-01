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

## 🛠️ Technical Architecture


This system uses a **Producer-Consumer threading model**:
1. **The Brain (Producer):** Handles heavy STT/LLM tasks on a background thread to keep the UI responsive.
2. **The HUD (Consumer):** Updates the visual interface at 60 FPS using a dedicated timer loop.

## 🚀 Setup & Installation

### 1. Prerequisites
- **Ollama:** [Download here](https://ollama.com/) and run `ollama pull llama3.2:3b`.
- **Piper TTS:** Place `piper.exe` and your `.onnx` voice model in `C:\Jarvis\`.

### 2. Installation
Clone this repository or download the source code, then install the dependencies:
pip install -r requirements.txt
