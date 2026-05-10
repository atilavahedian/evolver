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
def inspect(run_dir: Path = typer.Argument(..., help="Existing evidence bundle directory.")) -> None:
    """Inspect the best candidate and lineage from a run."""
    summary = load_summary(run_dir)
    _print_summary(summary, run_dir)


@app.command()
def report(run_dir: Path = typer.Argument(..., help="Existing evidence bundle directory.")) -> None:
    """Regenerate the HTML report from the SQLite archive and summary."""
    path = regenerate_report(run_dir)
    console.print(f"report: {path}")


@app.command()
def verify(run_dir: Path = typer.Argument(..., help="Existing evidence bundle directory.")) -> None:
    """Rerun the winning candidate against the original test and benchmark gates."""
    result = verify_run(run_dir)
    console.print(json.dumps(result, indent=2, sort_keys=True))


def _print_summary(summary: dict, run_dir: Path) -> None:
    table = Table(title="Evolver Run Summary")
    table.add_column("field")
    table.add_column("value")
    table.add_row("run_dir", str(run_dir))
    table.add_row("problem", str(summary["problem"]))
    table.add_row("attempts", str(summary["attempts"]))
    table.add_row("best_candidate", str(summary["best_candidate_id"]))
    table.add_row("best_strategy", str(summary["best_strategy"]))
    table.add_row("speedup", f"{summary['speedup']:.4f}x")
    table.add_row("lineage", " -> ".join(summary["lineage"]))
    console.print(table)


if __name__ == "__main__":
    app()

