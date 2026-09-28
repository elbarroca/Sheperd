from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
_CODE_PATTERN = re.compile(r"`([^`]+)`")
_SOURCE_PREFIX_PATTERN = re.compile(r"^source:", re.IGNORECASE)
_PDF_URI_PATTERN = re.compile(rb"/URI\s*(?:\(|<)")
_CHROME_CANDIDATES = (
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


def markdown_to_print_html(markdown_text: str) -> str:
    """Render the report's safe Markdown subset as standalone print HTML."""
    rendered: list[str] = []
    in_list = False
    in_finding_card = False
    lines = markdown_text.splitlines()
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    table_rows: list[list[str]] = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            rendered.append("</ul>")
            in_list = False

    def close_table() -> None:
        if not table_rows:
            return
        header, *rows = table_rows
        table_class = ""
        if header == ["Gate", "State"]:
            table_class = "status-table"
        if header == ["Date", "Event", "Type", "Region / lane", "Evidence", "Source"]:
            table_class = "event-table"
        elif header == ["Source", "Published", "Period", "Eligible", "Snapshot hash"]:
            table_class = "evidence-table"
        elif header == [
            "Source",
            "Publisher",
            "Published",
            "Date basis",
            "Use",
            "Validation",
        ]:
            table_class = "source-index-table"
        elif header == ["Article", "Published", "Priority", "Region / lane"]:
            table_class = "compact-article-table"
        class_attribute = f' class="{table_class}"' if table_class else ""
        rendered.append(f"<table{class_attribute}><thead><tr>")
        rendered.extend(f"<th>{_inline_html(cell)}</th>" for cell in header)
        rendered.append("</tr></thead><tbody>")
        for row in rows:
            rendered.append("<tr>")
            rendered.extend(f"<td>{_inline_html(cell)}</td>" for cell in row)
            rendered.append("</tr>")
        rendered.append("</tbody></table>")
        table_rows.clear()

    def close_finding_card() -> None:
        nonlocal in_finding_card
        close_list()
        close_table()
        if in_finding_card:
            rendered.append("</article>")
            in_finding_card = False

    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if in_frontmatter:
            if index > 0 and line == "---":
                in_frontmatter = False
            continue
        if line.startswith("|") and line.endswith("|"):
            close_list()
            cells = [
                cell.strip().replace(r"\|", "|")
                for cell in re.split(r"(?<!\\)\|", line[1:-1])
            ]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            table_rows.append(cells)
            continue
        close_table()
        if not line:
            close_list()
            continue
        if line == "---":
            continue
        if line == "<!-- pdf-page-break -->":
            close_finding_card()
            rendered.append('<div class="page-break"></div>')
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 6)
            text = line[level:].strip()
            close_list()
            if level == 1:
                close_finding_card()
                rendered.append(
                    '<div class="report-kicker">SHEPERD / SOURCE-BOUND INTELLIGENCE</div>'
                )
                rendered.append(f'<h1 class="report-title">{_inline_html(text)}</h1>')
            elif level == 3:
                close_finding_card()
                rendered.append('<article class="finding-card">')
                rendered.append(f"<h3>{_inline_html(text)}</h3>")
                in_finding_card = True
            else:
                if level <= 2:
                    close_finding_card()
                rendered.append(f"<h{level}>{_inline_html(text)}</h{level}>")
            continue
        if line.startswith("- "):
            if not in_list:
                rendered.append("<ul>")
                in_list = True
            rendered.append(f"<li>{_inline_html(line[2:].strip())}</li>")
            continue
        if in_list:
            close_list()
        rendered.append(f"<p>{_inline_html(line)}</p>")
    close_finding_card()
    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>SheperD research report</title>"
        "<style>"
        "@page { size: A4; margin: 16mm 15mm 20mm; }"
        "* { box-sizing: border-box; }"
        "body { margin: 0; color: #172b3a; background: #eef3f7; "
        "font: 10.5pt/1.52 -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; }"
        ".report-shell { max-width: 760px; margin: 0 auto; padding: 6pt 0 20pt; }"
        ".report-kicker { color: #0f766e; font-size: 8pt; font-weight: 800; "
        "letter-spacing: 1.6pt; margin: 0 0 9pt; text-transform: uppercase; }"
        "h1.report-title { color: #102a43; font-size: 25pt; letter-spacing: -.3pt; "
        "line-height: 1.08; margin: 0 0 17pt; max-width: 650px; }"
        "h2 { color: #102a43; border-bottom: 2px solid #c9d6df; break-after: avoid-page; "
        "font-size: 15pt; letter-spacing: -.1pt; margin: 20pt 0 9pt; padding-bottom: 5pt; }"
        "h3, h4 { break-after: avoid-page; }"
        "h3 { color: #102a43; font-size: 13pt; line-height: 1.25; margin: 0 0 8pt; }"
        "h4 { color: #31566e; font-size: 10.5pt; margin: 11pt 0 4pt; "
        "text-transform: uppercase; letter-spacing: .7pt; }"
        "p { margin: 0 0 8pt; } ul { margin: 0 0 9pt; padding-left: 19pt; }"
        "li { margin: 0 0 5pt; } a { color: #0b6477; text-decoration-thickness: 1px; "
        "text-underline-offset: 2px; }"
        ".finding-card { background: #fff; border: 1px solid #d6e0e7; "
        "border-left: 4px solid #0f766e; border-radius: 6px; break-inside: avoid-page; "
        "box-shadow: 0 2px 7px rgba(16, 42, 67, .07); margin: 0 0 13pt; padding: 12pt 13pt 9pt; }"
        ".finding-card p:last-child { margin-bottom: 0; }"
        ".source-line { background: #fff7d6; border: 1px solid #f0d98a; "
        "border-left: 3px solid #e2a400; border-radius: 4px; display: inline-block; "
        "margin-top: 2pt; padding: 3pt 7pt; }"
        ".source-label { color: #8a5a00; font-size: 8pt; font-weight: 800; "
        "letter-spacing: .8pt; margin-right: 4pt; }"
        ".source-line a { color: #795000; font-weight: 650; }"
        "table { background: #fff; border-collapse: separate; border-spacing: 0; "
        "border: 1px solid #cbd8e1; border-radius: 5px; margin: 0 0 12pt; "
        "overflow: hidden; width: 100%; }"
        ".event-table, .evidence-table, .source-index-table, .compact-article-table { "
        "font-size: 8.5pt; "
        "table-layout: fixed; }"
        ".event-table th:nth-child(1) { width: 13%; }"
        ".event-table th:nth-child(2) { width: 28%; }"
        ".event-table th:nth-child(3) { width: 10%; }"
        ".event-table th:nth-child(4) { width: 13%; }"
        ".event-table th:nth-child(5) { width: 10%; }"
        ".event-table th:nth-child(6) { width: 26%; }"
        ".evidence-table th:nth-child(1) { width: 30%; }"
        ".evidence-table th:nth-child(2) { width: 18%; }"
        ".evidence-table th:nth-child(3) { width: 12%; }"
        ".evidence-table th:nth-child(4) { width: 8%; }"
        ".evidence-table th:nth-child(5) { width: 32%; }"
        ".source-index-table th:nth-child(1) { width: 27%; }"
        ".source-index-table th:nth-child(2) { width: 16%; }"
        ".source-index-table th:nth-child(3) { width: 17%; }"
        ".source-index-table th:nth-child(4) { width: 12%; }"
        ".source-index-table th:nth-child(5) { width: 12%; }"
        ".source-index-table th:nth-child(6) { width: 16%; }"
        ".compact-article-table th:nth-child(1) { width: 50%; }"
        ".compact-article-table th:nth-child(2) { width: 16%; }"
        ".compact-article-table th:nth-child(3) { width: 12%; }"
        ".compact-article-table th:nth-child(4) { width: 22%; }"
        ".compact-article-table th { white-space: nowrap; }"
        "th, td { border-bottom: 1px solid #d6e0e7; padding: 5pt 6pt; text-align: left; "
        "vertical-align: top; overflow-wrap: anywhere; }"
        "th + th, td + td { border-left: 1px solid #d6e0e7; }"
        "tr:last-child td { border-bottom: 0; }"
        "tr { break-inside: avoid; page-break-inside: avoid; }"
        "th { background: #17324d; color: #fff; font-weight: 750; }"
        ".status-table td:first-child { color: #31566e; font-weight: 700; width: 43%; }"
        ".status-table td:nth-child(2) { font-weight: 650; }"
        ".source-index-table a, .compact-article-table a { color: #0b6477; font-weight: 650; }"
        ".page-break { break-before: page; page-break-before: always; }"
        "code { font: 9pt ui-monospace, SFMono-Regular, Menlo, monospace; "
        "overflow-wrap: anywhere; }"
        ".print-footer { border-top: 1px solid #cbd8e1; color: #6b8190; display: flex; "
        "font-size: 7.5pt; justify-content: space-between; letter-spacing: .5pt; "
        "margin-top: 22pt; padding-top: 5pt; text-transform: uppercase; }"
        "@media print { body { background: #fff; } .report-shell { max-width: none; } "
        ".finding-card { box-shadow: none; } .print-footer { margin-top: 20pt; } }"
        "</style></head><body><main class=\"report-shell\">"
        + "\n".join(rendered)
        + "\n<div class=\"print-footer\"><span>SheperD research</span>"
        + "<span>Source-bound intelligence</span></div></main></body></html>\n"
    )


