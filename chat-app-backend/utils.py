import secrets
from passlib.context import CryptContext
import requests
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth utilities
def generate_code(length=6):
    return ''.join(secrets.choice("0123456789") for _ in range(length))

def hash_code(code: str):
    return pwd_context.hash(code)

def verify_code(plain_code, hashed_code):
    return pwd_context.verify(plain_code, hashed_code)

# LLM API integration
API_URL = os.getenv("APIFREE_LLM_URL", "https://api.apifree-llm.com/generate")
API_KEY = os.getenv("APIFREE_LLM_KEY", "demo-key")

def call_llm(prompt: str) -> str:
    """
    Call ApiFreeLLM to get a response for the prompt.
    """
    try:
        res = requests.post(
            "https://apifreellm.com/api/chat",
            json={"message": prompt},
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
        return data.get("response", "Sorry, I could not generate a response.")
    except Exception as e:
        print("LLM API call failed:", e)
        return "Sorry, I could not generate a response."
