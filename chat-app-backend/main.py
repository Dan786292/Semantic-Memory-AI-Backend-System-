from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from auth import router as auth_router
from chat import router as chat_router
from logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting application...")

Base.metadata.create_all(bind=engine)
logger.info("Database tables ensured")

app = FastAPI(title="Chat App MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")

logger.info("Routers registered")