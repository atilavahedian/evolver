from pathlib import Path

from evolver.runner import SandboxRunner
from evolver.spec import load_problem


FAST_LEVENSHTEIN = """
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
"""


def test_runner_executes_candidate_tests_and_benchmark(tmp_path: Path):
    problem = load_problem("levenshtein")
    runner = SandboxRunner(problem, tmp_path)

    result = runner.evaluate("candidate-fast", FAST_LEVENSHTEIN)

    assert result.passed
    assert not result.timed_out
    assert result.scan.safe
    assert result.stats is not None
    assert len(result.stats.samples) == problem.benchmark_repeats
    assert result.stats.mean_seconds > 0


def test_runner_rejects_unsafe_candidate_without_execution(tmp_path: Path):
    problem = load_problem("levenshtein")
    runner = SandboxRunner(problem, tmp_path)

    result = runner.evaluate("candidate-unsafe", "import os\ndef levenshtein(a, b): return 0\n")

    assert not result.passed
    assert not result.scan.safe
    assert result.stats is None
    assert result.test_stdout == ""

