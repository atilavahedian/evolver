import random

from solution import longest_unique_substring


def brute_force(text):
    best = 0
    for start in range(len(text) + 1):
        for end in range(start, len(text) + 1):
            candidate = text[start:end]
            if len(set(candidate)) == len(candidate):
                best = max(best, len(candidate))
    return best


def test_known_cases():
    cases = [
        ("", 0),
        ("a", 1),
        ("abcabcbb", 3),
        ("bbbbb", 1),
        ("pwwkew", 3),
        ("dvdf", 3),
        ("åß∂å", 3),
    ]
    for text, expected in cases:
        assert longest_unique_substring(text) == expected


def test_matches_brute_force_on_seeded_cases():
    rng = random.Random(2028)
    alphabet = "abcdef"
    for _ in range(80):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 18)))
        assert longest_unique_substring(text) == brute_force(text)
