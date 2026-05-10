import json
from pathlib import Path

from evolver.engine import run_evolution, verify_run


def test_evolution_run_writes_reproducible_evidence_bundle(tmp_path: Path):
    run_dir = tmp_path / "levenshtein-run"

    summary = run_evolution("levenshtein", attempts=6, run_dir=run_dir, seed=11)

    assert summary["problem"] == "levenshtein"
    assert summary["attempts"] == 6
    assert summary["best_candidate_id"] != "baseline"
    assert summary["best_passed"]
    assert summary["speedup"] > 1.0
    assert (run_dir / "archive.sqlite").exists()
    assert (run_dir / "best_solution.py").exists()
    assert (run_dir / "environment.json").exists()
    assert (run_dir / "report.html").exists()
    assert (run_dir / "run_spec.json").exists()
    assert json.loads((run_dir / "summary.json").read_text())["best_candidate_id"]


def test_verify_run_reruns_winning_candidate(tmp_path: Path):
    run_dir = tmp_path / "verify-run"
    run_evolution("levenshtein", attempts=5, run_dir=run_dir, seed=17)

    verification = verify_run(run_dir)

    assert verification["verified"]
    assert verification["candidate_id"] == "winner-rerun"
    assert verification["mean_seconds"] > 0

