from __future__ import annotations

import ast
from typing import Iterable, List

from evolver.types import ScanResult


DANGEROUS_IMPORTS = {
    "builtins",
    "ctypes",
    "multiprocessing",
    "os",
    "pathlib",
    "shutil",
    "socket",
    "subprocess",
    "sys",
    "threading",
}

DANGEROUS_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "globals",
    "input",
    "locals",
    "open",
}

DANGEROUS_ATTRIBUTES = {
    "remove",
    "rename",
    "replace",
    "rmdir",
    "run",
    "spawn",
    "system",
    "unlink",
    "write_bytes",
    "write_text",
}

TAMPERING_MARKERS = {
    "benchmark.py",
    "test_correctness",
    "pytest",
    "archive.sqlite",
    "run_spec.json",
}


def scan_source(source: str) -> ScanResult:
    findings: List[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return ScanResult(safe=False, findings=[f"syntax error {exc.msg}"])

    for node in ast.walk(tree):
        findings.extend(_scan_node(node))

    for marker in TAMPERING_MARKERS:
        if marker in source:
            findings.append(f"benchmark tampering marker {marker}")

    return ScanResult(safe=not findings, findings=sorted(set(findings)))


def _scan_node(node: ast.AST) -> Iterable[str]:
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in DANGEROUS_IMPORTS:
                yield f"dangerous import {root}"

    if isinstance(node, ast.ImportFrom):
        root = (node.module or "").split(".", 1)[0]
        if root in DANGEROUS_IMPORTS:
            yield f"dangerous import {root}"

    if isinstance(node, ast.Call):
        name = _call_name(node.func)
        if name in DANGEROUS_CALLS:
            yield f"dangerous call {name}"
        if name.split(".")[-1] in DANGEROUS_ATTRIBUTES:
            yield f"dangerous call {name}"


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""

