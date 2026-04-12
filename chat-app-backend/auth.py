from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserCreateWithCode
from utils import generate_code, hash_code, verify_code
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret")

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserCreateWithCode)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Register attempt for email={user.email}")

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Register failed - email already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    code = generate_code()
    logger.debug(f"Generated verification code for {user.email}")

    db_user = User(email=user.email, hashed_code=hash_code(code))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"User created successfully: {user.email}")

    return {"email": db_user.email, "code": code}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email={user.email}")

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        logger.warning(f"Login failed - user not found: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_code(user.code, db_user.hashed_code):
        logger.warning(f"Login failed - invalid code for: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": db_user.email}, SECRET_KEY, algorithm="HS256")

    logger.info(f"Login successful: {user.email}")

    return {"access_token": token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    logger.debug("Validating JWT token")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")

        if email is None:
            logger.warning("JWT missing subject (email)")
            raise credentials_exception

    except JWTError:
        logger.warning("JWT decoding failed")
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        logger.warning(f"User from token not found: {email}")
        raise credentials_exception

    logger.debug(f"Authenticated user: {email}")

    return user