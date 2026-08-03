from __future__ import annotations

from unittest.mock import Mock


def test_cycle_transport_attaches_independent_inflation_policy_payload() -> None:
    from app.web.overview.market_context_helpers import (
        load_market_context_cycle_transport,
    )

    payload = load_market_context_cycle_transport(
        cycle_builder=lambda: {"schema_version": "economic_cycle_v2", "horizons": []},
        inflation_policy_builder=lambda: {
            "schema_version": "inflation_policy_v1",
            "publication_status": "LIMITED",
        },
    )

    assert payload["schema_version"] == "economic_cycle_v2"
    assert payload["inflation_policy"] == {
        "schema_version": "inflation_policy_v1",
        "publication_status": "LIMITED",
    }


def test_inflation_command_never_triggers_provider_refresh() -> None:
    from app.web.overview.market_context_helpers import (
        handle_inflation_policy_event,
    )

    provider_refresh = Mock(side_effect=AssertionError("provider must not run"))
    state: dict[str, object] = {}
    results: list[dict[str, object]] = []

    handled = handle_inflation_policy_event(
        {
            "event": {
                "id": "run_reverse_scenario",
                "nonce": "r1",
                "payload": {"instrument": "DGS10"},
            }
        },
        state=state,
        command_runner=lambda command: {
            "publication_status": "NOT_AVAILABLE",
            "reason": f"{command['instrument']} 공동 경로 부족",
        },
        provider_refresh=provider_refresh,
        store_result=results.append,
        clear_cache=Mock(),
        rerun=Mock(),
    )

    assert handled is True
    assert results == [
        {
            "publication_status": "NOT_AVAILABLE",
            "reason": "DGS10 공동 경로 부족",
            "command_id": "run_reverse_scenario",
        }
    ]
    provider_refresh.assert_not_called()


def test_inflation_command_nonce_is_consumed_once_and_uses_separate_state_key() -> None:
    from app.web.overview import market_context_helpers as helpers

    state: dict[str, object] = {
        helpers.ECONOMIC_CYCLE_EVENT_KEY: "refresh_economic_cycle_data:same"
    }
    runner = Mock(return_value={"publication_status": "READY"})
    event = {
        "event": {
            "id": "save_yield_criterion",
            "nonce": "same",
            "payload": {"owner": "USER"},
        }
    }

    assert helpers.handle_inflation_policy_event(
        event,
        state=state,
        command_runner=runner,
        store_result=Mock(),
        clear_cache=Mock(),
        rerun=Mock(),
    )
    assert not helpers.handle_inflation_policy_event(
        event,
        state=state,
        command_runner=runner,
        store_result=Mock(),
        clear_cache=Mock(),
        rerun=Mock(),
    )
    assert state[helpers.ECONOMIC_CYCLE_EVENT_KEY] == "refresh_economic_cycle_data:same"
    assert state[helpers.INFLATION_POLICY_EVENT_KEY] == "save_yield_criterion:same"
    runner.assert_called_once_with({"owner": "USER"})


def test_successful_save_clears_only_inflation_cache() -> None:
    from app.web.overview import market_context_helpers as helpers

    inflation_clear = Mock()
    cycle_clear = Mock(side_effect=AssertionError("cycle cache must remain"))
    handled = helpers.handle_inflation_policy_event(
        {
            "id": "save_yield_criterion",
            "nonce": "save-1",
            "payload": {"owner": "USER"},
        },
        state={},
        command_runner=lambda _: {"publication_status": "READY"},
        store_result=Mock(),
        clear_cache=inflation_clear,
        cycle_clear_cache=cycle_clear,
        rerun=Mock(),
    )

    assert handled is True
    inflation_clear.assert_called_once_with()
    cycle_clear.assert_not_called()


def test_invalid_command_is_returned_to_ui_without_crashing_render() -> None:
    from app.web.overview.market_context_helpers import (
        handle_inflation_policy_event,
    )

    results: list[dict[str, object]] = []
    handled = handle_inflation_policy_event(
        {
            "id": "run_reverse_scenario",
            "nonce": "bad-1",
            "payload": {"zone_lower_pct": 5.0, "zone_upper_pct": 4.0},
        },
        state={},
        command_runner=lambda _: (_ for _ in ()).throw(ValueError("하단 오류")),
        store_result=results.append,
        clear_cache=Mock(),
        rerun=Mock(),
    )

    assert handled is True
    assert results == [
        {
            "publication_status": "FAILED",
            "reason": "하단 오류",
            "command_id": "run_reverse_scenario",
        }
    ]


def test_equity_scenario_event_is_routed_without_provider_refresh() -> None:
    from app.web.overview.market_context_helpers import handle_inflation_policy_event

    runner = Mock(return_value={"publication_status": "READY", "scenario_kind": "USER_ASSUMPTION"})
    results: list[dict[str, object]] = []

    handled = handle_inflation_policy_event(
        {
            "id": "run_equity_stress_scenario",
            "nonce": "equity-1",
            "payload": {"target_level": 6123, "user_ai_eps_uplift_pct": 5},
        },
        state={},
        command_runner=runner,
        provider_refresh=Mock(side_effect=AssertionError("provider must not run")),
        store_result=results.append,
        clear_cache=Mock(),
        rerun=Mock(),
    )

    assert handled is True
    runner.assert_called_once_with(
        {"target_level": 6123, "user_ai_eps_uplift_pct": 5}
    )
    assert results[0]["command_id"] == "run_equity_stress_scenario"
