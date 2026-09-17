"""
Central config for VitalCheck AI.
Reads secrets/settings from .env (never hardcode API keys).
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))  # low temp = more consistent, less "creative" medical output

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing. Add it to your .env file (see .env.example).")
