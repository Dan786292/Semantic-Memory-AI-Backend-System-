from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- Existing UserCreate ---
class UserCreate(BaseModel):
    email: EmailStr

# --- New schema including code ---
class UserCreateWithCode(UserCreate):
    code: str

# Auth
class UserLogin(BaseModel):
    email: EmailStr
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Chat
class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageRead(BaseModel):
    id: int
    message: str
    response: str | None
    created_at: datetime

    class Config:
        orm_mode = True
