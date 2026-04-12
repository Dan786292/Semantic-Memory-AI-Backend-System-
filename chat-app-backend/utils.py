import secrets
from passlib.context import CryptContext
import requests
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_code(length=6):
    return ''.join(secrets.choice("0123456789") for _ in range(length))


def hash_code(code: str):
    return pwd_context.hash(code)


def verify_code(plain_code, hashed_code):
    return pwd_context.verify(plain_code, hashed_code)


API_URL = os.getenv("APIFREE_LLM_URL", "https://apifreellm.com/api/chat")


def call_llm(prompt: str) -> str:
    logger.info("Calling LLM service")

    try:
        start = time.time()

        res = requests.post(
            API_URL,
            json={"message": prompt},
            timeout=10
        )

        latency = time.time() - start
        logger.info(f"LLM response received in {latency:.2f}s")

        res.raise_for_status()

        data = res.json()
        return data.get("response", "Sorry, I could not generate a response.")

    except requests.exceptions.Timeout:
        logger.error("LLM request timed out")
        return "The service is taking too long. Please try again."

    except Exception as e:
        logger.error("LLM API call failed", exc_info=True)
        return "Sorry, I could not generate a response."