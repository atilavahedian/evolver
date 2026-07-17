from pathlib import Path

from typer.testing import CliRunner

from evolver.cli import app


def test_cli_lists_packaged_problems():
    runner = CliRunner()

    result = runner.invoke(app, ["list-problems"])

    assert result.exit_code == 0
    assert "levenshtein" in result.stdout
    assert "longest_unique_substring" in result.stdout
    assert "two_sum" in result.stdout


def test_cli_run_inspect_and_verify(tmp_path: Path):
    runner = CliRunner()
    run_dir = tmp_path / "cli-run"

    run_result = runner.invoke(
        app,
        ["run", "levenshtein", "--attempts", "5", "--run-dir", str(run_dir), "--seed", "19"],
    )
    inspect_result = runner.invoke(app, ["inspect", str(run_dir)])
    verify_result = runner.invoke(app, ["verify", str(run_dir)])

    assert run_result.exit_code == 0, run_result.stdout
    assert inspect_result.exit_code == 0, inspect_result.stdout
    assert verify_result.exit_code == 0, verify_result.stdout
    assert "speedup" in inspect_result.stdout.lower()
    assert "verified" in verify_result.stdout.lower()


def test_cli_runs_budget_normalized_suite(tmp_path: Path):
    runner = CliRunner()
    suite_dir = tmp_path / "cli-suite"

    result = runner.invoke(
        app,
        [
            "suite",
            "--problems",
            "two_sum,longest_unique_substring",
            "--attempts",
            "3",
            "--suite-dir",
            str(suite_dir),
            "--seed",
            "43",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "geometric mean speedup" in result.stdout.lower()
    assert (suite_dir / "suite_summary.json").exists()
