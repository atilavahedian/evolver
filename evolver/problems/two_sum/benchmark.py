import argparse
import json
import time

from solution import has_pair_sum


def workloads():
    ascending = list(range(700))
    spaced = [index * 3 for index in range(650)]
    return [
        (ascending, 1_397),
        (ascending, -1),
        (spaced, 3_891),
        (spaced, 3_892),
    ]


def workload():
    checksum = 0
    for _ in range(3):
        for values, target in workloads():
            checksum += int(has_pair_sum(values, target))
    if checksum != 6:
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
