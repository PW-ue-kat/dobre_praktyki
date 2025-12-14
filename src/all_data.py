import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import bcrypt
import jwt
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

# --- 1. Configuration & Database Setup ---
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database Connection
db_path = '../data/movies.db'
engine = create_engine(f'sqlite:///{db_path}', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# --- 2. Database Models (SQLAlchemy) ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Movie(Base):
    __tablename__ = 'movies'
    movieId = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)

    # Relationships
    links = relationship("Link", back_populates="movie", uselist=False)
    ratings = relationship("Rating", back_populates="movie")
    tags = relationship("Tag", back_populates="movie")


class Link(Base):
    __tablename__ = 'links'
    movieId = Column(Integer, ForeignKey('movies.movieId'), primary_key=True)
    imdbId = Column(Integer)
    tmdbId = Column(Float)
    movie = relationship("Movie", back_populates="links")


class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey('movies.movieId'))
    rating = Column(Float)
    timestamp = Column(Integer)
    movie = relationship("Movie", back_populates="ratings")


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey('movies.movieId'))
    tag = Column(String)
    timestamp = Column(Integer)
    movie = relationship("Movie", back_populates="tags")


# Create tables (includes 'users' now if not present)
Base.metadata.create_all(engine)


# --- 3. Pydantic Models (Schemas for API) ---

class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class MovieOut(BaseModel):
    movieId: int
    title: str
    genres: str

    class Config:
        orm_mode = True
        # Note: In Pydantic v2 use 'from_attributes = True'

# Model wejściowy (to co wysyła użytkownik)
class UserCreate(BaseModel):
    username: str
    password: str

# Model wyjściowy (to co zwraca API - bez hasła!)
class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


# --- 4. Dependency Injection ---

def get_db():
    """Opens a DB session for a request, then closes it automatically."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 5. The Application & Routes ---

app = FastAPI()


@app.post("/login", response_model=Token)
def login(data: LoginData, db: Session = Depends(get_db)):
    """
    1. Check if user exists in SQLite DB
    2. Verify password hash
    3. Return JWT Token
    """
    # Query the database for the user
    user = db.query(User).filter(User.username == data.username).first()

    # Generic error to avoid user enumeration
    invalid_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise invalid_exception

    # Verify password (convert stored string back to bytes for bcrypt)
    stored_hash_bytes = user.hashed_password.encode('utf-8')
    input_password_bytes = data.password.encode('utf-8')

    if not bcrypt.checkpw(input_password_bytes, stored_hash_bytes):
        raise invalid_exception

    # Generate Token
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}


# --- Converted Data Routes (Flask -> FastAPI) ---

@app.get("/movies", response_model=List[MovieOut])
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch movies with pagination."""
    movies = db.query(Movie).offset(skip).limit(limit).all()
    return movies


@app.get("/links")
def get_links(db: Session = Depends(get_db)):
    return db.query(Link).limit(100).all()


@app.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).limit(100).all()


@app.get("/ratings")
def get_ratings(db: Session = Depends(get_db)):
    # Limit added for safety on large table
    return db.query(Rating).limit(100).all()


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Tworzy nowego użytkownika w bazie danych.
    """
    # 1. Sprawdź, czy użytkownik już istnieje
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 2. Zahaszuj hasło
    # bcrypt.hashpw oczekuje bajtów, więc używamy encode()
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 3. Utwórz obiekt użytkownika
    new_user = User(username=user.username, hashed_password=hashed_pw)

    # 4. Zapisz w bazie
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Odśwież, aby pobrać wygenerowane ID
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)