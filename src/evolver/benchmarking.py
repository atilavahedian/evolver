from __future__ import annotations

import json
from typing import Any, Dict

from evolver.types import BenchmarkStats


def parse_benchmark_output(stdout: str) -> BenchmarkStats:
    payload = _last_json_object(stdout)
    samples = payload.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("benchmark output must contain a nonempty samples list")
    parsed = [float(sample) for sample in samples]
    if any(sample <= 0 for sample in parsed):
        raise ValueError("benchmark samples must be positive")
    return BenchmarkStats(samples=parsed)


def stats_to_json(stats: BenchmarkStats) -> Dict[str, Any]:
    return {
        "samples": stats.samples,
        "mean_seconds": stats.mean_seconds,
        "min_seconds": stats.min_seconds,
        "max_seconds": stats.max_seconds,
        "stdev_seconds": stats.stdev_seconds,
        "relative_stability": stats.relative_stability,
    }


def _last_json_object(stdout: str) -> Dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        if not isinstance(data, dict):
            raise ValueError("benchmark JSON payload must be an object")
        return data
    raise ValueError("benchmark command produced no JSON output")

