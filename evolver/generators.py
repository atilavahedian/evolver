from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from evolver.spec import ProblemSpec
from evolver.types import CandidateDraft


class CandidateGenerator(Protocol):
    def generate(self, problem: ProblemSpec, attempts: int) -> List[CandidateDraft]:
        ...


@dataclass(frozen=True)
class LibraryGenerator:
    """Deterministic program generator for reproducible local research runs."""

    def generate(self, problem: ProblemSpec, attempts: int) -> List[CandidateDraft]:
        if problem.name != "levenshtein":
            raise ValueError(f"no packaged generator for {problem.name}")
        library = _levenshtein_library()
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

