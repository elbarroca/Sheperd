"""Unit tests for fail-closed catalog, query, and ranking behavior."""

from __future__ import annotations

import json
import threading
import unittest
from urllib.request import urlopen

from src.server import create_server
from src.sheperd_os import DatasetCatalog


class DatasetCatalogTests(unittest.TestCase):
    """Verify admitted data remains queryable without weakening gates."""

    catalog: DatasetCatalog

    def setUp(self) -> None:
        self.catalog = DatasetCatalog()

    def tearDown(self) -> None:
        self.catalog.close()

    def test_catalog_contract_passes(self) -> None:
        self.assertEqual(self.catalog.validate(), [])
        self.assertEqual(len(self.catalog.table_names), 9)

    def test_read_only_query_returns_expected_blockers(self) -> None:
        result = self.catalog.safe_query(
            "SELECT blocker_id FROM blockers WHERE current_state = 'blocked' ORDER BY blocker_id"
        )
        self.assertEqual(result["row_count"], 12)
        self.assertEqual(result["rows"][0][0], "GAP-001")
        self.assertFalse(result["truncated"])

    def test_query_rejects_mutation_comments_and_multiple_statements(self) -> None:
        rejected = (
            "DELETE FROM blockers",
            "SELECT * FROM blockers; SELECT * FROM experiments",
            "SELECT * FROM blockers -- bypass",
            "PRAGMA table_info(blockers)",
        )
        for statement in rejected:
            with self.subTest(statement=statement), self.assertRaises(ValueError):
                self.catalog.safe_query(statement)

    def test_query_limit_is_enforced(self) -> None:
        result = self.catalog.safe_query("SELECT * FROM source_ledger", limit=5)
        self.assertEqual(result["row_count"], 5)
        self.assertTrue(result["truncated"])
        with self.assertRaises(ValueError):
            self.catalog.safe_query("SELECT * FROM source_ledger", limit=501)

    def test_ranking_never_unblocks_external_experiments(self) -> None:
        ranking = self.catalog.optimize(
            {
                "learning_value": 1.0,
                "evidence_readiness": 0.0,
                "lower_risk": 0.0,
                "lower_effort": 0.0,
            }
        )
        allowed_ids = {
            row["experiment_id"]
            for row in ranking["experiments"]
            if row["execution_allowed"]
        }
        self.assertEqual(allowed_ids, {"EXP-001", "EXP-002", "EXP-003"})
        for row in ranking["experiments"]:
            if row["execution_state"].startswith("blocked"):
                self.assertFalse(row["execution_allowed"])

    def test_ranking_rejects_unknown_or_invalid_weights(self) -> None:
        with self.assertRaises(ValueError):
            self.catalog.optimize({"expected_revenue": 1.0})
        with self.assertRaises(ValueError):
            self.catalog.optimize(
                {
                    key: 0.0
                    for key in (
                        "learning_value",
                        "evidence_readiness",
                        "lower_risk",
                        "lower_effort",
                    )
                }
            )
        with self.assertRaises(ValueError):
            self.catalog.optimize({"lower_risk": -1.0})

    def test_server_rejects_non_loopback_binding(self) -> None:
        with self.assertRaises(ValueError):
            create_server(catalog=self.catalog, host="0.0.0.0", port=8765)

    def test_http_summary_works_from_server_thread(self) -> None:
        server = create_server(catalog=self.catalog, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = int(server.server_address[1])
        try:
            with urlopen(f"http://127.0.0.1:{port}/api/summary", timeout=2) as response:  # noqa: S310
                payload: object = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(payload, dict)
            assert isinstance(payload, dict)
            self.assertEqual(
                payload["operating_state"], "research-only / external activation blocked"
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
