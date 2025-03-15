import os
import subprocess
from dotenv import load_dotenv


def validate_env():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY is missing in .env file.")
        exit(1)


def run_fastapi():
    try:
        subprocess.run(["fastapi", "run", "main.py"], check=True)
    except Exception as e:
        print(f"Error: failed to start. {e}")
        exit(1)
