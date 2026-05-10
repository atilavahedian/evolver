from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, Optional, Union

from evolver.archive import Archive
from evolver.environment import write_environment
from evolver.generators import LibraryGenerator
from evolver.reports import write_report, write_summary
from evolver.runner import SandboxRunner
from evolver.scoring import score_evaluation, speedup_against
from evolver.spec import load_problem
from evolver.types import CandidateRecord


def run_evolution(
    problem_reference: Union[str, Path],
    attempts: int,
    run_dir: Union[str, Path],
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    problem = load_problem(problem_reference)
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    output_dir = Path(run_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    archive = Archive.open(output_dir / "archive.sqlite")
    runner = SandboxRunner(problem, output_dir)
    baseline_source = problem.baseline_path.read_text(encoding="utf-8")
    baseline_eval = runner.evaluate("baseline", baseline_source)
    if not baseline_eval.passed or baseline_eval.stats is None:
        raise RuntimeError(f"baseline failed verification: {baseline_eval.test_stderr}")

    baseline_record = CandidateRecord(
        candidate_id="baseline",
        parent_id="",
        generation=0,
        source=baseline_source,
        strategy="baseline",
        evaluation=baseline_eval,
        score=1.0,
    )
    archive.record_candidate(baseline_record)

    generator = LibraryGenerator()
    best_so_far = baseline_record
    for draft in generator.generate(problem, attempts):
        draft = replace(draft, parent_id=best_so_far.candidate_id)
        evaluation = runner.evaluate(draft.candidate_id, draft.source)
        score = score_evaluation(baseline_eval.stats, evaluation, draft.source)
        record = CandidateRecord(
            candidate_id=draft.candidate_id,
            parent_id=draft.parent_id,
            generation=draft.generation,
            source=draft.source,
            strategy=draft.strategy,
            evaluation=evaluation,
            score=score,
        )
        archive.record_candidate(record)
        if record.evaluation.passed and record.score > best_so_far.score:
            best_so_far = record

    best = archive.best_candidate()
    if best is None or best.evaluation.stats is None:
        raise RuntimeError("no passing candidate was found")

    speedup = speedup_against(baseline_eval.stats, best.evaluation.stats)
    lineage = archive.lineage(best.candidate_id)
    summary: Dict[str, Any] = {
        "problem": problem.name,
        "attempts": attempts,
        "seed": problem.seed if seed is None else seed,
        "baseline_candidate_id": "baseline",
        "baseline_mean_seconds": baseline_eval.stats.mean_seconds,
        "best_candidate_id": best.candidate_id,
        "best_strategy": best.strategy,
        "best_passed": best.evaluation.passed,
        "best_score": best.score,
        "best_mean_seconds": best.evaluation.stats.mean_seconds,
        "speedup": speedup,
        "lineage": lineage,
    }

    (output_dir / "best_solution.py").write_text(best.source, encoding="utf-8")
    (output_dir / "run_spec.json").write_text(
        json.dumps(
            {
                "problem": problem.name,
                "attempts": attempts,
                "seed": summary["seed"],
                "entrypoint": problem.entrypoint,
                "function": problem.function,
                "goal": problem.goal,
                "timeout_seconds": problem.timeout_seconds,
                "benchmark_repeats": problem.benchmark_repeats,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_environment(output_dir / "environment.json")
    write_summary(output_dir, summary)
    write_report(output_dir, archive, summary)
    return summary


def verify_run(run_dir: Union[str, Path]) -> Dict[str, Any]:
    output_dir = Path(run_dir)
    run_spec = json.loads((output_dir / "run_spec.json").read_text(encoding="utf-8"))
    problem = load_problem(run_spec["problem"])
    source = (output_dir / "best_solution.py").read_text(encoding="utf-8")
    runner = SandboxRunner(problem, output_dir / "verification")
    result = runner.evaluate("winner-rerun", source)
    response = {
        "verified": result.passed and result.stats is not None,
        "candidate_id": result.candidate_id,
        "mean_seconds": result.stats.mean_seconds if result.stats is not None else 0.0,
        "test_command": result.test_command,
        "benchmark_command": result.benchmark_command,
    }
    (output_dir / "verification.json").write_text(
        json.dumps(response, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return response
