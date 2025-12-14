import pandas as pd
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# 1. Konfiguracja bazy
db_file = '../data/movies.db'
engine = create_engine(f'sqlite:///{db_file}', echo=False)
Base = declarative_base()


# 2. Definicja Modeli (Zgodna z main.py)

class Movie(Base):
    __tablename__ = 'movies'
    movieId = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)
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


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    roles = Column(String)  # Przechowujemy jako string "ROLE_USER,ROLE_ADMIN"


# 3. Resetowanie Bazy (Drop & Create)
print("--- RESETOWANIE BAZY DANYCH ---")
print("Usuwanie starych tabel...")
Base.metadata.drop_all(engine)
print("Tworzenie nowego schematu...")
Base.metadata.create_all(engine)
print("Schemat utworzony pomyślnie.")


# 4. Ładowanie danych
def load_csv_to_DB():
    try:
        # --- Filmy i inne dane ---
        print("Ładowanie danych filmowych...")
        # Pandas automatycznie dopasuje kolumny po nazwach nagłówków w CSV
        pd.read_csv('../data/movies.csv').to_sql('movies', con=engine, if_exists='append', index=False)
        pd.read_csv('../data/links.csv').to_sql('links', con=engine, if_exists='append', index=False)
        pd.read_csv('../data/ratings.csv').to_sql('ratings', con=engine, if_exists='append', index=False)
        pd.read_csv('../data/tags.csv').to_sql('tags', con=engine, if_exists='append', index=False)
        print("Dane filmowe załadowane.")

        # --- Użytkownicy ---
        print("Ładowanie użytkowników...")
        try:
            # Oczekujemy CSV: username, password, roles
            df_users = pd.read_csv('../data/users.csv')

            # Zabezpieczenie: jeśli w CSV brakuje kolumny roles, dodaj domyślną
            if 'roles' not in df_users.columns:
                df_users['roles'] = 'ROLE_USER'
            else:
                df_users['roles'] = df_users['roles'].fillna('ROLE_USER')

            # Funkcja haszująca
            def hash_password(plain_password):
                return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Tworzymy kolumnę hashed_password na podstawie password
            df_users['hashed_password'] = df_users['password'].apply(hash_password)

            # Wybieramy i porządkujemy kolumny tak, by pasowały do tabeli User w SQL
            # (username i roles już są poprawne z CSV, dodajemy hashed_password)
            df_users_final = df_users[['username', 'hashed_password', 'roles']]

            # Zapis do bazy
            df_users_final.to_sql('users', con=engine, if_exists='append', index=False)

            print(f"Sukces! Dodano {len(df_users_final)} użytkowników.")
            print("Przykładowe dane:")
            print(df_users_final.head())

        except FileNotFoundError:
            print("BŁĄD: Nie znaleziono pliku users.csv.")
        except KeyError as e:
            print(f"BŁĄD FORMATU CSV: Brakuje kolumny: {e}. Sprawdź nagłówki w users.csv.")

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")


if __name__ == "__main__":
    load_csv_to_DB()