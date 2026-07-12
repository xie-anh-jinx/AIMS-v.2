from datetime import datetime, timedelta
import os
import jwt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt
from pydantic import BaseModel

from packages.database.connection import get_db
from packages.database.models import User, Student, Advisor

# Hardcoded for Dev phase 1
SECRET_KEY = "aims-secret-super-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    name: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Auto-provision logic for demo phase: if username matches a known NIM/NIP and password is password123
    if not user and form_data.password == "password123":
        student = db.query(Student).filter(Student.nim == form_data.username).first()
        if student:
            user = User(username=student.nim, hashed_password=get_password_hash("password123"), role="STUDENT")
            db.add(user)
            db.commit()
            db.refresh(user)
            student.user_id = user.id
            db.commit()
        else:
            advisor = db.query(Advisor).filter(Advisor.nama.ilike(f"%{form_data.username}%")).first() # NIP usually mapped as username, fallback
            # Since advisors were already provisioned by cached token script, we skip auto-provision for them here.

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "id": user.id},
        expires_delta=access_token_expires
    )
    
    user_name = user.username
    if user.role == "STUDENT":
        student = db.query(Student).filter(Student.user_id == user.id).first()
        if student:
            user_name = student.nama
    elif user.role == "ADVISOR":
        advisor = db.query(Advisor).filter(Advisor.user_id == user.id).first()
        if advisor:
            user_name = advisor.nama
    elif user.role == "ADMIN":
        user_name = "Administrator"

    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "user_id": user.id, "name": user_name}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
