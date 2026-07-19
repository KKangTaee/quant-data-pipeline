from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from html import escape
from typing import Any, Callable, MutableMapping

import pandas as pd
import streamlit as st

from finance.data.db.mysql import MySQLClient
from finance.loaders import load_price_history

from app.services.portfolio_monitoring.catalog import search_monitoring_catalog
from app.services.portfolio_monitoring.commands import (
    CommandResult,
    EndResolution,
    EntryResolution,
    ensure_default_group,
    execute_add_item,
    execute_create_group,
    execute_end_item,
    execute_rename_group,
)
from app.services.portfolio_monitoring.persistence import (
    DEFAULT_PORTFOLIO_GROUP_ID,
    DEFAULT_PORTFOLIO_GROUP_NAME,
    MySQLMonitoringRepository,
)
from app.services.portfolio_monitoring.read_model import (
    WORKSPACE_SCHEMA_VERSION,
    build_portfolio_monitoring_workspace,
)
from app.services.portfolio_monitoring.schemas import (
    AddMonitoringItemInput,
    CommandStatus,
    CommandType,
    FundingMode,
    InstrumentKind,
    MonitoringCommandInput,
    SourceType,
)
from app.services.portfolio_monitoring.selected_strategy import (
    SelectedStrategyReplayAdapter,
    SelectedStrategyReplayError,
)
from app.services.portfolio_monitoring.valuation import (
    build_direct_security_value_lane,
    resolve_direct_security_entry,
)
from app.web.portfolio_monitoring_react_component import (
    render_portfolio_monitoring_workbench,
)

from app.services.backtest_evidence_read_model import build_decision_dossier
from app.services.backtest_practical_validation import build_market_sentiment_context_overlay
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.reference_contextual_help import render_reference_contextual_help
from app.web.final_selected_portfolio_dashboard_helpers import (
    build_selected_dashboard_handoff_checklist_table,
    build_selected_dashboard_handoff_table,
    build_selected_portfolio_allocation_drift_boundary_table,
    build_selected_portfolio_continuity_table,
    build_selected_portfolio_current_weight_input_table,
    build_selected_dashboard_portfolio_strategy_comparison_table,
    build_selected_dashboard_portfolio_strategy_table,
    build_selected_dashboard_portfolio_table,
    build_selected_dashboard_strategy_pool_table,
    build_selected_portfolio_deployment_readiness_table,
    build_selected_portfolio_drift_alert_table,
    build_selected_portfolio_drift_table,
    build_selected_portfolio_component_table,
    build_selected_portfolio_dashboard_table,
    build_selected_portfolio_evidence_table,
    build_selected_portfolio_monitoring_timeline_table,
    build_selected_portfolio_open_issue_followup_table,
    build_selected_portfolio_provider_evidence_table,
    build_selected_portfolio_provider_symbol_weight_table,
    build_selected_portfolio_recheck_comparison_table,
    build_selected_portfolio_recheck_preflight_table,
    build_selected_portfolio_recheck_readiness_table,
    build_selected_portfolio_review_signal_policy_table,
    build_selected_portfolio_source_contract_table,
    build_selected_portfolio_symbol_freshness_table,
    filter_selected_portfolio_rows,
    final_selected_portfolio_label,
    selected_dashboard_portfolio_label,
    selected_portfolio_active_components,
    selected_portfolio_benchmark_options,
    selected_portfolio_component_default_symbol,
    selected_portfolio_source_type_options,
    selected_portfolio_status_options,
)
from app.runtime import (
    FINAL_SELECTION_DECISION_FILE,
    FINAL_SELECTED_PORTFOLIO_STATUS_LABELS,
    FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS,
    add_selected_dashboard_portfolio_strategy,
    build_selected_dashboard_handoff_review,
    build_selected_dashboard_portfolio_state,
    build_selected_portfolio_allocation_drift_boundary,
    build_selected_portfolio_continuity_check,
    build_selected_portfolio_current_weight_inputs,
    build_selected_portfolio_drift_alert_preview,
    build_selected_portfolio_drift_check,
    build_selected_portfolio_deployment_readiness_preflight,
    build_selected_portfolio_monitoring_timeline,
    build_selected_portfolio_open_issue_followup,
    build_selected_portfolio_performance_recheck,
    build_selected_portfolio_provider_evidence,
    build_selected_portfolio_recheck_comparison,
    build_selected_portfolio_recheck_operations_preflight,
    build_selected_portfolio_recheck_defaults,
    build_selected_portfolio_review_signal_policy,
    delete_selected_dashboard_portfolio,
    load_final_selected_portfolio_dashboard,
    load_latest_selected_portfolio_prices,
    remove_selected_dashboard_portfolio_strategy,
    save_selected_dashboard_portfolio,
    update_selected_dashboard_portfolio_strategy_slot,
)


def _status_tone(status: str) -> str:
    if status in {"normal"}:
        return "positive"
    if status in {"watch", "rebalance_needed", "re_review_needed"}:
        return "warning"
    if status == "blocked":
        return "danger"
    return "neutral"


def _handoff_tone(route: str) -> str:
    if route == "HANDOFF_READY":
        return "positive"
    if route in {"HANDOFF_NO_FINAL_DECISION", "HANDOFF_NO_SELECTED_DECISION"}:
        return "warning"
    if route == "HANDOFF_BLOCKED":
        return "danger"
    return "neutral"


def _alert_tone(alert_route: str) -> str:
    if alert_route == "NO_ALERT":
        return "positive"
    if alert_route in {"WATCH_ALERT", "INPUT_REVIEW_ALERT"}:
        return "warning"
    if alert_route == "REBALANCE_REVIEW_ALERT":
        return "danger"
    return "neutral"


def _allocation_boundary_tone(route: str) -> str:
    if route in {"ALLOCATION_DRIFT_BOUNDARY_READY", "ALLOCATION_DRIFT_BOUNDARY_OPTIONAL"}:
        return "positive"
    if route in {"ALLOCATION_DRIFT_BOUNDARY_WATCH", "ALLOCATION_DRIFT_BOUNDARY_NEEDS_INPUT"}:
        return "warning"
    if route in {"ALLOCATION_DRIFT_BOUNDARY_BREACHED", "ALLOCATION_DRIFT_BOUNDARY_BLOCKED"}:
        return "danger"
    return "neutral"


def _review_trigger_tone(status: str) -> str:
    normalized = str(status or "")
    if normalized in {"Clear", "CLEAR"}:
        return "positive"
    if normalized in {"Watch", "WATCH", "Needs Input", "NEEDS_INPUT"}:
        return "warning"
    if normalized in {"Breached", "BREACHED"}:
        return "danger"
    return "neutral"


def _open_issue_tone(route: str) -> str:
    if route == "OPEN_ISSUES_CLEAR":
        return "positive"
    if route in {"OPEN_ISSUES_PRESENT", "OPEN_ISSUES_NEEDS_INPUT"}:
        return "warning"
    return "neutral"


def _deployment_readiness_tone(route: str) -> str:
    if route == "DEPLOYMENT_READINESS_READY":
        return "positive"
    if route in {"DEPLOYMENT_READINESS_REVIEW", "DEPLOYMENT_READINESS_NEEDS_INPUT"}:
        return "warning"
    if route == "DEPLOYMENT_READINESS_BLOCKED":
        return "danger"
    return "neutral"


def _continuity_tone(route: str) -> str:
    if route == "CONTINUITY_READY":
        return "positive"
    if route in {"CONTINUITY_NEEDS_INPUT", "CONTINUITY_REVIEW"}:
        return "warning"
    if route == "CONTINUITY_BLOCKED":
        return "danger"
    return "neutral"


def _recheck_readiness_tone(route: str) -> str:
    if route == "RECHECK_READINESS_READY":
        return "positive"
    if route in {"RECHECK_READINESS_REVIEW", "RECHECK_READINESS_NEEDS_DATA"}:
        return "warning"
    if route == "RECHECK_READINESS_BLOCKED":
        return "danger"
    return "neutral"


def _recheck_preflight_tone(route: str) -> str:
    if route == "RECHECK_PREFLIGHT_READY":
        return "positive"
    if route in {"RECHECK_PREFLIGHT_REVIEW", "RECHECK_PREFLIGHT_NEEDS_DATA"}:
        return "warning"
    if route == "RECHECK_PREFLIGHT_BLOCKED":
        return "danger"
    return "neutral"


def _symbol_freshness_tone(route: str) -> str:
    if route == "SYMBOL_FRESHNESS_READY":
        return "positive"
    if route in {"SYMBOL_FRESHNESS_WATCH", "SYMBOL_FRESHNESS_STALE", "SYMBOL_FRESHNESS_NEEDS_DATA"}:
        return "warning"
    if route in {"SYMBOL_FRESHNESS_MISSING", "SYMBOL_FRESHNESS_BLOCKED"}:
        return "danger"
    return "neutral"


def _provider_evidence_tone(route: str) -> str:
    if route == "SELECTED_PROVIDER_READY":
        return "positive"
    if route in {"SELECTED_PROVIDER_REVIEW", "SELECTED_PROVIDER_NEEDS_DATA"}:
        return "warning"
    if route == "SELECTED_PROVIDER_BLOCKED":
        return "danger"
    return "neutral"


def _format_pct(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return f"{numeric:.2%}"


def _format_sentiment_score(value: Any) -> str:
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "-"


def _format_sentiment_pct(value: Any) -> str:
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "-"


def _format_sentiment_pp(value: Any) -> str:
    try:
        return f"{float(value):+.1f} pp"
    except (TypeError, ValueError):
        return "-"


def _format_money(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return f"{numeric:,.0f}"


def _format_signed_money(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    sign = "+" if numeric >= 0 else "-"
    return f"{sign}{abs(numeric):,.0f}"


@dataclass
class PortfolioMonitoringPageServices:
    session_state: MutableMapping[str, Any]
    build_workspace: Callable[..., dict[str, Any]]
    render_workbench: Callable[[dict[str, Any]], dict[str, Any] | None]
    render_fallback: Callable[[dict[str, Any], str | None], None]
    rerun: Callable[[], None]
    create_group: Callable[[dict[str, Any]], CommandResult]
    rename_group: Callable[[dict[str, Any]], CommandResult]
    add_item: Callable[[dict[str, Any]], CommandResult]
    end_item: Callable[[dict[str, Any]], CommandResult]


def _monitoring_db_factory() -> MySQLClient:
    return MySQLClient("localhost", "root", "1234", 3306)


def _fallback_monitoring_workspace(
    *,
    catalog_query: str,
    catalog_source_type: str,
    storage_error: str,
) -> dict[str, Any]:
    try:
        catalog_items = search_monitoring_catalog(
            catalog_query,
            catalog_source_type,
            db_factory=_monitoring_db_factory,
        )
    except Exception:
        catalog_items = []
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "groups": [
            {
                "portfolio_group_id": DEFAULT_PORTFOLIO_GROUP_ID,
                "name": DEFAULT_PORTFOLIO_GROUP_NAME,
                "is_default": True,
                "selected": True,
                "status": "storage_unavailable",
                "version": 1,
                "active_item_count": 0,
                "history_item_count": 0,
            }
        ],
        "active_group": None,
        "catalog": {"query": catalog_query, "items": catalog_items},
        "commands": [],
        "method": {
            "basis": "storage migration required",
            "alignment": "not available until monitoring storage is ready",
        },
        "boundaries": {
            "db_only": True,
            "provider_fetch": False,
            "live_orders": False,
            "auto_rebalance": False,
            "storage_ready": False,
            "storage_error": storage_error,
        },
    }


def _catalog_with_entry_readiness(
    items: list[Any],
    *,
    requested_start_date: str | None = None,
) -> list[Any]:
    if not requested_start_date:
        return items
    enriched: list[Any] = []
    for item in items:
        if getattr(item, "source_type", "") != SourceType.DIRECT_SECURITY.value:
            enriched.append(item)
            continue
        try:
            history = load_price_history(
                symbols=[item.source_ref],
                start=requested_start_date,
                timeframe="1d",
            )
            entry = resolve_direct_security_entry(
                history,
                date.fromisoformat(requested_start_date),
                FundingMode.FIXED_NOTIONAL,
                Decimal("1"),
            )
            metadata = {
                **dict(item.metadata or {}),
                "effective_start_date": entry.effective_start_date.isoformat(),
                "entry_close": str(entry.entry_close),
            }
            enriched.append(type(item)(**{**asdict(item), "metadata": metadata, "readiness": "READY"}))
        except Exception:
            enriched.append(type(item)(**{**asdict(item), "readiness": "MISSING_PRICE"}))
    return enriched


def _default_portfolio_monitoring_services() -> PortfolioMonitoringPageServices:
    repository = MySQLMonitoringRepository(_monitoring_db_factory)
    selected_adapter = SelectedStrategyReplayAdapter()
    session_state = st.session_state

    def lane_loader(item):
        if item.source_type == SourceType.SELECTED_STRATEGY.value:
            return selected_adapter.build_value_lane(
                item,
                end_date=item.tracking_end_effective_date,
            )
        history = load_price_history(
            symbols=[item.source_ref],
            start=item.effective_start_date.isoformat(),
            end=(item.tracking_end_effective_date.isoformat() if item.tracking_end_effective_date else None),
            timeframe="1d",
        )
        return build_direct_security_value_lane(item, history)

    def build_workspace(*, active_group_id: str | None, catalog_query: str) -> dict[str, Any]:
        source_type = str(session_state.get("portfolio_monitoring_catalog_source_type") or SourceType.DIRECT_SECURITY.value)
        requested_date = session_state.get("portfolio_monitoring_catalog_requested_start_date")
        try:
            ensure_default_group(repository)
            workspace = build_portfolio_monitoring_workspace(
                repository,
                active_group_id=active_group_id,
                catalog_query=catalog_query,
                lane_loader=lane_loader,
            )
        except Exception as exc:
            return _fallback_monitoring_workspace(
                catalog_query=catalog_query,
                catalog_source_type=source_type,
                storage_error=str(exc),
            )
        try:
            catalog_items = search_monitoring_catalog(
                catalog_query,
                source_type,
                db_factory=_monitoring_db_factory,
            )
            catalog_items = _catalog_with_entry_readiness(
                catalog_items,
                requested_start_date=str(requested_date) if requested_date else None,
            )
        except Exception as exc:
            catalog_items = []
            workspace["boundaries"] = {**dict(workspace.get("boundaries") or {}), "catalog_error": str(exc)}
        workspace["catalog"] = {"query": catalog_query, "items": catalog_items}
        return workspace

    def create_group(event: dict[str, Any]) -> CommandResult:
        return execute_create_group(
            repository,
            MonitoringCommandInput(
                command_id=str(event.get("command_id") or ""),
                command_type=CommandType.CREATE_GROUP,
                target_id=None,
                payload={"name": event.get("name")},
            ),
        )

    def rename_group(event: dict[str, Any]) -> CommandResult:
        return execute_rename_group(
            repository,
            MonitoringCommandInput(
                command_id=str(event.get("command_id") or ""),
                command_type=CommandType.RENAME_GROUP,
                target_id=str(event.get("portfolio_group_id") or ""),
                payload={"name": event.get("name")},
                expected_version=int(event.get("expected_version") or 0),
            ),
        )

    def add_item(event: dict[str, Any]) -> CommandResult:
        item_input = AddMonitoringItemInput(
            portfolio_group_id=str(event.get("portfolio_group_id") or ""),
            source_type=SourceType(str(event.get("source_type") or "")),
            source_ref=str(event.get("source_ref") or ""),
            instrument_kind=InstrumentKind(str(event.get("instrument_kind") or "")),
            requested_start_date=date.fromisoformat(str(event.get("requested_start_date") or "")),
            funding_mode=FundingMode(str(event.get("funding_mode") or "")),
            input_notional=(Decimal(str(event["input_notional"])) if event.get("input_notional") is not None else None),
            input_shares=(int(event["input_shares"]) if event.get("input_shares") is not None else None),
        )

        def resolve_entry(value: AddMonitoringItemInput) -> EntryResolution:
            if value.source_type == SourceType.SELECTED_STRATEGY:
                contract = selected_adapter.load_candidate_contract(value.source_ref)
                if contract.readiness.status != "READY":
                    raise SelectedStrategyReplayError(contract.readiness)
                return EntryResolution(
                    effective_start_date=value.requested_start_date,
                    entry_close=Decimal("1"),
                    initial_capital=Decimal(value.input_notional or 0),
                    metadata={
                        "decision_id": value.source_ref,
                        "decision_updated_at": contract.readiness.source_dates.get("decision_updated_at"),
                    },
                )
            history = load_price_history(
                symbols=[value.source_ref],
                start=value.requested_start_date.isoformat(),
                timeframe="1d",
            )
            amount: Decimal | int = (
                int(value.input_shares or 0)
                if value.funding_mode == FundingMode.FIXED_SHARES
                else Decimal(value.input_notional or 0)
            )
            return resolve_direct_security_entry(
                history,
                value.requested_start_date,
                value.funding_mode,
                amount,
            )

        return execute_add_item(
            repository,
            MonitoringCommandInput(
                command_id=str(event.get("command_id") or ""),
                command_type=CommandType.ADD_ITEM,
                target_id=str(event.get("portfolio_group_id") or ""),
                payload=dict(event),
            ),
            item_input,
            resolve_entry=resolve_entry,
        )

    def end_item(event: dict[str, Any]) -> CommandResult:
        requested_end = date.fromisoformat(str(event.get("requested_end_date") or ""))

        def resolve_end(item) -> EndResolution:
            horizon = requested_end + timedelta(days=10)
            if item.source_type == SourceType.SELECTED_STRATEGY.value:
                lane = selected_adapter.build_value_lane(item, end_date=horizon)
            else:
                history = load_price_history(
                    symbols=[item.source_ref],
                    start=item.effective_start_date.isoformat(),
                    end=horizon.isoformat(),
                    timeframe="1d",
                )
                lane = build_direct_security_value_lane(item, history)
            eligible = lane.curve.loc[pd.to_datetime(lane.curve["date"]) >= pd.Timestamp(requested_end)]
            if eligible.empty:
                raise ValueError("No usable value is available on or after the requested end date.")
            row = eligible.iloc[0]
            return EndResolution(
                requested_end_date=requested_end,
                effective_end_date=pd.Timestamp(row["date"]).date(),
                exit_value=Decimal(str(row["total_value"])),
            )

        return execute_end_item(
            repository,
            MonitoringCommandInput(
                command_id=str(event.get("command_id") or ""),
                command_type=CommandType.END_ITEM,
                target_id=str(event.get("monitoring_item_id") or ""),
                payload={"requested_end_date": requested_end.isoformat()},
            ),
            resolve_end=resolve_end,
        )

    return PortfolioMonitoringPageServices(
        session_state=session_state,
        build_workspace=build_workspace,
        render_workbench=render_portfolio_monitoring_workbench,
        render_fallback=_render_portfolio_monitoring_fallback,
        rerun=st.rerun,
        create_group=create_group,
        rename_group=rename_group,
        add_item=add_item,
        end_item=end_item,
    )


def _session_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _coerce_date(value: Any, fallback: date) -> date:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return fallback
    return parsed.date()


def _slot_for_row(row: dict[str, Any]) -> dict[str, Any]:
    return dict(row.get("dashboard_slot") or {})


def _recheck_defaults_cache_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            str(row.get("decision_id") or ""),
            str(row.get("baseline_start") or ""),
            str(row.get("baseline_end") or ""),
        ]
    )


