"""Observed cross-asset cases and evidenced comparisons, without predictive probabilities."""

from datetime import timedelta
from math import isfinite

from app.services.futures_macro_windows import CURRENCIES, utc

RULE_VERSION = "intraday_evaluated_conditions_v2"
LABELS = {
    "ES=F": "S&P 500",
    "NQ=F": "나스닥 100",
    "ZN=F": "10년 국채선물",
    "GC=F": "금",
    "CL=F": "원유",
    "YM=F": "다우",
    "RTY=F": "소형주",
    "HG=F": "구리",
}


def direction(value):
    """Use the displayed 0.01% precision; a sign is not statistical significance."""
    try:
        value = round(float(value), 2)
        return (1 if value > 0 else -1 if value < 0 else 0) if isfinite(value) else None
    except (ValueError, TypeError, OverflowError):
        return None


EQUITY_CASES = {
    "aligned_up": (
        "두 지수 동반 상승",
        "positive",
        "S&P 500과 나스닥 선물이 함께 올라 두 핵심 지수의 상승 방향이 일치합니다. 특정 지수 하나만 오른 상황보다 관측된 상승 범위가 넓습니다.",
    ),
    "aligned_down": (
        "두 지수 동반 하락",
        "negative",
        "S&P 500과 나스닥 선물이 함께 내려 두 핵심 지수에서 약세가 관측됩니다. 한 지수에 국한된 하락으로 보기 어렵습니다.",
    ),
    "divergent": (
        "두 지수 방향 엇갈림",
        "mixed",
        "S&P 500과 나스닥 선물이 반대 방향입니다. 두 지수의 종목 구성과 비중이 달라 나타날 수 있으며, 미국 주식시장 전체의 공통 방향으로 확대할 근거는 부족합니다.",
    ),
    "one_flat": (
        "한 지수만 방향 형성",
        "mixed",
        "한 지수만 움직이고 다른 지수는 표시 단위에서 보합입니다. 두 지수의 동반 반응은 아직 확인되지 않았습니다.",
    ),
    "flat": (
        "두 지수 모두 보합",
        "neutral",
        "두 지수 모두 0.01% 표시 단위에서 보합입니다. 이 구간의 방향성은 뚜렷하지 않습니다.",
    ),
    "missing": (
        "주가지수 비교 자료 부족",
        "unavailable",
        "같은 구간의 두 지수 가격을 모두 확보하지 못해 동행 여부를 판정할 수 없습니다.",
    ),
    "unavailable": (
        "현재 동행 판정 보류",
        "unavailable",
        "자료가 오래됐거나 비교 구간을 확정하지 못했습니다. 아래 값은 마지막 저장 관측이며 현재 상태 판정은 보류합니다.",
    ),
}
MACRO_CASES = {
    "pressure": (
        "금리·달러 부담 동반",
        "negative",
        "국채선물 가격 하락은 금리 상승 압력과, 달러 대용지표 상승은 달러 강세와 들어맞습니다. 두 가격 반응이 주식에 부담을 주는 방향으로 모였습니다.",
    ),
    "relief": (
        "금리·달러 부담 완화",
        "positive",
        "국채선물 가격 상승은 금리 부담 완화와, 달러 대용지표 하락은 달러 약세와 들어맞습니다. 두 가격 반응이 주식의 부담을 덜어주는 방향으로 모였습니다.",
    ),
    "rates_relief_dollar_pressure": (
        "국채 상승 · 달러 강세",
        "mixed",
        "국채선물은 올라 금리 부담 완화 쪽이지만, 달러 대용지표도 올라 환율 부담 쪽입니다. 두 축이 엇갈리므로 주가와의 동반 반응을 각각 나눠 읽어야 합니다.",
    ),
    "rates_pressure_dollar_relief": (
        "국채 하락 · 달러 약세",
        "mixed",
        "국채선물은 내려 금리 부담 쪽이지만, 달러 대용지표도 내려 환율 부담 완화 쪽입니다. 금리와 달러가 같은 방향의 지지나 부담을 만들고 있지는 않습니다.",
    ),
    "rates_relief": (
        "국채 상승 · 달러 보합",
        "positive",
        "국채선물 상승에서 금리 부담 완화와 들어맞는 움직임이 관측됩니다. 달러는 보합이어서 두 축의 동반 완화로 해석할 수는 없습니다.",
    ),
    "rates_pressure": (
        "국채 하락 · 달러 보합",
        "negative",
        "국채선물 하락에서 금리 부담과 들어맞는 움직임이 관측됩니다. 달러는 보합이어서 환율 부담까지 동반한 조합은 아닙니다.",
    ),
    "dollar_pressure": (
        "달러 강세 · 국채 보합",
        "negative",
        "달러 대용지표는 오르고 국채선물은 보합입니다. 이 구간에서 관측되는 부담 축은 달러이며 국채가 금리 부담을 추가 확인해 주지는 않습니다.",
    ),
    "dollar_relief": (
        "달러 약세 · 국채 보합",
        "positive",
        "달러 대용지표는 내리고 국채선물은 보합입니다. 환율 부담 완화와 들어맞는 변화가 있으나 국채까지 동반한 조합은 아닙니다.",
    ),
    "neutral": (
        "국채·달러 모두 보합",
        "neutral",
        "두 지표 모두 0.01% 표시 단위에서 보합입니다. 이 구간의 주가 움직임을 금리·달러의 뚜렷한 변화와 연결할 근거가 없습니다.",
    ),
    "missing": (
        "국채·달러 비교 자료 부족",
        "unavailable",
        "국채 또는 고정된 5개 통화 구성 자료가 부족합니다. 가용 통화만으로 달러 지표를 다시 계산하지 않으며 결합 판정을 보류합니다.",
    ),
    "unavailable": (
        "현재 조합 판정 보류",
        "unavailable",
        "자료가 오래됐거나 비교 구간을 확정하지 못해 현재 금리·달러 조합 판정을 보류합니다.",
    ),
}
MACRO_DIRECTIONS = {
    (-1, 1): "pressure",
    (1, -1): "relief",
    (1, 1): "rates_relief_dollar_pressure",
    (-1, -1): "rates_pressure_dollar_relief",
    (1, 0): "rates_relief",
    (-1, 0): "rates_pressure",
    (0, 1): "dollar_pressure",
    (0, -1): "dollar_relief",
    (0, 0): "neutral",
}


