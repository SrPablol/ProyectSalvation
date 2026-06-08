import os
import sys
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = ["GROQ_API_KEY", "INSTANTLY_API_KEY", "INSTANTLY_CAMPAIGN_ID"]

def validate():
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print(f"ERROR: Faltan variables de entorno en tu .env: {', '.join(missing)}")
        print("Copia .env.example a .env y completa los valores.")
        sys.exit(1)

def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)