def _recheck_defaults(row: dict[str, Any]) -> dict[str, Any]:
    cache_key = _recheck_defaults_cache_key(row)
    cache = st.session_state.setdefault("selected_portfolio_recheck_defaults_cache", {})
    if cache_key not in cache:
        cache[cache_key] = build_selected_portfolio_recheck_defaults(row)
    return dict(cache.get(cache_key) or {})


def _slot_effective_start(row: dict[str, Any]) -> str:
    slot = _slot_for_row(row)
    defaults = _recheck_defaults(row)
    return str(slot.get("start") or defaults.get("default_start") or defaults.get("baseline_start") or "").strip()


def _slot_effective_end(row: dict[str, Any]) -> str:
    slot = _slot_for_row(row)
    defaults = _recheck_defaults(row)
    if bool(slot.get("use_latest_end", True)):
        return str(defaults.get("default_end") or defaults.get("latest_market_date") or "").strip()
    return str(slot.get("end") or "").strip()


def _slot_effective_capital(row: dict[str, Any]) -> float:
    slot = _slot_for_row(row)
    try:
        capital = float(slot.get("initial_capital") or 0.0)
    except (TypeError, ValueError):
        return 0.0
    return capital if not pd.isna(capital) else 0.0


def _dashboard_status_tone(status: str) -> str:
    if status == "Ready":
        return "positive"
    if status == "Needs Review":
        return "warning"
    return "neutral"


def _clip_text(value: Any, *, limit: int = 120, default: str = "-") -> str:
    text = str(value or "").strip()
    if not text:
        return default
    return text if len(text) <= limit else f"{text[: max(limit - 1, 0)].rstrip()}..."


