# Evolver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete self improving coding agent that improves code only when tests, benchmarks, lineage, and evidence prove the change.

**Architecture:** A Python package exposes a CLI, a problem spec format, deterministic and model ready candidate generation, sandboxed candidate execution, SQLite archival, scoring, verification reruns, and evidence report generation. The packaged Levenshtein problem demonstrates a real end to end improvement.

**Tech Stack:** Python 3.9+, pytest, SQLite, Typer, PyYAML, Rich, standard library subprocess isolation, GitHub Actions, Cloudflare Wrangler for the personal site update.

---

### Task 1: Repository Foundation

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `README.md`
- Create: `.github/workflows/ci.yml`

- [ ] Write packaging, metadata, docs, and CI files.
- [ ] Run metadata checks with `uv run python -m evolver.cli --help` after code exists.
- [ ] Commit and push.

### Task 2: Failing Tests For Core Contracts

**Files:**
- Create: `tests/test_spec.py`
- Create: `tests/test_scanner.py`
- Create: `tests/test_archive.py`
- Create: `tests/test_runner.py`
- Create: `tests/test_evolution.py`
- Create: `tests/test_cli.py`

- [ ] Write tests before production code for spec parsing, safety scanning, archive persistence, runner behavior, evolution loop behavior, and CLI commands.
- [ ] Run tests and confirm they fail because implementation modules do not exist.
- [ ] Commit and push the failing test suite.

### Task 3: Core Domain And Problem Spec

**Files:**
- Create: `evolver/spec.py`
- Create: `evolver/types.py`
- Create: `evolver/problems/levenshtein/problem.yaml`
- Create: `evolver/problems/levenshtein/baseline.py`
- Create: `evolver/problems/levenshtein/tests/test_correctness.py`
- Create: `evolver/problems/levenshtein/benchmark.py`

- [ ] Implement typed domain models and problem loading.
- [ ] Add the packaged Levenshtein problem.
- [ ] Run focused tests.
- [ ] Commit and push.

### Task 4: Safety Scanner, Sandbox Runner, And Benchmark Parser

**Files:**
- Create: `evolver/scanner.py`
- Create: `evolver/runner.py`
- Create: `evolver/benchmarking.py`

- [ ] Implement AST safety scanning.
- [ ] Implement isolated run directories, subprocess timeouts, resource limits, and command capture.
- [ ] Implement benchmark JSON parsing and timing summaries.
- [ ] Run focused tests.
- [ ] Commit and push.

### Task 5: Archive, Candidate Generation, Selection, And Scoring

**Files:**
- Create: `evolver/archive.py`
- Create: `evolver/generators.py`
- Create: `evolver/selection.py`
- Create: `evolver/scoring.py`

- [ ] Implement SQLite lineage archive.
- [ ] Implement deterministic library generator and extensible generator protocol.
- [ ] Implement tournament selection and score calculation.
- [ ] Run focused tests.
- [ ] Commit and push.

### Task 6: Evolution Engine And Evidence Reports

**Files:**
- Create: `evolver/engine.py`
- Create: `evolver/reports.py`
- Create: `evolver/environment.py`

- [ ] Implement the closed loop run.
- [ ] Write `run_spec.json`, `environment.json`, `best_solution.py`, `summary.json`, and `report.html`.
- [ ] Implement winner rerun verification.
- [ ] Run full end to end tests.
- [ ] Commit and push.

### Task 7: CLI, Documentation, And Final Verification

**Files:**
- Create: `evolver/cli.py`
- Create: `evolver/__init__.py`
- Create: `docs/architecture.md`
- Create: `docs/evidence.md`

- [ ] Implement CLI commands.
- [ ] Write technical documentation.
- [ ] Run formatting, tests, a real search run, inspect, report, and verify.
- [ ] Commit and push.

### Task 8: Personal Site Update And Deploy

**Files:**
- Modify: `/Users/atilavahedian/Documents/atilavahedian.com/src/index.js`

- [ ] Add Evolver to the personal projects section with a concise technical description.
- [ ] Deploy with Wrangler to the live Worker.
- [ ] Verify the Worker preview and custom domain independently.
- [ ] Commit any project repo documentation link update if needed and push.
