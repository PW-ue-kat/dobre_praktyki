import math
import re
from collections import Counter
from typing import List, Dict, Any # 'Any' jest przydatne dla zagnieżdżonych list

# --- Importy powinny znajdować się na górze pliku ---


# 1. Palindrom
def is_palindrome(text: str) -> bool:
    """
    Sprawdza, czy dany ciąg znaków jest palindromem
    (ignorując wielkość liter i znaki nieliterowe/niespacyjne).
    """
    # Usuwamy wszystko, co nie jest literą ani cyfrą, i zmieniamy na małe litery
    cleaned = "".join(filter(str.isalnum, text)).lower()
    
    # Porównujemy oczyszczony ciąg z jego odwrotnością
    return cleaned == cleaned[::-1]


# 2. Fibonacci
def fibonacci(n: int) -> int:
    """
    Zwraca n-ty element ciągu Fibonacciego (iteracyjnie).
    Założenia: fibonacci(0) == 0, fibonacci(1) == 1.
    """
    if n < 0:
        # Chociaż w poleceniu nie ma o tym mowy, warto obsłużyć ten przypadek
        raise ValueError("n nie może być ujemne")
    
    # Obsługa przypadków bazowych z polecenia
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Używamy podejścia iteracyjnego, które jest wydajniejsze niż rekurencja
    a, b = 0, 1
    # Musimy wykonać n-1 iteracji, aby dojść od F(1) do F(n)
    for _ in range(n - 1):
        a, b = b, a + b
        
    return b


# 3. Licznik samogłosek
def count_vowels(text: str) -> int:
    """
    Zlicza liczbę samogłosek w podanym ciągu (a, e, i, o, u, y)
    bez względu na wielkość liter.
    """
    VOWELS = "aeiouy"
    
    # Używamy wyrażenia generatorowego i sum() dla zwięzłości
    return sum(1 for char in text.lower() if char in VOWELS)


# 4. Obliczanie zniżki
def calculate_discount(price: float, discount: float) -> float:
    """
    Zwraca cenę po uwzględnieniu zniżki (discount jako ułamek, np. 0.2).
    Zgłasza ValueError, jeśli zniżka jest spoza zakresu [0, 1].
    """
    if not (0 <= discount <= 1):
        raise ValueError("Wartość zniżki (discount) musi być w zakresie od 0 do 1.")
        
    return price * (1.0 - discount)


# 5. Spłaszczanie listy
def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    Przyjmuje listę (mogącą zawierać zagnieżdżone listy) 
    i zwraca ją „spłaszczoną” (rekurencyjnie).
    Przykład: [1, [2, 3], [4, [5]]] → [1, 2, 3, 4, 5]
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            # Jeśli element jest listą, wywołujemy funkcję rekurencyjnie
            # i dodajemy jej elementy do naszej płaskiej listy
            flat_list.extend(flatten_list(item))
        else:
            # Jeśli element nie jest listą, po prostu go dodajemy
            flat_list.append(item)
    return flat_list


# 6. Częstość słów
def word_frequencies(text: str) -> Dict[str, int]:
    """
    Zwraca słownik z częstością występowania słów w tekście
    (ignorując wielkość liter i interpunkcję).
    """
    # Używamy regex (re.findall) do znalezienia wszystkich "słów"
    # \b - granica słowa, \w+ - jeden lub więcej znaków alfanumerycznych
    # text.lower() zapewnia ignorowanie wielkości liter
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Używamy collections.Counter do zliczenia, a następnie konwertujemy na dict
    return dict(Counter(words))


# 7. Liczba pierwsza
def is_prime(n: int) -> bool:
    """
    Sprawdza, czy liczba jest pierwsza.
    Jeśli n < 2, zwraca False.
    """
    # Zgodnie z wymaganiem: liczby pierwsze zaczynają się od 2
    if n < 2:
        return False
        
    # 2 jest jedyną parzystą liczbą pierwszą
    if n == 2:
        return True
        
    # Odrzucamy wszystkie inne liczby parzyste (optymalizacja)
    if n % 2 == 0:
        return False
        
    # Sprawdzamy dzielniki nieparzyste od 3 do pierwiastka kwadratowego z n
    # (włącznie, stąd +1 w zakresie)
    max_divisor = int(math.sqrt(n))
    
    # range(start, stop, step)
    for i in range(3, max_divisor + 1, 2):
        if n % i == 0:
            # Znaleziono dzielnik, więc n nie jest liczbą pierwszą
            return False
            
    # Jeśli pętla się zakończyła, nie znaleziono dzielników
    return True
