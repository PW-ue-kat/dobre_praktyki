from flask import Flask, jsonify, request, abort
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

app = Flask(__name__)

# --- 1. Konfiguracja Bazy Danych ---
# Używamy ścieżki absolutnej, aby uniknąć błędu "unable to open database file"
# niezależnie od tego, skąd uruchamiamy skrypt.
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'movies.db')

# Zauważ: create_engine jest "leniwy", samo utworzenie obiektu nie łączy z bazą.
engine = create_engine(f'sqlite:///{db_path}', echo=False)

Base = declarative_base()
Session = sessionmaker(bind=engine)


# --- 2. Modele SQLAlchemy ---
class Movie(Base):
    __tablename__ = 'movies'
    movieId = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)

    links = relationship("Link", back_populates="movie", uselist=False, cascade="all, delete")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete")
    tags = relationship("Tag", back_populates="movie", cascade="all, delete")

    def to_dict(self):
        return {'movieId': self.movieId, 'title': self.title, 'genres': self.genres}


class Link(Base):
    __tablename__ = 'links'
    movieId = Column(Integer, ForeignKey('movies.movieId'), primary_key=True)
    imdbId = Column(Integer)
    tmdbId = Column(Float)

    movie = relationship("Movie", back_populates="links")

    def to_dict(self):
        return {'movieId': self.movieId, 'imdbId': self.imdbId, 'tmdbId': self.tmdbId}


class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey('movies.movieId'))
    rating = Column(Float)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="ratings")

    def to_dict(self):
        return {'id': self.id, 'userId': self.userId, 'movieId': self.movieId,
                'rating': self.rating, 'timestamp': self.timestamp}


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey('movies.movieId'))
    tag = Column(String)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="tags")

    def to_dict(self):
        return {'id': self.id, 'userId': self.userId, 'movieId': self.movieId,
                'tag': self.tag, 'timestamp': self.timestamp}


# USUNIĘTO LINIĘ: Base.metadata.create_all(engine) z głównego zakresu!

def get_session():
    return Session()


# Helper do paginacji
def get_paginated_list(session, model_class):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    if per_page > 1000: per_page = 1000
    if per_page < 1: per_page = 10
    offset = (page - 1) * per_page
    items = session.query(model_class).limit(per_page).offset(offset).all()
    return [item.to_dict() for item in items]


@app.route('/')
def hello_world():
    return 'API Filmów działa.'


# --- ENDPOINTY (skrócone dla czytelności - są takie same jak wcześniej) ---
# ... (Wklej tutaj endpointy CRUD z poprzedniej odpowiedzi) ...
# Dla kompletności, upewnij się, że masz tu wszystkie definicje route'ów
# (get_movies, create_movie, etc.)

# --- START APLIKACJI ---
if __name__ == '__main__':
    # Tworzymy tabele TYLKO gdy uruchamiamy ten plik bezpośrednio (nie przy imporcie)
    Base.metadata.create_all(engine)
    print("Baza danych zainicjalizowana.")
    app.run(debug=True, host='0.0.0.0', port=5001)