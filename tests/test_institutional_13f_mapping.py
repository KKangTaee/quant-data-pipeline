from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class FakeResponse:
    def __init__(self, payload: object, headers: dict[str, str] | None = None) -> None:
        self.payload = payload
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class OpenFigiResolverTests(unittest.TestCase):
    def test_identifier_type_and_us_equity_filters(self) -> None:
        from finance.data.institutional_13f_mapping import (
            build_openfigi_mapping_job,
            normalize_13f_identifier,
        )

        self.assertEqual(normalize_13f_identifier(" 632307104 "), "632307104")
        self.assertEqual(normalize_13f_identifier("n62509109"), "N62509109")
        self.assertIsNone(normalize_13f_identifier("bad"))
        self.assertEqual(
            build_openfigi_mapping_job("632307104"),
            {
                "idType": "ID_CUSIP",
                "idValue": "632307104",
                "exchCode": "US",
                "marketSecDes": "Equity",
            },
        )
        self.assertEqual(build_openfigi_mapping_job("N62509109")["idType"], "ID_CINS")

    def test_result_normalization_dedupes_one_identity_and_blocks_multiple(self) -> None:
        from finance.data.institutional_13f_mapping import normalize_openfigi_mapping_result

        mapped = normalize_openfigi_mapping_result(
            "632307104",
            {
                "data": [
                    {"ticker": "NTRA", "name": "NATERA INC", "figi": "BBG1", "compositeFIGI": "BBG1"},
                    {"ticker": "NTRA", "name": "NATERA INC", "figi": "BBG1", "compositeFIGI": "BBG1"},
                ]
            },
            attempted_at="2026-07-18 12:00:00",
        )
        self.assertEqual(mapped["resolution_status"], "mapped")
        self.assertEqual(mapped["symbol"], "NTRA")
        self.assertEqual(mapped["figi"], "BBG1")
        self.assertEqual(mapped["candidate_count"], 1)

        ambiguous = normalize_openfigi_mapping_result(
            "000000001",
            {
                "data": [
                    {"ticker": "AAA", "compositeFIGI": "BBGA"},
                    {"ticker": "BBB", "compositeFIGI": "BBGB"},
                ]
            },
            attempted_at="2026-07-18 12:00:00",
        )
        self.assertEqual(ambiguous["resolution_status"], "ambiguous")
        self.assertIsNone(ambiguous["symbol"])
        self.assertEqual(ambiguous["candidate_count"], 2)

        missing = normalize_openfigi_mapping_result(
            "000000002",
            {"warning": "No identifier found."},
            attempted_at="2026-07-18 12:00:00",
        )
        self.assertEqual(missing["resolution_status"], "unmapped")
        self.assertEqual(missing["last_attempt_status"], "success")

    def test_collect_batches_10_without_key_and_100_with_key(self) -> None:
        from finance.data.institutional_13f_mapping import collect_openfigi_resolutions

        calls: list[tuple[object, float]] = []

        def opener(request: object, timeout: float) -> FakeResponse:
            calls.append((request, timeout))
            jobs = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                [
                    {
                        "data": [
                            {
                                "ticker": job["idValue"],
                                "compositeFIGI": f"FIGI-{job['idValue']}",
                            }
                        ]
                    }
                    for job in jobs
                ]
            )

        rows = [{"identifier_value": f"{index:09d}"} for index in range(25)]
        result = collect_openfigi_resolutions(rows, opener=opener, sleep_fn=lambda _: None)
        self.assertEqual(len(result), 25)
        self.assertEqual([len(json.loads(call[0].data)) for call in calls], [10, 10, 5])

        calls.clear()
        collect_openfigi_resolutions(rows, api_key="free-key", opener=opener, sleep_fn=lambda _: None)
        self.assertEqual([len(json.loads(call[0].data)) for call in calls], [25])
        self.assertEqual(calls[0][0].get_header("X-openfigi-apikey"), "free-key")

    def test_retryable_http_error_retries_but_401_does_not(self) -> None:
        from finance.data.institutional_13f_mapping import collect_openfigi_resolutions

        retry_calls = 0

        def retry_opener(request: object, timeout: float) -> FakeResponse:
            nonlocal retry_calls
            retry_calls += 1
            if retry_calls == 1:
                raise HTTPError(request.full_url, 429, "Too Many", {"ratelimit-reset": "0"}, None)
            return FakeResponse([{"warning": "No identifier found."}])

        rows = collect_openfigi_resolutions(
            [{"identifier_value": "632307104"}],
            opener=retry_opener,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(retry_calls, 2)
        self.assertEqual(rows[0]["resolution_status"], "unmapped")

        def unauthorized(request: object, timeout: float) -> FakeResponse:
            raise HTTPError(request.full_url, 401, "Unauthorized", {}, None)

        rows = collect_openfigi_resolutions(
            [{"identifier_value": "632307104"}],
            opener=unauthorized,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(rows[0]["last_attempt_status"], "error")

    def test_collect_waits_for_successful_rate_limit_reset_before_next_batch(self) -> None:
        from finance.data.institutional_13f_mapping import collect_openfigi_resolutions

        sleeps: list[float] = []
        calls = 0

        def opener(request: object, timeout: float) -> FakeResponse:
            nonlocal calls
            calls += 1
            jobs = json.loads(request.data.decode("utf-8"))
            headers = {"ratelimit-remaining": "0", "ratelimit-reset": "2"} if calls == 1 else {}
            return FakeResponse([{"warning": "No identifier found."} for _ in jobs], headers=headers)

        rows = [{"identifier_value": f"{index:09d}"} for index in range(11)]
        collect_openfigi_resolutions(rows, opener=opener, sleep_fn=sleeps.append)
        self.assertEqual(sleeps, [2.0])


class ResolutionPersistenceTests(unittest.TestCase):
    def test_schema_defines_identifier_resolution_current_state(self) -> None:
        from finance.data.db.schema import INSTITUTIONAL_13F_SCHEMAS

        sql = INSTITUTIONAL_13F_SCHEMAS["institutional_13f_identifier_resolution"]
        self.assertIn("UNIQUE KEY uk_identifier_source (identifier_value, source)", sql)
        self.assertIn("resolution_status", sql)
        self.assertIn("last_attempt_status", sql)
        self.assertIn("candidates_json JSON", sql)

    def test_resolution_upsert_preserves_normal_state_on_error_attempt(self) -> None:
        from finance.data.institutional_13f_mapping import upsert_13f_identifier_resolutions

        class FakeDB:
            def __init__(self) -> None:
                self.executemany_calls: list[tuple[str, list[dict[str, object]]]] = []

            def executemany(self, sql: str, rows: list[dict[str, object]]) -> None:
                self.executemany_calls.append((sql, rows))

        fake_db = FakeDB()
        error_row = {
            "identifier_value": "632307104",
            "identifier_type": "ID_CUSIP",
            "source": "openfigi_v3",
            "resolution_status": "unmapped",
            "symbol": None,
            "provider_name": None,
            "figi": None,
            "candidate_count": 0,
            "candidates_json": "[]",
            "source_ref": "https://www.openfigi.com/api/documentation",
            "warning_text": None,
            "error_text": "OpenFIGI HTTP 503: unavailable",
            "last_attempt_status": "error",
            "attempted_at": "2026-07-18 12:00:00",
            "resolved_at": None,
        }
        count = upsert_13f_identifier_resolutions(fake_db, [error_row])
        sql, params = fake_db.executemany_calls[0]
        self.assertEqual(count, 1)
        self.assertIn("IF(VALUES(last_attempt_status) = 'error', resolution_status", sql)
        self.assertIn("IF(VALUES(last_attempt_status) = 'error', symbol", sql)
        self.assertEqual(params[0]["last_attempt_status"], "error")

    def test_latest_13f_identifier_selection_uses_latest_accessions_and_default_retry_scope(self) -> None:
        from finance.data.institutional_13f_mapping import load_latest_13f_identifier_rows

        class FakeDB:
            def __init__(self) -> None:
                self.query_calls: list[tuple[str, tuple[object, ...]]] = []

            def query(self, sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
                self.query_calls.append((sql, params))
                return [
                    {"identifier_value": "632307104", "issuer_name": "Natera Inc"},
                    {"identifier_value": "632307104", "issuer_name": "Natera Inc"},
                    {"identifier_value": " n62509109 ", "issuer_name": "NewAmsterdam"},
                ]

        fake_db = FakeDB()
        rows = load_latest_13f_identifier_rows(fake_db, ["1536411", "0001067983"])
        sql, params = fake_db.query_calls[0]
        self.assertIn("m.latest_accession_number = h.accession_number", sql)
        self.assertIn("m.cik IN (%s, %s)", sql)
        self.assertIn("ir.identifier_value IS NULL", sql)
        self.assertIn("ir.last_attempt_status = 'error'", sql)
        self.assertEqual(params, ("0001536411", "0001067983"))
        self.assertEqual([row["identifier_value"] for row in rows], ["632307104", "N62509109"])

    def test_latest_13f_identifier_refresh_existing_omits_retry_filter(self) -> None:
        from finance.data.institutional_13f_mapping import load_latest_13f_identifier_rows

        class FakeDB:
            def __init__(self) -> None:
                self.sql = ""

            def query(self, sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
                self.sql = sql
                return []

        fake_db = FakeDB()
        load_latest_13f_identifier_rows(fake_db, ["0001536411"], refresh_existing=True)
        self.assertNotIn("ir.last_attempt_status = 'error'", fake_db.sql)


class ResolutionLoaderPrecedenceTests(unittest.TestCase):
    def test_loader_precedence_joins_provider_gate_exact_legacy_and_asset_profile(self) -> None:
        import finance.loaders.institutional_13f as loader

        class FakeDB:
            def __init__(self) -> None:
                self.sql = ""

            def query(self, sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
                self.sql = sql
                return []

            def close(self) -> None:
                return None

        fake_db = FakeDB()
        original_connect = loader._connect
        try:
            loader._connect = lambda *args, **kwargs: fake_db
            loader.load_institutional_13f_holdings("0001536411-26-000001")
        finally:
            loader._connect = original_connect

        self.assertIn("institutional_13f_identifier_resolution", fake_db.sql)
        self.assertIn("ir.resolution_status = 'mapped'", fake_db.sql)
        self.assertIn("ir.resolution_status = 'ambiguous'", fake_db.sql)
        self.assertIn("lm.issuer_key = UPPER(h.issuer_name)", fake_db.sql)
        self.assertIn("nyse_asset_profile", fake_db.sql)
        self.assertIn("AS mapping_status", fake_db.sql)

    def test_reverse_symbol_lookup_prefers_provider_and_dedupes_legacy_rows(self) -> None:
        from finance.loaders.institutional_13f import _load_mapped_cusips_for_symbol

        class FakeDB:
            def __init__(self) -> None:
                self.sql = ""

            def query(self, sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
                self.sql = sql
                return [
                    {"cusip": "632307104"},
                    {"cusip": "632307104"},
                    {"cusip": "457669307"},
                ]

        fake_db = FakeDB()
        cusips = _load_mapped_cusips_for_symbol(fake_db, "NTRA")
        self.assertIn("institutional_13f_identifier_resolution", fake_db.sql)
        self.assertIn("resolution_status = 'mapped'", fake_db.sql)
        self.assertEqual(cusips, ["632307104", "457669307"])


class IdentifierMappingIngestionActionTests(unittest.TestCase):
    def test_mapping_job_reports_provider_summary_without_secret(self) -> None:
        import app.jobs.ingestion_jobs as ingestion_jobs

        original_collector = ingestion_jobs.collect_and_store_openfigi_13f_mappings
        try:
            ingestion_jobs.collect_and_store_openfigi_13f_mappings = lambda **kwargs: {
                "rows_written": 68,
                "identifiers_requested": 68,
                "mapped": 68,
                "ambiguous": 0,
                "unmapped": 0,
                "errors": 0,
                "api_key_used": True,
                "target_table": "finance_meta.institutional_13f_identifier_resolution",
            }
            result = ingestion_jobs.run_collect_sec_13f_identifier_mappings(ciks=["0001536411"])
        finally:
            ingestion_jobs.collect_and_store_openfigi_13f_mappings = original_collector

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 68)
        self.assertEqual(result["symbols_requested"], 68)
        self.assertNotIn("free-key", json.dumps(result))

    def test_identifier_mapping_action_is_registered_guided_and_dispatched(self) -> None:
        import app.web.ingestion.dispatcher as dispatcher
        from app.web.ingestion.guides import JOB_GUIDE, PROGRESS_ENABLED_ACTIONS
        from app.web.ingestion.registry import INGESTION_ACTION_REGISTRY, active_ingestion_actions

        definition = INGESTION_ACTION_REGISTRY["collect_sec_13f_identifier_mappings"]
        self.assertTrue(definition["active"])
        self.assertEqual(
            definition["target_tables"],
            ["finance_meta.institutional_13f_identifier_resolution"],
        )
        self.assertIn("collect_sec_13f_identifier_mappings", active_ingestion_actions())
        self.assertIn("collect_sec_13f_identifier_mappings", PROGRESS_ENABLED_ACTIONS)
        self.assertIn("ticker", JOB_GUIDE["collect_sec_13f_identifier_mappings"]["title"].lower())

        captured: dict[str, object] = {}
        original_runner = dispatcher.run_collect_sec_13f_identifier_mappings

        def fake_runner(**kwargs: object) -> dict[str, object]:
            captured.update(kwargs)
            return {"status": "success"}

        callback = lambda event: None
        try:
            dispatcher.run_collect_sec_13f_identifier_mappings = fake_runner
            result = dispatcher.dispatch_job(
                {
                    "action": "collect_sec_13f_identifier_mappings",
                    "params": {"ciks": ["0001536411"], "refresh_existing": True},
                },
                progress_callback=callback,
            )
        finally:
            dispatcher.run_collect_sec_13f_identifier_mappings = original_runner

        self.assertEqual(result["status"], "success")
        self.assertEqual(captured["ciks"], ["0001536411"])
        self.assertTrue(captured["refresh_existing"])
        self.assertIs(captured["progress_callback"], callback)

    def test_existing_sec_13f_expander_exposes_mapping_button_without_api_key_input(self) -> None:
        source = Path("app/web/ingestion/sections.py").read_text(encoding="utf-8")
        self.assertIn("13F ticker 연결 보강", source)
        self.assertIn('"action": "collect_sec_13f_identifier_mappings"', source)
        self.assertNotIn("OPENFIGI_API_KEY", source)
        self.assertNotIn("OpenFIGI API Key", source)


if __name__ == "__main__":
    unittest.main()
