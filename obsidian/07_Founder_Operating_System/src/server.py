"""Local-only HTTP server for the founder dashboard."""

from __future__ import annotations

import json
import mimetypes
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from urllib.parse import parse_qs, urlparse

from .sheperd_os import DEFAULT_RESULT_ROWS, DatasetCatalog

HOST = "127.0.0.1"
PORT = 8765
MAX_REQUEST_BYTES = 65_536


class FounderRequestHandler(BaseHTTPRequestHandler):
    """Serve static assets and bounded JSON APIs without external connectors."""

    catalog: ClassVar[DatasetCatalog]
    web_root: ClassVar[Path]

    def do_GET(self) -> None:  # noqa: N802
        """Serve dashboard assets and read-only APIs."""

        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/summary":
                self._send_json(self.catalog.summary())
                return
            if parsed.path == "/api/table":
                parameters = parse_qs(parsed.query)
                table_name = parameters.get("name", [""])[0]
                limit_text = parameters.get("limit", [str(DEFAULT_RESULT_ROWS)])[0]
                limit = int(limit_text)
                self._send_json(self.catalog.table_preview(table_name, limit))
                return
            if parsed.path == "/api/tables":
                self._send_json(
                    {
                        "tables": [
                            {"name": name, "columns": self.catalog.columns_for(name)}
                            for name in self.catalog.table_names
                        ]
                    }
                )
                return
            self._serve_static(parsed.path)
        except (ValueError, FileNotFoundError) as error:
            self._send_error(HTTPStatus.BAD_REQUEST, str(error))

    def do_POST(self) -> None:  # noqa: N802
        """Run a bounded query or transparent planning ranker."""

        parsed = urlparse(self.path)
        try:
            payload = self._read_json_object()
            if parsed.path == "/api/query":
                sql = payload.get("sql")
                limit = payload.get("limit", DEFAULT_RESULT_ROWS)
                if not isinstance(sql, str):
                    raise ValueError("sql must be a string")
                if not isinstance(limit, int):
                    raise ValueError("limit must be an integer")
                self._send_json(self.catalog.safe_query(sql, limit))
                return
            if parsed.path == "/api/optimize":
                raw_weights = payload.get("weights", {})
                if not isinstance(raw_weights, dict):
                    raise ValueError("weights must be an object")
                weights = self._numeric_weights(raw_weights)
                self._send_json(self.catalog.optimize(weights))
                return
            self._send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            self._send_error(HTTPStatus.BAD_REQUEST, str(error))

    def _read_json_object(self) -> dict[str, object]:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        length_text = self.headers.get("Content-Length")
        if length_text is None:
            raise ValueError("Content-Length is required")
        length = int(length_text)
        if not 0 < length <= MAX_REQUEST_BYTES:
            raise ValueError("Request body size is invalid")
        decoded: object = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("JSON payload must be an object")
        result: dict[str, object] = {}
        for key, value in decoded.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            result[key] = value
        return result

    @staticmethod
    def _numeric_weights(raw_weights: Mapping[object, object]) -> dict[str, float]:
        weights: dict[str, float] = {}
        for key, value in raw_weights.items():
            if not isinstance(key, str):
                raise ValueError("Weight names must be strings")
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise ValueError(f"Weight {key} must be numeric")
            weights[key] = float(value)
        return weights

    def _serve_static(self, request_path: str) -> None:
        relative = "index.html" if request_path == "/" else request_path.lstrip("/")
        candidate = (self.web_root / relative).resolve()
        if self.web_root not in candidate.parents and candidate != self.web_root:
            self._send_error(HTTPStatus.NOT_FOUND, "Asset not found")
            return
        if not candidate.is_file():
            self._send_error(HTTPStatus.NOT_FOUND, "Asset not found")
            return

        content = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self._security_headers()
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_error(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"error": message}, status)

    def _security_headers(self) -> None:
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def log_message(self, format_string: str, *arguments: object) -> None:
        """Avoid logging query bodies or user-supplied values."""

        del format_string, arguments


def create_server(
    catalog: DatasetCatalog | None = None,
    host: str = HOST,
    port: int = PORT,
) -> ThreadingHTTPServer:
    """Create a loopback-only dashboard server."""

    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("The founder dashboard may bind only to loopback")
    if not 0 <= port <= 65_535:
        raise ValueError("Port must be between 0 and 65535")

    package_root = Path(__file__).resolve().parent.parent
    FounderRequestHandler.catalog = catalog or DatasetCatalog()
    FounderRequestHandler.web_root = package_root / "web"
    return ThreadingHTTPServer((host, port), FounderRequestHandler)


def run_server(host: str = HOST, port: int = PORT) -> None:
    """Run until interrupted; no external action or network binding is permitted."""

    server = create_server(host=host, port=port)
    print(f"SheperD Founder Operating System: http://{host}:{port}")
    print("Local D0/D1 planning data only. External activation remains blocked.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
