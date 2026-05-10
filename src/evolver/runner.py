from __future__ import annotations

import os
import resource
import shutil
import subprocess
import sys
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from evolver.benchmarking import parse_benchmark_output
from evolver.scanner import scan_source
from evolver.spec import ProblemSpec
from evolver.types import EvaluationResult


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool


class SandboxRunner:
    def __init__(self, problem: ProblemSpec, run_root: Path):
        self.problem = problem
        self.run_root = Path(run_root)
        self.run_root.mkdir(parents=True, exist_ok=True)

    def evaluate(self, candidate_id: str, source: str) -> EvaluationResult:
        scan = scan_source(source)
        test_command = _format_command(self._test_command())
        benchmark_command = _format_command(self._benchmark_command())

        if not scan.safe:
            return EvaluationResult(
                candidate_id=candidate_id,
                passed=False,
                timed_out=False,
                test_command=test_command,
                benchmark_command=benchmark_command,
                test_stdout="",
                test_stderr="",
                benchmark_stdout="",
                benchmark_stderr="",
                scan=scan,
                stats=None,
            )

        candidate_dir = self._prepare_candidate_dir(candidate_id, source)
        test_result = self._run(self._test_command(), candidate_dir, self.problem.timeout_seconds)
        if test_result.returncode != 0 or test_result.timed_out:
            return EvaluationResult(
                candidate_id=candidate_id,
                passed=False,
                timed_out=test_result.timed_out,
                test_command=test_command,
                benchmark_command=benchmark_command,
                test_stdout=test_result.stdout,
                test_stderr=test_result.stderr,
                benchmark_stdout="",
                benchmark_stderr="",
                scan=scan,
                stats=None,
            )

        benchmark_result = self._run(
            self._benchmark_command(), candidate_dir, self.problem.timeout_seconds
        )
        stats = None
        passed = benchmark_result.returncode == 0 and not benchmark_result.timed_out
        if passed:
            try:
                stats = parse_benchmark_output(benchmark_result.stdout)
            except ValueError as exc:
                passed = False
                benchmark_result = CommandResult(
                    stdout=benchmark_result.stdout,
                    stderr=f"{benchmark_result.stderr}\n{exc}".strip(),
                    returncode=1,
                    timed_out=False,
                )

        return EvaluationResult(
            candidate_id=candidate_id,
            passed=passed,
            timed_out=test_result.timed_out or benchmark_result.timed_out,
            test_command=test_command,
            benchmark_command=benchmark_command,
            test_stdout=test_result.stdout,
            test_stderr=test_result.stderr,
            benchmark_stdout=benchmark_result.stdout,
            benchmark_stderr=benchmark_result.stderr,
            scan=scan,
            stats=stats,
        )

    def _prepare_candidate_dir(self, candidate_id: str, source: str) -> Path:
        safe_name = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in candidate_id)
        candidate_dir = self.run_root / "workspaces" / safe_name
        if candidate_dir.exists():
            shutil.rmtree(candidate_dir)
        shutil.copytree(self.problem.problem_dir, candidate_dir)
        (candidate_dir / self.problem.entrypoint).write_text(source, encoding="utf-8")
        return candidate_dir

    def _test_command(self) -> List[str]:
        return [sys.executable, "-m", "pytest", self.problem.tests, "-q"]

    def _benchmark_command(self) -> List[str]:
        return [
            sys.executable,
            self.problem.benchmark,
            "--repeats",
            str(self.problem.benchmark_repeats),
        ]

    def _run(self, command: List[str], cwd: Path, timeout_seconds: int) -> CommandResult:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                env=self._child_env(cwd),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                preexec_fn=_resource_limiter(timeout_seconds),
                check=False,
            )
            return CommandResult(
                stdout=completed.stdout,
                stderr=completed.stderr,
                returncode=completed.returncode,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
                returncode=124,
                timed_out=True,
            )

    def _child_env(self, cwd: Path) -> Dict[str, str]:
        env = os.environ.copy()
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(cwd) if not existing else f"{cwd}{os.pathsep}{existing}"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env


def _format_command(command: List[str]) -> str:
    return " ".join(command)


def _resource_limiter(timeout_seconds: int):
    def limit() -> None:
        with suppress(OSError, ValueError):
            resource.setrlimit(resource.RLIMIT_CPU, (timeout_seconds + 1, timeout_seconds + 2))

    if os.name == "posix":
        return limit
    return None
