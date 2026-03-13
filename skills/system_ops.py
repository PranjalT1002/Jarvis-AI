import os
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard

# --- WINDOWS CONSTANTS ---
user32 = ctypes.windll.user32
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1


def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def set_volume(level_percent):
    try:
        volume = get_volume_interface()
        # clamp between 0 and 100
        level_percent = max(0, min(100, level_percent))

        # Scalar way
        volume.SetMasterVolumeLevelScalar(level_percent / 100.0, None)
        return f"Volume set to {level_percent}%"
    except Exception as e:
        return f"Failed to set volume: {e}"


def mute_volume(state=True):
    try:
        volume = get_volume_interface()
        volume.SetMute(1 if state else 0, None)
        return "Muted the system volume." if state else "Unmuted the system volume."
    except Exception as e:
        return f"Failed to modify mute state: {e}"


def media_play_pause():
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)
    return "Toggled play/pause."


def media_next():
    user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 2, 0)
    return "Playing next track."


def media_prev():
    user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, 2, 0)
    return "Playing previous track."


def minimize_all_windows():
    keyboard.send("win+d")
    return "Minimized all windows."


def lock_screen():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "Locked the screen."


def handle_system_query(query):
    query = query.lower()

    # Matching simple logic
    if "lock" in query and "screen" in query:
        return lock_screen()
    if "minimize" in query and "windows" in query:
        return minimize_all_windows()

    if "play" in query or "pause" in query:
        return media_play_pause()
    if "next" in query and ("track" in query or "song" in query):
        return media_next()
    if "previous" in query and ("track" in query or "song" in query):
        return media_prev()

    if "mute" in query:
        return mute_volume(True)
    if "unmute" in query:
        return mute_volume(False)
    if "volume" in query and "set" in query:
        try:
            # Extract number from query (e.g. "set volume to 50")
            words = query.split()
            vol = None
            for w in words:
                clean_w = w.replace("%", "")
                if clean_w.isdigit():
                    vol = int(clean_w)
                    break

            if vol is not None:
                return set_volume(vol)
        except Exception:
            pass

    return None
