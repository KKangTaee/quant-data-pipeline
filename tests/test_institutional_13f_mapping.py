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


if __name__ == "__main__":
    unittest.main()
