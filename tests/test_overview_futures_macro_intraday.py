from app.services.overview.futures_macro import build_futures_macro_intraday_read_model
from tests.test_futures_macro_reading import window


def test_refresh_nonce_is_consumed_once_and_failure_unlocks():
    from app.web.overview.futures_macro_helpers import dispatch_futures_macro_action

    state = {}
    calls = []

    def fail():
        calls.append(1)
        raise RuntimeError("offline")

    event = {"event": {"id": "daily_refresh", "nonce": "a"}}
    dispatch_futures_macro_action(event, state=state, run_action=fail)
    dispatch_futures_macro_action(event, state=state, run_action=fail)
    assert len(calls) == 1 and not state["futures_macro_pending"]
    assert state["futures_macro_ack"] == "a"
    assert state["futures_macro_result"]["status"] == "failed"


def test_reload_does_not_collect_and_busy_event_is_ignored():
    from app.web.overview.futures_macro_helpers import dispatch_futures_macro_action

    state = {}

    def forbidden():
        raise AssertionError("provider called")

    dispatch_futures_macro_action(
        {"id": "reload", "nonce": "b"}, state=state, run_action=forbidden
    )
    assert state["futures_macro_ack"] == "b"
    state["futures_macro_pending"] = True
    dispatch_futures_macro_action(
        {"id": "daily_refresh", "nonce": "c"}, state=state, run_action=forbidden
    )
    assert state["futures_macro_ack"] == "b"


def test_public_payload_has_two_windows_without_old_forecast_geometry():
    p = build_futures_macro_intraday_read_model(
        window_snapshot={"windows": {"since_close": window(), "last_hour": window()}},
        cycle_snapshot={},
    )
    assert set(p["windows"]) == {"since_close", "last_hour"}
    assert (
        not {"horizons", "pattern_map", "pattern_ribbon", "asset_pathways"} & p.keys()
    )
    assert p["research"]["status"] == "NOT_VALIDATED"


def test_streamlit_fallback_uses_same_windows_and_navigation(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import app.web.overview.futures_macro_helpers as ui

    model = build_futures_macro_intraday_read_model(
        window_snapshot={
            "windows": {"since_close": window(), "last_hour": window(es=-0.5)}
        },
        cycle_snapshot={},
    )
    monkeypatch.setattr(ui, "build_futures_macro_intraday_read_model", lambda: model)
    monkeypatch.setattr(ui, "futures_macro_react_component_available", lambda: False)
    app = AppTest.from_string(
        "from app.web.overview.futures_macro_helpers import _render_futures_macro_panel\n_render_futures_macro_panel()"
    ).run()
    assert not app.exception
    assert len(app.metric) == 6
    app.radio[0].set_value("last_hour").run()
    assert app.metric[0].value == "-0.50%"
    assert not app.exception


def test_read_failure_retains_last_observation_but_withholds_current_reading(
    monkeypatch,
):
    from streamlit.testing.v1 import AppTest
    import app.web.overview.futures_macro_helpers as ui

    model = build_futures_macro_intraday_read_model(
        window_snapshot={"windows": {"since_close": window(), "last_hour": window()}},
        cycle_snapshot={},
    )
    monkeypatch.setattr(ui, "build_futures_macro_intraday_read_model", lambda: model)
    monkeypatch.setattr(ui, "futures_macro_react_component_available", lambda: False)
    app = AppTest.from_string(
        "from app.web.overview.futures_macro_helpers import _render_futures_macro_panel\n_render_futures_macro_panel()"
    ).run()

    def fail():
        raise RuntimeError("db read failed")

    monkeypatch.setattr(ui, "build_futures_macro_intraday_read_model", fail)
    app.run()
    assert not app.exception and len(app.metric) == 6
    assert "보류" in app.subheader[0].value
