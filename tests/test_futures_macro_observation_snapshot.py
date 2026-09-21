from datetime import datetime, timezone
import json

import pandas as pd
import pytest


def _daily_rows():
    return [
        {"provider_symbol": symbol, "candle_time_utc": day, "close": 100 + i * step,
         "open": 100 + i * step, "high": 101 + i * step, "low": 99 + i * step,
         "collected_at": "2026-09-19 10:00:00"}
        for symbol, step in (("ES=F", .1), ("ZN=F", -.02), ("6E=F", -.01))
        for i, day in enumerate(pd.bdate_range("2026-02-02", "2026-09-18"))
    ]


def _query(_db, sql, _params=None):
    if "futures_ohlcv" in sql:
        return _daily_rows()
    if "futures_instrument" in sql:
        return []
    raise AssertionError(f"Unexpected research/context query: {sql[:80]}")


def test_observation_reuses_real_daily_math_without_outlook_or_history(monkeypatch):
    from app.services import futures_macro_pattern_validation as research
    from app.services.futures_macro_observation_snapshot import materialize_futures_macro_observation_snapshot
    from app.services.futures_macro_pattern import build_pattern_feature_frame, build_current_pattern_snapshot
    from app.services.futures_macro_thermometer import normalize_futures_macro_daily_candles
    from finance.data import futures_macro_snapshot as storage

    def forbidden(*_args, **_kwargs):
        pytest.fail("Current observation invoked research/history")

    monkeypatch.setattr(research, "build_pattern_outlook_snapshot", forbidden)
    monkeypatch.setattr(storage, "persist_futures_macro_snapshot_bundle", forbidden)
    saved = []
    result = materialize_futures_macro_observation_snapshot(
        evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
        query_fn=_query, load_fn=lambda: None,
        write_fn=lambda row: saved.append(row) or 1,
    )
    assert result["status"] == "materialized"
    assert len(saved) == 1
    row = saved[0]
    payload = json.loads(row["snapshot_json"])
    from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
    expected = build_current_pattern_snapshot(build_pattern_feature_frame(normalize_futures_macro_daily_candles(_daily_rows()), selected_symbols=DEFAULT_CORE_FUTURES_SYMBOLS))
    assert payload["pattern_outlook"]["current_pattern"]["families"] == expected["families"]
    assert payload["pattern_outlook"]["horizons"] == []
    assert payload["pattern_outlook"]["research_status"] == "NOT_COMPUTED"
    assert row["as_of_date"] == "2026-09-18"
    assert row["session_status"] == "FINAL"
    assert row["snapshot_key"] != "overview_current"


def test_repeated_inputs_reuse_but_corrected_price_rebuilds():
    from app.services.futures_macro_observation_snapshot import materialize_futures_macro_observation_snapshot
    saved = []
    kwargs = dict(evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
                  load_fn=lambda: saved[-1] if saved else None,
                  write_fn=lambda row: saved.append(row) or 1)
    materialize_futures_macro_observation_snapshot(query_fn=_query, **kwargs)
    result = materialize_futures_macro_observation_snapshot(query_fn=_query, **kwargs)
    assert result["status"] == "reused"
    assert len(saved) == 1

    def corrected(db, sql, params=None):
        rows = _query(db, sql, params)
        if "futures_ohlcv" in sql:
            rows[-1]["close"] += 1
        return rows
    result = materialize_futures_macro_observation_snapshot(query_fn=corrected, **kwargs)
    assert result["status"] == "materialized"
    assert len(saved) == 2


def test_older_result_cannot_replace_newer_completed_observation():
    from app.services.futures_macro_observation_snapshot import materialize_futures_macro_observation_snapshot
    written = []
    result = materialize_futures_macro_observation_snapshot(
        query_fn=_query, evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
        load_fn=lambda: {"as_of_date": "2026-09-22", "materialized_at": "2026-09-23 00:00:00"},
        write_fn=lambda row: written.append(row), force=True,
    )
    assert result["status"] == "kept_newer"
    assert written == []


def test_reader_prefers_observation_and_preserves_its_dates(monkeypatch):
    from app.services import futures_macro_snapshot as service
    from app.services.futures_macro_observation_snapshot import OBSERVATION_KEY, OBSERVATION_SCHEMA, OBSERVATION_ALGORITHM
    calls = []
    def load(*, snapshot_key):
        calls.append(snapshot_key)
        return {"snapshot_key": OBSERVATION_KEY, "schema_version": OBSERVATION_SCHEMA,
                "algorithm_version": OBSERVATION_ALGORITHM, "as_of_date": "2026-09-18",
                "status": "READY", "materialized_at": "2026-09-21 07:00:00",
                "snapshot_json": json.dumps({"macro": {}, "pattern_outlook": {"current_pattern": {"families": {"rate_pressure": {"five_day": .8}}}, "horizons": [], "research_status": "NOT_COMPUTED"}})}
    monkeypatch.setattr(service, "load_latest_futures_macro_snapshot", load)
    result = service.load_overview_futures_macro_materialized_snapshot()
    assert calls == [OBSERVATION_KEY]
    assert result["metadata"]["as_of_date"] == "2026-09-18"
    assert result["pattern_outlook"]["current_pattern"]["families"]["rate_pressure"]["five_day"] == .8


def test_default_ingestion_attach_does_not_run_research(monkeypatch):
    from app.jobs.ingestion_jobs import attach_futures_macro_materialization
    from app.services import futures_macro_observation_snapshot as observation
    from app.services import futures_macro_snapshot as research
    monkeypatch.setattr(observation, "materialize_futures_macro_observation_snapshot", lambda: {"status": "materialized", "kind": "observation"})
    monkeypatch.setattr(research, "materialize_overview_futures_macro_snapshot", lambda: pytest.fail("research invoked"))
    result = attach_futures_macro_materialization({"status": "success"}, interval="1d", rows_written=1)
    assert result["details"]["futures_macro_snapshot"]["kind"] == "observation"