def _inject_dashboard_product_styles() -> None:
    st.markdown(
        """
        <style>
          .fspd-shelf-card {
            min-height: 178px;
            height: 178px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 1rem;
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96));
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
          }
          .fspd-shelf-card-active {
            border-color: rgba(15, 118, 110, 0.55);
            box-shadow: inset 0 0 0 1px rgba(15, 118, 110, 0.16), 0 1px 3px rgba(15, 23, 42, 0.08);
          }
          .fspd-shelf-card-create {
            border-style: dashed;
            background: linear-gradient(180deg, rgba(240,253,250,0.82), rgba(248,250,252,0.96));
          }
          .fspd-card-kicker {
            font-size: 0.72rem;
            font-weight: 760;
            color: #0f766e;
            line-height: 1.2;
            text-transform: uppercase;
          }
          .fspd-card-title {
            margin-top: 0.35rem;
            font-size: 1rem;
            font-weight: 780;
            line-height: 1.25;
            color: #111827;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .fspd-card-desc {
            margin-top: 0.35rem;
            min-height: 2.4rem;
            font-size: 0.82rem;
            line-height: 1.35;
            color: #64748b;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .fspd-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            align-items: center;
            margin-top: 0.7rem;
          }
          .fspd-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            min-height: 24px;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            background: #e2e8f0;
            color: #0f172a;
            font-size: 0.76rem;
            font-weight: 720;
            line-height: 1.2;
            white-space: nowrap;
          }
          .fspd-chip-positive { background: #ccfbf1; color: #134e4a; }
          .fspd-chip-warning { background: #fef3c7; color: #78350f; }
          .fspd-chip-neutral { background: #e2e8f0; color: #334155; }
          .fspd-command-band,
          .fspd-scenario-cockpit,
          .fspd-add-panel,
          .fspd-strategy-card {
            border: 1px solid rgba(148, 163, 184, 0.32);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
          }
          .fspd-command-band {
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
            gap: 1rem;
            padding: 1rem;
            margin: 0.35rem 0 0.9rem;
          }
          .fspd-command-title {
            font-size: 1.15rem;
            font-weight: 820;
            line-height: 1.25;
            color: #111827;
            overflow-wrap: anywhere;
          }
          .fspd-command-desc {
            margin-top: 0.45rem;
            color: #64748b;
            font-size: 0.86rem;
            line-height: 1.45;
          }
          .fspd-command-metrics {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.5rem;
          }
          .fspd-mini-metric {
            padding: 0.55rem 0.65rem;
            border-radius: 8px;
            background: #f8fafc;
            border: 1px solid rgba(226, 232, 240, 0.9);
          }
          .fspd-mini-metric span {
            display: block;
            color: #64748b;
            font-size: 0.72rem;
            font-weight: 720;
          }
          .fspd-mini-metric strong {
            display: block;
            margin-top: 0.2rem;
            color: #111827;
            font-size: 0.95rem;
            line-height: 1.2;
          }
          .fspd-add-panel {
            padding: 0.95rem;
            margin: 0.45rem 0 0.9rem;
            background: #f8fafc;
          }
          .fspd-section-label {
            margin: 0.5rem 0 0.25rem;
            font-size: 0.9rem;
            font-weight: 800;
            color: #111827;
          }
          .fspd-section-help {
            margin: 0 0 0.5rem;
            color: #64748b;
            font-size: 0.82rem;
            line-height: 1.35;
          }
          .fspd-strategy-card {
            padding: 0.9rem 1rem;
            margin: 0.6rem 0 0.25rem;
          }
          .fspd-strategy-card-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
          }
          .fspd-strategy-title {
            font-size: 0.98rem;
            font-weight: 820;
            line-height: 1.25;
            color: #111827;
            overflow-wrap: anywhere;
          }
          .fspd-strategy-subtitle {
            margin-top: 0.25rem;
            color: #64748b;
            font-size: 0.8rem;
            line-height: 1.35;
          }
          .fspd-strategy-meta {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.45rem;
            margin-top: 0.8rem;
          }
          .fspd-scenario-cockpit {
            display: grid;
            grid-template-columns: minmax(240px, 0.85fr) minmax(0, 1.15fr);
            gap: 1rem;
            padding: 1rem;
            margin: 0.45rem 0 0.9rem;
          }
          .fspd-scenario-primary {
            padding: 0.9rem;
            border-radius: 8px;
            background: #0f172a;
            color: #f8fafc;
          }
          .fspd-scenario-primary span {
            display: block;
            color: #99f6e4;
            font-size: 0.76rem;
            font-weight: 760;
          }
          .fspd-scenario-primary strong {
            display: block;
            margin-top: 0.4rem;
            font-size: 1.55rem;
            line-height: 1.15;
          }
          .fspd-scenario-primary p {
            margin: 0.45rem 0 0;
            color: #cbd5e1;
            font-size: 0.84rem;
            line-height: 1.45;
          }
          .fspd-scenario-metrics {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
          }
          .fspd-performance-board {
            display: grid;
            gap: 0.5rem;
            margin: 0.35rem 0 0.85rem;
          }
          .fspd-performance-row {
            display: grid;
            grid-template-columns: minmax(220px, 1fr) repeat(4, minmax(90px, 0.45fr));
            gap: 0.55rem;
            align-items: center;
            padding: 0.7rem 0.8rem;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            background: #ffffff;
          }
          .fspd-row-title {
            font-weight: 780;
            line-height: 1.25;
            color: #111827;
            overflow-wrap: anywhere;
          }
          .fspd-row-sub {
            margin-top: 0.18rem;
            color: #64748b;
            font-size: 0.78rem;
          }
          @media (max-width: 900px) {
            .fspd-command-band,
            .fspd-scenario-cockpit,
            .fspd-performance-row {
              grid-template-columns: 1fr;
            }
            .fspd-strategy-meta,
            .fspd-scenario-metrics,
            .fspd-command-metrics {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
          }
          @media (prefers-color-scheme: dark) {
            .fspd-shelf-card,
            .fspd-command-band,
            .fspd-add-panel,
            .fspd-strategy-card,
            .fspd-scenario-cockpit,
            .fspd-performance-row {
              background: #111827;
              border-color: rgba(148, 163, 184, 0.28);
              box-shadow: none;
            }
            .fspd-shelf-card-create,
            .fspd-add-panel {
              background: #0f172a;
            }
            .fspd-card-title,
            .fspd-command-title,
            .fspd-section-label,
            .fspd-strategy-title,
            .fspd-row-title,
            .fspd-mini-metric strong {
              color: #f8fafc;
            }
            .fspd-card-desc,
            .fspd-command-desc,
            .fspd-section-help,
            .fspd-strategy-subtitle,
            .fspd-row-sub,
            .fspd-mini-metric span {
              color: #94a3b8;
            }
            .fspd-mini-metric {
              background: #0f172a;
              border-color: rgba(148, 163, 184, 0.24);
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _chip(label: str, value: Any, *, tone: str = "neutral") -> str:
    return (
        f'<span class="fspd-chip fspd-chip-{escape(tone)}">'
        f"{escape(label)} <strong>{escape(str(value if value is not None else '-'))}</strong>"
        "</span>"
    )


def _mini_metric(label: str, value: Any) -> str:
    return (
        '<div class="fspd-mini-metric">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(str(value if value is not None else '-'))}</strong>"
        "</div>"
    )


def _portfolio_card_html(portfolio: dict[str, Any], *, is_active: bool = False) -> str:
    status = str(portfolio.get("dashboard_status") or "Empty")
    classes = "fspd-shelf-card fspd-shelf-card-active" if is_active else "fspd-shelf-card"
    return (
        f'<div class="{classes}">'
        "<div>"
        f'<div class="fspd-card-kicker">{"Selected" if is_active else "Portfolio"}</div>'
        f'<div class="fspd-card-title">{escape(_clip_text(portfolio.get("name"), limit=72))}</div>'
        f'<div class="fspd-card-desc">{escape(_clip_text(portfolio.get("description"), limit=96, default="설명 없음"))}</div>'
        "</div>"
        '<div class="fspd-chip-row">'
        f'{_chip("Status", status, tone=_dashboard_status_tone(status))}'
        f'{_chip("Strategies", portfolio.get("strategy_count", 0))}'
        f'{_chip("Capital", _format_money(portfolio.get("virtual_capital_total")))}'
        "</div>"
        "</div>"
    )


def _create_portfolio_card_html() -> str:
    return (
        '<div class="fspd-shelf-card fspd-shelf-card-create">'
        "<div>"
        '<div class="fspd-card-kicker">New</div>'
        '<div class="fspd-card-title">+ 새 포트폴리오</div>'
        '<div class="fspd-card-desc">이름과 메모만 저장하고, 전략은 다음 단계에서 추가합니다.</div>'
        "</div>"
        '<div class="fspd-chip-row">'
        f'{_chip("Setup", "사용자 저장")}'
        "</div>"
        "</div>"
    )


def _render_portfolio_command_band(portfolio: dict[str, Any]) -> None:
    status = str(portfolio.get("dashboard_status") or "Empty")
    html = (
        '<div class="fspd-command-band">'
        "<div>"
        f'<div class="fspd-command-title">{escape(_clip_text(portfolio.get("name"), limit=120))}</div>'
        f'<div class="fspd-command-desc">{escape(_clip_text(portfolio.get("description"), limit=180, default="이 포트폴리오에 Final Review selected 전략을 담아 모니터링합니다."))}</div>'
        '<div class="fspd-chip-row">'
        f'{_chip("Status", status, tone=_dashboard_status_tone(status))}'
        f'{_chip("Source", "Final Review read-only")}'
        f'{_chip("Trading", "Disabled")}'
        "</div>"
        "</div>"
        '<div class="fspd-command-metrics">'
        f'{_mini_metric("Strategies", portfolio.get("strategy_count", 0))}'
        f'{_mini_metric("Total Balance", _format_money(portfolio.get("virtual_capital_total")))}'
        f'{_mini_metric("Complete Slots", portfolio.get("complete_strategy_slot_count", 0))}'
        f'{_mini_metric("Needs Review", portfolio.get("incomplete_strategy_slot_count", 0))}'
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def _render_info_card_grid(cards: list[dict[str, Any]], *, min_width: int = 210) -> None:
    html_cards: list[str] = []
    for card in cards:
        title = escape(str(card.get("title") or ""))
        value = escape(str(card.get("value") if card.get("value") is not None else "-"))
        detail = escape(str(card.get("detail") or ""))
        tone = escape(str(card.get("tone") or "neutral"))
        detail_html = f'<div class="fsp-info-card-detail">{detail}</div>' if detail else ""
        html_cards.append(
            f'<div class="fsp-info-card fsp-info-card-{tone}">'
            f'<div class="fsp-info-card-title">{title}</div>'
            f'<div class="fsp-info-card-value">{value}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        f"""
        <style>
          .fsp-info-card-grid {{
            display: grid;
            gap: 0.75rem;
            margin: 0.35rem 0 1rem 0;
          }}
          .fsp-info-card {{
            min-height: 92px;
            padding: 0.85rem 0.95rem;
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-top: 4px solid #64748b;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
          }}
          .fsp-info-card-positive {{ border-top-color: #0f766e; }}
          .fsp-info-card-warning {{ border-top-color: #b45309; }}
          .fsp-info-card-danger {{ border-top-color: #b91c1c; }}
          .fsp-info-card-neutral {{ border-top-color: #475569; }}
          .fsp-info-card-title {{
            font-size: 0.82rem;
            font-weight: 720;
            color: #64748b;
            line-height: 1.25;
            overflow-wrap: anywhere;
          }}
          .fsp-info-card-value {{
            margin-top: 0.35rem;
            font-size: 1.08rem;
            font-weight: 780;
            color: #111827;
            line-height: 1.25;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
          .fsp-info-card-detail {{
            margin-top: 0.4rem;
            font-size: 0.82rem;
            line-height: 1.35;
            color: #64748b;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="fsp-info-card-grid" style="grid-template-columns: repeat(auto-fit, minmax({min_width}px, 1fr));">{"".join(html_cards)}</div>',
        unsafe_allow_html=True,
    )


def _summary_cards(summary: dict[str, Any]) -> list[dict[str, Any]]:
    status_counts = dict(summary.get("status_counts") or {})
    return [
        {
            "title": "Final Review Records",
            "value": summary.get("final_decision_count", 0),
            "detail": "Final Review 전체 판단 row",
            "tone": "positive" if summary.get("final_decision_count") else "neutral",
        },
        {
            "title": "Selected Portfolios",
            "value": summary.get("selected_decision_count", 0),
            "detail": "최신 기간 재검증 대상",
            "tone": "positive" if summary.get("selected_decision_count") else "neutral",
        },
        {
            "title": "Monitoring Clear",
            "value": status_counts.get("normal", 0),
            "detail": "모니터링 후보 row / allocation / blocker 기준 모니터링 가능",
            "tone": "positive" if status_counts.get("normal") else "neutral",
        },
        {
            "title": "Watch / Review",
            "value": status_counts.get("watch", 0)
            + status_counts.get("rebalance_needed", 0)
            + status_counts.get("re_review_needed", 0),
            "detail": "관찰 또는 재검토 필요",
            "tone": "warning" if (
                status_counts.get("watch", 0)
                + status_counts.get("rebalance_needed", 0)
                + status_counts.get("re_review_needed", 0)
            ) else "neutral",
        },
        {
            "title": "Blocked",
            "value": status_counts.get("blocked", 0),
            "detail": "운영 대상으로 보기 전 보강 필요",
            "tone": "danger" if status_counts.get("blocked") else "neutral",
        },
        {
            "title": "Live Approval / Order",
            "value": "Disabled",
            "detail": "Phase36은 승인/주문을 만들지 않음",
            "tone": "neutral",
        },
    ]


def _render_market_sentiment_context_overlay() -> None:
    overlay = build_market_sentiment_context_overlay(surface="Operations > Portfolio Monitoring")
    risk_context = dict(overlay.get("risk_context") or {})
    metrics = dict(overlay.get("metrics") or {})
    boundary = dict(overlay.get("boundary") or {})
    tone = str(risk_context.get("tone") or "neutral")

    with st.container(border=True):
        st.markdown("#### 시장 심리 Context Overlay")
        st.caption(
            "CNN Fear & Greed / AAII sentiment를 현재 모니터링 화면의 시장 배경으로만 보여줍니다. "
            "Monitoring Scenario, Review Signal, saved setup, broker order, auto rebalance에는 연결되지 않습니다."
        )
        render_badge_strip(
            [
                {"label": "Risk Context", "value": risk_context.get("state_label") or "Neutral", "tone": tone},
                {"label": "Source Phase", "value": risk_context.get("source_phase_label") or "-", "tone": tone},
                {"label": "Boundary", "value": "Context only", "tone": "neutral"},
                {"label": "Monitoring Signal", "value": "Disabled", "tone": "neutral"},
                {"label": "Saved Setup", "value": "No write", "tone": "neutral"},
            ]
        )
        st.caption(f"{overlay.get('headline') or ''} {overlay.get('summary') or ''}".strip())
        _render_info_card_grid(
            [
                {
                    "title": "CNN Fear & Greed",
                    "value": _format_sentiment_score(metrics.get("cnn_fear_greed")),
                    "detail": metrics.get("cnn_rating") or overlay.get("status") or "-",
                    "tone": tone,
                },
                {
                    "title": "AAII Bearish",
                    "value": _format_sentiment_pct(metrics.get("aaii_bearish")),
                    "detail": "weekly survey",
                    "tone": "warning" if (metrics.get("aaii_bearish") or 0) and float(metrics.get("aaii_bearish") or 0) >= 35 else "neutral",
                },
                {
                    "title": "AAII Bull-Bear Spread",
                    "value": _format_sentiment_pp(metrics.get("aaii_bull_bear_spread")),
                    "detail": "bullish - bearish",
                    "tone": "positive" if (metrics.get("aaii_bull_bear_spread") or 0) and float(metrics.get("aaii_bull_bear_spread") or 0) > 0 else "warning",
                },
                {
                    "title": "Data Confidence",
                    "value": dict(overlay.get("data_confidence") or {}).get("status") or overlay.get("status") or "-",
                    "detail": f"missing {metrics.get('missing_count') or 0} / stale {metrics.get('stale_count') or 0}",
                    "tone": dict(overlay.get("data_confidence") or {}).get("tone") or "neutral",
                },
            ],
            min_width=190,
        )
        render_badge_strip(
            [
                {"label": "PASS / BLOCKER", "value": "No effect", "tone": "neutral"},
                {"label": "Registry Write", "value": "No", "tone": "neutral"},
                {"label": "Order / Rebalance", "value": "Disabled", "tone": "neutral"},
                {"label": "Surface", "value": overlay.get("surface") or "Portfolio Monitoring", "tone": "neutral"},
            ]
        )
        if boundary.get("message"):
            st.caption(str(boundary["message"]))
        warnings = list(overlay.get("warnings") or [])
        if warnings:
            st.warning(" / ".join(str(item) for item in warnings))
        evidence_rows = list(overlay.get("evidence_rows") or [])
        if evidence_rows:
            with st.expander("CNN / AAII context evidence", expanded=False):
                st.dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)
        if overlay.get("next_action"):
            st.caption(str(overlay["next_action"]))


def _render_empty_state(summary: dict[str, Any]) -> None:
    if not summary.get("final_decision_count"):
        st.info("아직 Final Review에서 저장된 모니터링 후보 row가 없습니다.")
        st.caption(f"Path: {FINAL_SELECTION_DECISION_FILE}")
        return
    st.warning(
        "Final Review 기록은 있지만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장된 모니터링 후보 포트폴리오가 없습니다. "
        "`Backtest > Final Review`에서 모니터링 후보로 저장된 row만 이 대시보드에 운영 대상으로 표시됩니다."
    )
    st.caption(f"Path: {FINAL_SELECTION_DECISION_FILE}")


def _render_final_review_handoff(all_final_decisions: list[dict[str, Any]]) -> None:
    handoff = build_selected_dashboard_handoff_review(all_final_decisions)
    summary = dict(handoff.get("summary") or {})
    route = str(handoff.get("route") or "")
    with st.container(border=True):
        st.markdown("#### Final Review Handoff")
        render_badge_strip(
            [
                {"label": "Handoff", "value": handoff.get("route_label") or route, "tone": _handoff_tone(route)},
                {
                    "label": "Final Decisions",
                    "value": summary.get("final_decision_count", 0),
                    "tone": "positive" if summary.get("final_decision_count") else "neutral",
                },
                {
                    "label": "Selected Rows",
                    "value": summary.get("selected_decision_count", 0),
                    "tone": "positive" if summary.get("selected_decision_count") else "warning",
                },
                {
                    "label": "Monitorable",
                    "value": summary.get("monitorable_count", 0),
                    "tone": "positive" if summary.get("monitorable_count") else "warning",
                },
                {
                    "label": "Blocked",
                    "value": summary.get("blocked_count", 0),
                    "tone": "danger" if summary.get("blocked_count") else "neutral",
                },
                {"label": "Approval / Order", "value": "Disabled", "tone": "neutral"},
            ]
        )
        message = f"{handoff.get('verdict') or '-'} 다음 단계: {handoff.get('next_action') or '-'}"
        if route == "HANDOFF_READY":
            st.success(message)
        elif route == "HANDOFF_BLOCKED":
            st.error(message)
        else:
            st.warning(message)
        handoff_df = build_selected_dashboard_handoff_table(handoff)
        if not handoff_df.empty:
            st.dataframe(handoff_df, width="stretch", hide_index=True)
        else:
            st.caption("Dashboard로 표시할 selected Final Review row가 아직 없습니다.")
        with st.expander("Handoff checklist / storage boundary", expanded=False):
            checklist_df = build_selected_dashboard_handoff_checklist_table(handoff)
            if not checklist_df.empty:
                st.dataframe(checklist_df, width="stretch", hide_index=True)
            boundary = dict(handoff.get("execution_boundary") or {})
            st.caption(
                f"Source: {summary.get('registry_path') or FINAL_SELECTION_DECISION_FILE} / "
                f"write policy: {boundary.get('write_policy') or '-'} / "
                f"monitoring auto-write: {boundary.get('monitoring_log_auto_write')} / "
                f"auto rebalance: {boundary.get('auto_rebalance')}"
            )


def _render_selected_portfolio_picker(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    st.markdown("#### Selected Portfolio")
    if len(rows) == 1:
        row = rows[0]
        with st.container(border=True):
            st.markdown(f"##### {row.get('source_title') or '-'}")
            render_badge_strip(
                [
                    {
                        "label": "Status",
                        "value": row.get("operation_status_label"),
                        "tone": _status_tone(str(row.get("operation_status") or "")),
                    },
                    {"label": "Benchmark", "value": row.get("benchmark_label"), "tone": "neutral"},
                    {"label": "Components", "value": row.get("component_count"), "tone": "neutral"},
                    {"label": "Target", "value": f"{float(row.get('target_weight_total') or 0.0):.1f}%", "tone": "neutral"},
                    {"label": "Original End", "value": row.get("baseline_end"), "tone": "neutral"},
                ]
            )
        return row

    with st.container(border=True):
        status_options = selected_portfolio_status_options(rows)
        source_type_options = selected_portfolio_source_type_options(rows)
        benchmark_options = selected_portfolio_benchmark_options(rows)
        filter_top_cols = st.columns(2, gap="small")
        with filter_top_cols[0]:
            selected_statuses = st.multiselect(
                "Status",
                options=status_options,
                default=status_options,
                format_func=lambda status: FINAL_SELECTED_PORTFOLIO_STATUS_LABELS.get(status, status),
                key="selected_portfolio_dashboard_status_filter",
            )
        with filter_top_cols[1]:
            selected_benchmark = st.selectbox(
                "Benchmark",
                options=benchmark_options,
                key="selected_portfolio_dashboard_benchmark_filter",
            )
        filter_bottom_cols = st.columns([0.64, 0.36], gap="small")
        with filter_bottom_cols[0]:
            selected_source_types = st.multiselect(
                "Source Type",
                options=source_type_options,
                default=source_type_options,
                key="selected_portfolio_dashboard_source_filter",
            )

        filtered_rows = filter_selected_portfolio_rows(
            rows,
            statuses=selected_statuses,
            source_types=selected_source_types,
            benchmark=str(selected_benchmark),
        )
        with filter_bottom_cols[1]:
            _render_info_card_grid(
                [
                    {"title": "Total", "value": len(rows), "detail": "selected rows", "tone": "neutral"},
                    {"title": "Shown", "value": len(filtered_rows), "detail": "after filter", "tone": "positive"},
                ],
                min_width=120,
            )
        if not filtered_rows:
            st.warning("현재 filter 조건에 맞는 선정 포트폴리오가 없습니다.")
            return None

        with st.expander("Selected portfolio list", expanded=False):
            st.dataframe(build_selected_portfolio_dashboard_table(filtered_rows), width="stretch", hide_index=True)
        labels = [final_selected_portfolio_label(row) for row in filtered_rows]
        selected_label = st.selectbox(
            "포트폴리오 선택",
            options=labels,
            key="selected_portfolio_dashboard_selected_row",
        )
        return filtered_rows[labels.index(selected_label)]


def _portfolio_by_id(portfolios: list[dict[str, Any]], portfolio_id: str | None) -> dict[str, Any] | None:
    clean_id = str(portfolio_id or "").strip()
    for portfolio in portfolios:
        if str(portfolio.get("portfolio_id") or "") == clean_id:
            return portfolio
    return None


def _selected_strategy_rows_for_portfolio(
    portfolio: dict[str, Any],
    dashboard_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if portfolio.get("strategy_rows"):
        return [dict(row or {}) for row in list(portfolio.get("strategy_rows") or [])]
    row_by_decision_id = {
        str(row.get("decision_id") or ""): row
        for row in dashboard_rows
        if str(row.get("decision_id") or "")
    }
    return [
        row_by_decision_id[decision_id]
        for decision_id in list(portfolio.get("selected_decision_ids") or [])
        if decision_id in row_by_decision_id
    ]


def _active_dashboard_portfolio(portfolios: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not portfolios:
        return None
    current_id = str(st.session_state.get("selected_dashboard_active_portfolio_id") or "")
    selected = _portfolio_by_id(portfolios, current_id) if current_id else None
    selected = selected or portfolios[0]
    st.session_state["selected_dashboard_active_portfolio_id"] = selected.get("portfolio_id")
    return selected


def _strategy_rows_for_active_portfolio(
    portfolio: dict[str, Any] | None,
    dashboard_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if portfolio is None:
        return []
    return [
        _with_portfolio_context(row, portfolio)
        for row in _selected_strategy_rows_for_portfolio(portfolio, dashboard_rows)
    ]


def _slot_blockers_for_row(row: dict[str, Any]) -> list[str]:
    blockers = [str(item) for item in list(row.get("slot_blockers") or []) if str(item)]
    if not _slot_effective_start(row):
        blockers.append("시작 날짜가 필요합니다.")
    if not _slot_effective_end(row):
        blockers.append("종료 날짜 또는 latest market date가 필요합니다.")
    if _slot_effective_capital(row) <= 0:
        blockers.append("투자금 / balance는 0보다 커야 합니다.")
    return blockers


def _strategy_card_html(row: dict[str, Any], index: int) -> str:
    slot = _slot_for_row(row)
    blockers = _slot_blockers_for_row(row)
    start = _slot_effective_start(row) or "-"
    end = "Latest" if bool(slot.get("use_latest_end", True)) else (_slot_effective_end(row) or "-")
    capital = _format_money(_slot_effective_capital(row))
    input_status = "Ready" if not blockers else "Needs Input"
    status_tone = "positive" if not blockers else "warning"
    result = _latest_recheck_result(row)
    result_status = "Stale" if _has_stale_recheck_result(row) else _strategy_result_status(row, result)
    return (
        '<div class="fspd-strategy-card">'
        '<div class="fspd-strategy-card-header">'
        "<div>"
        f'<div class="fspd-strategy-title">{index + 1}. {escape(_clip_text(row.get("source_title") or row.get("decision_id"), limit=120))}</div>'
        f'<div class="fspd-strategy-subtitle">{escape(_clip_text(row.get("decision_id"), limit=120, default="Final Review selected strategy"))}</div>'
        "</div>"
        f'{_chip("Input", input_status, tone=status_tone)}'
        "</div>"
        '<div class="fspd-strategy-meta">'
        f'{_mini_metric("Start", start)}'
        f'{_mini_metric("End", end)}'
        f'{_mini_metric("Balance", capital)}'
        f'{_mini_metric("Scenario", result_status)}'
        "</div>"
        "</div>"
    )


def _portfolio_detail_state_key(portfolio: dict[str, Any]) -> str:
    return f"selected_dashboard_active_strategy_detail_{portfolio.get('portfolio_id')}"


def _clear_portfolio_detail_selection(portfolio: dict[str, Any]) -> None:
    st.session_state.pop(_portfolio_detail_state_key(portfolio), None)


def _with_portfolio_context(row: dict[str, Any], portfolio: dict[str, Any]) -> dict[str, Any]:
    return {
        **row,
        "dashboard_portfolio_id": str(portfolio.get("portfolio_id") or ""),
        "dashboard_portfolio_name": str(portfolio.get("name") or ""),
    }


def _render_my_portfolio_manager(portfolios: list[dict[str, Any]]) -> dict[str, Any] | None:
    st.markdown("#### 2. 나의 포트폴리오")
    current_id = st.session_state.get("selected_dashboard_active_portfolio_id")
    selected_portfolio = _portfolio_by_id(portfolios, current_id) if current_id else None
    show_create = bool(st.session_state.get("selected_dashboard_show_create_portfolio")) or not portfolios

    shelf_count = min(len(portfolios) + 1, 4) or 1
    shelf_cols = st.columns(shelf_count, gap="small")
    with shelf_cols[0]:
        st.markdown(_create_portfolio_card_html(), unsafe_allow_html=True)
        if st.button(
            "+ 새 포트폴리오",
            key="selected_dashboard_open_create_portfolio",
            type="primary" if not portfolios else "secondary",
            width="stretch",
        ):
            st.session_state["selected_dashboard_show_create_portfolio"] = True
            st.rerun()

    for index, portfolio in enumerate(portfolios[: shelf_count - 1], start=1):
        with shelf_cols[index]:
            portfolio_id = str(portfolio.get("portfolio_id") or "")
            is_active = selected_portfolio is not None and str(selected_portfolio.get("portfolio_id") or "") == portfolio_id
            st.markdown(_portfolio_card_html(portfolio, is_active=is_active), unsafe_allow_html=True)
            if st.button(
                "선택됨" if is_active else "선택",
                key=f"selected_dashboard_pick_card_{portfolio_id}",
                disabled=is_active,
                width="stretch",
            ):
                st.session_state["selected_dashboard_active_portfolio_id"] = portfolio_id
                st.rerun()

    if len(portfolios) > shelf_count - 1:
        labels = [selected_dashboard_portfolio_label(portfolio) for portfolio in portfolios]
        default_index = 0
        if selected_portfolio in portfolios:
            default_index = portfolios.index(selected_portfolio)
        selected_label = st.selectbox(
            "More portfolios",
            options=labels,
            index=default_index,
            key="selected_dashboard_portfolio_picker",
        )
        selected_portfolio = portfolios[labels.index(selected_label)]
        st.session_state["selected_dashboard_active_portfolio_id"] = selected_portfolio.get("portfolio_id")

    if show_create:
        with st.container(border=True):
            with st.form("selected_dashboard_create_portfolio_form", clear_on_submit=True):
                cols = st.columns([0.35, 0.47, 0.18], gap="small")
                with cols[0]:
                    name = st.text_input("포트폴리오 이름", placeholder="예: Core ETF 모니터링")
                with cols[1]:
                    description = st.text_input("간단한 설명 / 메모", placeholder="선택 사항")
                with cols[2]:
                    submitted = st.form_submit_button("포트폴리오 저장", type="primary", width="stretch")
                if submitted:
                    try:
                        record = save_selected_dashboard_portfolio(name=name, description=description)
                    except ValueError as exc:
                        st.warning(str(exc))
                    else:
                        st.session_state["selected_dashboard_active_portfolio_id"] = record.get("portfolio_id")
                        st.session_state["selected_dashboard_show_create_portfolio"] = False
                        st.success("포트폴리오를 만들었습니다.")
                        st.rerun()

    if not portfolios:
        st.info("아직 만든 포트폴리오가 없습니다. `+ 새 포트폴리오`에서 먼저 포트폴리오를 저장하세요.")
        return None

    selected_portfolio = _portfolio_by_id(
        portfolios,
        str(st.session_state.get("selected_dashboard_active_portfolio_id") or ""),
    ) or selected_portfolio or portfolios[0]
    st.session_state["selected_dashboard_active_portfolio_id"] = selected_portfolio.get("portfolio_id")

    with st.expander("전체 포트폴리오 목록", expanded=False):
        st.dataframe(build_selected_dashboard_portfolio_table(portfolios), width="stretch", hide_index=True)

    with st.expander("포트폴리오 관리", expanded=False):
        manage_cols = st.columns([0.58, 0.22, 0.20], gap="small")
        with manage_cols[0]:
            st.caption(
                f"`{selected_portfolio.get('name') or '-'}`는 삭제 시 목록에서 숨겨지며, "
                "Final Review 원본 판단 row는 수정하지 않습니다."
            )
        with manage_cols[1]:
            confirm_delete = st.checkbox(
                "삭제 확인",
                key=f"selected_dashboard_confirm_delete_{selected_portfolio.get('portfolio_id')}",
            )
        with manage_cols[2]:
            if st.button(
                "포트폴리오 삭제",
                disabled=not confirm_delete,
                key=f"selected_dashboard_delete_portfolio_{selected_portfolio.get('portfolio_id')}",
                width="stretch",
            ):
                if delete_selected_dashboard_portfolio(str(selected_portfolio.get("portfolio_id") or "")):
                    st.session_state.pop("selected_dashboard_active_portfolio_id", None)
                    st.success("포트폴리오를 삭제했습니다.")
                    st.rerun()
                st.warning("삭제할 포트폴리오를 찾지 못했습니다.")
    return selected_portfolio


def _render_strategy_selection_manager(
    portfolio: dict[str, Any],
    dashboard_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    st.markdown("#### 3. 포트폴리오 상세 / 전략 보드")
    _render_portfolio_command_band(portfolio)
    with st.expander("포트폴리오 이름 / 설명 수정", expanded=False):
        with st.form(f"selected_dashboard_portfolio_edit_form_{portfolio.get('portfolio_id')}"):
            edit_cols = st.columns([0.36, 0.46, 0.18], gap="small")
            with edit_cols[0]:
                portfolio_name = st.text_input(
                    "포트폴리오 이름",
                    value=str(portfolio.get("name") or ""),
                )
            with edit_cols[1]:
                portfolio_description = st.text_input(
                    "포트폴리오 설명",
                    value=str(portfolio.get("description") or ""),
                )
            with edit_cols[2]:
                portfolio_submitted = st.form_submit_button("저장", type="primary", width="stretch")
            if portfolio_submitted:
                try:
                    save_selected_dashboard_portfolio(
                        portfolio_id=str(portfolio.get("portfolio_id") or ""),
                        name=portfolio_name,
                        description=portfolio_description,
                        selected_decision_ids=list(portfolio.get("selected_decision_ids") or []),
                        strategy_slots=list(portfolio.get("strategy_slots") or []),
                    )
                except ValueError as exc:
                    st.warning(str(exc))
                else:
                    st.success("포트폴리오 이름과 설명을 저장했습니다.")
                    st.rerun()
    selected_ids = [str(item) for item in list(portfolio.get("selected_decision_ids") or [])]
    selected_rows = [
        _with_portfolio_context(row, portfolio)
        for row in _selected_strategy_rows_for_portfolio(portfolio, dashboard_rows)
    ]
    st.markdown(
        '<div class="fspd-add-panel">'
        '<div class="fspd-section-label">+ 전략 추가</div>'
        '<div class="fspd-section-help">Final Review selected 후보를 이 포트폴리오의 모니터링 전략 slot으로 추가합니다.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    available_rows = [
        row for row in dashboard_rows if str(row.get("decision_id") or "") not in set(selected_ids)
    ]
    add_cols = st.columns([0.62, 0.16, 0.22], gap="small")
    with add_cols[0]:
        if available_rows:
            add_labels = [final_selected_portfolio_label(row) for row in available_rows]
            add_label = st.selectbox(
                "전략 선택",
                options=add_labels,
                key=f"selected_dashboard_add_strategy_{portfolio.get('portfolio_id')}",
            )
            add_row = available_rows[add_labels.index(add_label)]
        else:
            add_row = None
            st.selectbox(
                "전략 선택",
                options=["Final Review selected 후보 없음"],
                disabled=True,
                key=f"selected_dashboard_add_strategy_empty_{portfolio.get('portfolio_id')}",
            )
    with add_cols[1]:
        add_capital = st.number_input(
            "Balance",
            min_value=1_000.0,
            value=10_000.0,
            step=1_000.0,
            key=f"selected_dashboard_add_strategy_capital_{portfolio.get('portfolio_id')}",
            disabled=add_row is None,
        )
    with add_cols[2]:
        if st.button(
            "+ 전략 추가",
            disabled=add_row is None,
            key=f"selected_dashboard_add_strategy_button_{portfolio.get('portfolio_id')}",
            type="primary",
            width="stretch",
        ):
            defaults = _recheck_defaults(add_row or {})
            result = add_selected_dashboard_portfolio_strategy(
                str(portfolio.get("portfolio_id") or ""),
                str(add_row.get("decision_id") or ""),
                start=str(defaults.get("default_start") or defaults.get("baseline_start") or ""),
                use_latest_end=True,
                initial_capital=float(add_capital),
            )
            if result.get("status") == "added":
                _clear_portfolio_detail_selection(portfolio)
                st.success("전략을 추가했습니다.")
                st.rerun()
            elif result.get("status") == "duplicate":
                st.info("이미 추가된 전략입니다.")
            else:
                st.warning(str(result.get("message") or "전략을 추가하지 못했습니다."))
    if not dashboard_rows:
        st.info("Final Review에서 모니터링 후보 선정이 필요합니다.")
    elif not available_rows:
        st.caption("현재 포트폴리오에 추가 가능한 selected 후보가 없습니다.")
    with st.expander("Final Review selected 후보 풀", expanded=False):
        pool_df = build_selected_dashboard_strategy_pool_table(
            dashboard_rows,
            selected_decision_ids=selected_ids,
        )
        if pool_df.empty:
            st.info("Final Review selected 후보가 없습니다.")
        else:
            st.dataframe(pool_df, width="stretch", hide_index=True)

    if selected_rows:
        st.markdown("##### 전략 보드")
        st.caption("각 전략은 이 포트폴리오의 독립 slot입니다. 설정을 적용하면 기존 scenario 결과는 다시 실행해야 최신 상태가 됩니다.")
        with st.expander("전략 설정 테이블", expanded=False):
            st.dataframe(build_selected_dashboard_portfolio_strategy_table(selected_rows), width="stretch", hide_index=True)
        for index, row in enumerate(selected_rows):
            decision_id = str(row.get("decision_id") or f"decision_{index}")
            slot = _slot_for_row(row)
            defaults = _recheck_defaults(row)
            default_start = _coerce_date(slot.get("start") or defaults.get("default_start"), date(2024, 1, 1))
            default_end = _coerce_date(slot.get("end") or defaults.get("default_end"), date.today())
            use_latest_end_default = bool(slot.get("use_latest_end", True))
            st.markdown(_strategy_card_html(row, index), unsafe_allow_html=True)
            with st.expander(f"설정 편집 / 삭제 - {row.get('source_title') or decision_id}", expanded=False):
                blockers = _slot_blockers_for_row(row)
                if blockers:
                    st.warning(" / ".join(blockers))
                with st.form(f"selected_dashboard_strategy_slot_form_{portfolio.get('portfolio_id')}_{decision_id}"):
                    form_cols = st.columns([0.20, 0.20, 0.18, 0.27, 0.15], gap="small")
                    with form_cols[0]:
                        start_value = st.date_input("시작 날짜", value=default_start)
                    with form_cols[1]:
                        use_latest_end_value = st.checkbox("latest 사용", value=use_latest_end_default)
                        end_value = st.date_input("종료 날짜", value=default_end, disabled=use_latest_end_value)
                    with form_cols[2]:
                        capital_value = st.number_input(
                            "투자금 / balance",
                            min_value=1_000.0,
                            value=float(slot.get("initial_capital") or 10_000.0),
                            step=1_000.0,
                        )
                    with form_cols[3]:
                        memo_value = st.text_input("optional memo", value=str(slot.get("memo") or ""))
                    with form_cols[4]:
                        apply_clicked = st.form_submit_button("전략 적용", type="primary", width="stretch")
                        delete_clicked = st.form_submit_button("전략 삭제", width="stretch")
                    if apply_clicked:
                        result = update_selected_dashboard_portfolio_strategy_slot(
                            str(portfolio.get("portfolio_id") or ""),
                            decision_id,
                            start=str(start_value),
                            end="" if use_latest_end_value else str(end_value),
                            use_latest_end=bool(use_latest_end_value),
                            initial_capital=float(capital_value),
                            memo=memo_value,
                        )
                        if result.get("status") == "updated":
                            _clear_recheck_result(row)
                            _clear_portfolio_detail_selection(portfolio)
                            st.success("전략 설정을 저장했습니다.")
                            st.rerun()
                        st.warning(str(result.get("message") or "전략 설정을 저장하지 못했습니다."))
                    if delete_clicked:
                        result = remove_selected_dashboard_portfolio_strategy(
                            str(portfolio.get("portfolio_id") or ""),
                            decision_id,
                        )
                        if result.get("status") == "removed":
                            _clear_recheck_result(row)
                            _clear_portfolio_detail_selection(portfolio)
                            st.success("전략을 제거했습니다.")
                            st.rerun()
                        st.warning(str(result.get("message") or "전략을 제거하지 못했습니다."))
    else:
        st.info("현재 포트폴리오에 담긴 전략이 없습니다. Final Review selected 후보를 하나씩 추가하세요.")
    return selected_rows


def _portfolio_curve_from_results(results: list[dict[str, Any]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for index, result in enumerate(results):
        result_df = result.get("portfolio_result_df")
        if not isinstance(result_df, pd.DataFrame) or result_df.empty:
            continue
        frame = result_df[["Date", "Total Balance"]].copy()
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
        frame = frame.dropna(subset=["Date"])
        if frame.empty:
            continue
        frame = frame.rename(columns={"Total Balance": f"strategy_{index + 1}"})
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    combined = frames[0]
    for frame in frames[1:]:
        combined = combined.merge(frame, on="Date", how="outer")
    combined = combined.sort_values("Date").ffill().dropna(how="all", subset=[column for column in combined.columns if column != "Date"])
    value_columns = [column for column in combined.columns if column != "Date"]
    combined["Portfolio Value"] = combined[value_columns].sum(axis=1)
    first_value = float(combined["Portfolio Value"].iloc[0] or 0.0)
    combined["Total Return"] = (combined["Portfolio Value"] / first_value - 1.0) if first_value > 0 else 0.0
    return combined[["Date", "Portfolio Value", "Total Return"]]


def _portfolio_summary_from_results(strategy_rows: list[dict[str, Any]]) -> dict[str, Any]:
    results = [
        _latest_recheck_result(row)
        for row in strategy_rows
        if _latest_recheck_result(row).get("status") in {"ok", "partial"}
    ]
    configured_capital = sum(_slot_effective_capital(row) for row in strategy_rows)
    invested = sum(float(result.get("initial_capital") or 0.0) for result in results)
    current_value = sum(float(dict(result.get("portfolio_summary") or {}).get("end_balance") or 0.0) for result in results)
    profit = current_value - invested
    total_return = profit / invested if invested > 0 else None
    curve = _portfolio_curve_from_results(results)
    cagr = None
    mdd = None
    as_of = "-"
    if not curve.empty:
        start_value = float(curve["Portfolio Value"].iloc[0] or 0.0)
        end_value = float(curve["Portfolio Value"].iloc[-1] or 0.0)
        start_date = pd.to_datetime(curve["Date"].iloc[0], errors="coerce")
        end_date = pd.to_datetime(curve["Date"].iloc[-1], errors="coerce")
        as_of = end_date.strftime("%Y-%m-%d") if not pd.isna(end_date) else "-"
        if start_value > 0 and end_value > 0 and not pd.isna(start_date) and not pd.isna(end_date):
            years = max((end_date - start_date).days / 365.25, 1 / 365.25)
            cagr = (end_value / start_value) ** (1 / years) - 1
        running_peak = curve["Portfolio Value"].cummax()
        drawdown = curve["Portfolio Value"] / running_peak - 1.0
        mdd = float(drawdown.min()) if not drawdown.empty else None
    benchmark_spreads = [
        dict(result.get("change_summary") or {}).get("net_cagr_spread")
        for result in results
        if dict(result.get("change_summary") or {}).get("net_cagr_spread") is not None
    ]
    benchmark_spread = sum(float(value) for value in benchmark_spreads) / len(benchmark_spreads) if benchmark_spreads else None
    updated_values = [
        str(result.get("dashboard_updated_at") or "")
        for result in results
        if str(result.get("dashboard_updated_at") or "")
    ]
    return {
        "results": results,
        "curve": curve,
        "configured_capital": configured_capital,
        "invested": invested,
        "current_value": current_value,
        "profit": profit,
        "total_return": total_return,
        "cagr": cagr,
        "mdd": mdd,
        "benchmark_spread": benchmark_spread,
        "as_of": as_of,
        "updated_at": max(updated_values) if updated_values else "-",
    }


def _scenario_value(value: Any, *, completed: bool, formatter: str = "money") -> str:
    if not completed:
        return "-"
    if formatter == "pct":
        return _format_pct(value)
    if formatter == "signed_money":
        return _format_signed_money(value)
    return _format_money(value)


def _render_scenario_cockpit(summary: dict[str, Any], *, strategy_count: int) -> None:
    completed = len(summary.get("results") or [])
    all_complete = completed == strategy_count and strategy_count > 0
    partial = 0 < completed < strategy_count
    primary_status = "전체 집계 완료" if all_complete else ("부분 집계" if partial else "실행 전")
    primary_detail = (
        "선택된 포트폴리오 전체 strategy slot의 scenario 결과를 balance 기준으로 합산합니다."
        if not partial
        else "일부 전략만 실행되어 현재 값은 포트폴리오 전체가 아닌 부분 집계입니다."
    )
    completed_flag = completed > 0
    cagr_mdd_value = (
        f"{_scenario_value(summary.get('cagr'), completed=completed_flag, formatter='pct')} / "
        f"{_scenario_value(summary.get('mdd'), completed=completed_flag, formatter='pct')}"
    )
    html = (
        '<div class="fspd-scenario-cockpit">'
        '<div class="fspd-scenario-primary">'
        '<span>Portfolio-wide Monitoring Scenario</span>'
        f"<strong>{escape(primary_status)}</strong>"
        f"<p>{escape(primary_detail)}</p>"
        "</div>"
        '<div class="fspd-scenario-metrics">'
        f'{_mini_metric("실행 상태", f"{completed}/{strategy_count}")}'
        f'{_mini_metric("설정 투자금", _format_money(summary.get("configured_capital")))}'
        f'{_mini_metric("평가 금액", _scenario_value(summary.get("current_value"), completed=completed_flag))}'
        f'{_mini_metric("손익", _scenario_value(summary.get("profit"), completed=completed_flag, formatter="signed_money"))}'
        f'{_mini_metric("총 수익률", _scenario_value(summary.get("total_return"), completed=completed_flag, formatter="pct"))}'
        f'{_mini_metric("CAGR / MDD", cagr_mdd_value)}'
        f'{_mini_metric("기준일", summary.get("as_of") or "-")}'
        f'{_mini_metric("마지막 업데이트", summary.get("updated_at") or "-")}'
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
    if completed == 0:
        st.info("이 영역은 포트폴리오 전체 성과를 보여줍니다. 아래 전략 보드의 `포트폴리오 시나리오 업데이트`를 누르면 합산 결과가 채워집니다.")
    elif partial:
        st.warning("일부 전략만 실행된 부분 집계입니다. 전체 포트폴리오 성과로 보려면 남은 전략도 실행하세요.")


def _render_strategy_performance_board(strategy_rows: list[dict[str, Any]]) -> None:
    rows: list[str] = []
    for row in strategy_rows:
        result = _latest_recheck_result(row)
        summary = dict(result.get("portfolio_summary") or {})
        status = _strategy_result_status(row, result)
        rows.append(
            '<div class="fspd-performance-row">'
            "<div>"
            f'<div class="fspd-row-title">{escape(_clip_text(row.get("source_title") or row.get("decision_id"), limit=90))}</div>'
            f'<div class="fspd-row-sub">{escape(status)}</div>'
            "</div>"
            f'{_mini_metric("Invested", _format_money(result.get("initial_capital") or row.get("slot_initial_capital")))}'
            f'{_mini_metric("Value", _format_money(summary.get("end_balance")))}'
            f'{_mini_metric("Return", _format_pct(summary.get("total_return")))}'
            f'{_mini_metric("MDD", _format_pct(summary.get("mdd")))}'
            "</div>"
        )
    st.markdown(f'<div class="fspd-performance-board">{"".join(rows)}</div>', unsafe_allow_html=True)


def _run_strategy_recheck(row: dict[str, Any]) -> dict[str, Any]:
    result = build_selected_portfolio_performance_recheck(
        row,
        start=_slot_effective_start(row),
        end=_slot_effective_end(row),
        initial_capital=float(_slot_effective_capital(row)),
    )
    result = dict(result or {})
    result["dashboard_input_signature"] = _scenario_input_signature(row)
    result["dashboard_result_key"] = _decision_key(row)
    result["dashboard_updated_at"] = _session_timestamp()
    st.session_state[f"selected_portfolio_recheck_result_{_decision_key(row)}"] = result
    return result


def _strategy_result_status(row: dict[str, Any], result: dict[str, Any]) -> str:
    if not row.get("slot_input_complete"):
        return "Review Needed"
    if not result:
        return "Not Run"
    if result.get("status") == "error":
        return "Error"
    if result.get("status") == "partial":
        return "Review Needed"
    route = str(result.get("verdict_route") or "")
    if route == "SELECTION_THESIS_HOLDS":
        return "Good"
    if route in {"PERFORMANCE_WEAKENED", "RISK_DRAWDOWN_EXPANDED"}:
        return "Watch"
    return "Review Needed"


def _build_strategy_performance_table(strategy_rows: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in strategy_rows:
        result = _latest_recheck_result(row)
        summary = dict(result.get("portfolio_summary") or {})
        change = dict(result.get("change_summary") or {})
        invested = result.get("initial_capital") or row.get("slot_initial_capital")
        current_value = summary.get("end_balance")
        profit = None
        if invested is not None and current_value is not None:
            profit = float(current_value) - float(invested)
        rows.append(
            {
                "Strategy": row.get("source_title"),
                "Invested": _format_money(invested),
                "Current Value": _format_money(current_value),
                "P/L": _format_signed_money(profit),
                "Return": _format_pct(summary.get("total_return")),
                "CAGR": _format_pct(summary.get("cagr")),
                "MDD": _format_pct(summary.get("mdd")),
                "Benchmark Spread": _format_pct(change.get("net_cagr_spread")),
                "Status": _strategy_result_status(row, result),
            }
        )
    return pd.DataFrame(rows)


def _next_month_end(value: Any, interval: int = 1) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "-"
    base_month_end = parsed.to_period("M").to_timestamp("M")
    return (base_month_end + pd.offsets.MonthEnd(max(int(interval or 1), 1))).strftime("%Y-%m-%d")


def _build_rebalance_table(strategy_rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in strategy_rows:
        raw_decision = dict(row.get("raw_decision") or {})
        for component in list(raw_decision.get("selected_components") or []):
            component_row = dict(component or {})
            history = [dict(item or {}) for item in list(component_row.get("selection_history") or [])]
            latest = history[-1] if history else {}
            replay_contract = dict(component_row.get("replay_contract") or {})
            settings = dict(replay_contract.get("settings_snapshot") or {})
            interval = int(settings.get("rebalance_interval") or settings.get("interval") or 1)
            tickers = [str(item) for item in list(latest.get("selected_tickers") or []) if str(item)]
            weights = list(latest.get("target_weights") or [])
            allocation_parts = []
            for index, ticker in enumerate(tickers):
                weight = weights[index] if index < len(weights) else None
                if weight is None:
                    allocation_parts.append(ticker)
                else:
                    allocation_parts.append(f"{ticker} {float(weight):.1%}")
            cash_share = latest.get("cash_share")
            if cash_share is not None and float(cash_share or 0.0) > 0:
                allocation_parts.append(f"Cash / defensive {float(cash_share):.1%}")
            display_rows.append(
                {
                    "Strategy": row.get("source_title"),
                    "Component": component_row.get("title") or component_row.get("strategy_name") or "-",
                    "Target Snapshot Date": latest.get("date") or component_row.get("period_end") or "-",
                    "Next Review Date": _next_month_end(latest.get("date") or component_row.get("period_end"), interval=interval),
                    "Current Target Snapshot": ", ".join(allocation_parts) or "-",
                    "Target Meaning": "Target weights from the latest monitoring scenario; recomputed only during manual review.",
                    "Execution Boundary": "No order, account sync, or auto rebalance.",
                    "Cash / Defensive Sleeve": (
                        f"{float(cash_share):.1%}" if cash_share is not None else ("BIL / cash ticker" if "BIL" in tickers else "-")
                    ),
                }
            )
    return pd.DataFrame(display_rows)


def _latest_rebalance_summary(strategy_rows: list[dict[str, Any]]) -> dict[str, str]:
    rebalance_df = _build_rebalance_table(strategy_rows)
    if rebalance_df.empty:
        return {"next_rebalance": "-", "current_target_assets": "-"}
    first = dict(rebalance_df.iloc[0].to_dict())
    return {
        "next_rebalance": str(first.get("Next Rebalance") or "-"),
        "current_target_assets": str(first.get("Current Target Assets") or "-"),
    }


def _strategy_open_issue_count(strategy_rows: list[dict[str, Any]]) -> int:
    total = 0
    for row in strategy_rows:
        raw_decision = dict(row.get("raw_decision") or {})
        total += len([item for item in list(row.get("open_review_items") or raw_decision.get("open_review_items") or []) if item])
        total += len([item for item in list(row.get("blockers") or []) if item])
    return total


def _monitoring_status(summary: dict[str, Any], strategy_rows: list[dict[str, Any]]) -> tuple[str, str]:
    if not strategy_rows:
        return ("설정 필요", "warning")
    runnable_rows = [row for row in strategy_rows if not _slot_blockers_for_row(row)]
    completed = len(summary.get("results") or [])
    if len(runnable_rows) < len(strategy_rows):
        return ("설정 보강", "warning")
    if completed == 0:
        return ("실행 대기", "warning")
    if completed < len(strategy_rows):
        return ("부분 집계", "warning")
    if any(_strategy_result_status(row, _latest_recheck_result(row)) != "Good" for row in strategy_rows):
        return ("Watch", "warning")
    return ("Clear", "positive")


def _render_monitoring_daily_badges(summary: dict[str, Any], strategy_rows: list[dict[str, Any]]) -> None:
    status_label, status_tone = _monitoring_status(summary, strategy_rows)
    rebalance = _latest_rebalance_summary(strategy_rows)
    open_issue_count = _strategy_open_issue_count(strategy_rows)
    render_badge_strip(
        [
            {"label": "Status", "value": status_label, "tone": status_tone},
            {"label": "Next Rebalance", "value": rebalance.get("next_rebalance"), "tone": "neutral"},
            {
                "label": "Open Issues",
                "value": open_issue_count,
                "tone": "warning" if open_issue_count else "positive",
            },
            {"label": "Provider Freshness", "value": "하단 상세 점검", "tone": "neutral"},
            {"label": "Scenario Updated", "value": summary.get("updated_at") or "-", "tone": "neutral"},
            {"label": "Current Target", "value": _clip_text(rebalance.get("current_target_assets"), limit=72), "tone": "neutral"},
        ]
    )


def _render_portfolio_monitoring_overview(strategy_rows: list[dict[str, Any]]) -> None:
    summary = _portfolio_summary_from_results(strategy_rows)
    completed = len(summary["results"])
    runnable_rows = [row for row in strategy_rows if not _slot_blockers_for_row(row)]
    _render_monitoring_daily_badges(summary, strategy_rows)
    _render_scenario_cockpit(summary, strategy_count=len(strategy_rows))
    if len(runnable_rows) < len(strategy_rows):
        st.warning(f"{len(strategy_rows) - len(runnable_rows)}개 전략은 시작일 / 종료일 / balance 설정 보강이 필요합니다.")
    curve = summary.get("curve")
    if isinstance(curve, pd.DataFrame) and not curve.empty:
        chart_view = curve[["Date", "Portfolio Value"]].copy()
        chart_view["Date"] = pd.to_datetime(chart_view["Date"], errors="coerce")
        chart_view = chart_view.dropna(subset=["Date"]).set_index("Date")
        st.line_chart(chart_view)
    st.markdown("##### 전략별 성과")
    _render_strategy_performance_board(strategy_rows)
    with st.expander("전략별 성과 테이블", expanded=False):
        st.dataframe(_build_strategy_performance_table(strategy_rows), width="stretch", hide_index=True)
    with st.expander("Target Snapshot / Review Schedule", expanded=completed > 0):
        st.info(
            "`Target Snapshot Date`는 마지막 monitoring scenario가 산출한 목표 비중 기준일입니다. "
            "`Next Review Date`는 다음 수동 재계산 예정일이며, 표의 `Current Target Snapshot`은 주문 지시나 자동 리밸런싱 명령이 아닙니다."
        )
        rebalance_df = _build_rebalance_table(strategy_rows)
        if rebalance_df.empty:
            st.info("표시할 target snapshot / review schedule 정보가 없습니다.")
        else:
            st.dataframe(rebalance_df, width="stretch", hide_index=True)


def _portfolio_update_blockers(strategy_rows: list[dict[str, Any]]) -> list[str]:
    if not strategy_rows:
        return ["선택된 포트폴리오에 전략이 없습니다."]
    blockers: list[str] = []
    decision_ids = [str(row.get("decision_id") or "").strip() for row in strategy_rows]
    if any(not decision_id for decision_id in decision_ids):
        blockers.append("selected decision이 연결되지 않은 strategy slot이 있습니다.")
    duplicate_ids = sorted({decision_id for decision_id in decision_ids if decision_id and decision_ids.count(decision_id) > 1})
    if duplicate_ids:
        blockers.append(f"같은 selected decision이 중복되어 있습니다: {', '.join(duplicate_ids)}")
    for index, row in enumerate(strategy_rows, start=1):
        for blocker in _slot_blockers_for_row(row):
            title = _clip_text(row.get("source_title") or row.get("decision_id"), limit=64)
            blockers.append(f"{index}. {title}: {blocker}")
    return blockers


def _render_portfolio_scenario_update_controls(strategy_rows: list[dict[str, Any]]) -> None:
    st.markdown("##### 포트폴리오 시나리오 업데이트")
    st.caption(
        "전략 slot 구성을 확인한 뒤 실행합니다. 이미 현재 설정으로 실행된 전략은 재사용하고, 미실행 / stale 전략만 업데이트합니다."
    )
    runnable_rows = [row for row in strategy_rows if not _slot_blockers_for_row(row)]
    pending_rows = [row for row in runnable_rows if not _latest_recheck_result(row)]
    blockers = _portfolio_update_blockers(strategy_rows)
    force_refresh = st.checkbox(
        "전체 재실행",
        value=False,
        key="selected_dashboard_force_portfolio_scenarios",
        help="켜면 이미 최신 결과가 있는 전략까지 다시 실행합니다.",
    )
    rows_to_run = runnable_rows if force_refresh else pending_rows
    update_cols = st.columns([0.66, 0.34], gap="small")
    with update_cols[0]:
        if blockers:
            with st.expander("업데이트 제외 / 보강 이유", expanded=not runnable_rows):
                for blocker in blockers:
                    st.warning(blocker)
        elif runnable_rows and not rows_to_run:
            st.success("현재 설정 기준으로 모든 실행 결과가 최신입니다. 다시 계산하려면 `전체 재실행`을 켜세요.")
        elif pending_rows:
            st.info(f"업데이트 필요: {len(pending_rows)}개 / 최신 결과 재사용: {len(runnable_rows) - len(pending_rows)}개")
    with update_cols[1]:
        if st.button(
            "포트폴리오 시나리오 업데이트",
            key="selected_dashboard_run_portfolio_scenarios",
            type="primary",
            disabled=not rows_to_run,
            width="stretch",
        ):
            progress = st.progress(0.0)
            status = st.empty()
            with st.spinner("포트폴리오 전략 시나리오를 순서대로 실행하는 중입니다...", show_time=True):
                for index, row in enumerate(rows_to_run, start=1):
                    status.caption(
                        f"{index}/{len(rows_to_run)} 실행 중 - {row.get('source_title') or row.get('decision_id') or '-'}"
                    )
                    _run_strategy_recheck(row)
                    progress.progress(index / len(rows_to_run))
            status.empty()
            progress.empty()
            st.success(f"{len(rows_to_run)}개 전략 시나리오를 업데이트했습니다. 상단 모니터링 요약이 갱신되었습니다.")
            st.rerun()


def _render_active_monitoring_scenario(
    portfolio: dict[str, Any] | None,
    strategy_rows: list[dict[str, Any]],
) -> None:
    st.markdown("#### 1. Active Portfolio Monitoring Scenario")
    if portfolio is None:
        with st.container(border=True):
            st.info("아직 모니터링 포트폴리오가 없습니다. 아래에서 `+ 새 포트폴리오`를 만들어 시작하세요.")
        return

    _render_portfolio_command_band(portfolio)
    if not strategy_rows:
        summary = _portfolio_summary_from_results([])
        _render_monitoring_daily_badges(summary, [])
        _render_scenario_cockpit(summary, strategy_count=0)
        st.info("선택된 포트폴리오에 전략이 없습니다. 아래 전략 보드에서 Final Review selected 후보를 추가하세요.")
        return

    if not any(_latest_recheck_result(row) for row in strategy_rows):
        st.info("전략 구성이 완료되었습니다. 아래의 포트폴리오 시나리오 업데이트를 눌러 모니터링 결과를 계산하세요.")
    _render_portfolio_monitoring_overview(strategy_rows)


def _render_portfolio_strategy_comparison(strategy_rows: list[dict[str, Any]]) -> None:
    st.markdown("#### 5. 전환 비교")
    st.caption(
        "같은 포트폴리오 안에 담긴 selected 전략의 최신 monitoring scenario 결과를 비교합니다. "
        "결과가 없는 전략은 먼저 모니터 시나리오를 실행해야 합니다."
    )
    if len(strategy_rows) < 2:
        st.info("전환 비교는 같은 포트폴리오에 selected 전략이 2개 이상 있을 때 표시됩니다.")
        return
    results_by_decision_id = {
        str(row.get("decision_id") or ""): _latest_recheck_result(row)
        for row in strategy_rows
    }
    comparison_df = build_selected_dashboard_portfolio_strategy_comparison_table(
        strategy_rows,
        recheck_results_by_decision_id=results_by_decision_id,
    )
    st.dataframe(comparison_df, width="stretch", hide_index=True)
    ready_count = sum(1 for result in results_by_decision_id.values() if result.get("status") in {"ok", "partial"})
    render_badge_strip(
        [
            {"label": "Strategies", "value": len(strategy_rows), "tone": "neutral"},
            {
                "label": "Scenario Results",
                "value": f"{ready_count}/{len(strategy_rows)}",
                "tone": "positive" if ready_count == len(strategy_rows) else "warning",
            },
            {"label": "Auto Switch", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )


def _render_selected_strategy_detail(portfolio: dict[str, Any], strategy_rows: list[dict[str, Any]]) -> None:
    st.markdown("#### 4. 상세 점검")
    st.caption(
        "Streamlit 탭은 숨겨진 탭도 모두 계산하므로, 여기서는 선택한 전략 1개만 상세 근거를 엽니다. "
        "전략 추가 / 설정 변경만으로는 이 상세 재검증이 자동 실행되지 않습니다."
    )
    if not strategy_rows:
        st.info("상세 확인할 전략이 없습니다.")
        return

    labels = [
        f"{index + 1}. {_clip_text(row.get('source_title') or row.get('decision_id'), limit=70)}"
        for index, row in enumerate(strategy_rows)
    ]
    picker_cols = st.columns([0.68, 0.32], gap="small")
    with picker_cols[0]:
        selected_label = st.selectbox(
            "상세 확인할 전략",
            options=labels,
            key=f"selected_dashboard_strategy_detail_picker_{portfolio.get('portfolio_id')}",
        )
    selected_row = strategy_rows[labels.index(selected_label)]
    with picker_cols[1]:
        if st.button(
            "선택 전략 상세 열기",
            key=f"selected_dashboard_open_strategy_detail_{portfolio.get('portfolio_id')}",
            width="stretch",
        ):
            st.session_state[_portfolio_detail_state_key(portfolio)] = _decision_key(selected_row)

    active_key = str(st.session_state.get(_portfolio_detail_state_key(portfolio)) or "")
    active_row = next((row for row in strategy_rows if _decision_key(row) == active_key), None)
    if active_row is None:
        st.info("상단 요약만 보고 있다면 여기서 멈춰도 됩니다. 개별 evidence가 필요할 때만 전략을 선택하고 상세를 여세요.")
        return

    if _has_stale_recheck_result(active_row):
        st.warning("이 전략의 이전 scenario 결과는 현재 시작일 / 종료일 / balance 설정과 달라서 stale로 처리했습니다. 다시 실행하면 최신 결과로 갱신됩니다.")

    _render_snapshot(active_row)
    operations_evidence = _render_performance_recheck(active_row)
    _render_operator_context(active_row, operations_evidence=operations_evidence)
    _render_decision_dossier(active_row)


def _render_dashboard_portfolio_workspace(
    *,
    dashboard_rows: list[dict[str, Any]],
    monitoring_portfolios: list[dict[str, Any]],
) -> None:
    _inject_dashboard_product_styles()
    state = build_selected_dashboard_portfolio_state(
        portfolios=monitoring_portfolios,
        dashboard_rows=dashboard_rows,
    )
    metrics = dict(state.get("metrics") or {})
    render_badge_strip(
        [
            {"label": "My Portfolios", "value": metrics.get("portfolio_count", 0), "tone": "neutral"},
            {"label": "Selected Pool", "value": metrics.get("selected_strategy_pool_count", 0), "tone": "neutral"},
            {
                "label": "Assigned",
                "value": metrics.get("assigned_strategy_reference_count", 0),
                "tone": "positive" if metrics.get("assigned_strategy_reference_count") else "neutral",
            },
            {
                "label": "Missing Ref",
                "value": metrics.get("missing_reference_count", 0),
                "tone": "warning" if metrics.get("missing_reference_count") else "neutral",
            },
            {"label": "Trading", "value": "Disabled", "tone": "neutral"},
        ]
    )
    portfolios = list(state.get("portfolios") or [])
    active_portfolio = _active_dashboard_portfolio(portfolios)
    active_rows = _strategy_rows_for_active_portfolio(active_portfolio, dashboard_rows)
    _render_active_monitoring_scenario(active_portfolio, active_rows)

    portfolio = _render_my_portfolio_manager(portfolios)
    if portfolio is None:
        return
    selected_rows = _render_strategy_selection_manager(portfolio, dashboard_rows)
    _render_portfolio_scenario_update_controls(selected_rows)
    if not selected_rows:
        return
    _render_selected_strategy_detail(portfolio, selected_rows)
    _render_portfolio_strategy_comparison(selected_rows)


def _render_selected_row_detail(row: dict[str, Any]) -> None:
    _render_snapshot(row)
    operations_evidence = _render_performance_recheck(row)
    _render_operator_context(row, operations_evidence=operations_evidence)
    _render_decision_dossier(row)

    with st.expander("Audit / Developer Details", expanded=False):
        st.caption("데이터 출처, 화면 경계, 원본 저장 row 구조를 확인할 때만 펼쳐 봅니다.")
        _render_source_boundary(row)
        st.json(row.get("raw_decision") or {})


def _render_source_boundary(row: dict[str, Any] | None = None) -> None:
    cards = [
        {
            "title": "Source",
            "value": "Final Review Decisions",
            "detail": "모니터링 후보 판단 row를 읽습니다.",
            "tone": "neutral",
        },
        {
            "title": "Selected Filter",
            "value": "Practical Portfolio",
            "detail": "SELECT_FOR_PRACTICAL_PORTFOLIO 또는 selected flag만 운영 대상으로 봅니다.",
            "tone": "positive",
        },
        {
            "title": "Write Policy",
            "value": "Read Only",
            "detail": "재검증과 allocation 점검은 새 판단 row나 주문 row를 저장하지 않습니다.",
            "tone": "neutral",
        },
    ]
    if row is not None:
        cards.append(
            {
                "title": "Selected Decision",
                "value": row.get("decision_id") or "-",
                "detail": row.get("source_type") or "-",
                "tone": "neutral",
            }
        )
    _render_info_card_grid(cards, min_width=210)
    st.code(str(FINAL_SELECTION_DECISION_FILE), language="text")


def _decision_key(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("dashboard_portfolio_id") or "portfolio"),
        str(row.get("slot_id") or "slot"),
        str(row.get("decision_id") or "selected_portfolio"),
    ]
    return "::".join(parts)


def _scenario_input_signature(row: dict[str, Any]) -> dict[str, Any]:
    slot = _slot_for_row(row)
    return {
        "decision_id": str(row.get("decision_id") or ""),
        "dashboard_portfolio_id": str(row.get("dashboard_portfolio_id") or ""),
        "slot_id": str(row.get("slot_id") or ""),
        "start": _slot_effective_start(row),
        "end": _slot_effective_end(row),
        "use_latest_end": bool(slot.get("use_latest_end", True)),
        "initial_capital": round(float(_slot_effective_capital(row) or 0.0), 4),
    }


def _stored_recheck_result(row: dict[str, Any]) -> dict[str, Any]:
    return dict(st.session_state.get(f"selected_portfolio_recheck_result_{_decision_key(row)}") or {})


def _result_matches_current_slot(row: dict[str, Any], result: dict[str, Any]) -> bool:
    if not result:
        return False
    signature = result.get("dashboard_input_signature")
    if not signature:
        return False
    return dict(signature) == _scenario_input_signature(row)


def _has_stale_recheck_result(row: dict[str, Any]) -> bool:
    result = _stored_recheck_result(row)
    return bool(result) and not _result_matches_current_slot(row, result)


def _clear_recheck_result(row: dict[str, Any]) -> None:
    st.session_state.pop(f"selected_portfolio_recheck_result_{_decision_key(row)}", None)


def _latest_recheck_result(row: dict[str, Any]) -> dict[str, Any]:
    result = _stored_recheck_result(row)
    if not _result_matches_current_slot(row, result):
        return {}
    return result


def _latest_drift_check(row: dict[str, Any]) -> dict[str, Any]:
    return dict(st.session_state.get(f"selected_portfolio_drift_check_result_{_decision_key(row)}") or {})


def _latest_drift_alert_preview(row: dict[str, Any]) -> dict[str, Any]:
    return dict(st.session_state.get(f"selected_portfolio_drift_alert_result_{_decision_key(row)}") or {})


def _latest_monitoring_timeline(row: dict[str, Any]) -> dict[str, Any]:
    return build_selected_portfolio_monitoring_timeline(
        row,
        recheck_result=_latest_recheck_result(row),
        drift_check=_latest_drift_check(row),
        alert_preview=_latest_drift_alert_preview(row),
    )


def _render_snapshot(row: dict[str, Any]) -> None:
    st.markdown("#### Snapshot")
    component_df = build_selected_portfolio_component_table(row)
    component_count = int(row.get("component_count") or 0)
    target_detail = f"{component_count} component"
    if component_count == 1 and not component_df.empty:
        target_detail = str(component_df.iloc[0].get("Title") or target_detail)
    _render_info_card_grid(
        [
            {
                "title": "Selection Status",
                "value": row.get("operation_status_label"),
                "detail": row.get("status_reason"),
                "tone": _status_tone(str(row.get("operation_status") or "")),
            },
            {
                "title": "Original Test Period",
                "value": f"{row.get('baseline_start') or '-'} -> {row.get('baseline_end') or '-'}",
                "detail": "Final Review에서 선정할 때 확인된 기준 기간",
                "tone": "neutral",
            },
            {
                "title": "Baseline CAGR",
                "value": _format_pct(row.get("baseline_cagr")),
                "detail": f"Benchmark {row.get('benchmark_label') or '-'}",
                "tone": "positive",
            },
            {
                "title": "Baseline MDD",
                "value": _format_pct(row.get("baseline_mdd")),
                "detail": "선정 당시 최대 낙폭 기준",
                "tone": "warning",
            },
            {
                "title": "Target Allocation",
                "value": f"{float(row.get('target_weight_total') or 0.0):.1f}%",
                "detail": target_detail,
                "tone": "neutral",
            },
        ],
        min_width=180,
    )
    with st.expander("Identity / Source", expanded=False):
        st.markdown(f"**Decision ID**  \n`{row.get('decision_id') or '-'}`")
        st.markdown(f"**Source**  \n`{row.get('source_type') or '-'}` / `{row.get('source_id') or '-'}`")
        st.markdown(f"**Title**  \n{row.get('source_title') or '-'}")
    if component_df.empty:
        st.warning("선택된 포트폴리오에 active component가 없습니다.")
    elif component_count > 1:
        st.markdown("##### Target Allocation")
        st.caption("Final Review에서 확정된 component와 목표 비중입니다. 실제 또는 가상 보유금액 점검은 Portfolio Monitoring의 Actual Allocation에서 확인합니다.")
        st.dataframe(component_df, width="stretch", hide_index=True)
    else:
        with st.expander("Target allocation details", expanded=False):
            st.caption("단일 component 100% 포트폴리오라 기본 화면에서는 Snapshot 카드로 요약합니다.")
            st.dataframe(component_df, width="stretch", hide_index=True)


def _render_operator_context(row: dict[str, Any], *, operations_evidence: dict[str, Any] | None = None) -> None:
    st.markdown("#### 4. Monitoring Signals")
    st.caption(
        "모니터 시나리오 이후 이 전략을 계속 관찰할지, evidence 보강이 필요한지, 대체 검토가 필요한지 확인합니다. "
        "Deployment / Live 판단은 마지막 optional preflight에서만 보조로 봅니다."
    )
    triggers = [str(trigger) for trigger in list(row.get("review_triggers") or []) if str(trigger)]
    blockers = [str(blocker) for blocker in list(row.get("blockers") or []) if str(blocker)]
    operations = dict(operations_evidence or {})
    _render_info_card_grid(
        [
            {
                "title": "Signal Timeline",
                "value": "Read Only",
                "detail": "선정, 재검증, drift, trigger preview를 시간순으로 확인",
                "tone": "neutral",
            },
            {
                "title": "Review Signals",
                "value": "Latest Check",
                "detail": "계속 관찰 / 보강 필요 / 대체 검토로 번역",
                "tone": "neutral",
            },
            {
                "title": "Open Issues",
                "value": "Follow-up",
                "detail": "Final Review의 약점과 trigger를 계속 관찰",
                "tone": "neutral",
            },
            {
                "title": "Why Selected",
                "value": row.get("evidence_route"),
                "detail": "Final Review에서 이 포트폴리오를 통과시킨 근거",
                "tone": "positive" if not blockers else "warning",
            },
            {
                "title": "Actual Allocation",
                "value": "Optional",
                "detail": "실제 또는 가상 보유금액을 target allocation과 비교할 때만 사용",
                "tone": "neutral",
            },
            {
                "title": "Optional Preflight",
                "value": "Read Only",
                "detail": "Live / Deployment는 마지막 보조 확인",
                "tone": "neutral",
            },
        ],
        min_width=190,
    )
    evidence_df = build_selected_portfolio_evidence_table(row)
    continuity_timeline = _latest_monitoring_timeline(row)
    continuity = build_selected_portfolio_continuity_check(row, monitoring_timeline=continuity_timeline)
    continuity_metrics = dict(continuity.get("metrics") or {})
    continuity_route = str(continuity.get("route") or "")
    continuity_source_contract = dict(continuity.get("source_contract") or {})
    with st.container(border=True):
        st.markdown("##### Final Review -> Selected Dashboard Continuity")
        render_badge_strip(
            [
                {
                    "label": "Continuity",
                    "value": continuity.get("route_label"),
                    "tone": _continuity_tone(continuity_route),
                },
                {
                    "label": "Needs Input",
                    "value": continuity_metrics.get("needs_input_count", 0),
                    "tone": "warning" if continuity_metrics.get("needs_input_count") else "neutral",
                },
                {
                    "label": "Review",
                    "value": continuity_metrics.get("review_count", 0),
                    "tone": "warning" if continuity_metrics.get("review_count") else "neutral",
                },
                {
                    "label": "Blocked",
                    "value": continuity_metrics.get("blocked_count", 0),
                    "tone": "danger" if continuity_metrics.get("blocked_count") else "neutral",
                },
                {
                    "label": "Source Contract",
                    "value": "Consistent" if continuity_metrics.get("source_contract_consistent") else "Mismatch",
                    "tone": "positive" if continuity_metrics.get("source_contract_consistent") else "danger",
                },
                {"label": "Auto Save", "value": "Disabled", "tone": "neutral"},
            ]
        )
        if continuity_route == "CONTINUITY_BLOCKED":
            st.warning(str(continuity.get("next_action") or "-"))
        elif continuity_route in {"CONTINUITY_NEEDS_INPUT", "CONTINUITY_REVIEW"}:
            st.info(str(continuity.get("next_action") or "-"))
        else:
            st.success(str(continuity.get("next_action") or "-"))
        with st.expander("Continuity check rows", expanded=continuity_route != "CONTINUITY_READY"):
            st.dataframe(build_selected_portfolio_continuity_table(continuity), width="stretch", hide_index=True)
        with st.expander("Selected decision source contract", expanded=not continuity_metrics.get("source_contract_consistent")):
            st.caption(
                "Continuity, Timeline, Review Signals, and Decision Dossier should read the same Final Decision row. "
                "Session evidence is read-only context, not durable monitoring history."
            )
            st.dataframe(
                build_selected_portfolio_source_contract_table(continuity_source_contract),
                width="stretch",
                hide_index=True,
            )

    open_issue_followup = build_selected_portfolio_open_issue_followup(row)
    review_signal_policy = build_selected_portfolio_review_signal_policy(
        row,
        recheck_result=_latest_recheck_result(row),
        recheck_preflight=dict(operations.get("preflight") or {}),
        provider_evidence=dict(operations.get("provider_evidence") or {}),
        drift_check=_latest_drift_check(row),
    )
    allocation_boundary = build_selected_portfolio_allocation_drift_boundary(
        row,
        drift_check=_latest_drift_check(row),
        alert_preview=_latest_drift_alert_preview(row),
    )
    deployment_preflight = build_selected_portfolio_deployment_readiness_preflight(
        row,
        recheck_preflight=dict(operations.get("preflight") or {}),
        provider_evidence=dict(operations.get("provider_evidence") or {}),
        continuity_check=continuity,
        review_signal_policy=review_signal_policy,
        allocation_boundary=allocation_boundary,
    )

    trigger_tab, timeline_tab, issue_tab, evidence_tab, allocation_tab, preflight_tab, audit_tab = st.tabs(
        [
            "Review Signals",
            "Timeline",
            "Open Issues",
            "Why Selected",
            "Actual Allocation",
            "Optional Preflight",
            "Audit",
        ]
    )
    with timeline_tab:
        st.caption(
            "Final Review 모니터링 후보 선정 후 현재 화면에서 확인한 신호를 시간순으로 읽습니다. "
            "이 timeline은 monitoring log를 자동 저장하지 않습니다."
        )
        timeline = continuity_timeline
        metrics = dict(timeline.get("metrics") or {})
        boundary = dict(timeline.get("execution_boundary") or {})
        render_badge_strip(
            [
                {
                    "label": "Timeline",
                    "value": timeline.get("timeline_label"),
                    "tone": _review_trigger_tone(str(timeline.get("timeline_status") or "")),
                },
                {"label": "Rows", "value": metrics.get("row_count", 0), "tone": "neutral"},
                {
                    "label": "Needs Input",
                    "value": metrics.get("needs_input_count", 0),
                    "tone": "warning" if metrics.get("needs_input_count") else "neutral",
                },
                {
                    "label": "Breached",
                    "value": metrics.get("breached_count", 0),
                    "tone": "danger" if metrics.get("breached_count") else "neutral",
                },
                {"label": "Auto Save", "value": "Disabled", "tone": "neutral"},
            ]
        )
        status = str(timeline.get("timeline_status") or "")
        conclusion = str(timeline.get("conclusion") or "-")
        if status == "BREACHED":
            st.warning(conclusion)
        elif status in {"WATCH", "NEEDS_INPUT"}:
            st.info(conclusion)
        else:
            st.success(conclusion)
        timeline_df = build_selected_portfolio_monitoring_timeline_table(timeline)
        if timeline_df.empty:
            st.info("표시할 timeline row가 없습니다.")
        else:
            st.dataframe(timeline_df, width="stretch", hide_index=True)
        st.caption(
            f"Write policy: {boundary.get('write_policy') or '-'} / "
            f"monitoring auto write: {boundary.get('monitoring_log_auto_write')}"
        )
    with trigger_tab:
        st.caption(
            "Performance Recheck와 Actual Allocation의 최신 입력을 운영 signal 상태로 번역합니다. "
            "성과 threshold는 Recheck Comparison을 기준으로 읽고, Watch / Breached row의 Suggested Action을 확인합니다."
        )
        signal_metrics = dict(review_signal_policy.get("metrics") or {})
        signal_boundary = dict(review_signal_policy.get("execution_boundary") or {})
        board_status = str(review_signal_policy.get("overall_status") or "")
        board_conclusion = str(review_signal_policy.get("conclusion") or "-")
        render_badge_strip(
            [
                {
                    "label": "Board Status",
                    "value": review_signal_policy.get("route_label") or board_status,
                    "tone": _review_trigger_tone(board_status),
                },
                {"label": "Review Cadence", "value": row.get("review_cadence"), "tone": "neutral"},
                {"label": "Stored Triggers", "value": len(triggers), "tone": "neutral"},
                {
                    "label": "Needs Input",
                    "value": signal_metrics.get("needs_input_count", 0),
                    "tone": "warning" if signal_metrics.get("needs_input_count") else "neutral",
                },
                {
                    "label": "Breached",
                    "value": signal_metrics.get("breached_count", 0),
                    "tone": "danger" if signal_metrics.get("breached_count") else "neutral",
                },
                {"label": "Writes", "value": "Disabled", "tone": "neutral"},
            ]
        )
        if board_status == "BREACHED":
            st.warning(board_conclusion)
        elif board_status in {"WATCH", "NEEDS_INPUT"}:
            st.info(board_conclusion)
        else:
            st.success(board_conclusion)
        signal_df = build_selected_portfolio_review_signal_policy_table(review_signal_policy)
        if signal_df.empty:
            st.info("표시할 Review Signal row가 없습니다.")
        else:
            st.dataframe(signal_df, width="stretch", hide_index=True)
        st.caption(
            f"Write policy: {signal_boundary.get('write_policy') or '-'} / "
            f"monitoring auto write: {signal_boundary.get('monitoring_log_auto_write')}"
        )
        recheck_comparison = dict(review_signal_policy.get("recheck_comparison") or {})
        comparison_metrics = dict(recheck_comparison.get("metrics") or {})
        comparison_boundary = dict(recheck_comparison.get("execution_boundary") or {})
        st.markdown("##### Recheck Evidence Comparison")
        st.caption(
            "최신 Performance Recheck 결과가 Final Review에서 선정할 때의 baseline 근거를 계속 지지하는지 읽습니다. "
            "이 비교는 monitoring log를 저장하지 않습니다."
        )
        render_badge_strip(
            [
                {
                    "label": "Comparison",
                    "value": recheck_comparison.get("route_label"),
                    "tone": _review_trigger_tone(str(recheck_comparison.get("overall_status") or "")),
                },
                {
                    "label": "Breached",
                    "value": comparison_metrics.get("breached_count", 0),
                    "tone": "danger" if comparison_metrics.get("breached_count") else "neutral",
                },
                {
                    "label": "Watch",
                    "value": comparison_metrics.get("watch_count", 0),
                    "tone": "warning" if comparison_metrics.get("watch_count") else "neutral",
                },
                {
                    "label": "Needs Input",
                    "value": comparison_metrics.get("needs_input_count", 0),
                    "tone": "warning" if comparison_metrics.get("needs_input_count") else "neutral",
                },
                {"label": "Auto Save", "value": "Disabled", "tone": "neutral"},
            ]
        )
        comparison_status = str(recheck_comparison.get("overall_status") or "")
        comparison_conclusion = str(recheck_comparison.get("conclusion") or "-")
        if comparison_status == "BREACHED":
            st.warning(comparison_conclusion)
        elif comparison_status in {"WATCH", "NEEDS_INPUT"}:
            st.info(comparison_conclusion)
        else:
            st.success(comparison_conclusion)
        with st.expander("Recheck comparison rows", expanded=comparison_status != "CLEAR"):
            comparison_df = build_selected_portfolio_recheck_comparison_table(recheck_comparison)
            if comparison_df.empty:
                st.info("표시할 recheck comparison row가 없습니다.")
            else:
                st.dataframe(comparison_df, width="stretch", hide_index=True)
            st.caption(
                f"Write policy: {comparison_boundary.get('write_policy') or '-'} / "
                f"monitoring auto write: {comparison_boundary.get('monitoring_log_auto_write')}"
            )
        with st.expander("Original Operator Notes", expanded=False):
            st.markdown(f"**선정 사유**  \n{row.get('operator_reason') or '-'}")
            st.markdown(f"**제약 조건**  \n{row.get('operator_constraints') or '-'}")
            st.markdown(f"**다음 행동**  \n{row.get('operator_next_action') or '-'}")
            st.markdown(f"**점검 주기**  \n{row.get('review_cadence') or '-'}")
            if triggers:
                st.markdown("**Final Review에 저장된 원본 trigger**")
                for trigger in triggers:
                    st.markdown(f"- {trigger}")
            else:
                st.caption("등록된 review trigger가 없습니다.")
            if blockers:
                st.warning("남아 있는 blocker: " + ", ".join(blockers))
    with issue_tab:
        st.caption(
            "Final Review에서 selection은 허용했지만 Dashboard monitoring에서 계속 봐야 할 open issue와 follow-up trigger입니다. "
            "이 표는 monitoring log를 자동 저장하지 않습니다."
        )
        issue_metrics = dict(open_issue_followup.get("metrics") or {})
        issue_boundary = dict(open_issue_followup.get("execution_boundary") or {})
        issue_route = str(open_issue_followup.get("route") or "")
        render_badge_strip(
            [
                {
                    "label": "Open Issues",
                    "value": open_issue_followup.get("route_label") or issue_route,
                    "tone": _open_issue_tone(issue_route),
                },
                {
                    "label": "Open Review",
                    "value": issue_metrics.get("open_review_item_count", 0),
                    "tone": "warning" if issue_metrics.get("open_review_item_count") else "neutral",
                },
                {
                    "label": "Triggers",
                    "value": issue_metrics.get("review_trigger_count", 0),
                    "tone": "neutral",
                },
                {
                    "label": "Needs Input",
                    "value": issue_metrics.get("needs_input_count", 0),
                    "tone": "warning" if issue_metrics.get("needs_input_count") else "neutral",
                },
                {"label": "Auto Save", "value": "Disabled", "tone": "neutral"},
            ]
        )
        if issue_route == "OPEN_ISSUES_NEEDS_INPUT":
            st.warning(str(open_issue_followup.get("conclusion") or "-"))
        elif issue_route == "OPEN_ISSUES_PRESENT":
            st.info(str(open_issue_followup.get("conclusion") or "-"))
        else:
            st.success(str(open_issue_followup.get("conclusion") or "-"))
        issue_df = build_selected_portfolio_open_issue_followup_table(open_issue_followup)
        if issue_df.empty:
            st.info("표시할 open issue / follow-up row가 없습니다.")
        else:
            st.dataframe(issue_df, width="stretch", hide_index=True)
        st.caption(
            f"Write policy: {issue_boundary.get('write_policy') or '-'} / "
            f"monitoring auto write: {issue_boundary.get('monitoring_log_auto_write')} / "
            f"live approval: {issue_boundary.get('live_approval')}"
        )
    with preflight_tab:
        st.caption(
            "실제 자금 투입 전에 선택적으로 확인할 blocker / review / data gap을 read-only로 묶어 봅니다. "
            "이 preflight는 승인, 주문, 계좌 연결, 자동 리밸런싱을 만들지 않습니다."
        )
        deployment_metrics = dict(deployment_preflight.get("metrics") or {})
        deployment_boundary = dict(deployment_preflight.get("execution_boundary") or {})
        deployment_route = str(deployment_preflight.get("route") or "")
        render_badge_strip(
            [
                {
                    "label": "Deployment",
                    "value": deployment_preflight.get("route_label") or deployment_route,
                    "tone": _deployment_readiness_tone(deployment_route),
                },
                {
                    "label": "Blocked",
                    "value": deployment_metrics.get("blocked_count", 0),
                    "tone": "danger" if deployment_metrics.get("blocked_count") else "neutral",
                },
                {
                    "label": "Needs Input",
                    "value": deployment_metrics.get("needs_input_count", 0),
                    "tone": "warning" if deployment_metrics.get("needs_input_count") else "neutral",
                },
                {
                    "label": "Review",
                    "value": deployment_metrics.get("review_count", 0),
                    "tone": "warning" if deployment_metrics.get("review_count") else "neutral",
                },
                {"label": "Approval / Order", "value": "Disabled", "tone": "neutral"},
            ]
        )
        if deployment_route == "DEPLOYMENT_READINESS_BLOCKED":
            st.warning(str(deployment_preflight.get("conclusion") or "-"))
        elif deployment_route in {"DEPLOYMENT_READINESS_REVIEW", "DEPLOYMENT_READINESS_NEEDS_INPUT"}:
            st.info(str(deployment_preflight.get("conclusion") or "-"))
        else:
            st.success(str(deployment_preflight.get("conclusion") or "-"))
        deployment_df = build_selected_portfolio_deployment_readiness_table(deployment_preflight)
        if deployment_df.empty:
            st.info("표시할 deployment readiness row가 없습니다.")
        else:
            st.dataframe(deployment_df, width="stretch", hide_index=True)
        st.caption(
            f"Write policy: {deployment_boundary.get('write_policy') or '-'} / "
            f"account connection: {deployment_boundary.get('account_connection')} / "
            f"order instruction: {deployment_boundary.get('order_instruction')} / "
            f"auto rebalance: {deployment_boundary.get('auto_rebalance')}"
        )
    with evidence_tab:
        st.caption("Final Review에서 이 포트폴리오가 모니터링 후보로 선정될 수 있었던 검증 근거입니다.")
        if evidence_df.empty:
            st.info("표시할 evidence check row가 없습니다.")
        else:
            st.dataframe(evidence_df, width="stretch", hide_index=True)
    with allocation_tab:
        _render_selected_row_drift_check(row)
    with audit_tab:
        _render_execution_boundary(key_prefix=f"selected_dashboard_execution_{_decision_key(row)}")


def _render_decision_dossier(row: dict[str, Any]) -> None:
    st.markdown("#### Decision Dossier")
    st.caption(
        "Final Review 판단 근거와 현재 Selected Dashboard timeline을 markdown dossier로 읽습니다. "
        "자동 report 저장, monitoring log 저장, 주문 지시는 만들지 않습니다."
    )
    dossier = build_decision_dossier(row, monitoring_timeline=_latest_monitoring_timeline(row))
    decision = dict(dossier.get("decision") or {})
    metrics = dict(dossier.get("metrics") or {})
    source_contract = dict(dossier.get("source_contract") or {})
    boundary = dict(dossier.get("execution_boundary") or {})
    render_badge_strip(
        [
            {"label": "Decision", "value": decision.get("decision_label"), "tone": "neutral"},
            {"label": "Evidence", "value": metrics.get("evidence_check_count", 0), "tone": "neutral"},
            {
                "label": "Needs Review",
                "value": metrics.get("not_ready_evidence_check_count", 0),
                "tone": "warning" if metrics.get("not_ready_evidence_check_count") else "neutral",
            },
            {
                "label": "Timeline",
                "value": "Included" if metrics.get("monitoring_timeline_present") else "Not Included",
                "tone": "neutral",
            },
            {
                "label": "Source Contract",
                "value": "Consistent" if metrics.get("source_contract_consistent") else "Check",
                "tone": "positive" if metrics.get("source_contract_consistent") else "warning",
            },
            {"label": "Auto Write", "value": "Disabled", "tone": "neutral"},
        ]
    )
    action_cols = st.columns([0.34, 0.66], gap="small")
    with action_cols[0]:
        st.download_button(
            "Markdown 다운로드",
            data=str(dossier.get("markdown") or ""),
            file_name=str(dossier.get("filename") or "decision_dossier.md"),
            mime="text/markdown",
            key=f"selected_dossier_download_{row.get('decision_id') or 'selected'}",
            width="stretch",
        )
    with action_cols[1]:
        st.caption(
            f"Write policy: {boundary.get('write_policy') or '-'} / "
            f"report auto write: {boundary.get('report_auto_write')} / "
            f"monitoring auto write: {boundary.get('monitoring_log_auto_write')}"
        )
    with st.expander("Dossier source contract", expanded=not metrics.get("source_contract_consistent")):
        st.dataframe(
            build_selected_portfolio_source_contract_table(source_contract),
            width="stretch",
            hide_index=True,
        )
    with st.expander("Dossier preview", expanded=False):
        st.markdown(str(dossier.get("markdown") or "-"))


def _render_execution_boundary(*, key_prefix: str = "selected_dashboard_execution_boundary") -> None:
    with st.container(border=True):
        st.markdown("#### Execution Boundary")
        st.caption(
            "이 대시보드는 Final Review 모니터링 후보 포트폴리오를 운영 대상으로 읽는 화면입니다. "
            "기간 확장 재검증과 drift 점검은 read-only이며 실제 투자 승인, broker 주문, 자동 리밸런싱은 만들지 않습니다."
        )
        action_cols = st.columns(3, gap="small")
        action_cols[0].button(
            "Live Approval",
            disabled=True,
            key=f"{key_prefix}_live_approval",
            width="stretch",
        )
        action_cols[1].button(
            "Broker Order",
            disabled=True,
            key=f"{key_prefix}_broker_order",
            width="stretch",
        )
        action_cols[2].button(
            "Auto Rebalance",
            disabled=True,
            key=f"{key_prefix}_auto_rebalance",
            width="stretch",
        )


def _render_recheck_evidence_detail(preflight: dict[str, Any], provider_evidence: dict[str, Any]) -> None:
    with st.expander("하단 상세 점검 / 감사 근거", expanded=False):
        preflight_metrics = dict(preflight.get("metrics") or {})
        preflight_boundary = dict(preflight.get("execution_boundary") or {})
        preflight_route = str(preflight.get("route") or "")
        st.markdown("##### Recheck Readiness / Source")
        render_badge_strip(
            [
                {
                    "label": "Preflight",
                    "value": preflight.get("route_label"),
                    "tone": _recheck_preflight_tone(preflight_route),
                },
                {"label": "DB Latest", "value": preflight_metrics.get("latest_market_date") or "-", "tone": "neutral"},
                {
                    "label": "Replay Contracts",
                    "value": f"{preflight_metrics.get('replay_contract_count', 0)}/{preflight_metrics.get('active_component_count', 0)}",
                    "tone": "positive"
                    if preflight_metrics.get("replay_contract_count") == preflight_metrics.get("active_component_count")
                    and preflight_metrics.get("active_component_count")
                    else "warning",
                },
                {
                    "label": "Missing/Stale",
                    "value": f"{preflight_metrics.get('missing_symbol_count', 0)}/{preflight_metrics.get('stale_symbol_count', 0)}",
                    "tone": "warning"
                    if preflight_metrics.get("missing_symbol_count") or preflight_metrics.get("stale_symbol_count")
                    else "neutral",
                },
                {"label": "Writes", "value": "Disabled", "tone": "neutral"},
            ]
        )
        st.caption(str(preflight.get("conclusion") or "-"))
        st.markdown("###### Preflight rows")
        preflight_df = build_selected_portfolio_recheck_preflight_table(preflight)
        if preflight_df.empty:
            st.info("표시할 preflight row가 없습니다.")
        else:
            st.dataframe(preflight_df, width="stretch", hide_index=True)
        st.caption(
            f"Write policy: {preflight_boundary.get('write_policy') or '-'} / "
            f"monitoring log auto write: {preflight_boundary.get('monitoring_log_auto_write')}"
        )

        readiness = dict(preflight.get("readiness") or {})
        readiness_metrics = dict(readiness.get("metrics") or {})
        readiness_route = str(readiness.get("route") or "")
        render_badge_strip(
            [
                {
                    "label": "Readiness",
                    "value": readiness.get("route_label"),
                    "tone": _recheck_readiness_tone(readiness_route),
                },
                {"label": "DB Latest", "value": readiness_metrics.get("latest_market_date") or "-", "tone": "neutral"},
                {
                    "label": "Blocked",
                    "value": readiness_metrics.get("blocked_count", 0),
                    "tone": "danger" if readiness_metrics.get("blocked_count") else "neutral",
                },
                {"label": "Writes", "value": "Disabled", "tone": "neutral"},
            ]
        )
        st.markdown("###### Readiness rows")
        readiness_df = build_selected_portfolio_recheck_readiness_table(readiness)
        if readiness_df.empty:
            st.info("표시할 readiness row가 없습니다.")
        else:
            st.dataframe(readiness_df, width="stretch", hide_index=True)

        symbol_freshness = dict(preflight.get("symbol_freshness") or {})
        freshness_metrics = dict(symbol_freshness.get("metrics") or {})
        freshness_route = str(symbol_freshness.get("route") or "")
        st.markdown("##### Symbol Freshness")
        render_badge_strip(
            [
                {
                    "label": "Freshness",
                    "value": symbol_freshness.get("route_label"),
                    "tone": _symbol_freshness_tone(freshness_route),
                },
                {"label": "Symbols", "value": freshness_metrics.get("symbol_count", 0), "tone": "neutral"},
                {
                    "label": "Missing",
                    "value": freshness_metrics.get("missing_count", 0),
                    "tone": "danger" if freshness_metrics.get("missing_count") else "neutral",
                },
                {
                    "label": "Stale",
                    "value": freshness_metrics.get("stale_count", 0),
                    "tone": "warning" if freshness_metrics.get("stale_count") else "neutral",
                },
            ]
        )
        st.markdown("###### Symbol freshness rows")
        freshness_df = build_selected_portfolio_symbol_freshness_table(symbol_freshness)
        if freshness_df.empty:
            st.info("표시할 symbol freshness row가 없습니다.")
        else:
            st.dataframe(freshness_df, width="stretch", hide_index=True)

        provider_metrics = dict(provider_evidence.get("metrics") or {})
        provider_boundary = dict(provider_evidence.get("execution_boundary") or {})
        provider_route = str(provider_evidence.get("route") or "")
        look_through = dict(provider_evidence.get("look_through_board") or {})
        st.markdown("##### Provider Evidence")
        render_badge_strip(
            [
                {
                    "label": "Provider",
                    "value": provider_evidence.get("route_label"),
                    "tone": _provider_evidence_tone(provider_route),
                },
                {"label": "Symbols", "value": provider_metrics.get("provider_symbol_count", 0), "tone": "neutral"},
                {
                    "label": "Holdings",
                    "value": f"{provider_metrics.get('holdings_coverage_weight', 0) or 0}%",
                    "tone": "warning"
                    if provider_metrics.get("holdings_coverage_weight") is not None
                    and float(provider_metrics.get("holdings_coverage_weight") or 0.0) < 80.0
                    else "neutral",
                },
                {
                    "label": "Exposure",
                    "value": f"{provider_metrics.get('exposure_coverage_weight', 0) or 0}%",
                    "tone": "warning"
                    if provider_metrics.get("exposure_coverage_weight") is not None
                    and float(provider_metrics.get("exposure_coverage_weight") or 0.0) < 80.0
                    else "neutral",
                },
                {"label": "Writes", "value": "Disabled", "tone": "neutral"},
            ]
        )
        st.caption(str(provider_evidence.get("conclusion") or "-"))
        st.markdown("###### Provider evidence rows")
        provider_df = build_selected_portfolio_provider_evidence_table(provider_evidence)
        if provider_df.empty:
            st.info("표시할 provider evidence row가 없습니다.")
        else:
            st.dataframe(provider_df, width="stretch", hide_index=True)
        symbol_weight_df = build_selected_portfolio_provider_symbol_weight_table(provider_evidence)
        if not symbol_weight_df.empty:
            st.markdown("###### Selected provider symbol weights")
            st.dataframe(symbol_weight_df, width="stretch", hide_index=True)
        st.caption(
            f"Write policy: {provider_boundary.get('write_policy') or '-'} / "
            f"DB write: {provider_boundary.get('db_write')} / "
            f"provider collection: {provider_boundary.get('provider_collection')}"
        )
        summary_rows = list(look_through.get("summary_rows") or [])
        if summary_rows:
            st.markdown("###### Look-through summary")
            st.caption(str(look_through.get("summary") or "-"))
            st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)


def _render_performance_recheck(row: dict[str, Any]) -> dict[str, Any]:
    st.markdown("##### Monitoring Scenario")
    defaults = _recheck_defaults(row)
    if defaults.get("latest_market_date_error"):
        st.warning(f"최신 시장일 확인 실패: {defaults.get('latest_market_date_error')}")

    latest_market_result = {
        "status": defaults.get("latest_market_date_status"),
        "latest_market_date": defaults.get("latest_market_date"),
        "error": defaults.get("latest_market_date_error"),
    }
    preflight = build_selected_portfolio_recheck_operations_preflight(
        row,
        latest_market_result=latest_market_result,
    )
    provider_evidence = build_selected_portfolio_provider_evidence(
        row,
        as_of_date=defaults.get("latest_market_date") or date.today().isoformat(),
    )
    decision_id = str(row.get("decision_id") or "selected_portfolio")
    result_decision_key = _decision_key(row)
    slot = _slot_for_row(row)
    start = _slot_effective_start(row)
    end = _slot_effective_end(row)
    capital = _slot_effective_capital(row)
    slot_blockers = _slot_blockers_for_row(row)

    with st.container(border=True):
        st.markdown("##### Scenario Setup")
        render_badge_strip(
            [
                {"label": "Start", "value": start or "-", "tone": "positive" if start else "warning"},
                {
                    "label": "End",
                    "value": "Latest market date" if bool(slot.get("use_latest_end", True)) else end or "-",
                    "tone": "positive" if end else "warning",
                },
                {"label": "Balance", "value": _format_money(capital), "tone": "positive" if capital > 0 else "warning"},
                {"label": "DB Latest", "value": defaults.get("latest_market_date") or "-", "tone": "neutral"},
                {"label": "Writes", "value": "Disabled", "tone": "neutral"},
            ]
        )
        if slot.get("memo"):
            st.caption(f"Memo: {slot.get('memo')}")
        for blocker in slot_blockers:
            st.warning(blocker)
        run_cols = st.columns([0.68, 0.32], gap="small")
        with run_cols[0]:
            st.caption(
                f"Original period: {defaults.get('baseline_start') or '-'} -> {defaults.get('baseline_end') or '-'} / "
                f"Scenario end: {end or '-'}"
            )
        with run_cols[1]:
            run_clicked = st.button(
                "모니터 시나리오 실행",
                disabled=bool(slot_blockers),
                key=f"selected_portfolio_run_recheck_{result_decision_key}",
                type="primary",
                width="stretch",
            )

    if run_clicked:
        with st.spinner("선정 포트폴리오 contract를 재실행하는 중입니다...", show_time=True):
            _run_strategy_recheck(row)

    operations_payload = {
        "preflight": preflight,
        "provider_evidence": provider_evidence,
    }
    result = _latest_recheck_result(row)
    if not result:
        if _has_stale_recheck_result(row):
            st.warning("이전 scenario 결과가 있지만 현재 setup과 입력값이 달라서 표시하지 않았습니다. 다시 실행하면 최신 결과가 채워집니다.")
        st.info("`모니터 시나리오 실행`을 누르면 이 전략의 현재 가치, 손익, 수익률, 리스크 지표가 계산됩니다.")
        _render_recheck_evidence_detail(preflight, provider_evidence)
        return operations_payload
    if result.get("status") == "error":
        st.error(str(result.get("error") or "Performance recheck failed."))
        for blocker in list(result.get("blockers") or []):
            st.warning(str(blocker))
        _render_recheck_evidence_detail(preflight, provider_evidence)
        return operations_payload

    for blocker in list(result.get("blockers") or []):
        st.warning(str(blocker))

    portfolio_summary = dict(result.get("portfolio_summary") or {})
    benchmark_summary = dict(result.get("benchmark_summary") or {})
    baseline_summary = dict(result.get("baseline_summary") or {})
    change_summary = dict(result.get("change_summary") or {})
    period = dict(result.get("period") or {})
    summary_tab, curve_tab, result_table_tab, changed_tab, contribution_tab, extremes_tab = st.tabs(
        ["Summary", "Equity Curve", "Result Table", "What Changed", "Contribution", "Extremes"]
    )
    with summary_tab:
        render_status_card_grid(
            [
                {
                    "title": "Recheck Verdict",
                    "value": result.get("verdict_route"),
                    "detail": result.get("verdict"),
                    "tone": "positive" if result.get("verdict_route") == "SELECTION_THESIS_HOLDS" else "warning",
                },
                {
                    "title": "Invested",
                    "value": _format_money(result.get("initial_capital")),
                    "detail": f"Start {period.get('start') or '-'}",
                    "tone": "neutral",
                },
                {
                    "title": "Portfolio Value",
                    "value": _format_money(portfolio_summary.get("end_balance")),
                    "detail": f"Total return {_format_pct(portfolio_summary.get('total_return'))}",
                    "tone": "positive",
                },
                {
                    "title": "Recheck CAGR",
                    "value": _format_pct(portfolio_summary.get("cagr")),
                    "detail": f"Original {_format_pct(baseline_summary.get('cagr'))}",
                    "tone": "positive" if (change_summary.get("cagr_delta_vs_baseline") or 0.0) >= 0 else "warning",
                },
                {
                    "title": "Recheck MDD",
                    "value": _format_pct(portfolio_summary.get("mdd")),
                    "detail": f"Original {_format_pct(baseline_summary.get('mdd'))}",
                    "tone": "warning",
                },
                {
                    "title": "Benchmark Spread",
                    "value": _format_pct(change_summary.get("net_cagr_spread")),
                    "detail": f"Benchmark {result.get('benchmark_label') or '-'} CAGR {_format_pct(benchmark_summary.get('cagr'))}",
                    "tone": "positive" if (change_summary.get("net_cagr_spread") or 0.0) >= 0 else "warning",
                },
            ]
        )
        st.caption(
            f"Original period: {period.get('baseline_start') or '-'} -> {period.get('baseline_end') or '-'} | "
            f"Recheck period: {period.get('start') or '-'} -> {period.get('end') or '-'}"
        )

    chart_df = result.get("chart_df")
    with curve_tab:
        if isinstance(chart_df, pd.DataFrame) and not chart_df.empty:
            chart_view = chart_df.copy()
            chart_view["Date"] = pd.to_datetime(chart_view["Date"], errors="coerce")
            chart_view = chart_view.dropna(subset=["Date"]).set_index("Date")
            st.line_chart(chart_view)
        else:
            st.info("표시할 equity curve가 없습니다.")

    with result_table_tab:
        result_df = result.get("portfolio_result_df")
        if isinstance(result_df, pd.DataFrame) and not result_df.empty:
            display_df = result_df[["Date", "Total Balance", "Total Return"]].copy()
            display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
            display_df["Total Balance"] = display_df["Total Balance"].map(lambda value: _format_money(value))
            display_df["Total Return"] = display_df["Total Return"].map(lambda value: _format_pct(value))
            st.dataframe(display_df, width="stretch", hide_index=True)
        else:
            st.info("표시할 result table이 없습니다.")

    with changed_tab:
        comparison_df = pd.DataFrame(
            [
                {
                    "Metric": "CAGR",
                    "Original": baseline_summary.get("cagr"),
                    "Recheck": portfolio_summary.get("cagr"),
                    "Change": change_summary.get("cagr_delta_vs_baseline"),
                },
                {
                    "Metric": "Maximum Drawdown",
                    "Original": baseline_summary.get("mdd"),
                    "Recheck": portfolio_summary.get("mdd"),
                    "Change": change_summary.get("mdd_delta_vs_baseline"),
                },
                {
                    "Metric": "Benchmark CAGR Spread",
                    "Original": None,
                    "Recheck": change_summary.get("net_cagr_spread"),
                    "Change": None,
                },
            ]
        )
        for column in ["Original", "Recheck", "Change"]:
            comparison_df[column] = comparison_df[column].map(
                lambda value: _format_pct(value) if value is not None else "-"
            )
        st.dataframe(comparison_df, width="stretch", hide_index=True)

    with contribution_tab:
        component_df = pd.DataFrame(list(result.get("component_rows") or []))
        if component_df.empty:
            st.info("표시할 component contribution이 없습니다.")
        else:
            for column in ["Total Return", "Weighted Contribution", "CAGR", "MDD"]:
                if column in component_df.columns:
                    component_df[column] = component_df[column].map(
                        lambda value: _format_pct(value) if value is not None else "-"
                    )
            if "Target Weight" in component_df.columns:
                component_df["Target Weight"] = component_df["Target Weight"].map(
                    lambda value: f"{float(value):.1f}%" if value is not None and not pd.isna(value) else "-"
                )
            st.dataframe(component_df, width="stretch", hide_index=True)

    with extremes_tab:
        extremes = dict(result.get("period_extremes") or {})
        extreme_cols = st.columns(2, gap="small")
        with extreme_cols[0]:
            best_df = pd.DataFrame(extremes.get("best") or [])
            st.markdown("##### Strongest periods")
            if best_df.empty:
                st.caption("표시할 strong period가 없습니다.")
            else:
                if "Total Return" in best_df.columns:
                    best_df["Total Return"] = best_df["Total Return"].map(lambda value: _format_pct(value))
                if "Total Balance" in best_df.columns:
                    best_df["Total Balance"] = best_df["Total Balance"].map(lambda value: _format_money(value))
                st.dataframe(best_df, width="stretch", hide_index=True)
        with extreme_cols[1]:
            worst_df = pd.DataFrame(extremes.get("worst") or [])
            st.markdown("##### Weakest periods")
            if worst_df.empty:
                st.caption("표시할 weak period가 없습니다.")
            else:
                if "Total Return" in worst_df.columns:
                    worst_df["Total Return"] = worst_df["Total Return"].map(lambda value: _format_pct(value))
                if "Total Balance" in worst_df.columns:
                    worst_df["Total Balance"] = worst_df["Total Balance"].map(lambda value: _format_money(value))
                st.dataframe(worst_df, width="stretch", hide_index=True)

    _render_recheck_evidence_detail(preflight, provider_evidence)
    return operations_payload


def _render_selected_row_drift_check(row: dict[str, Any]) -> None:
    st.markdown("##### Actual Allocation Check")
    st.caption(
        "전략이나 백테스트 기간이 바뀌었는지 보는 기능이 아닙니다. "
        "사용자가 실제 또는 가상으로 배정한 금액이 Final Review의 target allocation과 얼마나 다른지 확인하는 선택 점검입니다."
    )
    components = selected_portfolio_active_components(row)
    if not components:
        st.info("allocation을 계산할 active component가 없습니다.")
        return

    target_total = sum(float(component.get("target_weight") or 0.0) for component in components)
    single_component_target = len(components) == 1 and target_total >= 99.0
    render_badge_strip(
        [
            {"label": "Target Components", "value": len(components), "tone": "neutral"},
            {"label": "Target Total", "value": f"{target_total:.1f}%", "tone": "neutral"},
            {"label": "Use When", "value": "Actual / Virtual Holdings", "tone": "neutral"},
            {"label": "Writes", "value": "Disabled", "tone": "neutral"},
        ]
    )
    if single_component_target:
        st.info(
            "이 포트폴리오는 단일 component 100% 구조입니다. 여기서는 component 간 리밸런싱보다, "
            "이 포트폴리오에 배정한 금액과 현금/포트폴리오 밖 금액 때문에 target 100%에서 벗어났는지 확인하는 용도로 봅니다."
        )

    drift_threshold = 5.0
    watch_threshold = 2.0
    total_tolerance = 1.0
    with st.expander("Review thresholds", expanded=False):
        threshold_cols = st.columns([0.34, 0.33, 0.33], gap="small")
        with threshold_cols[0]:
            drift_threshold = st.number_input(
                "Rebalance threshold (%)",
                min_value=0.5,
                max_value=50.0,
                value=5.0,
                step=0.5,
                key=f"selected_portfolio_drift_threshold_{row.get('decision_id')}",
                help="component별 target/current 차이가 이 값 이상이면 리밸런싱 검토 필요로 봅니다.",
            )
        with threshold_cols[1]:
            watch_threshold = st.number_input(
                "Watch threshold (%)",
                min_value=0.1,
                max_value=50.0,
                value=2.0,
                step=0.5,
                key=f"selected_portfolio_watch_threshold_{row.get('decision_id')}",
                help="리밸런싱 전 관찰이 필요한 drift 기준입니다.",
            )
        with threshold_cols[2]:
            total_tolerance = st.number_input(
                "Total tolerance (%)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                key=f"selected_portfolio_total_tolerance_{row.get('decision_id')}",
                help="현재 비중 합계가 100%에서 이 범위 이상 벗어나면 입력 확인이 필요합니다.",
            )

    current_weights: dict[str, float] = {}
    input_mode = "current_value"
    with st.expander("Advanced input modes", expanded=False):
        input_mode = st.radio(
            "현재 보유 상태 입력 방식",
            options=["current_value", "shares_x_price", "current_weight"],
            format_func=lambda mode: FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(mode, mode),
            horizontal=True,
            key=f"selected_portfolio_current_input_mode_{row.get('decision_id')}",
        )
    value_input_contract: dict[str, Any] | None = None
    if input_mode == "current_weight":
        st.caption("외부에서 이미 현재 비중을 계산해 둔 경우에만 씁니다. 기본값은 target weight입니다.")
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            target_weight = float(component.get("target_weight") or 0.0)
            with input_cols[index % 2]:
                current_weights[component_id] = st.number_input(
                    f"{title} current weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=target_weight,
                    step=0.5,
                    key=f"selected_portfolio_current_weight_{row.get('decision_id')}_{component_id}",
                )
    elif input_mode == "current_value":
        st.markdown("###### Current Value Input")
        st.caption("가장 쉬운 방식입니다. component별 현재 평가금액을 넣으면 전체 금액 대비 현재 비중으로 변환합니다.")
        cash_value = st.number_input(
            "Cash or value outside this selected portfolio",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"selected_portfolio_cash_value_{row.get('decision_id')}",
            help="이 포트폴리오 target component 밖에 남아 있는 현금이나 제외 자산이 있으면 입력합니다.",
        )
        component_inputs: dict[str, dict[str, Any]] = {}
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            target_weight = float(component.get("target_weight") or 0.0)
            with input_cols[index % 2]:
                component_inputs[component_id] = {
                    "current_value": st.number_input(
                        f"{title} assigned value",
                        min_value=0.0,
                        value=10_000.0 if single_component_target else target_weight,
                        step=1.0,
                        key=f"selected_portfolio_current_value_{row.get('decision_id')}_{component_id}",
                    ),
                    "price_source": "manual_current_value",
                }
        value_input_contract = build_selected_portfolio_current_weight_inputs(
            row,
            component_inputs=component_inputs,
            cash_value=cash_value,
            input_mode="current_value",
        )
        current_weights = dict(value_input_contract.get("current_weights") or {})
    else:
        st.caption(
            "실제 보유 수량과 현재가를 알고 있을 때 쓰는 고급 입력입니다. "
            "DB latest close는 보조값이며, 가격과 수량은 저장되지 않습니다."
        )
        component_symbols: dict[str, str] = {}
        symbol_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            default_symbol = selected_portfolio_component_default_symbol(component)
            with symbol_cols[index % 2]:
                component_symbols[component_id] = st.text_input(
                    f"{title} holding symbol",
                    value=default_symbol,
                    key=f"selected_portfolio_holding_symbol_{row.get('decision_id')}_{component_id}",
                    help="DB latest close 조회에만 쓰는 선택 입력입니다.",
                ).strip().upper()

        fetch_cols = st.columns([0.35, 0.35, 0.30], gap="small")
        with fetch_cols[0]:
            price_end = st.text_input(
                "DB price end date",
                value="",
                placeholder="YYYY-MM-DD",
                key=f"selected_portfolio_price_end_{row.get('decision_id')}",
            ).strip()
        symbols_to_fetch = sorted({symbol for symbol in component_symbols.values() if symbol})
        fetch_key = f"selected_portfolio_latest_price_result_{row.get('decision_id')}"
        with fetch_cols[1]:
            if st.button(
                "Load latest close",
                disabled=not symbols_to_fetch,
                key=f"selected_portfolio_load_latest_price_{row.get('decision_id')}",
                width="stretch",
            ):
                price_result = load_latest_selected_portfolio_prices(symbols_to_fetch, end=price_end or None)
                st.session_state[fetch_key] = price_result
                price_by_symbol = dict(price_result.get("price_by_symbol") or {})
                for index, component in enumerate(components):
                    component_id = str(component.get("component_id") or f"component_{index + 1}")
                    symbol = component_symbols.get(component_id)
                    price_row = dict(price_by_symbol.get(symbol) or {})
                    if price_row.get("price") is not None:
                        st.session_state[
                            f"selected_portfolio_holding_price_{row.get('decision_id')}_{component_id}"
                        ] = float(price_row.get("price") or 0.0)
                        st.session_state[
                            f"selected_portfolio_holding_price_date_{row.get('decision_id')}_{component_id}"
                        ] = price_row.get("latest_date")
        with fetch_cols[2]:
            st.metric("Symbols", len(symbols_to_fetch))

        latest_price_result = dict(st.session_state.get(fetch_key) or {})
        if latest_price_result.get("status") == "error":
            st.warning(f"DB latest close 조회 실패: {latest_price_result.get('error')}")
        elif latest_price_result.get("rows"):
            with st.expander("Loaded latest close rows", expanded=False):
                st.dataframe(list(latest_price_result.get("rows") or []), width="stretch", hide_index=True)
                missing = list(latest_price_result.get("missing_symbols") or [])
                if missing:
                    st.caption(f"missing symbols: {', '.join(missing)}")

        cash_value = st.number_input(
            "Unassigned cash / outside value",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"selected_portfolio_holding_cash_value_{row.get('decision_id')}",
            help="target component 밖에 남아 있는 현금이나 제외 자산이 있으면 입력합니다.",
        )
        component_inputs = {}
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            price_key = f"selected_portfolio_holding_price_{row.get('decision_id')}_{component_id}"
            price_date_key = f"selected_portfolio_holding_price_date_{row.get('decision_id')}_{component_id}"
            with input_cols[index % 2]:
                shares = st.number_input(
                    f"{title} shares",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"selected_portfolio_holding_shares_{row.get('decision_id')}_{component_id}",
                )
                price_kwargs = {
                    "min_value": 0.0,
                    "step": 0.01,
                    "key": price_key,
                }
                if price_key not in st.session_state:
                    price_kwargs["value"] = 0.0
                price = st.number_input(f"{title} current price", **price_kwargs)
            component_inputs[component_id] = {
                "symbol": component_symbols.get(component_id),
                "shares": shares,
                "price": price,
                "price_date": st.session_state.get(price_date_key),
                "price_source": "db_latest_close" if st.session_state.get(price_date_key) else "manual_price",
            }
        value_input_contract = build_selected_portfolio_current_weight_inputs(
            row,
            component_inputs=component_inputs,
            cash_value=cash_value,
            input_mode="shares_x_price",
        )
        current_weights = dict(value_input_contract.get("current_weights") or {})

    if value_input_contract is not None:
        value_metrics = dict(value_input_contract.get("metrics") or {})
        render_badge_strip(
            [
                {"label": "Input Mode", "value": value_input_contract.get("input_mode_label"), "tone": "neutral"},
                {"label": "Portfolio Value", "value": f"{float(value_metrics.get('portfolio_value_total') or 0.0):,.2f}", "tone": "neutral"},
                {"label": "Cash / Outside", "value": f"{float(value_metrics.get('cash_value') or 0.0):,.2f}", "tone": "neutral"},
                {"label": "Weight Total", "value": f"{float(value_metrics.get('current_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            ]
        )
        input_df = build_selected_portfolio_current_weight_input_table(value_input_contract)
        if not input_df.empty:
            st.dataframe(input_df, width="stretch", hide_index=True)
        for blocker in list(value_input_contract.get("blockers") or []):
            st.warning(str(blocker))

    drift_check = build_selected_portfolio_drift_check(
        row,
        current_weights=current_weights,
        drift_threshold_pct=float(drift_threshold),
        watch_threshold_pct=float(watch_threshold),
        total_weight_tolerance_pct=float(total_tolerance),
    )
    metrics = dict(drift_check.get("metrics") or {})
    render_badge_strip(
        [
            {"label": "Allocation Status", "value": drift_check.get("route_label"), "tone": _status_tone("rebalance_needed" if drift_check.get("route") == "REBALANCE_NEEDED" else "normal" if drift_check.get("route") == "DRIFT_ALIGNED" else "watch")},
            {"label": "Current Total", "value": f"{float(metrics.get('current_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Target Total", "value": f"{float(metrics.get('target_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Max Drift", "value": f"{float(metrics.get('max_abs_drift') or 0.0):.1f}%", "tone": "warning" if float(metrics.get("max_abs_drift") or 0.0) >= float(drift_threshold) else "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    route = str(drift_check.get("route") or "")
    verdict = str(drift_check.get("verdict") or "-")
    if route == "REBALANCE_NEEDED":
        st.warning(verdict)
    elif route in {"DRIFT_WATCH", "DRIFT_INPUT_INCOMPLETE"}:
        st.info(verdict)
    else:
        st.success(verdict)
    drift_df = build_selected_portfolio_drift_table(drift_check)
    if not drift_df.empty:
        st.dataframe(drift_df, width="stretch", hide_index=True)
    if drift_check.get("blockers"):
        for blocker in list(drift_check.get("blockers") or []):
            st.warning(str(blocker))
    alert_preview = build_selected_portfolio_drift_alert_preview(row, drift_check=drift_check)
    allocation_boundary = build_selected_portfolio_allocation_drift_boundary(
        row,
        weight_inputs=value_input_contract,
        drift_check=drift_check,
        alert_preview=alert_preview,
        input_mode=input_mode,
    )
    apply_cols = st.columns([0.62, 0.38], gap="small")
    with apply_cols[0]:
        st.caption(
            "이 결과는 현재 session의 Review Signals에만 반영됩니다. "
            "입력값, alert record, monitoring log, 주문은 저장하지 않습니다."
        )
    with apply_cols[1]:
        if st.button(
            "Reflect Session Signal",
            key=f"selected_portfolio_update_allocation_signal_{row.get('decision_id')}",
            width="stretch",
        ):
            st.session_state[f"selected_portfolio_drift_check_result_{_decision_key(row)}"] = drift_check
            st.session_state[f"selected_portfolio_drift_alert_result_{_decision_key(row)}"] = alert_preview
            st.rerun()
    alert_metrics = dict(alert_preview.get("metrics") or {})
    with st.expander("Allocation review notes", expanded=route in {"REBALANCE_NEEDED", "DRIFT_WATCH"}):
        st.caption(
            "allocation 결과를 운영 경고와 Final Review review trigger 관점으로 다시 읽습니다. "
            "이 preview는 alert registry를 저장하지 않고 주문 지시도 만들지 않습니다."
        )
        render_badge_strip(
            [
                {
                    "label": "Alert Route",
                    "value": alert_preview.get("alert_route_label"),
                    "tone": _alert_tone(str(alert_preview.get("alert_route") or "")),
                },
                {"label": "Alert Level", "value": alert_preview.get("alert_level"), "tone": "neutral"},
                {
                    "label": "Review Triggers",
                    "value": alert_metrics.get("review_trigger_count", 0),
                    "tone": "neutral",
                },
                {"label": "Alert Save", "value": "Disabled", "tone": "neutral"},
                {"label": "Order", "value": "Disabled", "tone": "neutral"},
            ]
        )
        st.caption(str(alert_preview.get("verdict") or "-"))
        alert_df = build_selected_portfolio_drift_alert_table(alert_preview)
        if alert_df.empty:
            st.info("표시할 allocation review row가 없습니다.")
        else:
            st.dataframe(alert_df, width="stretch", hide_index=True)
    boundary_metrics = dict(allocation_boundary.get("metrics") or {})
    boundary_expanded = allocation_boundary.get("route") in {
        "ALLOCATION_DRIFT_BOUNDARY_BREACHED",
        "ALLOCATION_DRIFT_BOUNDARY_BLOCKED",
    }
    with st.expander("Allocation evidence boundary", expanded=boundary_expanded):
        st.caption(
            "Actual Allocation 결과가 수동/session 증거인지 확인합니다. "
            "이 boundary는 DB 저장, registry 저장, 계좌 연결, 주문, 자동 리밸런싱을 허용하지 않습니다."
        )
        render_badge_strip(
            [
                {
                    "label": "Boundary",
                    "value": allocation_boundary.get("route_label"),
                    "tone": _allocation_boundary_tone(str(allocation_boundary.get("route") or "")),
                },
                {"label": "Raw Input Save", "value": "Disabled", "tone": "neutral"},
                {"label": "Alert Save", "value": "Disabled", "tone": "neutral"},
                {
                    "label": "Boundary Violations",
                    "value": boundary_metrics.get("boundary_violation_count", 0),
                    "tone": "danger" if boundary_metrics.get("boundary_violation_count") else "neutral",
                },
                {"label": "Order / Rebalance", "value": "Disabled", "tone": "neutral"},
            ]
        )
        st.caption(str(allocation_boundary.get("conclusion") or "-"))
        boundary_df = build_selected_portfolio_allocation_drift_boundary_table(allocation_boundary)
        if not boundary_df.empty:
            st.dataframe(boundary_df, width="stretch", hide_index=True)
    st.info(str(drift_check.get("next_action") or "-"))
    st.info(str(alert_preview.get("next_action") or "-"))


def _render_portfolio_monitoring_fallback(
    workspace: dict[str, Any],
    error: str | None = None,
) -> None:
    """Render compact recovery guidance instead of the retired legacy dashboard."""

    st.title("Portfolio Monitoring")
    st.caption("React Command Center를 불러오지 못해 읽기 전용 요약만 표시합니다.")
    if error:
        st.warning(error)
    groups = list(workspace.get("groups") or [])
    st.metric("포트폴리오 그룹", len(groups))
    active_group = workspace.get("active_group")
    metrics = getattr(active_group, "metrics", None)
    if metrics is not None:
        columns = st.columns(3)
        columns[0].metric("투자금", _format_money(metrics.invested_capital))
        columns[1].metric("현재 가치", _format_money(metrics.current_value))
        columns[2].metric("총수익률", _format_pct(metrics.total_return))
    st.info(
        "`portfolio_monitoring_workbench/component_static` 빌드를 복구한 뒤 새로고침하세요. "
        "이 fallback에서는 그룹·종목 변경을 수행하지 않습니다."
    )


def _dispatch_portfolio_monitoring_event(
    event: dict[str, Any],
    services: PortfolioMonitoringPageServices | Any,
) -> CommandResult | None:
    """Route one React event to view state or exactly one server command."""

    event_id = str(event.get("id") or "").strip()
    if event_id == "select_group":
        services.session_state["portfolio_monitoring_active_group_id"] = str(
            event.get("portfolio_group_id") or ""
        )
        return None
    if event_id == "search_catalog":
        services.session_state["portfolio_monitoring_catalog_query"] = str(
            event.get("query") or ""
        ).strip()
        services.session_state["portfolio_monitoring_catalog_source_type"] = str(
            event.get("source_type") or SourceType.DIRECT_SECURITY.value
        )
        if event.get("requested_start_date"):
            services.session_state["portfolio_monitoring_catalog_requested_start_date"] = str(
                event.get("requested_start_date")
            )
        return None
    if event_id in {"select_item", "open_item_detail"}:
        services.session_state["portfolio_monitoring_selected_item_id"] = str(
            event.get("monitoring_item_id") or ""
        )
        return None
    if event_id == "create_group":
        return services.create_group(event)
    if event_id == "rename_group":
        return services.rename_group(event)
    if event_id == "add_item":
        return services.add_item(event)
    if event_id == "end_item":
        return services.end_item(event)
    return None


def _event_identity(event: dict[str, Any]) -> str:
    return str(
        event.get("nonce")
        or event.get("command_id")
        or "|".join(
            [
                str(event.get("id") or ""),
                str(event.get("portfolio_group_id") or ""),
                str(event.get("monitoring_item_id") or ""),
                str(event.get("query") or ""),
            ]
        )
    )


def _command_projection(result: CommandResult) -> dict[str, Any]:
    return {
        "command_id": result.command_id,
        "status": "success" if result.status == CommandStatus.SUCCEEDED else result.status.value,
        "message": result.message,
        "target_id": result.target_id,
        "replayed": result.replayed,
    }


def load_portfolio_monitoring_workspace_for_operations() -> dict[str, Any]:
    """Load the same compact workspace for the Operations landing summary."""

    runtime = _default_portfolio_monitoring_services()
    return runtime.build_workspace(
        active_group_id=runtime.session_state.get("portfolio_monitoring_active_group_id"),
        catalog_query="",
    )


def render_final_selected_portfolio_dashboard_page(
    *,
    services: PortfolioMonitoringPageServices | Any | None = None,
) -> None:
    """Render load -> React -> dispatch -> rerun with no legacy normal path."""

    runtime = services or _default_portfolio_monitoring_services()
    active_group_id = runtime.session_state.get("portfolio_monitoring_active_group_id")
    catalog_query = str(runtime.session_state.get("portfolio_monitoring_catalog_query") or "")
    try:
        workspace = runtime.build_workspace(
            active_group_id=active_group_id,
            catalog_query=catalog_query,
        )
    except Exception as exc:
        workspace = _fallback_monitoring_workspace(
            catalog_query=catalog_query,
            catalog_source_type=str(
                runtime.session_state.get("portfolio_monitoring_catalog_source_type")
                or SourceType.DIRECT_SECURITY.value
            ),
            storage_error=str(exc),
        )
    last_command = runtime.session_state.get("portfolio_monitoring_last_command")
    workspace["commands"] = [dict(last_command)] if isinstance(last_command, dict) else []
    component_value = runtime.render_workbench(workspace)
    if component_value is None:
        runtime.render_fallback(workspace, None)
        return
    event = component_value.get("event") if isinstance(component_value, dict) else None
    if not isinstance(event, dict) or not event.get("id"):
        return
    identity = _event_identity(event)
    if identity == runtime.session_state.get("portfolio_monitoring_last_event_identity"):
        return
    runtime.session_state["portfolio_monitoring_last_event_identity"] = identity
    try:
        result = _dispatch_portfolio_monitoring_event(event, runtime)
    except Exception as exc:
        command_id = str(event.get("command_id") or identity)
        runtime.session_state["portfolio_monitoring_last_command"] = {
            "command_id": command_id,
            "status": "error",
            "message": str(exc),
            "target_id": None,
        }
        runtime.rerun()
        return
    if result is not None:
        runtime.session_state["portfolio_monitoring_last_command"] = _command_projection(result)
        if str(event.get("id")) == "create_group":
            runtime.session_state["portfolio_monitoring_active_group_id"] = result.target_id
    runtime.rerun()
