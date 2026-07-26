from __future__ import annotations

from typing import Any


DAILY_SWING_VALIDATION_SCHEMA_VERSION = "daily_swing_practical_validation_v1"


def _is_daily_swing_source(source: dict[str, Any]) -> bool:
    return any(
        str(dict(component or {}).get("strategy_key") or "").strip().lower()
        == "risk_on_momentum_5d"
        for component in list(dict(source or {}).get("components") or [])
    )


def _evidence_packet(
    source: dict[str, Any],
    replay_result: dict[str, Any] | None,
) -> dict[str, Any]:
    replay = dict(replay_result or {})
    replay_packet = dict(replay.get("daily_swing_evidence") or {})
    if replay_packet:
        return replay_packet
    return dict(dict(source or {}).get("daily_swing_evidence_snapshot") or {})


def build_daily_swing_validation(
    source: dict[str, Any],
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate compact Daily Swing evidence and keep universe bias explicit."""

    source_row = dict(source or {})
    applies = _is_daily_swing_source(source_row)
    if not applies:
        return {
            "schema_version": DAILY_SWING_VALIDATION_SCHEMA_VERSION,
            "applies": False,
            "status": "NOT_APPLICABLE",
            "evidence_state": "not_applicable",
            "rows": [],
            "blockers": [],
            "review_required": [],
        }
    packet = _evidence_packet(source_row, replay_result)
    if not packet:
        return {
            "schema_version": DAILY_SWING_VALIDATION_SCHEMA_VERSION,
            "applies": True,
            "status": "NEEDS_INPUT",
            "evidence_state": "missing",
            "rows": [
                {
                    "Criteria": "Compact Daily Swing evidence",
                    "Status": "NEEDS_INPUT",
                    "Evidence": "daily_swing_evidence_v1 packet 없음",
                    "Action": "Backtest Analysis에서 전략을 다시 실행하고 후보를 다시 보냅니다.",
                }
            ],
            "blockers": ["Compact Daily Swing evidence is missing."],
            "review_required": [],
        }

    performance = dict(packet.get("performance") or {})
    execution = dict(packet.get("execution") or {})
    robustness = dict(packet.get("robustness") or {})
    universe = dict(packet.get("universe") or {})
    artifact = dict(packet.get("artifact") or {})
    rows: list[dict[str, Any]] = []

    trade_count = int(performance.get("trade_count") or 0)
    holding = execution.get("average_holding_days")
    rows.append(
        {
            "Criteria": "Trade execution evidence",
            "Status": "PASS" if trade_count > 0 and holding is not None else "NEEDS_INPUT",
            "Evidence": f"trades={trade_count}, average holding={holding}",
            "Action": "거래 수와 보유기간 evidence가 없으면 runtime replay를 다시 실행합니다.",
        }
    )
    turnover = execution.get("annualized_turnover")
    rows.append(
        {
            "Criteria": "Cost / turnover realism",
            "Status": "PASS" if turnover is not None else "NEEDS_INPUT",
            "Evidence": (
                f"annualized turnover={turnover}, cost={execution.get('transaction_cost_bps')}bps, "
                f"slippage={execution.get('slippage_bps')}bps"
            ),
            "Action": "turnover가 계산되지 않으면 trade artifact와 balance curve를 확인합니다.",
        }
    )
    has_comparator = bool(dict(robustness.get("best_benchmark") or {}).get("label"))
    has_random = robustness.get("random_median_cagr") is not None
    rows.append(
        {
            "Criteria": "Benchmark / random robustness",
            "Status": "PASS" if has_comparator and has_random else "REVIEW",
            "Evidence": (
                f"intensity={robustness.get('analysis_intensity')}, "
                f"benchmark={'yes' if has_comparator else 'no'}, random={'yes' if has_random else 'no'}"
            ),
            "Action": "표준 또는 정밀 분석 evidence가 없으면 비교 검증을 추가합니다.",
        }
    )
    universe_verified = bool(universe.get("pit_membership_verified")) and bool(
        universe.get("delisting_coverage_verified")
    )
    rows.append(
        {
            "Criteria": "Universe survivorship / PIT",
            "Status": "PASS" if universe_verified else "REVIEW",
            "Evidence": (
                f"PIT membership={bool(universe.get('pit_membership_verified'))}, "
                f"delisting coverage={bool(universe.get('delisting_coverage_verified'))}"
            ),
            "Action": "현재 membership 기반 결과는 한계로 명시하고 Monitoring 조건에 남깁니다.",
        }
    )
    compact_only = artifact.get("raw_rows_embedded") is False
    rows.append(
        {
            "Criteria": "Artifact storage boundary",
            "Status": "PASS" if compact_only else "BLOCKED",
            "Evidence": f"raw rows embedded={artifact.get('raw_rows_embedded')}",
            "Action": "raw trade/scanner는 generated artifact에만 두고 compact evidence만 전달합니다.",
        }
    )
    blockers = [
        str(row["Criteria"])
        for row in rows
        if str(row.get("Status") or "") in {"BLOCKED", "NEEDS_INPUT"}
    ]
    review_required = [
        str(row["Criteria"])
        for row in rows
        if str(row.get("Status") or "") == "REVIEW"
    ]
    status = "NEEDS_INPUT" if blockers else "REVIEW" if review_required else "PASS"
    return {
        "schema_version": DAILY_SWING_VALIDATION_SCHEMA_VERSION,
        "applies": True,
        "status": status,
        "evidence_state": "computed" if review_required else "verified",
        "rows": rows,
        "blockers": blockers,
        "review_required": review_required,
        "review_limitations": list(packet.get("review_blockers") or []),
        "evidence_snapshot": packet,
        "boundaries": {
            "registry_write": False,
            "live_approval": False,
            "auto_order": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "DAILY_SWING_VALIDATION_SCHEMA_VERSION",
    "build_daily_swing_validation",
]
