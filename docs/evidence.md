# Evidence Model

Evolver treats a claimed code improvement as a measurement problem.

## Required Evidence

A candidate is only meaningful when these records exist:

1. Source code that was executed.
2. Parent candidate identifier.
3. Static scan result.
4. Correctness test output.
5. Benchmark output with repeated samples.
6. Environment fingerprint.
7. Score and raw speedup.
8. Winner rerun result.

## Failure Handling

Unsafe candidates are archived as failures without execution. Candidates that pass the static scan but fail correctness are archived with test output and no benchmark score. Candidates that pass tests but fail benchmark parsing are archived with benchmark stderr and no performance claim.

## Reproducibility Boundary

The evidence bundle records the local interpreter, platform, command lines, benchmark samples, and winning source. It does not claim cross machine determinism. Timing claims are local to the recorded environment unless rerun elsewhere.

