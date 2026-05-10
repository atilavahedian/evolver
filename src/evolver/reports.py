from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict

from evolver.archive import Archive


def write_summary(run_dir: Path, summary: Dict[str, Any]) -> None:
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_summary(run_dir: Path) -> Dict[str, Any]:
    return json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))


def write_report(run_dir: Path, archive: Archive, summary: Dict[str, Any]) -> Path:
    rows = []
    for record in archive.all_candidates():
        mean = ""
        if record.evaluation.stats is not None:
            mean = f"{record.evaluation.stats.mean_seconds:.6f}"
        rows.append(
            "<tr>"
            f"<td>{html.escape(record.candidate_id)}</td>"
            f"<td>{html.escape(record.parent_id)}</td>"
            f"<td>{record.generation}</td>"
            f"<td>{html.escape(record.strategy)}</td>"
            f"<td>{record.evaluation.passed}</td>"
            f"<td>{record.score:.4f}</td>"
            f"<td>{mean}</td>"
            "</tr>"
        )

    report = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Evolver Report {html.escape(summary["problem"])}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; color: #111827; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 24px; }}
    th, td {{ border-bottom: 1px solid #d1d5db; padding: 8px; text-align: left; font-size: 14px; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Evolver Evidence Report</h1>
  <p><strong>Problem:</strong> {html.escape(summary["problem"])}</p>
  <p><strong>Best candidate:</strong> <code>{html.escape(summary["best_candidate_id"])}</code></p>
  <p><strong>Speedup:</strong> {summary["speedup"]:.4f}x</p>
  <p><strong>Lineage:</strong> {html.escape(" -> ".join(summary["lineage"]))}</p>
  <h2>Candidates</h2>
  <table>
    <thead>
      <tr>
        <th>Candidate</th>
        <th>Parent</th>
        <th>Generation</th>
        <th>Strategy</th>
        <th>Passed</th>
        <th>Score</th>
        <th>Mean seconds</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    path = run_dir / "report.html"
    path.write_text(report, encoding="utf-8")
    return path


def regenerate_report(run_dir: Path) -> Path:
    archive = Archive.open(run_dir / "archive.sqlite")
    summary = load_summary(run_dir)
    return write_report(run_dir, archive, summary)

