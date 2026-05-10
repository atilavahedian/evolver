from pathlib import Path

from evolver.archive import Archive
from evolver.types import BenchmarkStats, CandidateRecord, EvaluationResult, ScanResult


def _record(candidate_id: str, parent_id: str, score: float) -> CandidateRecord:
    return CandidateRecord(
        candidate_id=candidate_id,
        parent_id=parent_id,
        generation=1,
        source="def levenshtein(a, b): return 0\n",
        strategy="unit-test",
        evaluation=EvaluationResult(
            candidate_id=candidate_id,
            passed=True,
            timed_out=False,
            test_command="python -m pytest",
            benchmark_command="python benchmark.py",
            test_stdout="passed",
            test_stderr="",
            benchmark_stdout='{"samples":[1.0,1.1,0.9]}',
            benchmark_stderr="",
            scan=ScanResult(safe=True, findings=[]),
            stats=BenchmarkStats(samples=[1.0, 1.1, 0.9]),
        ),
        score=score,
    )


def test_archive_persists_candidates_and_best_record(tmp_path: Path):
    archive = Archive.open(tmp_path / "archive.sqlite")

    archive.record_candidate(_record("c1", "baseline", 1.2))
    archive.record_candidate(_record("c2", "c1", 2.1))

    reopened = Archive.open(tmp_path / "archive.sqlite")
    best = reopened.best_candidate()

    assert best is not None
    assert best.candidate_id == "c2"
    assert best.parent_id == "c1"
    assert reopened.lineage("c2") == ["baseline", "c1", "c2"]

