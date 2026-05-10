from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml


@dataclass(frozen=True)
class ProblemSpec:
    name: str
    entrypoint: str
    function: str
    baseline: str
    tests: str
    benchmark: str
    goal: str
    timeout_seconds: int
    benchmark_repeats: int
    seed: int
    problem_dir: Path

    @property
    def entrypoint_path(self) -> Path:
        return self.problem_dir / self.entrypoint

    @property
    def baseline_path(self) -> Path:
        return self.problem_dir / self.baseline

    @property
    def tests_path(self) -> Path:
        return self.problem_dir / self.tests

    @property
    def benchmark_path(self) -> Path:
        return self.problem_dir / self.benchmark


def package_problem_root() -> Path:
    return Path(__file__).resolve().parent / "problems"


def list_packaged_problems() -> List[str]:
    root = package_problem_root()
    if not root.exists():
        return []
    return sorted(
        path.name for path in root.iterdir() if path.is_dir() and (path / "problem.yaml").exists()
    )


def load_problem(reference: Union[str, Path]) -> ProblemSpec:
    problem_dir = _resolve_problem_dir(reference)
    raw = _load_yaml(problem_dir / "problem.yaml")
    spec = ProblemSpec(
        name=_require_string(raw, "name"),
        entrypoint=_require_string(raw, "entrypoint"),
        function=_require_string(raw, "function"),
        baseline=_require_string(raw, "baseline"),
        tests=_require_string(raw, "tests"),
        benchmark=_require_string(raw, "benchmark"),
        goal=_require_string(raw, "goal"),
        timeout_seconds=int(raw.get("timeout_seconds", 5)),
        benchmark_repeats=int(raw.get("benchmark_repeats", 5)),
        seed=int(raw.get("seed", 0)),
        problem_dir=problem_dir,
    )
    _validate_spec_paths(spec)
    if spec.goal != "minimize_latency":
        raise ValueError(f"unsupported goal {spec.goal!r}")
    if spec.benchmark_repeats < 1:
        raise ValueError("benchmark_repeats must be at least 1")
    return spec


def _resolve_problem_dir(reference: Union[str, Path]) -> Path:
    path = Path(reference)
    if path.exists():
        return path.resolve()
    packaged = package_problem_root() / str(reference)
    if packaged.exists():
        return packaged.resolve()
    raise FileNotFoundError(f"problem {reference!s} was not found")


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing problem spec {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"problem spec {path} must be a mapping")
    return data


def _require_string(raw: Dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"problem spec field {key!r} must be a nonempty string")
    return value


def _validate_spec_paths(spec: ProblemSpec) -> None:
    root = spec.problem_dir.resolve()
    for label, raw_path in {
        "entrypoint": spec.entrypoint,
        "baseline": spec.baseline,
        "tests": spec.tests,
        "benchmark": spec.benchmark,
    }.items():
        resolved = (spec.problem_dir / raw_path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"{label} must stay inside the problem directory") from exc
        if label != "entrypoint" and not resolved.exists():
            raise FileNotFoundError(f"{label} path does not exist: {resolved}")

