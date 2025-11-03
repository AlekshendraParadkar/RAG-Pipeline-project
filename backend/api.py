# backend/api.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import init_db, get_db
from auth import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from generate import generate_answer  # uses your retrieve + Groq

app = FastAPI(title="RAG + Auth API", version="1.0.0")

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# CORS for local dev; tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set explicit origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=256)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Query(BaseModel):
    question: str = Field(min_length=3)

# Routes
@app.post("/auth/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    create_user(db, user.username, user.password)
    return {"message": "User created successfully"}

@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# Optional: JSON login for fetch-based clients
class LoginJSON(BaseModel):
    username: str
    password: str

@app.post("/auth/login-json", response_model=Token)
def login_json(payload: LoginJSON, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return {"username": user.username}

# Protected RAG endpoint
@app.post("/ask")
def ask(query: Query, user=Depends(get_current_user)):
    try:
        answer = generate_answer(query.question)
        return {"answer": answer}
    except Exception as e:
        # Keep failures informative without leaking sensitive internals
        raise HTTPException(status_code=500, detail=f"RAG failed: {str(e)}")
