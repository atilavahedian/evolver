from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from evolver.spec import ProblemSpec
from evolver.types import CandidateDraft


class CandidateGenerator(Protocol):
    def generate(self, problem: ProblemSpec, attempts: int) -> List[CandidateDraft]: ...


@dataclass(frozen=True)
class LibraryGenerator:
    """Deterministic program generator for reproducible local research runs."""

    name: str = "packaged-library"

    def generate(self, problem: ProblemSpec, attempts: int) -> List[CandidateDraft]:
        libraries = {
            "levenshtein": _levenshtein_library,
            "longest_unique_substring": _longest_unique_substring_library,
            "two_sum": _two_sum_library,
        }
        library_factory = libraries.get(problem.name)
        if library_factory is None:
            raise ValueError(f"no packaged generator for {problem.name}")
        library = library_factory()
        drafts = []
        parent = "baseline"
        for index, (strategy, source) in enumerate(library[:attempts], start=1):
            candidate_id = f"candidate-{index:03d}"
            drafts.append(
                CandidateDraft(
                    candidate_id=candidate_id,
                    parent_id=parent,
                    generation=index,
                    source=source,
                    strategy=strategy,
                )
            )
            parent = candidate_id
        return drafts


def _levenshtein_library() -> List[tuple[str, str]]:
    return [
        (
            "memoized recursion",
            """
def levenshtein(a, b):
    cache = {}

    def distance(i, j):
        key = (i, j)
        if key in cache:
            return cache[key]
        if i == len(a):
            value = len(b) - j
        elif j == len(b):
            value = len(a) - i
        else:
            value = min(
                distance(i + 1, j) + 1,
                distance(i, j + 1) + 1,
                distance(i + 1, j + 1) + (a[i] != b[j]),
            )
        cache[key] = value
        return value

    return distance(0, 0)
""".strip()
            + "\n",
        ),
        (
            "matrix dynamic programming",
            """
def levenshtein(a, b):
    rows = len(a) + 1
    cols = len(b) + 1
    table = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        table[i][0] = i
    for j in range(cols):
        table[0][j] = j
    for i in range(1, rows):
        ca = a[i - 1]
        for j in range(1, cols):
            cb = b[j - 1]
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + (ca != cb),
            )
    return table[-1][-1]
""".strip()
            + "\n",
        ),
        (
            "row dynamic programming",
            """
def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (ca != cb)
            current.append(min(insert, delete, replace))
        previous = current
    return previous[-1]
""".strip()
            + "\n",
        ),
        (
            "shorter row dynamic programming",
            """
def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]
""".strip()
            + "\n",
        ),
        (
            "trimmed row dynamic programming",
            """
def levenshtein(a, b):
    if a == b:
        return 0
    prefix = 0
    limit = min(len(a), len(b))
    while prefix < limit and a[prefix] == b[prefix]:
        prefix += 1
    if prefix:
        a = a[prefix:]
        b = b[prefix:]
    suffix = 0
    limit = min(len(a), len(b))
    while suffix < limit and a[-suffix - 1] == b[-suffix - 1]:
        suffix += 1
    if suffix:
        a = a[:-suffix]
        b = b[:-suffix]
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]
""".strip()
            + "\n",
        ),
        (
            "bounded row dynamic programming",
            """
def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        left = i
        for j, cb in enumerate(b, 1):
            insert = left + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (ca != cb)
            left = min(insert, delete, replace)
            current.append(left)
        previous = current
    return previous[-1]
""".strip()
            + "\n",
        ),
    ]


def _two_sum_library() -> List[tuple[str, str]]:
    return [
        (
            "sorted two-pointer scan",
            """
def has_pair_sum(values, target):
    ordered = sorted(values)
    left = 0
    right = len(ordered) - 1
    while left < right:
        total = ordered[left] + ordered[right]
        if total == target:
            return True
        if total < target:
            left += 1
        else:
            right -= 1
    return False
""".strip()
            + "\n",
        ),
        (
            "incremental seen list",
            """
def has_pair_sum(values, target):
    seen = []
    for value in values:
        if target - value in seen:
            return True
        seen.append(value)
    return False
""".strip()
            + "\n",
        ),
        (
            "incremental hash set",
            """
def has_pair_sum(values, target):
    seen = set()
    for value in values:
        if target - value in seen:
            return True
        seen.add(value)
    return False
""".strip()
            + "\n",
        ),
        (
            "remaining complement set",
            """
def has_pair_sum(values, target):
    needed = set()
    for value in values:
        if value in needed:
            return True
        needed.add(target - value)
    return False
""".strip()
            + "\n",
        ),
        (
            "frequency map",
            """
def has_pair_sum(values, target):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    for value, count in counts.items():
        complement = target - value
        if complement != value and complement in counts:
            return True
        if complement == value and count > 1:
            return True
    return False
""".strip()
            + "\n",
        ),
        (
            "indexed complement lookup",
            """
def has_pair_sum(values, target):
    first_index = {}
    for index, value in enumerate(values):
        complement = target - value
        if complement in first_index and first_index[complement] != index:
            return True
        if value not in first_index:
            first_index[value] = index
    return False
""".strip()
            + "\n",
        ),
    ]


def _longest_unique_substring_library() -> List[tuple[str, str]]:
    return [
        (
            "restart on duplicate",
            """
def longest_unique_substring(text):
    best = 0
    for start in range(len(text)):
        seen = set()
        for end in range(start, len(text)):
            character = text[end]
            if character in seen:
                break
            seen.add(character)
            best = max(best, end - start + 1)
    return best
""".strip()
            + "\n",
        ),
        (
            "moving substring window",
            """
def longest_unique_substring(text):
    window = ""
    best = 0
    for character in text:
        duplicate = window.find(character)
        if duplicate >= 0:
            window = window[duplicate + 1:]
        window += character
        best = max(best, len(window))
    return best
""".strip()
            + "\n",
        ),
        (
            "last-seen index map",
            """
def longest_unique_substring(text):
    last_seen = {}
    window_start = 0
    best = 0
    for index, character in enumerate(text):
        previous = last_seen.get(character, -1)
        if previous >= window_start:
            window_start = previous + 1
        last_seen[character] = index
        best = max(best, index - window_start + 1)
    return best
""".strip()
            + "\n",
        ),
        (
            "sliding hash-set window",
            """
def longest_unique_substring(text):
    seen = set()
    left = 0
    best = 0
    for right, character in enumerate(text):
        while character in seen:
            seen.remove(text[left])
            left += 1
        seen.add(character)
        best = max(best, right - left + 1)
    return best
""".strip()
            + "\n",
        ),
        (
            "bounded last-seen map",
            """
def longest_unique_substring(text):
    last_seen = {}
    left = 0
    best = 0
    for right in range(len(text)):
        character = text[right]
        if character in last_seen:
            left = max(left, last_seen[character] + 1)
        last_seen[character] = right
        length = right - left + 1
        if length > best:
            best = length
    return best
""".strip()
            + "\n",
        ),
        (
            "one-based last-seen map",
            """
def longest_unique_substring(text):
    next_start = {}
    start = 0
    best = 0
    for index, character in enumerate(text):
        start = max(start, next_start.get(character, 0))
        best = max(best, index - start + 1)
        next_start[character] = index + 1
    return best
""".strip()
            + "\n",
        ),
    ]
