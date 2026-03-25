from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from auth import router as auth_router
from chat import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat App MVP")

# ✅ CORS — REQUIRED for browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # 👈 IMPORTANT (see below)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")