def _condition(window, key):
    """Only require the inputs needed by this condition; missing FX need not hide equities."""
    values = window.get("returns_pct", {})
    missing = set(window.get("missing_symbols", []))
    if key == "equity_alignment":
        pairs = [
            ("ES=F", "S&P 500 선물", values.get("ES=F")),
            ("NQ=F", "나스닥 100 선물", values.get("NQ=F")),
        ]
        a, b = [direction(p[2]) for p in pairs]
        case = (
            "missing"
            if None in (a, b) or missing.intersection({"ES=F", "NQ=F"})
            else "aligned_up"
            if a == b == 1
            else "aligned_down"
            if a == b == -1
            else "flat"
            if a == b == 0
            else "one_flat"
            if 0 in (a, b)
            else "divergent"
        )
        cases = EQUITY_CASES
        title = "주가지수 방향은 같은가?"
    else:
        dollar = (
            None if missing.intersection(CURRENCIES) else window.get("dollar_proxy_pct")
        )
        pairs = [
            ("ZN=F", "10년 국채선물", values.get("ZN=F")),
            ("dollar", "달러 대용지표", dollar),
        ]
        case = (
            MACRO_DIRECTIONS.get(tuple(direction(p[2]) for p in pairs), "missing")
            if "ZN=F" not in missing
            else "missing"
        )
        cases = MACRO_CASES
        title = "국채·달러는 지지인가, 부담인가?"
    if window.get("status") not in {"AVAILABLE", "PARTIAL", "MARKET_CLOSED"}:
        case = "unavailable"
    if window.get("status") == "UNAVAILABLE":
        pairs = [(symbol, label, None) for symbol, label, _ in pairs]
    verdict, tone, explanation = cases[case]
    return {
        "key": key,
        "title": title,
        "case": case,
        "verdict": verdict,
        "tone": tone,
        "explanation": explanation,
        "evidence": [
            {
                "symbol": s,
                "label": label,
                "return_pct": v if direction(v) is not None else None,
                "direction": {1: "상승", -1: "하락", 0: "보합", None: "자료 부족"}[
                    direction(v)
                ],
            }
            for s, label, v in pairs
        ],
    }


