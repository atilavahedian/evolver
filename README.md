# Evolver

Evolver is a closed loop program search system for improving code under real verification. It treats every candidate as untrusted until it passes a static scan, correctness tests, repeated benchmarks, lineage recording, and a winner rerun.

The project is meant to be read as a research system. It stores the evidence that decides whether a program improved, not just the final source file.

## What It Does

Evolver takes a problem directory with a baseline implementation, tests, and a benchmark. It generates candidate implementations, runs them in isolated workspaces, rejects unsafe code, scores only candidates that pass correctness, archives the full lineage in SQLite, then writes a reproducible evidence bundle.

```text
problem spec
  candidate generator
  static safety scan
  sandboxed tests
  repeated benchmarks
  scoring and selection
  SQLite lineage archive
  evidence report
```

## Quick Start

```bash
uv sync --extra dev
uv run evolver list-problems
uv run evolver run levenshtein --attempts 8 --run-dir runs/levenshtein-demo
uv run evolver inspect runs/levenshtein-demo
uv run evolver verify runs/levenshtein-demo
```

The packaged Levenshtein benchmark starts with a correct but slow recursive baseline. The deterministic generator proposes algorithmic variants, and the engine only accepts an improvement when tests pass and timing evidence is recorded.

## Evidence Bundle

A run directory contains:

```text
archive.sqlite
best_solution.py
environment.json
report.html
run_spec.json
summary.json
```

The SQLite archive records candidate source, parent identifiers, static scan findings, test output, benchmark samples, score, and timing summaries.

## Technical Focus

Evolver is built around four constraints:

1. Generated code is untrusted.
2. Correctness is a gate, not part of a weighted score.
3. Performance claims require repeated measurements.
4. Every accepted result must have enough evidence to rerun or audit.

## Commands

```bash
evolver run <problem>
evolver inspect <run-dir>
evolver report <run-dir>
evolver verify <run-dir>
evolver list-problems
```

## Repository Layout

```text
src/evolver/              core package
src/evolver/problems/     packaged research problems
tests/                    behavioral and end to end tests
docs/                     design, architecture, and evidence notes
```

## License

MIT

