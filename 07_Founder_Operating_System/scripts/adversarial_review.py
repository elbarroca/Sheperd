"""Run fail-closed P0/P1 checks against the founder workspace."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from src.sheperd_os import DatasetCatalog  # noqa: E402

EXPECTED_EXPERIMENT_STATES = {
    "EXP-001": "prepare-now",
    "EXP-002": "synthetic-only",
    "EXP-003": "synthetic-only",
    "EXP-004": "blocked-external",
    "EXP-005": "blocked-external",
    "EXP-006": "blocked-external",
    "EXP-007": "blocked-publication",
    "EXP-008": "blocked-security",
}
EXPECTED_SOURCE_STATES = {
    "verified": 17,
    "company-claim": 15,
    "mixed": 6,
    "unverified": 2,
    "internal-proposal": 1,
    "internal-observation": 1,
}
REMOTE_ASSET = re.compile(r"(?:src|href)=[\"'](?:https?:)?//", re.IGNORECASE)


def read_csv(relative_path: str) -> list[dict[str, str]]:
    """Read one UTF-8 CSV as dictionaries."""

    with (REPO_ROOT / relative_path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    """Return nonzero when a P0 or P1 fail-closed invariant is violated."""

    findings: list[tuple[str, str]] = []
    checks = 0

    def require(condition: bool, priority: str, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            findings.append((priority, message))

    blockers = read_csv("07_Founder_Operating_System/data/blockers.csv")
    require(len(blockers) == 12, "P0", "blocker register must contain GAP-001 through GAP-012")
    require(
        {row["blocker_id"] for row in blockers} == {f"GAP-{number:03d}" for number in range(1, 13)},
        "P0",
        "blocker IDs are incomplete or duplicated",
    )
    require(
        all(row["current_state"] == "blocked" for row in blockers),
        "P0",
        "an activation blocker was silently promoted",
    )

    experiments = read_csv("07_Founder_Operating_System/data/experiments.csv")
    experiment_states = {row["experiment_id"]: row["execution_state"] for row in experiments}
    require(
        experiment_states == EXPECTED_EXPERIMENT_STATES,
        "P0",
        "experiment execution states differ from the approved fail-closed map",
    )

    content = read_csv("07_Founder_Operating_System/data/content_backlog.csv")
    require(
        all(row["current_state"] in {"internal-outline", "blocked"} for row in content),
        "P0",
        "content backlog contains an externally active state",
    )

    source_rows = read_csv("06_Research/data/source-ledger.csv")
    source_states = Counter(row["evidence_status"] for row in source_rows)
    require(len(source_rows) == 42, "P1", "source ledger row count is not 42")
    require(dict(source_states) == EXPECTED_SOURCE_STATES, "P1", "source-state totals drifted")

    manifest = read_csv("07_Founder_Operating_System/data/artifact_manifest.csv")
    require(
        all((REPO_ROOT / row["path"]).is_file() for row in manifest),
        "P1",
        "artifact manifest points to a missing file",
    )

    for relative_path in (
        "03_GTM/Sales and Objection Playbook.md",
        "03_GTM/Content and Distribution System.md",
    ):
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        require(
            "DRAFT - HUMAN REVIEW REQUIRED" in text,
            "P0",
            f"{relative_path} lacks the exact draft label",
        )
        require(
            "DRAFT — HUMAN REVIEW REQUIRED" not in text,
            "P1",
            f"{relative_path} uses a noncanonical draft label",
        )

    html = (PACKAGE_ROOT / "web/index.html").read_text(encoding="utf-8")
    require(REMOTE_ASSET.search(html) is None, "P0", "dashboard loads a remote asset")
    require('type="file"' not in html, "P0", "dashboard exposes a file-upload control")
    require(
        "external activation blocked" in html.lower(),
        "P0",
        "dashboard omits the activation warning",
    )
    require("D3 remains outside this workspace" in html, "P0", "dashboard omits the D3 boundary")

    catalog = DatasetCatalog(REPO_ROOT)
    try:
        safe_result = catalog.safe_query("WITH one(value) AS (SELECT 1) SELECT value FROM one")
        require(safe_result["rows"] == [[1]], "P1", "bounded read-only CTE failed")
        for mutation in (
            "DELETE FROM blockers",
            "SELECT * FROM blockers; DELETE FROM blockers",
            "ATTACH DATABASE 'x' AS external",
        ):
            try:
                catalog.safe_query(mutation)
            except ValueError:
                rejected = True
            else:
                rejected = False
            require(rejected, "P0", f"query layer accepted prohibited SQL: {mutation}")

        ranking = catalog.optimize()
        allowed = {
            row["experiment_id"]
            for row in ranking["experiments"]
            if row["execution_allowed"]
        }
        require(
            allowed == {"EXP-001", "EXP-002", "EXP-003"},
            "P0",
            "ranker changed the execution allowlist",
        )
        require(
            all(
                not row["execution_allowed"]
                for row in ranking["experiments"]
                if row["execution_state"].startswith("blocked")
            ),
            "P0",
            "ranker promoted a blocked experiment",
        )
    finally:
        catalog.close()

    if findings:
        print(f"FAIL: {checks} adversarial checks; {len(findings)} finding(s)")
        for priority, message in findings:
            print(f"- {priority}: {message}")
        return 1

    print(f"PASS: {checks} adversarial checks; P0=0; P1=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
