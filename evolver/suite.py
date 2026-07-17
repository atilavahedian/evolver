from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path
from typing import Any, Dict, Sequence, Union

from evolver.engine import run_evolution, verify_run
from evolver.spec import load_problem


def run_suite(
    problem_references: Sequence[Union[str, Path]],
    attempts_per_problem: int,
    suite_dir: Union[str, Path],
    seed: int = 13,
) -> Dict[str, Any]:
    if not problem_references:
        raise ValueError("a suite must contain at least one problem")
    if attempts_per_problem < 1:
        raise ValueError("attempts_per_problem must be at least 1")

    output_dir = Path(suite_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    results = []
    for index, reference in enumerate(problem_references):
        problem = load_problem(reference)
        problem_seed = seed + index
        problem_dir = output_dir / "runs" / problem.name
        run = run_evolution(
            reference,
            attempts=attempts_per_problem,
            run_dir=problem_dir,
            seed=problem_seed,
        )
        verification = verify_run(problem_dir)
        results.append(
            {
                "problem": problem.name,
                "seed": problem_seed,
                "attempts_requested": run["attempts_requested"],
                "attempts_evaluated": run["attempts_evaluated"],
                "passing_candidates": run["passing_candidates"],
                "candidate_pass_rate": run["candidate_pass_rate"],
                "best_candidate_id": run["best_candidate_id"],
                "best_strategy": run["best_strategy"],
                "baseline_mean_seconds": run["baseline_mean_seconds"],
                "best_mean_seconds": run["best_mean_seconds"],
                "speedup": run["speedup"],
                "improved": run["speedup"] > 1.0,
                "verified": verification["verified"],
                "run_dir": str(Path("runs") / problem.name),
            }
        )

    speedups = [float(result["speedup"]) for result in results]
    evaluated = sum(int(result["attempts_evaluated"]) for result in results)
    passing = sum(int(result["passing_candidates"]) for result in results)
    summary: Dict[str, Any] = {
        "protocol": "budget-normalized-local-suite-v1",
        "seed": seed,
        "problem_count": len(results),
        "attempts_per_problem": attempts_per_problem,
        "total_attempts_requested": attempts_per_problem * len(results),
        "total_attempts_evaluated": evaluated,
        "total_passing_candidates": passing,
        "candidate_pass_rate": passing / evaluated if evaluated else 0.0,
        "problems_improved": sum(int(result["improved"]) for result in results),
        "improvement_rate": sum(int(result["improved"]) for result in results) / len(results),
        "all_winners_verified": all(bool(result["verified"]) for result in results),
        "geometric_mean_speedup": math.exp(
            sum(math.log(max(speedup, 1e-12)) for speedup in speedups) / len(speedups)
        ),
        "results": results,
    }
    (output_dir / "suite_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_results_csv(output_dir / "suite_results.csv", results)
    return summary


def _write_results_csv(path: Path, results: Sequence[Dict[str, Any]]) -> None:
    fieldnames = [
        "problem",
        "seed",
        "attempts_requested",
        "attempts_evaluated",
        "passing_candidates",
        "candidate_pass_rate",
        "best_candidate_id",
        "best_strategy",
        "baseline_mean_seconds",
        "best_mean_seconds",
        "speedup",
        "improved",
        "verified",
        "run_dir",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
