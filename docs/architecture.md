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

`LibraryGenerator` is deterministic and packaged so the project runs without network access. It is intentionally shaped like a generator protocol, which means an external model backed generator can be added without changing the engine.

Every generated candidate has:

```text
candidate_id
parent_id
generation
source
strategy
```

That is enough to reconstruct lineage.

During a run, each new candidate is attached to the best passing candidate known so far. This makes the local deterministic run evidence guided: later candidates inherit from measured winners rather than from unverified proposals.

## Verification Runtime

`SandboxRunner` scans source before execution. Accepted candidates are copied into fresh workspaces under the run directory. Tests execute before benchmarks. A candidate with failing tests never receives a performance score.

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
