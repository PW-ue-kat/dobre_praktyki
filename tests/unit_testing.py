import pytest
import math
import re
from collections import Counter
from typing import List, Dict, Any


# --- SEKCJA 1: FUNKCJE DO TESTOWANIA ---
# (Wklejone z poprzedniej odpowiedzi, aby plik był samowystarczalny)

def is_palindrome(text: str) -> bool:
    cleaned = "".join(filter(str.isalnum, text)).lower()
    return cleaned == cleaned[::-1]


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n nie może być ujemne")
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    VOWELS = "aeiouy"
    return sum(1 for char in text.lower() if char in VOWELS)


def calculate_discount(price: float, discount: float) -> float:
    if not (0 <= discount <= 1):
        raise ValueError("Wartość zniżki (discount) musi być w zakresie od 0 do 1.")
    return price * (1.0 - discount)


def flatten_list(nested_list: List[Any]) -> List[Any]:
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def word_frequencies(text: str) -> Dict[str, int]:
    words = re.findall(r'\b\w+\b', text.lower())
    return dict(Counter(words))


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    max_divisor = int(math.sqrt(n))
    for i in range(3, max_divisor + 1, 2):
        if n % i == 0:
            return False
    return True


# --- SEKCJA 2: TESTY JEDNOSTKOWE (PYTEST) ---

# 1. Testy dla is_palindrome
def test_is_palindrome():
    assert is_palindrome("kajak")
    assert is_palindrome("Kobyła ma mały bok")
    assert not is_palindrome("python")  # Używamy 'not' zamiast '== False'
    assert is_palindrome("")
    assert is_palindrome("A")


# 2. Testy dla fibonacci
def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55

    # Testowanie oczekiwanego wyjątku
    with pytest.raises(ValueError):
        fibonacci(-1)


# 3. Testy dla count_vowels
def test_count_vowels():
    assert count_vowels("Python") == 2
    assert count_vowels("AEIOUY") == 6
    assert count_vowels("bcd") == 0
    assert count_vowels("") == 0
    # Ten sam komentarz co poprzednio: funkcja liczy tylko 'a' i 'i'
    assert count_vowels("Próba żółwia") == 2


# 4. Testy dla calculate_discount
def test_calculate_discount():
    # Używamy pytest.approx do bezpiecznego porównywania floatów
    assert calculate_discount(100, 0.2) == pytest.approx(80.0)
    assert calculate_discount(50, 0) == pytest.approx(50.0)
    assert calculate_discount(200, 1) == pytest.approx(0.0)

    # Testowanie wyjątków dla wartości spoza zakresu [0, 1]
    with pytest.raises(ValueError):
        calculate_discount(100, -0.1)
    with pytest.raises(ValueError):
        calculate_discount(100, 1.5)


# 5. Testy dla flatten_list
def test_flatten_list():
    assert flatten_list([1, 2, 3]) == [1, 2, 3]
    assert flatten_list([1, [2, 3], [4, [5]]]) == [1, 2, 3, 4, 5]
    assert flatten_list([]) == []
    assert flatten_list([[[1]]]) == [1]
    assert flatten_list([1, [2, [3, [4]]]]) == [1, 2, 3, 4]


# 6. Testy dla word_frequencies
def test_word_frequencies():
    assert word_frequencies("To be or not to be") == {
        "to": 2, "be": 2, "or": 1, "not": 1
    }
    assert word_frequencies("Hello, hello!") == {"hello": 2}
    assert word_frequencies("") == {}
    assert word_frequencies("Python Python python") == {"python": 3}
    assert word_frequencies("Ala ma kota, a kot ma Ale.") == {
        "ala": 2, "ma": 2, "kota": 1, "a": 1, "kot": 1
    }


# 7. Testy dla is_prime
def test_is_prime():
    assert is_prime(2)
    assert is_prime(3)
    assert not is_prime(4)
    assert not is_prime(0)
    assert not is_prime(1)
    # Poprawka błędu z oryginalnej listy testów: 5 jest liczbą pierwszą
    assert is_prime(5)
    assert is_prime(97)
    assert not is_prime(99)