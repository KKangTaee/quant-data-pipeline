"""Compact DB-only read model for both intraday comparison windows."""

from datetime import datetime, timezone
import hashlib
import json

from app.services.futures_macro_inputs import load_futures_macro_windows
from app.services.futures_macro_reading import (
    LABELS,
    RULE_VERSION,
    build_futures_macro_change_reading,
)
from app.services.futures_macro_windows import CURRENCIES
from finance.loaders.economic_cycle import load_cycle_snapshot

SCHEMA_VERSION = "futures_macro_intraday_workbench_v1"


def build_futures_macro_intraday_read_model(
    *,
    evaluation_time=None,
    window_snapshot=None,
    cycle_snapshot=None,
    rule_version=RULE_VERSION,
):
    """Keep all evidence in the identity; no persistent interpretation cache can outlive corrections."""
    snapshot = (
        window_snapshot
        if window_snapshot is not None
        else load_futures_macro_windows(evaluation_time=evaluation_time)
    )
    if cycle_snapshot is None:
        try:
            cycle_snapshot = load_cycle_snapshot() or {}
        except Exception:
            cycle_snapshot = {}
    raw = cycle_snapshot.get("observed_state_json") or {}
    try:
        state = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (ValueError, TypeError):
        state = {}
    phase = {
        "recovery": "회복",
        "expansion": "확장",
        "slowdown": "둔화",
        "contraction": "위축",
    }.get(state.get("phase"), "자료 부족")
    windows = {}
    for key, window in snapshot["windows"].items():
        prices = [
            {
                "key": s,
                "label": LABELS[s],
                "return_pct": window["returns_pct"].get(s),
                "source_symbols": [s],
            }
            for s in ("ES=F", "NQ=F", "ZN=F")
        ]
        prices += [
            {
                "key": "dollar",
                "label": "달러 대용지표",
                "return_pct": window.get("dollar_proxy_pct"),
                "source_symbols": list(CURRENCIES),
            }
        ]
        prices += [
            {
                "key": s,
                "label": LABELS[s],
                "return_pct": window["returns_pct"].get(s),
                "source_symbols": [s],
            }
            for s in ("GC=F", "CL=F")
        ]
        windows[key] = {
            **window,
            "prices": prices,
            "reading": build_futures_macro_change_reading(
                window,
                companion_window=snapshot["windows"].get("since_close")
                if key == "last_hour"
                else None,
            ),
            "evidence": {
                "source": "yfinance · 완료 5분봉",
                "rule_version": rule_version,
                "calendar_quality": snapshot.get("calendar_quality"),
                "missing_symbols": window.get("missing_symbols", []),
                "caveats": [
                    "달러 대용지표는 EUR·JPY·GBP·AUD·CAD 선물 수익률의 역방향 동일 가중 평균이며 DXY가 아닙니다.",
                    "국채선물의 가격 변화율입니다. 국채금리 bp 변화나 정책금리 확률이 아닙니다.",
                    "연속선물은 계약 교체 시 가격 차이가 생길 수 있습니다. 이상 움직임은 실제 계약과 함께 확인해야 합니다.",
                    "같은 시작·종료 시각이 없는 값은 보간하지 않습니다. 현재 가격 조합은 향후 수익률 예측이 아닙니다.",
                ],
            },
        }
    identity = hashlib.sha256(
        json.dumps(
            {
                "snapshot": snapshot,
                "cycle": cycle_snapshot,
                "rules": rule_version,
                "schema": SCHEMA_VERSION,
            },
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "input_identity": identity,
        "generated_at_utc": snapshot.get("evaluated_at_utc")
        or (evaluation_time or datetime.now(timezone.utc)).isoformat(),
        "cycle_background": {
            "state": phase,
            "as_of_date": str(cycle_snapshot.get("as_of_date") or "")[:10] or None,
            "destination": "economic_cycle",
        },
        "windows": windows,
        "research": {"status": "NOT_VALIDATED", "scope": "intraday_windows"},
        "action_boundary": "python_dispatch_only",
    }
