"""Validate scoped YAML, wikilinks, claims, CSVs, labels, and secret boundaries."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from src.sheperd_os import DatasetCatalog  # noqa: E402

CONTROLLED_EVIDENCE_STATES = {
    "verified",
    "company-claim",
    "internal-proposal",
    "internal-observation",
    "internal-data",
    "internal-decision",
    "inference",
    "unverified",
    "mixed",
    "policy",
}
REQUIRED_YAML = {"type", "status", "owner", "updated", "evidence_status", "confidentiality"}
WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
CLAIM_PATTERN = re.compile(r"\bC-\d{3}\b")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}

SCOPED_MARKDOWN_PATHS = (
    "01_Company/Claims and Evidence Register.md",
    "02_Domain/Market and Competitive Landscape.md",
    "03_GTM/ICP and Stakeholder Personas.md",
    "03_GTM/Sales and Objection Playbook.md",
    "03_GTM/Partner Strategy.md",
    "03_GTM/Website and Content Audit.md",
    "03_GTM/Content and Distribution System.md",
    "03_GTM/SheperD GTM Validation and Optimization - Control Note.md",
    "04_Operations/CRM Data Model.md",
    "04_Operations/Operating Cadence and KPI Dictionary.md",
    "05_AI/AI Enablement Roadmap.md",
    "05_AI/Human Approval Policy.md",
    "06_Research/Industry Regulatory and Competitive Dossier.md",
    "10_Sources/Source - Competitor Websites - 2026-07-15.md",
    "10_Sources/Source - GTM Market and Demand Scan - 2026-07-15.md",
    "90_Templates/Experiment.md",
    "90_Templates/Weekly Scorecard.md",
    "90_Templates/GTM Operator Kit.md",
    "07_Founder_Operating_System/README.md",
    "07_Founder_Operating_System/ARTIFACT_MANIFEST.md",
    "07_Founder_Operating_System/QA_REPORT.md",
)


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse top-level scalar YAML keys required by the vault contract."""

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing YAML delimiter") from error

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line.startswith((" ", "\t", "-")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def link_resolves(source_path: Path, target: str) -> bool:
    """Resolve one Obsidian wikilink as root-relative or note-relative."""

    link_path = target.split("|", 1)[0].split("#", 1)[0].strip()
    if not link_path:
        return True

    raw_candidates = [REPO_ROOT / link_path, source_path.parent / link_path]
    candidates: list[Path] = []
    for raw in raw_candidates:
        if raw.suffix in {".md", ".html", ".base", ".canvas"}:
            candidates.append(raw)
        else:
            candidates.extend(
                Path(f"{raw}{suffix}") for suffix in (".md", ".html", ".base", ".canvas")
            )
    return any(candidate.resolve().is_file() for candidate in candidates)


def validate_markdown() -> tuple[int, list[str]]:
    """Validate frontmatter, wikilinks, claim IDs, labels, and secret patterns."""

    issues: list[str] = []
    checks = 0
    claims_text = (REPO_ROOT / "01_Company/Claims and Evidence Register.md").read_text(
        encoding="utf-8"
    )
    admitted_claim_ids = set(CLAIM_PATTERN.findall(claims_text))

    for relative_path in SCOPED_MARKDOWN_PATHS:
        path = REPO_ROOT / relative_path
        if not path.is_file():
            issues.append(f"{relative_path}: missing scoped Markdown artifact")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            frontmatter = parse_frontmatter(path)
        except ValueError as error:
            issues.append(f"{relative_path}: {error}")
            continue

        missing = REQUIRED_YAML - set(frontmatter)
        checks += len(REQUIRED_YAML)
        if missing:
            issues.append(f"{relative_path}: missing YAML keys {', '.join(sorted(missing))}")
        evidence_status = frontmatter.get("evidence_status", "")
        checks += 1
        if evidence_status not in CONTROLLED_EVIDENCE_STATES:
            issues.append(f"{relative_path}: invalid evidence_status {evidence_status!r}")

        for target in WIKILINK_PATTERN.findall(text):
            checks += 1
            if not link_resolves(path, target):
                issues.append(f"{relative_path}: unresolved wikilink [[{target}]]")

        for claim_id in CLAIM_PATTERN.findall(text):
            checks += 1
            if claim_id not in admitted_claim_ids:
                issues.append(f"{relative_path}: unknown claim ID {claim_id}")

        for label, pattern in SECRET_PATTERNS.items():
            checks += 1
            if pattern.search(text):
                issues.append(f"{relative_path}: possible {label}")

    draft_paths = (
        REPO_ROOT / "03_GTM/Sales and Objection Playbook.md",
        REPO_ROOT / "03_GTM/Content and Distribution System.md",
    )
    for path in draft_paths:
        text = path.read_text(encoding="utf-8")
        checks += 2
        if "DRAFT - HUMAN REVIEW REQUIRED" not in text:
            issues.append(f"{path.relative_to(REPO_ROOT)}: exact draft label missing")
        if "DRAFT — HUMAN REVIEW REQUIRED" in text:
            issues.append(f"{path.relative_to(REPO_ROOT)}: noncanonical em-dash label present")

    return checks, issues


def main() -> int:
    """Run all scoped validation gates."""

    checks, issues = validate_markdown()
    catalog = DatasetCatalog(REPO_ROOT)
    try:
        data_issues = catalog.validate()
        checks += len(catalog.table_names) * 4
        issues.extend(data_issues)
    finally:
        catalog.close()

    if issues:
        print(f"FAIL: {checks} checks; {len(issues)} issue(s)")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {checks} scoped YAML, wikilink, claim, label, secret, and data checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
