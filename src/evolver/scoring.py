from __future__ import annotations

from evolver.types import BenchmarkStats, EvaluationResult


def score_evaluation(baseline: BenchmarkStats, evaluation: EvaluationResult, source: str) -> float:
    if not evaluation.passed or evaluation.stats is None:
        return 0.0
    speedup = baseline.mean_seconds / evaluation.stats.mean_seconds
    stability_penalty = min(evaluation.stats.relative_stability, 1.0) * 0.05
    complexity_penalty = min(len(source) / 20_000, 0.05)
    return max(speedup - stability_penalty - complexity_penalty, 0.0)


def speedup_against(baseline: BenchmarkStats, candidate: BenchmarkStats) -> float:
    return baseline.mean_seconds / candidate.mean_seconds