def _comparison(window, current):
    """A maintained label requires actual prior endpoints of the same comparison basis."""
    prior = window.get("previous_window") or {}
    unavailable = {
        "status": "UNAVAILABLE",
        "summary": "1시간 전의 같은 기준 자료가 부족해 변화 여부는 확인하지 못했습니다.",
    }
    if current["case"] in {"missing", "unavailable"}:
        return {
            **unavailable,
            "summary": "현재 판정 자료가 부족해 이전 관측과의 비교를 보류합니다.",
        }
    try:
        start, end = utc(window["start_utc"]), utc(window["end_utc"])
        pstart, pend = utc(prior["start_utc"]), utc(prior["end_utc"])
        if (
            pend != end - timedelta(hours=1)
            or not pstart < pend
            or not (
                pstart == start
                or (
                    end - start == timedelta(hours=1)
                    and pend - pstart == timedelta(hours=1)
                )
            )
        ):
            return unavailable
    except (KeyError, ValueError, TypeError):
        return unavailable
    old = _condition(prior, current["key"])
    if old["case"] in {"missing", "unavailable"}:
        return unavailable
    # A broad category can stay divergent while the leading index reverses.
    direction_changes = [
        f"{after['label']} {before['direction']}→{after['direction']}"
        for before, after in zip(old["evidence"], current["evidence"])
        if before["direction"] != after["direction"]
    ]
    same = current["case"] == old["case"] and not direction_changes
    summary = (
        f"1시간 전에도 ‘{old['verdict']}’ 조합이었습니다. 두 비교 시점에서 같은 조합이 관측됐습니다."
        if same
        else f"1시간 전 ‘{old['verdict']}’에서 현재 ‘{current['verdict']}’으로 달라졌습니다."
    )
    if not same and current["case"] == old["case"]:
        summary = f"판정 유형은 ‘{current['verdict']}’이지만, 1시간 전과 비교하면 {', '.join(direction_changes)}으로 방향이 달라졌습니다."
    return {
        "status": "UNCHANGED" if same else "CHANGED",
        "previous_case": old["case"],
        "previous_verdict": old["verdict"],
        "previous_start_utc": prior["start_utc"],
        "previous_end_utc": prior["end_utc"],
        "previous_evidence": old["evidence"],
        "summary": summary,
    }


