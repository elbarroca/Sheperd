"""Evidence-controlled CSV catalog, query layer, and planning ranker."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Final, TypedDict

MAX_RESULT_ROWS: Final = 500
DEFAULT_RESULT_ROWS: Final = 100
DISALLOWED_SQL = re.compile(
    r"\b(attach|alter|analyze|create|delete|detach|drop|insert|pragma|reindex|replace|"
    r"update|vacuum)\b",
    re.IGNORECASE,
)
SQL_COMMENT = re.compile(r"--|/\*")


@dataclass(frozen=True)
class TableSpec:
    """Location and minimum structural contract for one admitted table."""

    relative_path: str
    primary_key: str
    required_columns: frozenset[str]
    minimum_rows: int


class QueryResult(TypedDict):
    """Serializable result from a bounded read-only query."""

    columns: list[str]
    rows: list[list[str | int | float | None]]
    row_count: int
    truncated: bool


class RankedExperiment(TypedDict):
    """One transparent planning-ranking result."""

    experiment_id: str
    name: str
    execution_state: str
    execution_allowed: bool
    priority_score: float
    primary_hypothesis: str
    gate: str


class RankingResult(TypedDict):
    """Serializable planning-ranking output."""

    formula: str
    weights: dict[str, float]
    warning: str
    experiments: list[RankedExperiment]


TABLE_SPECS: Final[dict[str, TableSpec]] = {
    "source_ledger": TableSpec(
        "06_Research/data/source-ledger.csv",
        "source_id",
        frozenset({"source_id", "evidence_status", "confidence", "url_path"}),
        40,
    ),
    "workflows": TableSpec(
        "06_Research/data/workflows.csv",
        "workflow_id",
        frozenset({"workflow_id", "coverage_status", "owner", "review_gate"}),
        45,
    ),
    "ai_opportunities": TableSpec(
        "06_Research/data/ai-opportunities.csv",
        "opportunity_id",
        frozenset({"opportunity_id", "initial_class", "allowed_data_class", "state"}),
        26,
    ),
    "time_savings": TableSpec(
        "06_Research/data/time-savings.csv",
        "model_scenario_key",
        frozenset({"model_id", "scenario", "sample_size", "confidence"}),
        30,
    ),
    "blockers": TableSpec(
        "07_Founder_Operating_System/data/blockers.csv",
        "blocker_id",
        frozenset({"blocker_id", "gate", "owner", "current_state", "next_action"}),
        12,
    ),
    "experiments": TableSpec(
        "07_Founder_Operating_System/data/experiments.csv",
        "experiment_id",
        frozenset(
            {
                "experiment_id",
                "primary_hypothesis",
                "execution_state",
                "learning_value",
                "evidence_readiness",
                "risk",
                "effort",
            }
        ),
        8,
    ),
    "measurements": TableSpec(
        "07_Founder_Operating_System/data/measurements.csv",
        "measurement_id",
        frozenset({"measurement_id", "numerator", "denominator", "current_state"}),
        14,
    ),
    "content_backlog": TableSpec(
        "07_Founder_Operating_System/data/content_backlog.csv",
        "week",
        frozenset({"week", "asset_hypothesis", "required_gate", "current_state"}),
        12,
    ),
    "artifact_manifest": TableSpec(
        "07_Founder_Operating_System/data/artifact_manifest.csv",
        "artifact_id",
        frozenset({"artifact_id", "path", "purpose", "canonical"}),
        10,
    ),
}

DEFAULT_WEIGHTS: Final[dict[str, float]] = {
    "learning_value": 0.35,
    "evidence_readiness": 0.35,
    "lower_risk": 0.20,
    "lower_effort": 0.10,
}


def _quote_identifier(value: str) -> str:
    """Quote a trusted SQLite identifier."""

    return f'"{value.replace(chr(34), chr(34) * 2)}"'


class DatasetCatalog:
    """Load admitted CSVs into an ephemeral, local, read-only query catalog."""

    def __init__(self, repo_root: Path | None = None) -> None:
        package_root = Path(__file__).resolve().parent.parent
        self.repo_root = repo_root.resolve() if repo_root else package_root.parent
        self._lock = RLock()
        self._connection = sqlite3.connect(":memory:", check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._columns: dict[str, tuple[str, ...]] = {}
        self._load_tables()

    def close(self) -> None:
        """Release the in-memory SQLite catalog."""

        with self._lock:
            self._connection.close()

    @property
    def table_names(self) -> tuple[str, ...]:
        """Return admitted table names in stable order."""

        return tuple(TABLE_SPECS)

    def columns_for(self, table_name: str) -> tuple[str, ...]:
        """Return columns for an admitted table."""

        if table_name not in self._columns:
            raise ValueError(f"Unknown table: {table_name}")
        return self._columns[table_name]

    def _load_tables(self) -> None:
        for table_name, spec in TABLE_SPECS.items():
            path = self.repo_root / spec.relative_path
            if not path.is_file():
                raise FileNotFoundError(f"Missing admitted dataset: {path}")

            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    raise ValueError(f"Dataset has no header: {path}")
                if len(reader.fieldnames) != len(set(reader.fieldnames)):
                    raise ValueError(f"Dataset has duplicate columns: {path}")
                rows = list(reader)

            columns = tuple(reader.fieldnames)
            self._columns[table_name] = columns
            column_sql = ", ".join(f"{_quote_identifier(column)} TEXT" for column in columns)
            self._connection.execute(
                f"CREATE TABLE {_quote_identifier(table_name)} ({column_sql})"
            )
            placeholders = ", ".join("?" for _ in columns)
            values = [tuple(row.get(column, "") for column in columns) for row in rows]
            self._connection.executemany(
                f"INSERT INTO {_quote_identifier(table_name)} VALUES ({placeholders})",
                values,
            )

        self._connection.commit()

    @staticmethod
    def _authorizer(
        action: int,
        parameter_one: str | None,
        parameter_two: str | None,
        database_name: str | None,
        trigger_name: str | None,
    ) -> int:
        del parameter_one, database_name, trigger_name
        allowed_actions = {
            sqlite3.SQLITE_FUNCTION,
            sqlite3.SQLITE_READ,
            sqlite3.SQLITE_SELECT,
        }
        recursive = getattr(sqlite3, "SQLITE_RECURSIVE", None)
        if recursive is not None:
            allowed_actions.add(recursive)
        if action == sqlite3.SQLITE_FUNCTION and parameter_two == "load_extension":
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action in allowed_actions else sqlite3.SQLITE_DENY

    def safe_query(self, sql: str, limit: int = DEFAULT_RESULT_ROWS) -> QueryResult:
        """Execute one bounded SELECT/CTE query against admitted local data."""

        statement = sql.strip()
        if not statement:
            raise ValueError("Query cannot be empty")
        if not re.match(r"^(select|with)\b", statement, re.IGNORECASE):
            raise ValueError("Only SELECT or WITH queries are allowed")
        if ";" in statement or SQL_COMMENT.search(statement):
            raise ValueError("Multiple statements and SQL comments are not allowed")
        if DISALLOWED_SQL.search(statement):
            raise ValueError("Query contains a prohibited SQL operation")
        if not 1 <= limit <= MAX_RESULT_ROWS:
            raise ValueError(f"Limit must be between 1 and {MAX_RESULT_ROWS}")

        with self._lock:
            self._connection.set_authorizer(self._authorizer)
            try:
                cursor = self._connection.execute(statement)
                raw_rows = cursor.fetchmany(limit + 1)
                columns = [description[0] for description in cursor.description or ()]
            except sqlite3.Error as error:
                raise ValueError(f"Query failed: {error}") from error
            finally:
                self._connection.set_authorizer(None)

        truncated = len(raw_rows) > limit
        rows = raw_rows[:limit]
        return {
            "columns": columns,
            "rows": [[row[column] for column in columns] for row in rows],
            "row_count": len(rows),
            "truncated": truncated,
        }

    def table_preview(self, table_name: str, limit: int = 50) -> QueryResult:
        """Return a bounded preview of one admitted table."""

        if table_name not in TABLE_SPECS:
            raise ValueError(f"Unknown table: {table_name}")
        return self.safe_query(f"SELECT * FROM {_quote_identifier(table_name)}", limit=limit)

    def summary(self) -> dict[str, object]:
        """Return evidence-state counts used by the local dashboard."""

        table_rows: dict[str, int] = {}
        for table_name in TABLE_SPECS:
            result = self.safe_query(
                f"SELECT COUNT(*) AS count FROM {_quote_identifier(table_name)}", limit=1
            )
            table_rows[table_name] = int(str(result["rows"][0][0]))

        blocker_states = self.safe_query(
            "SELECT current_state, COUNT(*) AS count FROM blockers "
            "GROUP BY current_state ORDER BY current_state"
        )
        experiment_states = self.safe_query(
            "SELECT execution_state, COUNT(*) AS count FROM experiments "
            "GROUP BY execution_state ORDER BY execution_state"
        )
        source_states = self.safe_query(
            "SELECT evidence_status, COUNT(*) AS count FROM source_ledger "
            "GROUP BY evidence_status ORDER BY count DESC"
        )
        return {
            "operating_state": "research-only / external activation blocked",
            "scores": {
                "research_system": 9.3,
                "gtm_system_design": 9.2,
                "real_market_evidence": 1.8,
                "safe_execution_readiness": 3.3,
            },
            "table_rows": table_rows,
            "blocker_states": blocker_states,
            "experiment_states": experiment_states,
            "source_states": source_states,
            "warning": "Internal planning data; no market-validation or execution authority.",
        }

    def optimize(self, weights: Mapping[str, float] | None = None) -> RankingResult:
        """Rank experiments transparently without overriding any execution gate."""

        selected = dict(DEFAULT_WEIGHTS)
        if weights is not None:
            unknown = set(weights) - set(DEFAULT_WEIGHTS)
            if unknown:
                raise ValueError(f"Unknown weight(s): {', '.join(sorted(unknown))}")
            selected.update(weights)

        if any(value < 0 for value in selected.values()):
            raise ValueError("Weights cannot be negative")
        total_weight = sum(selected.values())
        if total_weight <= 0:
            raise ValueError("At least one weight must be positive")

        result = self.safe_query(
            "SELECT experiment_id, name, execution_state, primary_hypothesis, "
            "learning_value, evidence_readiness, risk, effort FROM experiments",
            limit=MAX_RESULT_ROWS,
        )
        columns = result["columns"]
        rows = [dict(zip(columns, row, strict=True)) for row in result["rows"]]

        ranked: list[RankedExperiment] = []
        eligible_states = {"prepare-now", "synthetic-only"}
        for row in rows:
            learning = self._score_value(row["learning_value"], "learning_value")
            readiness = self._score_value(row["evidence_readiness"], "evidence_readiness")
            risk = self._score_value(row["risk"], "risk")
            effort = self._score_value(row["effort"], "effort")
            score = (
                learning * selected["learning_value"]
                + readiness * selected["evidence_readiness"]
                + (6 - risk) * selected["lower_risk"]
                + (6 - effort) * selected["lower_effort"]
            ) / total_weight
            state = str(row["execution_state"])
            allowed = state in eligible_states
            ranked.append(
                {
                    "experiment_id": str(row["experiment_id"]),
                    "name": str(row["name"]),
                    "execution_state": state,
                    "execution_allowed": allowed,
                    "priority_score": round(score, 3),
                    "primary_hypothesis": str(row["primary_hypothesis"]),
                    "gate": (
                        "Eligible for internal preparation"
                        if allowed
                        else "Blocked by source gate"
                    ),
                }
            )

        ranked.sort(
            key=lambda item: (item["execution_allowed"], item["priority_score"]), reverse=True
        )
        return {
            "formula": (
                "weighted mean of learning value, evidence readiness, inverse risk, and "
                "inverse effort; "
                "all inputs are 1-5 internal-proposal scores"
            ),
            "weights": selected,
            "warning": (
                "Ranking does not override blockers and is not ROI, conversion prediction, causal "
                "optimization, or execution approval."
            ),
            "experiments": ranked,
        }

    @staticmethod
    def _score_value(value: object, field: str) -> int:
        try:
            parsed = int(str(value))
        except ValueError as error:
            raise ValueError(f"{field} must be an integer from 1 to 5") from error
        if not 1 <= parsed <= 5:
            raise ValueError(f"{field} must be an integer from 1 to 5")
        return parsed

    def validate(self) -> list[str]:
        """Return structural or fail-closed data-contract violations."""

        issues: list[str] = []
        for table_name, spec in TABLE_SPECS.items():
            columns = set(self.columns_for(table_name))
            missing = spec.required_columns - columns
            if missing:
                issues.append(f"{table_name}: missing columns {', '.join(sorted(missing))}")

            count_result = self.safe_query(
                f"SELECT COUNT(*) AS count FROM {_quote_identifier(table_name)}", limit=1
            )
            row_count = int(str(count_result["rows"][0][0]))
            if row_count < spec.minimum_rows:
                issues.append(
                    f"{table_name}: expected at least {spec.minimum_rows} rows; found {row_count}"
                )

            if table_name == "time_savings":
                duplicate_query = (
                    "SELECT model_id || ':' || scenario AS key, COUNT(*) AS count "
                    "FROM time_savings GROUP BY model_id, scenario HAVING COUNT(*) > 1"
                )
                blanks_query = (
                    "SELECT COUNT(*) AS count FROM time_savings "
                    "WHERE model_id = '' OR scenario = ''"
                )
            else:
                key = _quote_identifier(spec.primary_key)
                duplicate_query = (
                    f"SELECT {key} AS key, COUNT(*) AS count FROM {_quote_identifier(table_name)} "
                    f"GROUP BY {key} HAVING COUNT(*) > 1"
                )
                blanks_query = (
                    f"SELECT COUNT(*) AS count FROM {_quote_identifier(table_name)} "
                    f"WHERE {key} = ''"
                )

            duplicates = self.safe_query(duplicate_query, limit=MAX_RESULT_ROWS)
            if duplicates["row_count"]:
                issues.append(f"{table_name}: duplicate primary keys")
            blanks = self.safe_query(blanks_query, limit=1)
            if int(str(blanks["rows"][0][0])):
                issues.append(f"{table_name}: blank primary key")

        for row in self.optimize()["experiments"]:
            if row["execution_state"].startswith("blocked") and row["execution_allowed"]:
                issues.append(f"{row['experiment_id']}: blocked experiment marked executable")

        source_paths = self.safe_query(
            "SELECT source_id, url_path FROM source_ledger WHERE url_path NOT LIKE 'http%'",
            limit=MAX_RESULT_ROWS,
        )
        for source_id, relative_path in source_paths["rows"]:
            path = self.repo_root / str(relative_path)
            if not path.is_file():
                issues.append(f"{source_id}: missing local source path {relative_path}")

        return issues


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query the SheperD founder operating system")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate admitted datasets")
    subparsers.add_parser("tables", help="List admitted tables")
    query_parser = subparsers.add_parser("query", help="Run one bounded read-only SQL query")
    query_parser.add_argument("sql")
    query_parser.add_argument("--limit", type=int, default=DEFAULT_RESULT_ROWS)
    subparsers.add_parser("optimize", help="Rank experiment priorities without overriding gates")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    arguments = _build_parser().parse_args(argv)
    catalog = DatasetCatalog()
    try:
        if arguments.command == "validate":
            issues = catalog.validate()
            print(json.dumps({"ok": not issues, "issues": issues}, indent=2))
            return 0 if not issues else 1
        if arguments.command == "tables":
            print(json.dumps({"tables": catalog.table_names}, indent=2))
            return 0
        if arguments.command == "query":
            print(json.dumps(catalog.safe_query(arguments.sql, arguments.limit), indent=2))
            return 0
        if arguments.command == "optimize":
            print(json.dumps(catalog.optimize(), indent=2))
            return 0
        raise RuntimeError(f"Unhandled command: {arguments.command}")
    finally:
        catalog.close()


if __name__ == "__main__":
    raise SystemExit(main())
