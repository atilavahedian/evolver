from pathlib import Path

from evolver.spec import list_packaged_problems, load_problem


def test_loads_packaged_problem_with_resolved_paths():
    spec = load_problem("levenshtein")

    assert spec.name == "levenshtein"
    assert spec.entrypoint == "solution.py"
    assert spec.function == "levenshtein"
    assert spec.goal == "minimize_latency"
    assert spec.timeout_seconds > 0
    assert spec.benchmark_repeats >= 3
    assert spec.problem_dir.exists()
    assert spec.baseline_path.name == "baseline.py"
    assert spec.tests_path.name == "test_correctness.py"
    assert spec.benchmark_path.name == "benchmark.py"


def test_lists_packaged_problems():
    assert "levenshtein" in list_packaged_problems()


def test_rejects_problem_specs_that_point_outside_problem_dir(tmp_path: Path):
    problem_dir = tmp_path / "bad_problem"
    problem_dir.mkdir()
    (problem_dir / "problem.yaml").write_text(
        "\n".join(
            [
                "name: bad_problem",
                "entrypoint: ../escape.py",
                "function: f",
                "baseline: baseline.py",
                "tests: tests/test_correctness.py",
                "benchmark: benchmark.py",
                "goal: minimize_latency",
                "timeout_seconds: 2",
                "benchmark_repeats: 3",
                "seed: 7",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_problem(problem_dir)
    except ValueError as exc:
        assert "inside the problem directory" in str(exc)
    else:
        raise AssertionError("unsafe spec path was accepted")