def build_futures_macro_change_reading(window, *, companion_window=None):
    """Explain the observed pair first, then contrast its macro context without forecasting."""
    values = window.get("returns_pct", {})
    conditions = [
        _condition(window, key) for key in ("equity_alignment", "macro_combination")
    ]
    for condition in conditions:
        condition["comparison"] = _comparison(window, condition)
    equity, macro = conditions
    eq, mc = equity["case"], macro["case"]
    facts = [
        f"{LABELS[s]} {'상승' if direction(v) == 1 else '하락' if direction(v) == -1 else '보합'} ({v:+.2f}%)"
        for s, v in values.items()
        if s in LABELS and direction(v) is not None
    ]
    dollar = window.get("dollar_proxy_pct")
    if direction(dollar) is not None:
        facts.append(
            f"달러 대용지표 {'상승' if direction(dollar) == 1 else '하락' if direction(dollar) == -1 else '보합'} ({dollar:+.2f}%)"
        )
    headline = equity["verdict"]
    counter = []
    if mc == "pressure":
        headline = (
            "금리·달러 부담 속 두 주가지수 상승"
            if eq == "aligned_up"
            else "주가지수 하락 · 금리·달러 부담 동반"
            if eq == "aligned_down"
            else f"{equity['verdict']} · 금리·달러 부담"
        )
        if eq == "aligned_up":
            counter = [
                "S&P 500과 나스닥은 상승했습니다. 부담 조합에도 현재 두 지수의 상승 방향은 확인됩니다."
            ]
    elif mc == "relief":
        headline = (
            "부담 완화 조합과 주가 하락이 엇갈립니다"
            if eq == "aligned_down"
            else "주가지수 상승 · 금리·달러 부담 완화"
            if eq == "aligned_up"
            else f"{equity['verdict']} · 부담 완화"
        )
        if eq == "aligned_down":
            counter = [
                "S&P 500과 나스닥은 하락했습니다. 완화 조합이 현재 주식 상승과 동반한 상황은 아닙니다."
            ]
    elif mc in {"rates_relief_dollar_pressure", "rates_pressure_dollar_relief"}:
        headline = f"{equity['verdict']} · 국채·달러는 엇갈림"
    else:
        headline = f"{equity['verdict']} · {macro['verdict']}"
    if eq == "aligned_up" and mc == "pressure":
        interpretation = "두 주가지수는 함께 올랐지만 국채·달러는 부담 방향입니다. 주가의 상승과 거시 가격의 지지가 일치한 구간은 아닙니다."
    elif eq == "aligned_down" and mc == "relief":
        interpretation = "국채·달러의 부담이 완화되는 조합인데도 두 주가지수는 내렸습니다. 이 구간의 약세를 금리·달러 부담만으로 설명할 수 없습니다."
    elif eq == "aligned_up" and mc == "relief":
        interpretation = "두 주가지수 상승과 국채·달러 부담 완화가 함께 관측됩니다. 선택 구간에서는 주가와 거시 가격 반응이 지지 방향으로 일치합니다."
    elif eq == "aligned_down" and mc == "pressure":
        interpretation = "두 주가지수 하락과 국채·달러 부담이 함께 관측됩니다. 선택 구간에서는 주가 약세와 거시 가격 부담이 겹쳤습니다."
    elif mc in {"rates_relief_dollar_pressure", "rates_pressure_dollar_relief"}:
        interpretation = f"{equity['verdict']}입니다. 국채·달러는 서로 다른 영향을 시사하므로, 아래에서 어느 축이 지지이고 어느 축이 부담인지 나눠 확인합니다."
    else:
        interpretation = f"주가지수는 ‘{equity['verdict']}’, 국채·달러는 ‘{macro['verdict']}’입니다. 두 확인 결과를 함께 읽되 개별 지표의 반응을 시장 전체로 확대하지 않습니다."
    tone = (
        "positive"
        if eq == "aligned_up" and mc == "relief"
        else "negative"
        if eq == "aligned_down" and mc == "pressure"
        else "mixed"
    )
    if (
        window.get("status") not in {"AVAILABLE", "MARKET_CLOSED"}
        or eq in {"missing", "unavailable"}
        or mc in {"missing", "unavailable"}
    ):
        headline = "종합 판정 보류 · 확인 가능한 지표만 표시"
        interpretation = "전체 조합을 판정할 자료가 부족합니다. 아래 두 항목에서 각각 확인 가능한 결과와 제한을 구분했습니다."
        tone = "unavailable"
        if window.get("status") == "STALE":
            interpretation = "마지막 관측이 오래되어 현재 판정을 보류합니다. 아래 수치는 표시된 과거 구간의 가격 변화입니다. 최신 데이터 반영 후 관측 시각을 확인해 주세요."
    if window.get("status") == "UNAVAILABLE":
        facts = []
    breadth = [direction(values.get(s)) for s in ("ES=F", "NQ=F", "YM=F", "RTY=F")]
    if (
        len(set(breadth)) == 1
        and breadth[0] in (-1, 1)
        and window.get("status") in {"AVAILABLE", "MARKET_CLOSED"}
    ):
        extra = f"다우·소형주까지 관측한 네 지수가 동반 {'상승' if breadth[0] == 1 else '하락'}했습니다."
        equity["explanation"] += " " + extra
        facts.append(extra)
    if (
        companion_window
        and companion_window.get("end_utc") == window.get("end_utc")
        and window.get("status") in {"AVAILABLE", "MARKET_CLOSED"}
        and companion_window.get("status") in {"AVAILABLE", "MARKET_CLOSED"}
    ):
        for symbol in ("ES=F", "NQ=F"):
            if (
                direction(values.get(symbol)) == -1
                and direction(companion_window.get("returns_pct", {}).get(symbol)) == 1
            ):
                facts.append(
                    f"{LABELS[symbol]}: 마감 대비 상승 상태에서 최근 1시간 상승분 일부 반납."
                )
    return {
        "headline": headline,
        "interpretation": interpretation,
        "tone": tone,
        "observation_facts": facts,
        "counter_evidence": counter,
        "condition_results": conditions,
    }
