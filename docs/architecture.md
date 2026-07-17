# Architecture

Evolver is organized around the evidence needed to trust a code improvement.

## Problem Spec

`ProblemSpec` resolves a problem directory and validates that the baseline, tests, benchmark, and generated entrypoint all stay inside that directory. A problem is portable when it contains:

```text
problem.yaml
baseline.py
tests/test_correctness.py
benchmark.py
```

The tests define semantic validity. The benchmark defines the measured objective.

## Candidate Generation

`LibraryGenerator` is deterministic and packaged so the project runs without network access. `run_evolution` accepts the `CandidateGenerator` protocol, so an external model-backed generator can be evaluated without changing the verifier or archive.

Every generated candidate has:

```text
candidate_id
parent_id
generation
source
strategy
```

That is enough to reconstruct lineage.

During a run, each new candidate is attached to the best passing candidate known so far. In the packaged deterministic fixture this is attribution lineage: the fixed sources do not mutate their recorded parent. A generator that uses parent source or evidence can implement actual iterative search through the same protocol.

## Verification Runtime

`SandboxRunner` scans source before execution. Accepted candidates are copied into fresh workspaces under the run directory and run in subprocesses with time and CPU limits. Tests execute before benchmarks. A candidate with failing tests never receives a performance score.

This runner is a reproducible evaluation boundary, not a hardened security sandbox. The scanner rejects known dangerous imports, dynamic execution, and benchmark-tampering markers, but untrusted model output should still run inside an OS-level sandbox or isolated container.

The runner records:

```text
static scan findings
test command
test stdout and stderr
benchmark command
benchmark stdout and stderr
timing samples
timeout state
```

## Archive

`Archive` stores candidates in SQLite. This keeps the full run auditable after the process exits and allows `inspect`, `report`, and future selection strategies to operate from persisted state.

## Scoring

Correctness is a gate. Passing candidates are scored against the baseline using mean latency speedup, with small penalties for timing instability and source complexity. The summary still reports raw speedup separately from the score.

## Evidence Bundle

Each run writes:

```text
archive.sqlite
best_solution.py
environment.json
report.html
run_spec.json
summary.json
verification.json
```

`verify` reruns the winning source from `best_solution.py` against the original problem.

## Suite Aggregation

`run_suite` applies the same requested budget to each selected problem, assigns deterministic per-problem seeds, executes `verify_run` for every winner, and writes `suite_summary.json` plus `suite_results.csv`. Geometric-mean speedup prevents one large ratio from dominating the aggregate as strongly as an arithmetic mean would.
