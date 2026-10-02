import io
import wave

import numpy as np
import pyttsx3
import sounddevice as sd

from agent import ask, client, history

SAMPLE_RATE = 16000


def record_until_enter():
    """Push-to-talk: Enter to start, Enter to stop."""
    input("\nPress Enter, then speak...")
    chunks = []

    def callback(indata, frame_count, time_info, status):
        chunks.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype="int16", callback=callback):
        input("Listening... press Enter when done.")

    if not chunks:
        return None
    return np.concatenate(chunks)


def to_wav_bytes(audio):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit audio
        w.setframerate(SAMPLE_RATE)
        w.writeframes(audio.tobytes())
    return buf.getvalue()


def transcribe(wav_bytes):
    result = client.audio.transcriptions.create(
        file=("audio.wav", wav_bytes),
        model="whisper-large-v3",
        language="en",
    )
    return result.text.strip()


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


if __name__ == "__main__":
    greeting = "Hello, Sunrise Dental Clinic. How can I help you today?"
    history.append({"role": "assistant", "content": greeting})
    print("Riya:", greeting)
    speak(greeting)

    while True:
        audio = record_until_enter()
        if audio is None or len(audio) < SAMPLE_RATE // 2:
            print("(didn't catch that, try again)")
            continue

        text = transcribe(to_wav_bytes(audio))
        if not text:
            print("(didn't catch that, try again)")
            continue
        print("You:", text)

        if text.lower().strip(" .!") in ("quit", "exit", "goodbye"):
            break

        reply = ask(text)
        print("Riya:", reply)
        speak(reply)