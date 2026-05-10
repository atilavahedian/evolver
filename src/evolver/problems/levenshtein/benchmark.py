import argparse
import json
import time

from solution import levenshtein

PAIRS = [
    ("benchmarking", "benchmarkers"),
    ("verification", "reification"),
    ("lineage", "language"),
    ("candidate", "cadence"),
    ("deterministic", "stochastic"),
    ("programsearch", "programchange"),
]


def workload():
    total = 0
    for _ in range(9):
        for left, right in PAIRS:
            total += levenshtein(left, right)
            total += levenshtein(right, left)
    if total <= 0:
        raise AssertionError("invalid distance workload")
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    samples = []
    checksum = None
    for _ in range(args.repeats):
        start = time.perf_counter()
        checksum = workload()
        samples.append(time.perf_counter() - start)
    print(json.dumps({"samples": samples, "checksum": checksum}))


if __name__ == "__main__":
    main()

