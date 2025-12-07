import unittest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Importujemy aplikację i modele z pliku all_data
from src.all_data import app, Base, Movie, Link, Rating, Tag
import src.all_data as all_data


class APITestCase(unittest.TestCase):

    def setUp(self):
        """Uruchamiane przed każdym testem."""
        app.config['TESTING'] = True
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.client = app.test_client()

        # Monkey-patching bazy danych dla testów
        all_data.engine = self.engine
        all_data.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_all_lists_exist(self):
        """Testuje czy działają endpointy listujące (GET all) dla każdej kategorii"""

        # 1. Dodajemy dane testowe
        self.client.post('/movies', json={'movieId': 1, 'title': 'M1', 'genres': 'G1'})
        self.client.post('/movies', json={'movieId': 2, 'title': 'M2', 'genres': 'G2'})

        self.client.post('/links', json={'movieId': 1, 'imdbId': 100, 'tmdbId': 200})
        self.client.post('/links', json={'movieId': 2, 'imdbId': 101, 'tmdbId': 201})

        self.client.post('/ratings', json={'userId': 1, 'movieId': 1, 'rating': 5.0, 'timestamp': 123})
        self.client.post('/ratings', json={'userId': 1, 'movieId': 2, 'rating': 4.0, 'timestamp': 124})

        self.client.post('/tags', json={'userId': 1, 'movieId': 1, 'tag': 'Funny', 'timestamp': 123})

        # 2. Sprawdzamy endpointy LIST

        # Movies List
        res_m = self.client.get('/movies')
        self.assertEqual(res_m.status_code, 200)
        self.assertEqual(len(res_m.get_json()), 2)

        # Links List
        res_l = self.client.get('/links')
        self.assertEqual(res_l.status_code, 200)
        self.assertEqual(len(res_l.get_json()), 2)

        # Ratings List
        res_r = self.client.get('/ratings')
        self.assertEqual(res_r.status_code, 200)
        self.assertEqual(len(res_r.get_json()), 2)

        # Tags List
        res_t = self.client.get('/tags')
        self.assertEqual(res_t.status_code, 200)
        self.assertEqual(len(res_t.get_json()), 1)

    def test_crud_flow_rating(self):
        """Szybki test CRUD dla Ratingu"""
        self.client.post('/movies', json={'movieId': 10, 'title': 'Test', 'genres': 'Test'})

        # Create
        res = self.client.post('/ratings', json={'userId': 99, 'movieId': 10, 'rating': 3.0, 'timestamp': 1})
        self.assertEqual(res.status_code, 201)
        r_id = res.get_json()['id']

        # Read Item
        self.assertEqual(self.client.get(f'/ratings/{r_id}').status_code, 200)

        # Update
        self.client.put(f'/ratings/{r_id}', json={'rating': 5.0})
        self.assertEqual(self.client.get(f'/ratings/{r_id}').get_json()['rating'], 5.0)

        # Delete
        self.client.delete(f'/ratings/{r_id}')
        self.assertEqual(self.client.get(f'/ratings/{r_id}').status_code, 404)


if __name__ == '__main__':
    unittest.main()