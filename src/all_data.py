from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

app = Flask(__name__)

# --- 1. Database Setup ---
# Point this to the location of your database file
db_path = '../data/movies.db'
engine = create_engine(f'sqlite:///{db_path}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


# --- 2. Define SQLAlchemy ORM Models ---
class Movie(Base):
    __tablename__ = 'movies'
    movieId = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)

    links = relationship("Link", back_populates="movie", uselist=False)
    ratings = relationship("Rating", back_populates="movie")
    tags = relationship("Tag", back_populates="movie")

    def to_dict(self):
        """Convert object to dictionary for JSON response."""
        return {
            'movieId': self.movieId,
            'title': self.title,
            'genres': self.genres
        }


class Link(Base):
    __tablename__ = 'links'
    movieId = Column(Integer, ForeignKey('movies.movieId'), primary_key=True)
    imdbId = Column(Integer)
    tmdbId = Column(Float)

    movie = relationship("Movie", back_populates="links")

    def to_dict(self):
        return {
            'movieId': self.movieId,
            'imdbId': self.imdbId,
            'tmdbId': self.tmdbId
        }


class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey('movies.movieId'))
    rating = Column(Float)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="ratings")

    def to_dict(self):
        return {
            'userId': self.userId,
            'movieId': self.movieId,
            'rating': self.rating,
            'timestamp': self.timestamp
        }


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey('movies.movieId'))
    tag = Column(String)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="tags")

    def to_dict(self):
        return {
            'userId': self.userId,
            'movieId': self.movieId,
            'tag': self.tag,
            'timestamp': self.timestamp
        }


# --- 3. Refactored Load Functions (Reading from DB) ---

def load_movies_from_db():
    session = Session()
    try:
        movies = session.query(Movie).all()
        # Convert to dict immediately so we can close the session
        return [movie.to_dict() for movie in movies]
    except Exception as e:
        print(f"Error loading movies: {e}")
        return []
    finally:
        session.close()


def load_links_from_db():
    session = Session()
    try:
        links = session.query(Link).all()
        return [link.to_dict() for link in links]
    except Exception as e:
        print(f"Error loading links: {e}")
        return []
    finally:
        session.close()


def load_ratings_from_db():
    session = Session()
    try:
        ratings = session.query(Rating).all()
        return [rating.to_dict() for rating in ratings]
    except Exception as e:
        print(f"Error loading ratings: {e}")
        return []
    finally:
        session.close()


def load_tags_from_db():
    session = Session()
    try:
        tags = session.query(Tag).all()
        return [tag.to_dict() for tag in tags]
    except Exception as e:
        print(f"Error loading tags: {e}")
        return []
    finally:
        session.close()


# --- 4. Flask Routes ---

@app.route('/')
def hello_world():
    return 'Hello, World! The database is connected.'


@app.route('/movies')
def get_movies():
    movies_data = load_movies_from_db()
    return jsonify(movies_data)


@app.route('/links')
def get_links():
    links_data = load_links_from_db()
    return jsonify(links_data)


@app.route('/tags')
def get_tags():
    tags_data = load_tags_from_db()
    return jsonify(tags_data)


@app.route('/ratings')
def get_ratings():
    # Warning: This table can be very large.
    # In a real app, you would likely want to limit this query or paginate.
    ratings_data = load_ratings_from_db()
    return jsonify(ratings_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)