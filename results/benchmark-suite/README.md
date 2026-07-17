# Checked Benchmark Suite

This compact artifact records the `budget-normalized-local-suite-v1` run produced on 2026-07-17 UTC with Python 3.12.13 on arm64 macOS.

| Problem | Evaluated | Passing | Selected strategy | Speedup | Winner rerun |
| --- | ---: | ---: | --- | ---: | --- |
| Levenshtein | 6 | 6 | trimmed row dynamic programming | 5.0082x | verified |
| Longest unique substring | 6 | 6 | last-seen index map | 13.4189x | verified |
| Two sum | 6 | 6 | remaining complement set | 214.9960x | verified |

All 18 requested candidates were evaluated and passed their correctness gates. All three selected winners improved over their deliberately slow baselines and passed independent reruns. Geometric-mean speedup was **24.3562x**.

These are local algorithmic microbenchmarks, not application-level or model-discovery results. The deterministic candidate library is hand-authored, and the two-sum result is large because it replaces a quadratic baseline with a linear-time method. See `docs/benchmark-protocol.md` for the full interpretation boundary and reproduction command.
