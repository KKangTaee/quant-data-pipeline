"""The former 1D/5D/20D UI is replaced by observed intraday windows."""

from app.services.futures_macro_windows import build_futures_macro_window_snapshot
from app.services.overview.futures_macro import build_futures_macro_intraday_read_model
from tests.test_futures_macro_windows import market_rows, calendar, UTC
from datetime import datetime


def test_raw_bars_flow_to_both_windows_without_forecast_geometry():
    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    snapshot = build_futures_macro_window_snapshot(
        rows=market_rows(end), evaluation_time=end, calendar=calendar()
    )
    payload = build_futures_macro_intraday_read_model(
        window_snapshot=snapshot, cycle_snapshot={}
    )
    close = payload["windows"]["since_close"]
    hour = payload["windows"]["last_hour"]
    assert close["start_utc"] == "2026-09-18T20:00:00+00:00"
    assert hour["start_utc"] == "2026-09-21T06:00:00+00:00"
    assert close["end_utc"] == hour["end_utc"]
    assert close["prices"][0]["return_pct"] == hour["prices"][0]["return_pct"]
    assert payload["research"]["status"] == "NOT_VALIDATED"
    assert "horizons" not in payload
