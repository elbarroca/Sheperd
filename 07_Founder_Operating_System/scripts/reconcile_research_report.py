"""Reconcile the accepted offline report with the canonical source-ledger CSV."""

from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent
REPORT_PATH = REPO_ROOT / "06_Research/SheperD Interactive Report.html"
LEDGER_PATH = REPO_ROOT / "06_Research/data/source-ledger.csv"

STATUS_COLORS = {
    "verified": "#0F766E",
    "company-claim": "#B45309",
    "mixed": "#6D28D9",
    "unverified": "#B42318",
    "internal-proposal": "#475569",
    "internal-observation": "#1D4ED8",
}


def source_rows() -> list[dict[str, str]]:
    """Load the current canonical ledger."""

    with LEDGER_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def source_table_body(rows: list[dict[str, str]]) -> str:
    """Render source rows using the report's existing accessible table contract."""

    rendered: list[str] = []
    for row in rows:
        source = html.escape(row["url_path"])
        if row["url_path"].startswith(("http://", "https://")):
            source = (
                f'<a href="{source}" rel="noopener noreferrer">'
                f'{html.escape(row["author_publisher"])}</a>'
            )
        status = html.escape(row["evidence_status"])
        rendered.append(
            f'<tr data-evidence="{status}" data-authority="{html.escape(row["authority"])}" '
            f'data-confidence="{html.escape(row["confidence"])}">'
            f'<td>{html.escape(row["source_id"])}</td>'
            f'<td>{html.escape(row["title"])}</td>'
            f'<td>{html.escape(row["authority"])}</td>'
            f'<td><span class="tag ev-{status}">{status}</span></td>'
            f'<td>{html.escape(row["confidence"])}</td>'
            f'<td>{html.escape(row["checked_date"])}</td>'
            f'<td>{source}</td>'
            f'<td>{html.escape(row["claim_supported"])}</td>'
            f'<td>{html.escape(row["conflicts"])}</td>'
            "</tr>"
        )
    return "".join(rendered)


def evidence_chart(rows: list[dict[str, str]]) -> str:
    """Render the source-status chart with numeric equivalents."""

    counts = Counter(row["evidence_status"] for row in rows)
    total = len(rows)
    x_position = 0.0
    fragments = [
        '<svg class="chart-svg" viewBox="0 0 960 92" role="img" '
        'aria-labelledby="evidence-chart-title evidence-chart-desc">',
        '<title id="evidence-chart-title">Evidence status of admitted sources</title>',
        f'<desc id="evidence-chart-desc">{total} source-ledger rows split by controlled '
        "evidence state.</desc>",
    ]
    for status in STATUS_COLORS:
        count = counts.get(status, 0)
        if not count:
            continue
        width = 960 * count / total
        fragments.append(
            f'<rect x="{x_position:.2f}" y="24" width="{width:.2f}" height="34" '
            f'fill="{STATUS_COLORS[status]}"><title>{status}: {count}</title></rect>'
        )
        if width >= 60:
            fragments.append(
                f'<text x="{x_position + width / 2:.2f}" y="46" text-anchor="middle" '
                f'fill="#fff" font-size="13" font-weight="700">{count}</text>'
            )
        x_position += width
    fragments.extend(
        (
            '<line x1="0" y1="68" x2="960" y2="68" stroke="#9FB3C8"/>',
            '<text x="0" y="85" fill="#486581" font-size="12">0</text>',
            f'<text x="960" y="85" text-anchor="end" fill="#486581" '
            f'font-size="12">{total} sources</text>',
            "</svg>",
        )
    )
    return "".join(fragments)


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    """Replace one required report fragment or fail closed."""

    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return updated


def reconcile() -> None:
    """Update source count, chart, table, and embedded JSON atomically in memory."""

    rows = source_rows()
    report = REPORT_PATH.read_text(encoding="utf-8")
    report = replace_once(
        report,
        r'<div class="metric"><b>\d+</b><span>admitted source-ledger rows</span></div>',
        f'<div class="metric"><b>{len(rows)}</b><span>admitted source-ledger rows</span></div>',
        "source metric",
    )
    report = replace_once(
        report,
        r'<svg class="chart-svg" viewBox="0 0 960 92" role="img" '
        r'aria-labelledby="evidence-chart-title evidence-chart-desc">.*?</svg>',
        evidence_chart(rows),
        "evidence chart",
    )
    report = replace_once(
        report,
        r'(<table id="source-table">.*?<tbody>).*?(</tbody>)',
        rf"\g<1>{source_table_body(rows)}\g<2>",
        "source table",
    )

    data_match = re.search(
        r'<script type="application/json" id="report-data">(.*?)</script>', report, re.DOTALL
    )
    if data_match is None:
        raise RuntimeError("Embedded report data was not found")
    report_data: object = json.loads(data_match.group(1))
    if not isinstance(report_data, dict) or "sources" not in report_data:
        raise RuntimeError("Embedded report data has an unexpected schema")
    report_data["sources"] = rows
    embedded = json.dumps(report_data, ensure_ascii=False, separators=(",", ":"))
    report = replace_once(
        report,
        r'(<script type="application/json" id="report-data">).*?(</script>)',
        rf"\g<1>{embedded}\g<2>",
        "embedded report data",
    )
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    reconcile()
