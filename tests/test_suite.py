import csv
import json
from pathlib import Path

from evolver.suite import run_suite


def test_suite_runs_equal_budgets_and_writes_aggregate_evidence(tmp_path: Path):
    suite_dir = tmp_path / "suite"

    summary = run_suite(
        ["levenshtein", "two_sum", "longest_unique_substring"],
        attempts_per_problem=3,
        suite_dir=suite_dir,
        seed=41,
    )

    assert summary["protocol"] == "budget-normalized-local-suite-v1"
    assert summary["problem_count"] == 3
    assert summary["total_attempts_requested"] == 9
    assert summary["total_attempts_evaluated"] == 9
    assert summary["problems_improved"] == 3
    assert summary["all_winners_verified"]
    assert summary["geometric_mean_speedup"] > 1.0
    assert json.loads((suite_dir / "suite_summary.json").read_text())["problem_count"] == 3
    with (suite_dir / "suite_results.csv").open(newline="") as handle:
        assert len(list(csv.DictReader(handle))) == 3
    for problem in ["levenshtein", "two_sum", "longest_unique_substring"]:
        assert (suite_dir / "runs" / problem / "verification.json").exists()
