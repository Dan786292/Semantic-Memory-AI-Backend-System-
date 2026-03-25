from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token
from utils import generate_code, hash_code, verify_code
from jose import jwt
from schemas import UserCreateWithCode
import os

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret")

router = APIRouter(tags=["auth"])

# Register
@router.post("/register", response_model=UserCreateWithCode)
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("📩 REGISTER endpoint reached")
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        print("❌ Email already exists")
        raise HTTPException(status_code=400, detail="Email already registered")

    code = generate_code()
    print("🔑 Generated code:", code)
    db_user = User(email=user.email, hashed_code=hash_code(code))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print("✅ User committed to DB")
    return {"email": db_user.email, "code": code}

# Login
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_code(user.code, db_user.hashed_code):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": db_user.email}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

# JWT helper
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
