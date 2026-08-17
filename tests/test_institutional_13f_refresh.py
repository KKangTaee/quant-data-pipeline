from __future__ import annotations

from datetime import date
import importlib
import io
import urllib.error


def test_2026_deadlines_roll_weekend_and_federal_holiday() -> None:
    from app.services.institutional_13f_refresh import form_13f_due_date

    assert form_13f_due_date("2026-03-31") == date(2026, 5, 15)
    assert form_13f_due_date("2026-06-30") == date(2026, 8, 14)
    assert form_13f_due_date("2026-09-30") == date(2026, 11, 16)
    assert form_13f_due_date("2026-12-31") == date(2027, 2, 16)


def test_refresh_action_targets_latest_due_quarter_from_local_manager_periods() -> None:
    from app.services.institutional_13f_refresh import build_institutional_refresh_action

    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-03-31", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )

    assert action == {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "partial",
        "target_report_period": "2026-06-30",
        "target_quarter_label": "2026년 2분기",
        "label": "2026년 2분기 업데이트 확인 및 갱신",
        "description": "버튼을 누르면 SEC 공개 자료를 확인한 뒤 가능한 기관을 갱신합니다.",
        "completed_managers": 1,
        "expected_managers": 2,
        "pending_ciks": ["0001067983"],
        "next_due_date": "2026-11-16",
    }


def test_refresh_action_hides_when_every_expected_manager_is_current() -> None:
    from app.services.institutional_13f_refresh import build_institutional_refresh_action

    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-06-30", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )

    assert action["status"] == "current"
    assert action["visible"] is False
    assert action["pending_ciks"] == []
    assert action["next_due_date"] == "2026-11-16"


def test_workbench_payload_preserves_injected_local_refresh_action() -> None:
    from app.services.institutional_portfolios import build_institutional_workbench_payload

    refresh_action = {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "due",
        "target_report_period": "2026-06-30",
    }

    payload = build_institutional_workbench_payload(
        model={"summary": {}, "holdings": [], "changes": [], "sector_exposure": []},
        managers=[],
        selected_cik=None,
        interest_model=None,
        refresh_action=refresh_action,
    )

    assert payload["refresh_action"] == refresh_action


def test_bulk_listing_selects_dataset_whose_window_contains_due_date() -> None:
    from finance.data.institutional_13f import (
        parse_sec_13f_dataset_candidates,
        select_sec_13f_dataset_candidate,
    )

    html = """
    <table>
      <tr><td><a href="/files/01mar2026-31may2026_form13f.zip">2026 March April May 13F</a></td></tr>
      <tr><td><a href="/files/01jun2026-31aug2026_form13f.zip">2026 June July August 13F</a></td></tr>
    </table>
    """

    candidates = parse_sec_13f_dataset_candidates(html, base_url="https://www.sec.gov/data")
    selected = select_sec_13f_dataset_candidate(candidates, report_period="2026-06-30")

    assert selected is not None
    assert selected["dataset_url"] == "https://www.sec.gov/files/01jun2026-31aug2026_form13f.zip"
    assert selected["window_start"] == "2026-06-01"
    assert selected["window_end"] == "2026-08-31"


def test_bulk_listing_rejects_non_dataset_anchors_and_out_of_window_dataset() -> None:
    from finance.data.institutional_13f import (
        parse_sec_13f_dataset_candidates,
        select_sec_13f_dataset_candidate,
    )

    html = """
    <a href="/files/not-a-range_form13f.zip">Malformed label</a>
    <a href="/files/01jun2026-31aug2026_form13f.csv">Wrong format</a>
    <a href="/files/01mar2026-31may2026_form13f.zip">Valid older window</a>
    """

    candidates = parse_sec_13f_dataset_candidates(html, base_url="https://www.sec.gov/data")

    assert len(candidates) == 1
    assert select_sec_13f_dataset_candidate(candidates, report_period="2026-06-30") is None


def test_bulk_discovery_fetches_official_listing_with_declared_user_agent(monkeypatch) -> None:
    collector = importlib.import_module("finance.data.institutional_13f")

    captured: dict[str, object] = {}

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    def fake_urlopen(request, *, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response(b'<a href="/files/01jun2026-31aug2026_form13f.zip">Q2 window</a>')

    monkeypatch.setattr(collector.urllib.request, "urlopen", fake_urlopen)

    selected = collector.discover_sec_13f_dataset_candidate(
        "2026-06-30",
        user_agent="Institutional research contact@example.com",
        timeout=7.0,
    )

    assert selected is not None
    assert selected["window_end"] == "2026-08-31"
    assert captured["timeout"] == 7.0
    request = captured["request"]
    assert request.full_url == collector.SEC_13F_DATASETS_PAGE
    assert request.get_header("User-agent") == "Institutional research contact@example.com"


def test_bulk_discovery_preserves_sec_http_status_in_runtime_error(monkeypatch) -> None:
    collector = importlib.import_module("finance.data.institutional_13f")

    def reject(_request, *, timeout):
        raise urllib.error.HTTPError(
            collector.SEC_13F_DATASETS_PAGE,
            429,
            "Too Many Requests",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(collector.urllib.request, "urlopen", reject)

    try:
        collector.discover_sec_13f_dataset_candidate("2026-06-30")
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("SEC HTTP failure must not be swallowed")

    assert collector.SEC_13F_DATASETS_PAGE in message
    assert "429" in message
