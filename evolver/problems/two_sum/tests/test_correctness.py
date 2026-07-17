import random

from solution import has_pair_sum


def brute_force(values, target):
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            if values[left] + values[right] == target:
                return True
    return False


def test_known_cases():
    cases = [
        ([], 4, False),
        ([2], 4, False),
        ([2, 2], 4, True),
        ([2, 7, 11, 15], 9, True),
        ([3, 1, 8], 20, False),
        ([-5, 2, 7, 9], 4, True),
    ]
    for values, target, expected in cases:
        assert has_pair_sum(values, target) is expected


def test_matches_brute_force_on_seeded_cases():
    rng = random.Random(2027)
    for _ in range(80):
        values = [rng.randint(-30, 30) for _ in range(rng.randint(0, 24))]
        target = rng.randint(-50, 50)
        assert has_pair_sum(values, target) is brute_force(values, target)
