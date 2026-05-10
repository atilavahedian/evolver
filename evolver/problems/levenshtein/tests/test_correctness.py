from solution import levenshtein


def test_known_distances():
    cases = [
        ("", "", 0),
        ("a", "", 1),
        ("", "abc", 3),
        ("kitten", "sitting", 3),
        ("saturday", "sunday", 3),
        ("gumbo", "gambol", 2),
        ("book", "back", 2),
    ]

    for left, right, expected in cases:
        assert levenshtein(left, right) == expected
        assert levenshtein(right, left) == expected


def test_distance_identity_and_length_bounds():
    words = ["research", "verification", "archive", "candidate"]

    for word in words:
        assert levenshtein(word, word) == 0
        assert levenshtein(word, "") == len(word)
        assert levenshtein("", word) == len(word)

