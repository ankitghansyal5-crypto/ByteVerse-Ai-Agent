import os
from pathlib import Path

# Load environment variables from local .env file if available
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing. "
        "Please configure GEMINI_API_KEY in your environment or in a local .env file. "
        "See .env.example for guidance."
    )
