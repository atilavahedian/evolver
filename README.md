# Evolver

Evolver is a closed-loop program search system for improving code under executable verification. It treats every candidate as untrusted until it passes a static scan, correctness tests, repeated benchmarks, lineage recording, and a winner rerun.

The project is meant to be read as a research system. It stores the evidence that decides whether a program improved, not just the final source file.

## What It Does

Evolver takes a problem directory with a baseline implementation, tests, and a benchmark. It generates candidate implementations, runs them in isolated workspaces, rejects unsafe code, scores only candidates that pass correctness, archives the full lineage in SQLite, then writes a reproducible evidence bundle. Each new candidate is linked to the best passing candidate measured so far, so the search trace is driven by evidence rather than by unverified generations.

```text
problem spec
  candidate generator
  static safety scan
  resource-limited test subprocess
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
uv run evolver suite --attempts 6 --suite-dir runs/benchmark-suite
```

The three packaged problems cover dynamic programming, substring search, and pair-sum detection. Their deterministic candidate libraries make the verification pipeline reproducible and runnable offline. `run_evolution` also accepts an injected generator, so a model-backed search policy can use the same correctness, measurement, and archive boundary.

The packaged library is a test fixture for search infrastructure, not evidence that an evolutionary or language-model policy discovered the candidates. Candidate sources are proposed independently; evidence-guided lineage records which measured winner was current when each proposal was evaluated.

## Benchmark Suite

`evolver suite` gives every problem the same requested candidate budget, reruns each winner, and writes both per-problem and aggregate evidence. The aggregate includes requested versus evaluated candidates, correctness pass rate, improvement rate, and geometric-mean speedup.

The checked local result is in [`results/benchmark-suite`](results/benchmark-suite). See [`docs/benchmark-protocol.md`](docs/benchmark-protocol.md) before interpreting the timing numbers: they are local algorithmic microbenchmarks, not cross-machine or model-quality claims.

## Evidence Bundle

A run directory contains:

```text
archive.sqlite
best_solution.py
environment.json
report.html
run_spec.json
summary.json
verification.json
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
evolver suite [--problems a,b,c]
evolver inspect <run-dir>
evolver report <run-dir>
evolver verify <run-dir>
evolver list-problems
```

## Repository Layout

```text
evolver/                  core package
evolver/problems/         packaged research problems
tests/                    behavioral and end to end tests
docs/                     design, architecture, and evidence notes
results/                  checked compact benchmark evidence
```

## License

MIT
