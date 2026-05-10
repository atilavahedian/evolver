from evolver.scanner import scan_source


def test_accepts_pure_algorithm_source():
    source = """
def levenshtein(a, b):
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]
"""

    result = scan_source(source)

    assert result.safe
    assert result.findings == []


def test_rejects_process_and_dynamic_execution():
    source = """
import subprocess

def levenshtein(a, b):
    eval("1 + 1")
    subprocess.run(["echo", "bad"])
    return 0
"""

    result = scan_source(source)

    assert not result.safe
    assert "dangerous import subprocess" in result.findings
    assert "dangerous call eval" in result.findings


def test_rejects_benchmark_tampering_strings():
    source = """
def levenshtein(a, b):
    marker = "benchmark.py"
    return len(marker)
"""

    result = scan_source(source)

    assert not result.safe
    assert "benchmark tampering marker benchmark.py" in result.findings

