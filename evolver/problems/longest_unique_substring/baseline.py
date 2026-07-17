def longest_unique_substring(text):
    best = 0
    for start in range(len(text)):
        seen = []
        for end in range(start, len(text)):
            character = text[end]
            if character in seen:
                break
            seen.append(character)
            best = max(best, end - start + 1)
    return best
