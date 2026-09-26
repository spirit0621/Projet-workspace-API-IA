import os
import sys
import time
import wave
import json
import signal

RECORDINGS_DIR = "recordings"
STATE_FILE = ".recording_state.json"

def record_live_meeting(title="reunion"):
    """
    Enregistre l'audio en direct (micro / réunion) jusqu'à ce que l'utilisateur appuie sur Entrée.
    Retourne le chemin du fichier .wav généré.
    """
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError:
        print("❌ Erreur : 'sounddevice' et 'numpy' sont requis pour l'enregistrement audio.")
        print("Installez-les avec : pip install sounddevice numpy")
        return None

    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filename = os.path.join(RECORDINGS_DIR, f"{clean_title.replace(' ', '_')}_{int(time.time())}.wav")

    sample_rate = 16000  # 16 kHz mono (optimal pour la reconnaissance vocale et Gemini)
    channels = 1
    frames = []

    def audio_callback(indata, frame_count, time_info, status):
        if status:
            pass
        frames.append(indata.copy())

    print("\n" + "="*60)
    print(f"🎙️  [ENREGISTREMENT EN DIRECT] : '{title}'")
    print("👂 Écoute active de votre microphone et de la réunion...")
    print("👉 Appuyez sur [ENTRÉE] dans ce terminal pour arrêter et générer la fiche...")
    print("="*60 + "\n")

    try:
        with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='int16', callback=audio_callback):
            input()  # Attend l'appui sur Entrée
    except KeyboardInterrupt:
        print("\n⏹️  Interruption détectée (Ctrl+C).")

    print("\n⏳ Finalisation et sauvegarde du fichier audio...")
    if not frames:
        print("❌ Aucun signal audio capturé.")
        return None

    audio_data = np.concatenate(frames, axis=0)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16 bits = 2 octets
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    file_size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"✅ Fichier audio sauvegardé : {filename} ({file_size_mb:.2f} Mo)")
    return filename


def start_background_recording(title="reunion"):
    """Démarre un enregistrement audio en tâche de fond."""
    import subprocess
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filename = os.path.join(RECORDINGS_DIR, f"{clean_title.replace(' ', '_')}_{int(time.time())}.wav")

    # Script d'arrière-plan autonome
    script_code = f"""
import sounddevice as sd
import numpy as np
import wave
import signal
import sys

sample_rate = 16000
channels = 1
frames = []

def audio_callback(indata, frame_count, time_info, status):
    frames.append(indata.copy())

def save_and_exit(signum, frame):
    if frames:
        data = np.concatenate(frames, axis=0)
        with wave.open(r'{filename}', 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(data.tobytes())
    sys.exit(0)

signal.signal(signal.SIGTERM, save_and_exit)
signal.signal(signal.SIGINT, save_and_exit)

with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='int16', callback=audio_callback):
    while True:
        sd.sleep(1000)
"""
    bg_script_path = os.path.join(RECORDINGS_DIR, ".bg_recorder.py")
    with open(bg_script_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    proc = subprocess.Popen([sys.executable, bg_script_path], creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))

    state = {
        "pid": proc.pid,
        "filename": filename,
        "title": title,
        "start_time": time.time()
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    print(f"\n🎙️  Enregistrement en tâche de fond démarré (PID: {proc.pid})")
    print(f"📁 Fichier cible : {filename}")
    print("💡 Tapez 'python google_assistant.py record stop' pour terminer et générer la fiche.\n")


def stop_background_recording():
    """Arrête l'enregistrement en tâche de fond et retourne le fichier audio."""
    if not os.path.exists(STATE_FILE):
        print("❌ Aucun enregistrement en tâche de fond n'est actif.")
        return None, None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        pid = state.get("pid")
        filename = state.get("filename")
        title = state.get("title", "Réunion")
    except Exception as e:
        print(f"Erreur lors de la lecture de l'état : {e}")
        return None, None

    print(f"⏳ Arrêt du processus d'enregistrement (PID: {pid})...")
    try:
        if sys.platform == "win32":
            import subprocess
            subprocess.run(["taskkill", "/PID", str(pid), "/T"], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
        time.sleep(1.5)
    except Exception as e:
        print(f"Note lors de l'arrêt du processus : {e}")

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

    if os.path.exists(filename):
        duration = time.time() - state.get("start_time", time.time())
        mins, secs = divmod(int(duration), 60)
        print(f"✅ Enregistrement terminé (Durée: {mins}m {secs}s).")
        print(f"💾 Fichier audio : {filename}")
        return filename, title
    else:
        print(f"⚠️ Le fichier {filename} est introuvable ou n'a pas pu être finalisé.")
        return None, None
