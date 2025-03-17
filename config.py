import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyB9pIQu18j_pIgeIU1FThFk3Q2SMHEan90')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

# Security Configuration
MAX_INPUT_LENGTH = 1000  # Maximum allowed input length
LOG_FILE = 'security_logs.jsonl'  # Security log file
BLOCKED_PATTERNS = [
    # Prompt injection attempts
    "ignore previous instructions",
    "disregard all instructions",
    "ignore your guidelines",
    "forget your training",
    # System prompt attempts
    "system prompt:",
    "as an AI language model",
    # Jailbreak patterns
    "DAN mode",
    "developer mode",
    "root access",
    # Other security concerns
    "execute code",
    "shell command",
    "sudo",
    "password"
]

# Add sensitive topics that should be filtered
SENSITIVE_TOPICS = [
    "child abuse",
    "terrorism",
    "illegal activities",
    "self-harm",
    "hate speech"
]