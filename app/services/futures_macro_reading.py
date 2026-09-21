"""Deterministic interpretation of observed prices, separate from predictive research."""

from math import isfinite

RULE_VERSION = "intraday_price_combinations_v1"
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
    """Direction follows the displayed 0.01% precision, not an economic threshold."""
    try:
        value = round(float(value), 2)
        return (1 if value > 0 else -1 if value < 0 else 0) if isfinite(value) else None
    except (ValueError, TypeError, OverflowError):
        return None


def build_futures_macro_change_reading(window, *, companion_window=None):
    values = window.get("returns_pct", {})
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
    result = {
        "headline": "자산별 방향이 엇갈립니다",
        "observation_facts": facts,
        "interpretation": "관측한 가격 조합만으로 주식시장에 공통된 부담이나 지지를 단정하기 어렵습니다.",
        "counter_evidence": [],
        "next_checks": [
            "다음 관측에서도 S&P 500과 나스닥의 방향이 같은지 확인합니다.",
            "국채 가격과 달러 대용지표의 조합이 유지되는지 확인합니다.",
        ],
    }
    if window.get("status") not in {"AVAILABLE", "MARKET_CLOSED"} or window.get(
        "missing_symbols"
    ):
        result.update(
            headline="현재 조합 해석 보류",
            interpretation="같은 시각의 충분히 최근인 자료가 확보되지 않았습니다. 아래 값은 마지막 저장 관측입니다.",
            next_checks=[
                "최신 데이터 반영 후 관측 종료 시각을 확인합니다.",
                "누락 자료와 비교 시작 시각이 확보되면 두 구간을 다시 비교합니다.",
            ],
        )
        return result
    es, nq, zn, usd = [
        direction(v)
        for v in (values.get("ES=F"), values.get("NQ=F"), values.get("ZN=F"), dollar)
    ]
    if None in (es, nq, zn, usd):
        result.update(
            headline="현재 조합 해석 보류",
            interpretation="주가지수·국채·달러를 함께 해석할 자료가 부족합니다.",
        )
        return result
    pressure, relief = zn == -1 and usd == 1, zn == 1 and usd == -1
    if pressure:
        result.update(
            headline="금리·달러 부담과 들어맞는 조합",
            interpretation="국채선물 가격 하락과 달러 대용지표 상승은 주식의 할인율·환율 부담과 들어맞습니다. 실제 금리 변화나 주가 하락의 원인을 확정한 것은 아닙니다.",
        )
        if es == nq == 1:
            result["headline"] = "금리·달러 부담 속 두 주가지수 상승"
            result["counter_evidence"] = [
                "S&P 500과 나스닥은 상승했습니다. 부담 조합이 주가 약세로 이어진 관측은 아닙니다."
            ]
        result["next_checks"] = [
            "S&P 500·나스닥에서 관측한 반응이 다우·소형주에도 나타나는지 확인합니다.",
            "국채 하락·달러 상승 조합이 풀리는지 확인합니다.",
        ]
    elif relief:
        result.update(
            headline="금리·환율 부담 완화와 들어맞는 조합",
            interpretation="국채선물 가격 상승과 달러 대용지표 하락은 주식에 대한 금리·환율 부담 완화와 들어맞습니다. 경기 개선이나 이후 상승을 확정하지 않습니다.",
        )
        if es == nq == -1:
            result["headline"] = "부담 완화 조합과 주가 하락이 엇갈립니다"
            result["counter_evidence"] = [
                "S&P 500과 나스닥은 하락했습니다. 완화 조합만으로 주식 지지가 확인됐다고 보기 어렵습니다."
            ]
        result["next_checks"] = [
            "S&P 500과 나스닥이 함께 상승하는지 확인합니다.",
            "국채 상승·달러 하락 조합이 다음 관측에도 유지되는지 확인합니다.",
        ]
    elif es == nq and es:
        result["headline"] = f"S&P 500·나스닥 동반 {'상승' if es == 1 else '하락'}"
    breadth = [direction(values.get(s)) for s in ("ES=F", "NQ=F", "YM=F", "RTY=F")]
    if len(set(breadth)) == 1 and breadth[0] in (-1, 1):
        facts.append(
            f"관측한 네 지수가 동반 {'상승' if breadth[0] == 1 else '하락'}했습니다."
        )
    elif es != nq:
        result["counter_evidence"].append(
            "S&P 500과 나스닥의 방향이 달라 주식시장 전체의 반응으로 확대하기 어렵습니다."
        )
    if (
        companion_window
        and companion_window.get("end_utc") == window.get("end_utc")
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
    return result
