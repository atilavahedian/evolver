from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from evolver.benchmarking import stats_to_json
from evolver.types import BenchmarkStats, CandidateRecord, EvaluationResult, ScanResult


class Archive:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path))
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()

    @classmethod
    def open(cls, path: Path) -> "Archive":
        return cls(path)

    def record_candidate(self, record: CandidateRecord) -> None:
        stats_json = "{}"
        if record.evaluation.stats is not None:
            stats_json = json.dumps(stats_to_json(record.evaluation.stats), sort_keys=True)
        self.connection.execute(
            """
            insert or replace into candidates (
                candidate_id,
                parent_id,
                generation,
                source,
                strategy,
                passed,
                timed_out,
                score,
                scan_json,
                stats_json,
                test_command,
                benchmark_command,
                test_stdout,
                test_stderr,
                benchmark_stdout,
                benchmark_stderr
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.candidate_id,
                record.parent_id,
                record.generation,
                record.source,
                record.strategy,
                int(record.evaluation.passed),
                int(record.evaluation.timed_out),
                record.score,
                json.dumps(
                    {
                        "safe": record.evaluation.scan.safe,
                        "findings": record.evaluation.scan.findings,
                    },
                    sort_keys=True,
                ),
                stats_json,
                record.evaluation.test_command,
                record.evaluation.benchmark_command,
                record.evaluation.test_stdout,
                record.evaluation.test_stderr,
                record.evaluation.benchmark_stdout,
                record.evaluation.benchmark_stderr,
            ),
        )
        self.connection.commit()

    def get_candidate(self, candidate_id: str) -> Optional[CandidateRecord]:
        row = self.connection.execute(
            "select * from candidates where candidate_id = ?", (candidate_id,)
        ).fetchone()
        if row is None:
            return None
        return self._record_from_row(row)

    def all_candidates(self) -> List[CandidateRecord]:
        rows = self.connection.execute(
            "select * from candidates order by generation asc, candidate_id asc"
        ).fetchall()
        return [self._record_from_row(row) for row in rows]

    def best_candidate(self) -> Optional[CandidateRecord]:
        row = self.connection.execute(
            """
            select * from candidates
            where passed = 1
            order by score desc, generation asc
            limit 1
            """
        ).fetchone()
        if row is None:
            return None
        return self._record_from_row(row)

    def lineage(self, candidate_id: str) -> List[str]:
        lineage = [candidate_id]
        current = self.get_candidate(candidate_id)
        while current is not None and current.parent_id:
            parent_id = current.parent_id
            lineage.insert(0, parent_id)
            current = self.get_candidate(parent_id)
            if current is None:
                break
        return lineage

    def _ensure_schema(self) -> None:
        self.connection.execute(
            """
            create table if not exists candidates (
                candidate_id text primary key,
                parent_id text not null,
                generation integer not null,
                source text not null,
                strategy text not null,
                passed integer not null,
                timed_out integer not null,
                score real not null,
                scan_json text not null,
                stats_json text not null,
                test_command text not null,
                benchmark_command text not null,
                test_stdout text not null,
                test_stderr text not null,
                benchmark_stdout text not null,
                benchmark_stderr text not null,
                created_at text not null default current_timestamp
            )
            """
        )
        self.connection.commit()

    def _record_from_row(self, row: sqlite3.Row) -> CandidateRecord:
        scan_data = json.loads(row["scan_json"])
        stats_data: Dict[str, object] = json.loads(row["stats_json"])
        stats = None
        if stats_data.get("samples"):
            stats = BenchmarkStats(samples=[float(sample) for sample in stats_data["samples"]])
        evaluation = EvaluationResult(
            candidate_id=row["candidate_id"],
            passed=bool(row["passed"]),
            timed_out=bool(row["timed_out"]),
            test_command=row["test_command"],
            benchmark_command=row["benchmark_command"],
            test_stdout=row["test_stdout"],
            test_stderr=row["test_stderr"],
            benchmark_stdout=row["benchmark_stdout"],
            benchmark_stderr=row["benchmark_stderr"],
            scan=ScanResult(
                safe=bool(scan_data["safe"]),
                findings=[str(finding) for finding in scan_data["findings"]],
            ),
            stats=stats,
        )
        return CandidateRecord(
            candidate_id=row["candidate_id"],
            parent_id=row["parent_id"],
            generation=int(row["generation"]),
            source=row["source"],
            strategy=row["strategy"],
            evaluation=evaluation,
            score=float(row["score"]),
        )

