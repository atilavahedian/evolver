from __future__ import annotations

import random
from typing import List

from evolver.types import CandidateRecord


def select_parents(records: List[CandidateRecord], limit: int, seed: int) -> List[CandidateRecord]:
    passing = [record for record in records if record.evaluation.passed]
    ranked = sorted(passing, key=lambda record: record.score, reverse=True)
    if len(ranked) <= limit:
        return ranked
    rng = random.Random(seed)
    elite = ranked[: max(1, limit // 2)]
    remainder = ranked[max(1, limit // 2) :]
    rng.shuffle(remainder)
    return elite + remainder[: limit - len(elite)]

