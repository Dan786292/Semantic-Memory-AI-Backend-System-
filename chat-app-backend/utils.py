import secrets
from passlib.context import CryptContext
import requests
import os
import logging
import time
import math
import json

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "true").lower() == "true"

load_dotenv()

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =========================
# AUTH
# =========================

def generate_code(length=6):
    return ''.join(
        secrets.choice("0123456789")
        for _ in range(length)
    )


def hash_code(code: str):
    return pwd_context.hash(code)


def verify_code(plain_code, hashed_code):
    return pwd_context.verify(plain_code, hashed_code)


# =========================
# LLM CONFIG
# =========================

API_URL = os.getenv(
    "APIFREE_LLM_URL",
    "https://hf.space/embed/fffiloni/SmallGPT/api/predict/"
)

# =========================
# EMBEDDING MODEL
# =========================

logger.info("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

logger.info("Embedding model loaded")

# =========================
# INPUT SANITIZATION
# =========================

BLOCKED_PATTERNS = [
    "ignore previous",
    "system prompt",
    "developer mode",
    "reveal instructions"
]


def sanitize_input(text: str) -> str:

    lowered = text.lower()

    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            logger.warning(
                f"Blocked suspicious prompt: {text}"
            )
            return "[FILTERED INPUT]"

    return text


# =========================
# EMBEDDINGS
# =========================

def text_to_vector(text: str):

    vector = embedding_model.encode(text)

    return vector.tolist()


def cosine_similarity(v1, v2):

    dot = sum(a * b for a, b in zip(v1, v2))

    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot / (norm1 * norm2)


def serialize_vector(vec):
    return json.dumps(vec)


def deserialize_vector(vec_str):

    if not vec_str:
        return None

    return json.loads(vec_str)


# =========================
# LLM CALL
# =========================

def call_llm(prompt: str) -> str:

    logger.info("Calling LLM service")

    print("---- Prompt being sent to LLM ----")
    print(prompt)
    print("---------------------------------")

    #if USE_MOCK_LLM:
    #    return "This is a mock response for testing purposes."


    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):

        try:

            start = time.time()

            res = requests.post(
                API_URL,
                json={"message": prompt},
                timeout=15
            )

            latency = time.time() - start

            logger.info(
                f"LLM response received in "
                f"{latency:.2f}s"
            )

            res.raise_for_status()

            data = res.json()

            logger.debug(f"LLM raw response: {data}")

            return data.get(
                "response",
                "Sorry, I could not generate a response."
            )

        except requests.exceptions.Timeout:

            logger.warning(
                f"LLM timeout attempt "
                f"{attempt + 1}/{MAX_RETRIES}"
            )

        except Exception:

            logger.error(
                "LLM API call failed",
                exc_info=True
            )

        time.sleep(2 ** attempt)

    return (
        "The AI service is currently unavailable. "
        "Please try again later."
    )