import argparse
import json
import time

from solution import longest_unique_substring

TEXTS = [
    "abcdefghijklmnopqrstuvwxyz" * 18,
    "verificationevidence" * 24,
    "programsearchbenchmark" * 22,
    "a" * 500,
]


def workload():
    checksum = 0
    for _ in range(4):
        for text in TEXTS:
            checksum += longest_unique_substring(text)
    if checksum != 180:
        raise AssertionError(f"unexpected checksum {checksum}")
    return checksum


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
