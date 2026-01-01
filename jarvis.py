import sys, os, queue, threading, datetime, subprocess, uuid, time, wave, winsound, webbrowser
import numpy as np
import pyaudio
import ollama
import psutil
import keyboard
import win32gui, win32con
from faster_whisper import WhisperModel
from AppOpener import open as open_app
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer, Qt, QRectF, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient

# --- 1. THE BRAIN (Backend Processing) ---
class JarvisBrain(QThread):
    log_signal = pyqtSignal(str)
    abort_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.speech_queue = queue.Queue()
        self.chat_history = [{'role': 'system', 'content': 'You are Jarvis, a sophisticated assistant. Use "Sir".'}]
        # PATH CONFIGURATION - Ensure these paths are correct for your PC
        self.PIPER_EXE = r"C:\Jarvis\piper.exe"
        self.VOICE_MODEL = r"C:\Jarvis\voice\en_GB-jarvis-medium.onnx"
        self.is_listening = False
        self.current_proc = None

    def run(self):
        # 1. Initialize TTS Worker first
        threading.Thread(target=self.tts_worker, daemon=True).start()
        
        # 2. JARVIS STARTUP GREETING
        self.log_signal.emit("SYSTEM ONLINE")
        self.speak("Systems online. Jarvis is at your service, Sir.")
        
        # 3. Load heavy STT model
        self.log_signal.emit("LOADING NEURAL CORE...")
        stt_engine = WhisperModel("base.en", device="cpu", compute_type="int8")
        
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        
        self.log_signal.emit("ALL SYSTEMS NOMINAL")
        
        # HOTKEYS: TALK [CTRL+SHIFT+J+O], CANCEL [CTRL+SHIFT+J+C]
        keyboard.add_hotkey('ctrl+shift+j+o', lambda: self.trigger_listening(stream, stt_engine))
        keyboard.add_hotkey('ctrl+shift+j+c', self.stop_jarvis)
        
        keyboard.wait()

    def trigger_listening(self, stream, engine):
        if not self.is_listening:
            self.is_listening = True
            winsound.Beep(1000, 100)
            user_text = self.capture_and_transcribe(stream, engine)
            if user_text:
                self.log_signal.emit(f"USER: {user_text}")
                answer = self.handle_query(user_text)
                self.speak(answer)
            self.is_listening = False

    def capture_and_transcribe(self, stream, engine):
        self.log_signal.emit("LISTENING...")
        frames = []
        stream.stop_stream(); stream.start_stream()
        # Record for 4 seconds
        for _ in range(0, int(16000 / 1280 * 4)):
            if keyboard.is_pressed('ctrl+shift+j+c'): return None
            frames.append(stream.read(1280))
        
        temp_file = os.path.join(os.environ['TEMP'], "query.wav")
        with wave.open(temp_file, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000); wf.writeframes(b''.join(frames))
        
        segments, _ = engine.transcribe(temp_file, beam_size=5, vad_filter=True)
        text = " ".join([s.text for s in segments]).strip()
        return text if text else None

    def handle_query(self, query):
        query = query.lower()
        
        # --- TOOL: TIME & DATE ---
        if "time" in query or "date" in query:
            now = datetime.datetime.now()
            if "date" in query:
                return f"Today is {now.strftime('%A, %B %d, %Y')}, Sir."
            return f"It is currently {now.strftime('%I:%M %p')}."

        # --- TOOL: APPS ---
        if "open" in query or "launch" in query:
            app = query.replace("open", "").replace("launch", "").strip()
            open_app(app, match_closest=True)
            return f"Opening {app}, Sir."

        # --- TOOL: WEB ---
        if "google" in query or "search" in query:
            term = query.replace("google", "").replace("search", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={term}")
            return f"Searching for {term} on Google."

        # --- LLM CHAT ---
        self.chat_history.append({'role': 'user', 'content': query})
        try:
            response = ollama.chat(model='llama3.2:3b', messages=self.chat_history)
            reply = response['message']['content']
            self.chat_history.append({'role': 'assistant', 'content': reply})
            return reply
        except Exception:
            return "The local neural core is unreachable. Please ensure Ollama is running."

    def stop_jarvis(self):
        self.abort_signal.emit()
        self.log_signal.emit("COMMAND ABORTED")
        while not self.speech_queue.empty():
            try: self.speech_queue.get_nowait(); self.speech_queue.task_done()
            except: break
        if self.current_proc:
            try: subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.current_proc.pid)])
            except: pass
        winsound.PlaySound(None, winsound.SND_PURGE)

    def speak(self, text): 
        self.speech_queue.put(text)

    def tts_worker(self):
        while True:
            text = self.speech_queue.get()
            out = os.path.join(os.environ['TEMP'], f"j_{uuid.uuid4().hex}.wav")
            # Using Piper for high-quality local voice
            cmd = [self.PIPER_EXE, "--model", self.VOICE_MODEL, "--output_file", out]
            self.current_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
            self.current_proc.communicate(input=text)
            if os.path.exists(out):
                time.sleep(0.1)
                winsound.PlaySound(out, winsound.SND_FILENAME)
                os.remove(out)
            self.speech_queue.task_done()
            self.current_proc = None

# --- 2. THE INTERFACE (HUD) ---
class JarvisHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0; self.logs = []
        self.theme_color = QColor(0, 212, 255)
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(16)
        
        self.brain = JarvisBrain()
        self.brain.log_signal.connect(self.add_log)
        self.brain.abort_signal.connect(self.trigger_red_alert)
        self.brain.start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        # Position in bottom right
        self.setGeometry(screen.width() - 620, screen.height() - 650, 600, 600)

    def trigger_red_alert(self):
        self.theme_color = QColor(255, 50, 50)
        QTimer.singleShot(1500, lambda: setattr(self, 'theme_color', QColor(0, 212, 255)))

    def add_log(self, text):
        self.logs.append(f"> {text.upper()}")
        if len(self.logs) > 6: self.logs.pop(0)

    def update_ui(self):
        self.angle = (self.angle + 2) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()//2, self.height()//2
        now = datetime.datetime.now()
        
        # Rotating Arc (Visualizer)
        p.save(); p.translate(cx, cy); p.rotate(self.angle)
        grad = QConicalGradient(0, 0, 0); grad.setColorAt(0, self.theme_color); grad.setColorAt(0.6, QColor(0,0,0,0))
        p.setPen(QPen(grad, 4)); p.drawArc(QRectF(-150, -150, 300, 300), 0, 150 * 16); p.restore()
        
        # Center Clock
        p.setPen(self.theme_color); p.setFont(QFont("Consolas", 32, QFont.Weight.Bold))
        p.drawText(cx - 95, cy + 15, now.strftime("%H:%M:%S"))
        
        # Stats & Logs
        p.setFont(QFont("Consolas", 10))
        p.drawText(40, 520, f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
        y = 400
        for msg in self.logs: 
            p.drawText(cx - 100, y, msg)
            y += 20

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisHUD()
    window.show()
    sys.exit(app.exec())