# Benchmark Protocol

The checked suite answers a narrow question: can Evolver evaluate the same candidate budget across several algorithm families, preserve the evidence, and independently rerun every selected winner?

## Procedure

1. Run all packaged problems with six candidate evaluations requested per problem.
2. Gate every candidate on the packaged seeded correctness tests.
3. Measure passing candidates with five repeated workload samples.
4. Select by baseline-relative latency score with stability and source-size penalties.
5. Rerun the winning source through the original correctness and benchmark gates.
6. Report requested and evaluated budgets, pass rate, improvement rate, per-problem speedup, and geometric-mean speedup.

Reproduce the checked run with:

```bash
uv sync --extra dev
uv run evolver suite \
  --attempts 6 \
  --suite-dir runs/research-suite \
  --seed 2027
```

## Interpretation Boundary

- The problems are algorithmic microbenchmarks with deliberately improvable baselines. Large speedups show that the verifier detects asymptotic improvements; they do not estimate application-level gains.
- Timings are local wall-clock measurements and can vary with machine load, interpreter, and hardware.
- The generator is a deterministic, hand-authored candidate library. Seeds are recorded for protocol reproducibility but do not change this library's proposals.
- The suite does not compare search policies. A model-backed or evolutionary generator should be compared with baselines under equal candidate and compute budgets before making discovery claims.
- Static scanning and subprocess limits are not a hardened sandbox. Run truly untrusted generators in an OS-level isolation boundary.

The compact checked artifact is stored under `results/benchmark-suite`. Full SQLite archives and candidate workspaces are intentionally left under ignored `runs/` directories and can be regenerated with the command above.
