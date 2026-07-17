from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from evolver.engine import run_evolution, verify_run
from evolver.reports import load_summary, regenerate_report
from evolver.spec import list_packaged_problems
from evolver.suite import run_suite

app = typer.Typer(no_args_is_help=True, help="Closed loop program search with verification.")
console = Console()


@app.command("list-problems")
def list_problems() -> None:
    """List packaged research problems."""
    for problem in list_packaged_problems():
        console.print(problem)


@app.command()
def run(
    problem: str = typer.Argument(..., help="Packaged problem name or path."),
    attempts: int = typer.Option(8, min=1, help="Number of candidates to evaluate."),
    run_dir: Optional[Path] = typer.Option(None, help="Directory for the evidence bundle."),
    seed: int = typer.Option(13, help="Deterministic search seed."),
) -> None:
    """Run the full candidate generation, verification, scoring, and reporting loop."""
    if run_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        run_dir = Path("runs") / f"{problem}-{stamp}"
    summary = run_evolution(problem, attempts=attempts, run_dir=run_dir, seed=seed)
    _print_summary(summary, run_dir)


@app.command()
def suite(
    problems: Optional[str] = typer.Option(
        None,
        help="Comma-separated packaged problems; defaults to every packaged problem.",
    ),
    attempts: int = typer.Option(6, min=1, help="Candidate budget for each problem."),
    suite_dir: Path = typer.Option(
        Path("runs/benchmark-suite"), help="Directory for suite evidence."
    ),
    seed: int = typer.Option(13, help="Base deterministic suite seed."),
) -> None:
    """Run a budget-normalized benchmark across multiple problems."""
    selected = list_packaged_problems()
    if problems:
        selected = [problem.strip() for problem in problems.split(",") if problem.strip()]
    summary = run_suite(
        selected,
        attempts_per_problem=attempts,
        suite_dir=suite_dir,
        seed=seed,
    )
    table = Table(title="Evolver Benchmark Suite")
    table.add_column("problem")
    table.add_column("evaluated")
    table.add_column("passing")
    table.add_column("speedup")
    table.add_column("verified")
    for result in summary["results"]:
        table.add_row(
            str(result["problem"]),
            str(result["attempts_evaluated"]),
            str(result["passing_candidates"]),
            f"{result['speedup']:.4f}x",
            str(result["verified"]),
        )
    console.print(table)
    console.print(f"geometric mean speedup: {summary['geometric_mean_speedup']:.4f}x")
    console.print(f"suite evidence: {suite_dir}")


@app.command()
def inspect(
    run_dir: Path = typer.Argument(..., help="Existing evidence bundle directory."),
) -> None:
    """Inspect the best candidate and lineage from a run."""
    summary = load_summary(run_dir)
    _print_summary(summary, run_dir)


@app.command()
def report(
    run_dir: Path = typer.Argument(..., help="Existing evidence bundle directory."),
) -> None:
    """Regenerate the HTML report from the SQLite archive and summary."""
    path = regenerate_report(run_dir)
    console.print(f"report: {path}")


@app.command()
def verify(
    run_dir: Path = typer.Argument(..., help="Existing evidence bundle directory."),
) -> None:
    """Rerun the winning candidate against the original test and benchmark gates."""
    result = verify_run(run_dir)
    console.print(json.dumps(result, indent=2, sort_keys=True))


def _print_summary(summary: dict, run_dir: Path) -> None:
    table = Table(title="Evolver Run Summary")
    table.add_column("field")
    table.add_column("value")
    table.add_row("run_dir", str(run_dir))
    table.add_row("problem", str(summary["problem"]))
    table.add_row(
        "candidate budget",
        f"{summary.get('attempts_evaluated', summary['attempts'])} / "
        f"{summary.get('attempts_requested', summary['attempts'])}",
    )
    table.add_row("passing candidates", str(summary.get("passing_candidates", "unknown")))
    table.add_row("best_candidate", str(summary["best_candidate_id"]))
    table.add_row("best_strategy", str(summary["best_strategy"]))
    table.add_row("speedup", f"{summary['speedup']:.4f}x")
    table.add_row("lineage", " -> ".join(summary["lineage"]))
    console.print(table)


if __name__ == "__main__":
    app()
