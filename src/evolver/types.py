from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import List, Optional


@dataclass(frozen=True)
class ScanResult:
    safe: bool
    findings: List[str]


@dataclass(frozen=True)
class BenchmarkStats:
    samples: List[float]

    @property
    def mean_seconds(self) -> float:
        return mean(self.samples)

    @property
    def min_seconds(self) -> float:
        return min(self.samples)

    @property
    def max_seconds(self) -> float:
        return max(self.samples)

    @property
    def stdev_seconds(self) -> float:
        if len(self.samples) < 2:
            return 0.0
        return pstdev(self.samples)

    @property
    def relative_stability(self) -> float:
        if self.mean_seconds == 0:
            return 0.0
        return self.stdev_seconds / self.mean_seconds


@dataclass(frozen=True)
class EvaluationResult:
    candidate_id: str
    passed: bool
    timed_out: bool
    test_command: str
    benchmark_command: str
    test_stdout: str
    test_stderr: str
    benchmark_stdout: str
    benchmark_stderr: str
    scan: ScanResult
    stats: Optional[BenchmarkStats]


@dataclass(frozen=True)
class CandidateDraft:
    candidate_id: str
    parent_id: str
    generation: int
    source: str
    strategy: str


@dataclass(frozen=True)
class CandidateRecord:
    candidate_id: str
    parent_id: str
    generation: int
    source: str
    strategy: str
    evaluation: EvaluationResult
    score: float

