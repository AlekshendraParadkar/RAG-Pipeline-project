# backend/db.py
import os
from sqlalchemy import create_engine, String, Integer, Column
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        # For cases where path/permissions are off
        raise

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
