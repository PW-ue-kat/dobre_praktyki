# 1. Importuj niezbędne moduły
from flask import Flask, jsonify
import csv

# 2. Stwórz instancję klasy Flask
app = Flask(__name__)


# --- Nowy kod: Definicja klasy Movie ---
class Rating:
    """
    Prosta klasa (model danych) do przechowywania informacji o filmie.
    """

    def __init__(self, userId, movieId, rating, timestamp):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
        self.timestamp = timestamp

# --- Nowy kod: Definicja klasy Movie ---
class Tag:
    """
    Prosta klasa (model danych) do przechowywania informacji o filmie.
    """

    def __init__(self, userId, movieId, tag, timestamp):
        self.userId = userId
        self.movieId = movieId
        self.tag = tag
        self.timestamp = timestamp

# --- Nowy kod: Definicja klasy Movie ---
class Movie:
    """
    Prosta klasa (model danych) do przechowywania informacji o filmie.
    """

    def __init__(self, movieId, title, genres):
        self.movieId = movieId
        self.title = title
        self.genres = genres


# --- Nowy kod: Definicja klasy Movie ---
class Link:
    """
    Prosta klasa (model danych) do przechowywania informacji o filmie.
    """

    def __init__(self, movieId, imdbId, tmdbId):
        self.movieId = movieId
        self.title = imdbId
        self.genres = tmdbId








# --- Nowy kod: Funkcja do wczytania filmów ---
def load_movies_from_csv(filepath='../data/movies.csv'):

    """
    Wczytuje dane z pliku CSV i zwraca listę obiektów Movie.
    """
    movies = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            # Używamy DictReader, aby automatycznie mapować nagłówki na klucze słownika
            reader = csv.DictReader(file)

            # 3. Iterowanie po wierszach i tworzenie obiektów
            for row in reader:
                movie = Movie(row['movieId'], row['title'], row['genres'])
                movies.append(movie)
        print(f"Wczytano {len(movies)} filmów z pliku '{filepath}'.")
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku '{filepath}'. Upewnij się, że plik istnieje.")
    except Exception as e:
        print(f"Wystąpił błąd podczas wczytywania pliku: {e}")

    return movies

# --- Nowy kod: Funkcja do wczytania filmów ---
def load_ratings_from_csv(filepath='../data/ratings.csv'):

    """
    Wczytuje dane z pliku CSV i zwraca listę obiektów Movie.
    """
    ratings = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            # Używamy DictReader, aby automatycznie mapować nagłówki na klucze słownika
            reader = csv.DictReader(file)

            # 3. Iterowanie po wierszach i tworzenie obiektów
            for row in reader:
                rating = Rating(row['userId'], row['movieId'], row['rating'], row['timestamp'])
                ratings.append(rating)
        print(f"Wczytano {len(ratings)} ratings z pliku '{filepath}'.")
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku '{filepath}'. Upewnij się, że plik istnieje.")
    except Exception as e:
        print(f"Wystąpił błąd podczas wczytywania pliku: {e}")

    return ratings

# --- Nowy kod: Funkcja do wczytania filmów ---
def load_tags_from_csv(filepath='../data/tags.csv'):

    """
    Wczytuje dane z pliku CSV i zwraca listę obiektów Movie.
    """
    tags = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            # Używamy DictReader, aby automatycznie mapować nagłówki na klucze słownika
            reader = csv.DictReader(file)

            # 3. Iterowanie po wierszach i tworzenie obiektów
            for row in reader:
                tag = Tag(row['userId'], row['movieId'], row['tag'], row['timestamp'])
                tags.append(tag)
        print(f"Wczytano {len(tags)} tag z pliku '{filepath}'.")
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku '{filepath}'. Upewnij się, że plik istnieje.")
    except Exception as e:
        print(f"Wystąpił błąd podczas wczytywania pliku: {e}")

    return tags



# --- Nowy kod: Funkcja do wczytania filmów ---
def load_links_from_csv(filepath='../data/links.csv'):

    """
    Wczytuje dane z pliku CSV i zwraca listę obiektów Movie.
    """
    links = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            # Używamy DictReader, aby automatycznie mapować nagłówki na klucze słownika
            reader = csv.DictReader(file)

            # 3. Iterowanie po wierszach i tworzenie obiektów
            for row in reader:
                link = Link(row['movieId'], row['imdbId'], row['tmdbId'])
                links.append(link)
        print(f"Wczytano {len(links)} linków z pliku '{filepath}'.")
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku '{filepath}'. Upewnij się, że plik istnieje.")
    except Exception as e:
        print(f"Wystąpił błąd podczas wczytywania pliku: {e}")

    return links



# Wczytaj listę filmów raz, przy starcie aplikacji
# (bardziej wydajne niż wczytywanie przy każdym żądaniu)
movie_list = load_movies_from_csv()
link_list = load_links_from_csv()
rating_list = load_ratings_from_csv()
tag_list = load_tags_from_csv()


# --- Koniec nowego kodu ---


# 3. Definicja trasy głównej (pozostaje bez zmian)
@app.route('/')
def hello_world():
    """
    Ta funkcja uruchamia się dla trasy '/' (strona główna).
    """
    return 'Hello, World!'


# --- Nowy kod: Trasa /movies ---
@app.route('/movies')
def get_movies():
    """
    Zwraca pełną listę filmów w formacie JSON.
    """
    # 4. Wykorzystanie metody magicznej __dict__ do serializacji
    #    Używamy list comprehension do konwersji każdego obiektu Movie na słownik
    serialized_movies = [movie.__dict__ for movie in movie_list]

    # 5. Zwrócenie listy zserializowanych obiektów jako JSON
    return jsonify(serialized_movies)



@app.route('/links')
def get_links():
    """
    Zwraca pełną listę filmów w formacie JSON.
    """
    # 4. Wykorzystanie metody magicznej __dict__ do serializacji
    #    Używamy list comprehension do konwersji każdego obiektu Movie na słownik
    serialized_links = [link.__dict__ for link in link_list]

    # 5. Zwrócenie listy zserializowanych obiektów jako JSON
    return jsonify(serialized_links)

@app.route('/tags')
def get_tags():
    """
    Zwraca pełną listę filmów w formacie JSON.
    """
    # 4. Wykorzystanie metody magicznej __dict__ do serializacji
    #    Używamy list comprehension do konwersji każdego obiektu Movie na słownik
    serialized_tags = [tag.__dict__ for tag in tag_list]

    # 5. Zwrócenie listy zserializowanych obiektów jako JSON
    return jsonify(serialized_tags)


@app.route('/ratings')
def get_ratings():
    """
    Zwraca pełną listę filmów w formacie JSON.
    """
    # 4. Wykorzystanie metody magicznej __dict__ do serializacji
    #    Używamy list comprehension do konwersji każdego obiektu Movie na słownik
    serialized_ratings = [rating.__dict__ for rating in rating_list]

    # 5. Zwrócenie listy zserializowanych obiektów jako JSON
    return jsonify(serialized_ratings)






# 4. Sprawdzenie, czy skrypt jest uruchamiany bezpośrednio
if __name__ == '__main__':
    # 5. Uruchomienie aplikacji
    app.run(debug=True, host='0.0.0.0', port=5001)