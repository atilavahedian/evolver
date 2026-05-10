# Evolver Design

## Goal

Evolver is a closed loop program search system for improving code under real verification. It proposes candidate programs, executes them in an isolated workspace, gates them through correctness tests, scores them with repeated benchmarks, stores lineage and evidence, and emits reproducible reports for every run.

## Research Standard

The project is built as a research artifact rather than a demo script. A valid improvement must include the exact problem spec, candidate code, parent lineage, static safety scan, test command, benchmark command, environment fingerprint, repeated timing samples, statistical summary, and a generated report that can be inspected after the run.

## Core Architecture

Evolver has seven bounded units:

1. Problem specs describe the function under search, required files, test command, benchmark command, scoring direction, timeouts, and seed.
2. Candidate generators produce complete replacement source files from a baseline and prior evidence. The default generator is deterministic so the full system works without a paid model key, while the interface supports external model driven generators.
3. The sandbox runner creates a fresh execution directory for every candidate, writes the candidate code, applies resource limits where the operating system supports them, and runs tests and benchmarks with timeouts.
4. The safety scanner rejects candidate code with dangerous imports, filesystem mutation calls, process spawning, network modules, dynamic evaluation, or benchmark tampering signals.
5. The scorer treats correctness as mandatory. Failed tests receive zero rank. Passing candidates are scored by speedup, timing stability, memory proxy, and source complexity.
6. The archive records candidates, run events, benchmark samples, static scan findings, lineage, and environment metadata in SQLite.
7. The report builder writes JSON and HTML evidence bundles that can be committed, shared, or rerun.

## Complete Behavior

The CLI supports these commands:

`evolver run <problem>` runs the full search loop.

`evolver inspect <run-dir>` prints the best candidate, score, speedup, and lineage.

`evolver report <run-dir>` regenerates the evidence report from SQLite.

`evolver verify <run-dir>` reruns the winning candidate against the original tests and benchmark.

`evolver list-problems` lists packaged research problems.

## Built In Problem

The initial packaged benchmark is Levenshtein edit distance. The baseline is intentionally correct but inefficient. The candidate library includes algorithmic mutations that move from recursive dynamic programming to row based dynamic programming and early equality checks. This gives the system a real measurable improvement without relying on network access.

## Trust Boundary

Evolver does not trust generated code. It scans source before execution, runs each candidate in a fresh directory, applies timeouts, records all command output, verifies benchmark files are not modified, and reruns the winner before declaring the result complete.

## Testing

Tests cover spec loading, static scanning, candidate lineage, SQLite archive persistence, sandbox execution, benchmark parsing, scoring, report generation, CLI behavior, and a full end to end search on the packaged Levenshtein problem.

