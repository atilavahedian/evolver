import json
from pathlib import Path

from evolver.engine import run_evolution, verify_run
from evolver.types import CandidateDraft


class SingleCandidateGenerator:
    name = "test-generator"

    def generate(self, problem, attempts):
        source = problem.baseline_path.read_text(encoding="utf-8")
        return [
            CandidateDraft(
                candidate_id="external-001",
                parent_id="baseline",
                generation=1,
                source=source,
                strategy="external candidate",
            )
        ]


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


def test_evolution_runs_across_packaged_problem_families(tmp_path: Path):
    for problem in ["two_sum", "longest_unique_substring"]:
        summary = run_evolution(problem, attempts=6, run_dir=tmp_path / problem, seed=31)

        assert summary["problem"] == problem
        assert summary["best_passed"]
        assert summary["best_candidate_id"] != "baseline"
        assert summary["speedup"] > 1.0


def test_run_reports_actual_budget_and_accepts_injected_generator(tmp_path: Path):
    summary = run_evolution(
        "levenshtein",
        attempts=9,
        run_dir=tmp_path / "injected",
        seed=37,
        generator=SingleCandidateGenerator(),
    )

    assert summary["attempts_requested"] == 9
    assert summary["attempts_evaluated"] == 1
    assert summary["passing_candidates"] == 1
    assert summary["candidate_pass_rate"] == 1.0
    assert summary["generator"] == "test-generator"
    run_spec = json.loads((tmp_path / "injected" / "run_spec.json").read_text())
    assert run_spec["generator"] == "test-generator"
