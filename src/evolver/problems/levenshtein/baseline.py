def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    return min(
        levenshtein(a[1:], b) + 1,
        levenshtein(a, b[1:]) + 1,
        levenshtein(a[1:], b[1:]) + (a[0] != b[0]),
    )

