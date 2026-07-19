from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Iterable

import pandas as pd

from app.runtime.backtest.stores.portfolio_selection import (
    load_current_final_selection_decisions,
)

from .persistence import MonitoringItemRecord
from .valuation import CorporateActionReview, ItemValueLane


DecisionLoader = Callable[[], Iterable[dict[str, Any]]]
ReplayRunner = Callable[..., dict[str, Any]]


class SelectedStrategyInputError(ValueError):
    pass


class SelectedStrategyReplayError(RuntimeError):
    def __init__(self, readiness: "SelectedStrategyReadiness") -> None:
        super().__init__("; ".join(readiness.blockers) or "Selected strategy replay failed.")
        self.readiness = readiness


@dataclass(frozen=True)
class SelectedStrategyReadiness:
    status: str
    blockers: tuple[str, ...]
    source_dates: dict[str, str | None]


@dataclass(frozen=True)
class SelectedStrategyContract:
    decision_id: str
    decision_row: dict[str, Any] | None
    readiness: SelectedStrategyReadiness


def _default_replay_runner(
    row: dict[str, Any],
    *,
    start: str,
    end: str,
    initial_capital: float,
) -> dict[str, Any]:
    from app.runtime.backtest.read_models.final_selected_portfolios import (
        build_selected_portfolio_performance_recheck,
    )

    return build_selected_portfolio_performance_recheck(
        row,
        start=start,
        end=end,
        initial_capital=initial_capital,
    )


