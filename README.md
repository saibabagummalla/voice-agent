# Riya: AI Voice Receptionist for a Dental Clinic

A voice agent that answers as a clinic receptionist, checks real availability,
and books appointments into a database. Built from scratch in Python.

## How it works

Mic → Whisper (speech-to-text) → LLM with tool calling → text-to-speech → Speaker

- `agent.py`: system prompt, conversation history, and the tool-calling loop
- `voice.py`: push-to-talk recording, transcription, spoken replies, latency timing
- `tools.py`: availability check and booking, with validation (closed Sundays,
  no past dates, no double booking), stored in SQLite

## Tech stack

Python, Groq API (LLM and Whisper), SQLite, sounddevice, pyttsx3

## Setup

1. `pip install -r requirements.txt`
2. Create a `.env` file containing `GROQ_API_KEY=your_key_here`
3. Run `python voice.py` for voice, or `python agent.py` for text-only

## Performance

Speech-to-text: ~2.09 s per turn. LLM + tool calls: ~0.96 s per turn.

## Challenges and fixes

- The model invented dates, so I inject today's date into the system prompt.
- It confirmed bookings that were never saved, so I added tool calling and a database.
- Occasional malformed model output, so I added retry logic and error handling.
- Prompt rules weren't reliable on their own, so closed days and double bookings
  are enforced in code.

## Limitations and next steps

Push-to-talk only, a robotic offline voice, one clinic, no cancellations.
Next: streaming audio, a better TTS voice, cancel/reschedule tools, phone integration.