def _inline_html(value: str) -> str:
    escaped = html.escape(value, quote=True)
    linked = _LINK_PATTERN.sub(
        lambda match: f'<a href="{match.group(2)}">{match.group(1)}</a>',
        escaped,
    )
    linked = _CODE_PATTERN.sub(lambda match: f"<code>{match.group(1)}</code>", linked)
    if _SOURCE_PREFIX_PATTERN.match(value):
        linked = _SOURCE_PREFIX_PATTERN.sub(
            '<span class="source-label">SOURCE</span>',
            linked,
            count=1,
        )
        return f'<span class="source-line">{linked}</span>'
    return linked


def find_chrome_binary() -> str | None:
    for candidate in _CHROME_CANDIDATES:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
        path = Path(candidate)
        if path.is_file() and path.stat().st_mode & 0o111:
            return str(path)
    return None


def render_pdf(markdown_text: str, destination: Path, *, chrome_binary: str | None = None) -> Path:
    binary = chrome_binary or find_chrome_binary()
    if binary is None:
        raise RuntimeError("pdf_renderer_unavailable")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="sheperd-pdf-") as temporary_dir:
            html_path = Path(temporary_dir) / "report.html"
            html_path.write_text(markdown_to_print_html(markdown_text), encoding="utf-8")
            subprocess.run(
                [
                    binary,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={destination}",
                    html_path.as_uri(),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("pdf_generation_failed") from error
    verify_pdf(destination)
    return destination


def verify_pdf(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError("pdf_missing")
    raw = path.read_bytes()
    if not raw.startswith(b"%PDF"):
        raise RuntimeError("pdf_invalid_header")
    page_count = _pdfinfo_page_count(path)
    pdf_text = _extract_pdf_text(path)
    selectable_text = bool(pdf_text.strip())
    has_application_chrome = "sheperd-pdf-" in pdf_text and "report.html" in pdf_text
    result: dict[str, object] = {
        "valid": True,
        "page_count": page_count,
        "selectable_text": selectable_text,
        "link_count": len(_PDF_URI_PATTERN.findall(raw)),
        "has_application_chrome": has_application_chrome,
    }
    if page_count < 1 or not selectable_text or has_application_chrome:
        raise RuntimeError("pdf_verification_failed")
    return result


def _pdfinfo_page_count(path: Path) -> int:
    binary = shutil.which("pdfinfo")
    if binary is None:
        return max(1, path.read_bytes().count(b"/Type /Page"))
    try:
        result = subprocess.run(
            [binary, str(path)], check=True, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("pdf_page_count_failed") from error
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("pdf_page_count_missing")


def _extract_pdf_text(path: Path) -> str:
    binary = shutil.which("pdftotext")
    if binary is not None:
        try:
            result = subprocess.run(
                [binary, str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            raise RuntimeError("pdf_text_check_failed") from error
        return result.stdout
    osascript = shutil.which("osascript")
    if osascript is None:
        raise RuntimeError("pdf_text_checker_unavailable")
    script = (
        'ObjC.import("Foundation"); ObjC.import("PDFKit"); '
        "function run(argv) { "
        "const doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(argv[0])); "
        'if (!doc) throw new Error("pdf_open_failed"); let output = ""; '
        "for (let index = 0; index < doc.pageCount; index++) { "
        "const value = doc.pageAtIndex(index).string; "
        'if (value) output += ObjC.unwrap(value) + "\\n"; } return output; }'
    )
    try:
        result = subprocess.run(
            [osascript, "-l", "JavaScript", "-e", script, str(path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("pdf_text_check_failed") from error
    return result.stdout