def _clean_blockers(values: Iterable[Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in blockers:
            blockers.append(text)
    return tuple(blockers)


def _selected_components(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = dict(row.get("raw_decision") or row)
    values = raw.get("selected_components")
    if not isinstance(values, list):
        return []
    return [dict(value) for value in values if isinstance(value, dict)]


class SelectedStrategyReplayAdapter:
    """Adapt the legacy Final Review replay into a stable monitoring value lane."""

    def __init__(
        self,
        *,
        decision_loader: DecisionLoader = load_current_final_selection_decisions,
        replay_runner: ReplayRunner = _default_replay_runner,
    ) -> None:
        self._decision_loader = decision_loader
        self._replay_runner = replay_runner

    def load_candidate_contract(self, decision_id: str) -> SelectedStrategyContract:
        clean_id = str(decision_id or "").strip()
        rows = [
            dict(row)
            for row in self._decision_loader()
            if str(row.get("decision_id") or "").strip() == clean_id
        ]
        if not rows:
            return SelectedStrategyContract(
                decision_id=clean_id,
                decision_row=None,
                readiness=SelectedStrategyReadiness(
                    status="BLOCKED",
                    blockers=("Final Review decision was not found.",),
                    source_dates={},
                ),
            )
        row = rows[0]
        source_dates = {"decision_updated_at": str(row.get("updated_at") or "") or None}
        if row.get("monitoring_candidate") is not True:
            return SelectedStrategyContract(
                decision_id=clean_id,
                decision_row=row,
                readiness=SelectedStrategyReadiness(
                    status="BLOCKED",
                    blockers=("Final Review decision is not an authoritative monitoring candidate.",),
                    source_dates=source_dates,
                ),
            )
        if not _selected_components(row):
            return SelectedStrategyContract(
                decision_id=clean_id,
                decision_row=row,
                readiness=SelectedStrategyReadiness(
                    status="BLOCKED",
                    blockers=("Selected strategy replay contract has no selected components.",),
                    source_dates=source_dates,
                ),
            )
        return SelectedStrategyContract(
            decision_id=clean_id,
            decision_row=row,
            readiness=SelectedStrategyReadiness(
                status="READY",
                blockers=(),
                source_dates=source_dates,
            ),
        )

    def build_value_lane(
        self,
        item: MonitoringItemRecord,
        end_date: date | None = None,
    ) -> ItemValueLane:
        if item.source_type != "selected_strategy" or item.instrument_kind != "strategy":
            raise SelectedStrategyInputError("A selected strategy monitoring item is required.")
        if item.funding_mode != "fixed_notional" or item.input_notional is None:
            raise SelectedStrategyInputError("Selected strategy supports fixed notional only.")
        if item.input_notional <= 0 or item.initial_capital <= 0:
            raise SelectedStrategyInputError("Selected strategy fixed notional must be positive.")

        contract = self.load_candidate_contract(item.source_ref)
        if contract.readiness.status != "READY" or contract.decision_row is None:
            raise SelectedStrategyReplayError(contract.readiness)

        resolved_end = end_date or date.today()
        if resolved_end < item.effective_start_date:
            raise SelectedStrategyInputError("Replay end date cannot precede the effective start date.")
        result = self._replay_runner(
            contract.decision_row,
            start=item.effective_start_date.isoformat(),
            end=resolved_end.isoformat(),
            initial_capital=float(item.initial_capital),
        )
        blockers = list(result.get("blockers") or [])
        error = str(result.get("error") or "").strip()
        if error:
            blockers.insert(0, error)
        result_status = str(result.get("status") or "error").strip().lower()
        replay_frame = result.get("portfolio_result_df")
        if result_status not in {"ok", "partial"} or not isinstance(replay_frame, pd.DataFrame):
            readiness = SelectedStrategyReadiness(
                status="BLOCKED",
                blockers=_clean_blockers(blockers or ["Selected strategy replay did not return a value curve."]),
                source_dates=dict(contract.readiness.source_dates),
            )
            raise SelectedStrategyReplayError(readiness)

        frame = replay_frame.copy()
        if "Date" not in frame.columns or "Total Balance" not in frame.columns:
            raise SelectedStrategyReplayError(
                SelectedStrategyReadiness(
                    status="BLOCKED",
                    blockers=("Selected strategy replay curve contract is invalid.",),
                    source_dates=dict(contract.readiness.source_dates),
                )
            )
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.normalize()
        frame["Total Balance"] = pd.to_numeric(frame["Total Balance"], errors="coerce")
        frame = frame.dropna(subset=["Date", "Total Balance"])
        frame = frame.loc[frame["Total Balance"] > 0].sort_values("Date")
        frame = frame.drop_duplicates(subset=["Date"], keep="last").reset_index(drop=True)
        if frame.empty:
            raise SelectedStrategyReplayError(
                SelectedStrategyReadiness(
                    status="BLOCKED",
                    blockers=("Selected strategy replay value curve is empty.",),
                    source_dates=dict(contract.readiness.source_dates),
                )
            )

        normalized = frame["Total Balance"] / float(frame.iloc[0]["Total Balance"])
        total_value = normalized * float(item.initial_capital)
        source_dates = {
            **contract.readiness.source_dates,
            "replay_start": frame.iloc[0]["Date"].date().isoformat(),
            "replay_end": frame.iloc[-1]["Date"].date().isoformat(),
        }
        readiness = SelectedStrategyReadiness(
            status="REVIEW" if blockers or result_status == "partial" else "READY",
            blockers=_clean_blockers(blockers),
            source_dates=source_dates,
        )
        lane_status = "data_review" if readiness.status == "REVIEW" else item.status
        curve = pd.DataFrame(
            {
                "date": frame["Date"],
                "effective_units": [None] * len(frame),
                "market_value": total_value,
                "dividend_cash": [0.0] * len(frame),
                "total_value": total_value,
                "raw_return_index": normalized,
                "adjusted_return_index": [None] * len(frame),
                "data_status": [lane_status] * len(frame),
            }
        )
        return ItemValueLane(
            monitoring_item_id=item.monitoring_item_id,
            source_ref=item.source_ref,
            effective_start_date=frame.iloc[0]["Date"].date(),
            latest_usable_date=frame.iloc[-1]["Date"].date(),
            initial_capital=item.initial_capital,
            status=lane_status,
            curve=curve,
            review=CorporateActionReview(
                status="NOT_APPLICABLE",
                total_return_gap=None,
                max_session_gap=None,
                reasons=("Selected strategy uses its stored replay contract.",),
            ),
            readiness=readiness,
        )
