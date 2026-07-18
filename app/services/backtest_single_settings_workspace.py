"""Pure schema and validation contract for Level1 single-strategy settings."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any, Mapping, Sequence


SETTINGS_SCHEMA_VERSION = "backtest_single_settings_workspace_v2"
ALLOWED_CONTROLS = frozenset(
    {
        "date",
        "number",
        "text",
        "single_select",
        "multi_select",
        "segmented",
        "toggle",
    }
)

SINGLE_SETTINGS_CONCRETE_KEYS: dict[str, tuple[str | None, ...]] = {
    "Equal Weight": (None,),
    "GTAA": (None,),
    "Global Relative Strength": (None,),
    "Risk Parity": (None,),
    "Dual Momentum": (None,),
    "Risk-On Momentum 5D": (None,),
    "Quality": ("Annual", "Quarterly", "Snapshot"),
    "Value": ("Annual", "Quarterly"),
    "Quality + Value": ("Annual", "Quarterly"),
}

_CONCRETE_STRATEGY_KEYS: dict[tuple[str, str | None], str] = {
    ("Equal Weight", None): "equal_weight",
    ("GTAA", None): "gtaa",
    ("Global Relative Strength", None): "global_relative_strength",
    ("Risk Parity", None): "risk_parity_trend",
    ("Dual Momentum", None): "dual_momentum",
    ("Risk-On Momentum 5D", None): "risk_on_momentum_5d",
    ("Quality", "Annual"): "quality_snapshot_strict_annual",
    ("Quality", "Quarterly"): "quality_snapshot_strict_quarterly_prototype",
    ("Quality", "Snapshot"): "quality_snapshot",
    ("Value", "Annual"): "value_snapshot_strict_annual",
    ("Value", "Quarterly"): "value_snapshot_strict_quarterly_prototype",
    ("Quality + Value", "Annual"): "quality_value_snapshot_strict_annual",
    (
        "Quality + Value",
        "Quarterly",
    ): "quality_value_snapshot_strict_quarterly_prototype",
}

_PROFILES: dict[str, dict[str, str]] = {
    "Equal Weight": {
        "display_name": "Equal Weight",
        "purpose_label": "분산·기본 포트폴리오",
        "maturity_label": "운영 전략",
        "description": "선택한 자산을 같은 비중으로 보유하고 정해진 주기로 조정합니다.",
        "selection_rule": "지정한 투자 대상 전체를 같은 비중으로 선택합니다.",
        "holding_rule": "설정한 리밸런싱 간격마다 목표 비중으로 되돌립니다.",
        "risk_note": "투자 대상 구성과 거래비용이 결과에 직접 영향을 줍니다.",
    },
    "GTAA": {
        "display_name": "GTAA",
        "purpose_label": "모멘텀·전술 자산배분",
        "maturity_label": "운영 전략",
        "description": "자산군의 상대강도와 추세를 함께 비교해 공격·방어 자산을 선택합니다.",
        "selection_rule": "여러 관찰 기간의 수익률과 추세 기준으로 상위 자산을 고릅니다.",
        "holding_rule": "정해진 신호 갱신 주기마다 순위와 방어 전환 여부를 다시 계산합니다.",
        "risk_note": "점수 기간, 추세선, 방어 규칙을 함께 확인해야 합니다.",
    },
    "Global Relative Strength": {
        "display_name": "Global Relative Strength",
        "purpose_label": "글로벌 상대강도",
        "maturity_label": "운영 전략",
        "description": "글로벌 자산의 상대 성과를 비교해 강한 자산을 보유합니다.",
        "selection_rule": "설정한 관찰 기간의 상대강도 상위 자산을 선택합니다.",
        "holding_rule": "신호 갱신 시 순위를 다시 계산하고 필요하면 현금성 자산으로 이동합니다.",
        "risk_note": "관찰 기간과 추세 필터가 교체 빈도와 낙폭에 영향을 줍니다.",
    },
    "Risk Parity": {
        "display_name": "Risk Parity",
        "purpose_label": "위험 균형 자산배분",
        "maturity_label": "운영 전략",
        "description": "자산별 변동성을 반영해 위험 기여도를 균형 있게 배분합니다.",
        "selection_rule": "선택한 자산의 변동성과 추세 조건을 함께 확인합니다.",
        "holding_rule": "변동성 추정치와 리밸런싱 주기에 따라 목표 비중을 갱신합니다.",
        "risk_note": "변동성 관찰 기간과 거래비용 가정에 민감합니다.",
    },
    "Dual Momentum": {
        "display_name": "Dual Momentum",
        "purpose_label": "절대·상대 모멘텀",
        "maturity_label": "운영 전략",
        "description": "상대적으로 강하면서 절대 추세도 양호한 자산을 선택합니다.",
        "selection_rule": "상대 순위와 기준 자산 대비 절대 모멘텀을 함께 적용합니다.",
        "holding_rule": "신호 주기마다 상위 자산과 방어 자산 전환 여부를 갱신합니다.",
        "risk_note": "급격한 추세 반전에서는 신호 지연이 발생할 수 있습니다.",
    },
    "Risk-On Momentum 5D": {
        "display_name": "Risk-On Momentum 5D",
        "purpose_label": "단기 위험선호 모멘텀",
        "maturity_label": "개발 중 전략",
        "description": "단기 모멘텀과 시장 위험선호 조건을 결합한 개발 단계 전략입니다.",
        "selection_rule": "가격·유동성·거시 필터를 통과한 단기 모멘텀 후보를 선택합니다.",
        "holding_rule": "진입·청산·손절·익절 규칙으로 포지션을 관리합니다.",
        "risk_note": "개발 중이므로 Level2 후보 승격 전에 실행 근거를 더 검토해야 합니다.",
    },
    "Quality": {
        "display_name": "Quality",
        "purpose_label": "기업 품질 팩터",
        "maturity_label": "검증 전략",
        "description": "재무 품질 근거가 충분한 기업을 선별합니다.",
        "selection_rule": "point-in-time 재무지표와 품질 팩터를 결합해 상위 종목을 고릅니다.",
        "holding_rule": "재무 공시 주기와 월별 universe 기준에 맞춰 후보를 갱신합니다.",
        "risk_note": "재무 데이터 시점과 coverage 부족 종목 처리 기준을 확인해야 합니다.",
    },
    "Value": {
        "display_name": "Value",
        "purpose_label": "기업 가치 팩터",
        "maturity_label": "검증 전략",
        "description": "가격 대비 기업가치가 낮은 후보를 point-in-time 기준으로 선별합니다.",
        "selection_rule": "복수 가치 팩터와 데이터 coverage를 결합해 상위 종목을 고릅니다.",
        "holding_rule": "재무 공시와 월별 universe 변화에 맞춰 후보를 다시 평가합니다.",
        "risk_note": "가치 함정과 데이터 결측 처리 기준을 함께 확인해야 합니다.",
    },
    "Quality + Value": {
        "display_name": "Quality + Value",
        "purpose_label": "품질·가치 복합 팩터",
        "maturity_label": "검증 전략",
        "description": "재무 품질과 가격 매력을 함께 만족하는 기업을 선별합니다.",
        "selection_rule": "품질·가치 팩터와 coverage 기준을 결합해 최종 후보를 고릅니다.",
        "holding_rule": "공시 시점과 월별 universe 기준에 맞춰 복합 점수를 갱신합니다.",
        "risk_note": "팩터 균형과 결측 종목 대체 규칙을 함께 확인해야 합니다.",
    },
}

_SECTION_METADATA = {
    "execution": (
        "핵심 실행 설정",
        "검증 기간과 결과를 다시 계산하는 기본 주기를 정합니다.",
    ),
    "universe": (
        "투자 대상 Universe",
        "전략이 실제로 비교하고 선택할 자산 범위를 정합니다.",
    ),
    "rules": (
        "선택·보유 규칙",
        "어떤 후보를 선택하고 언제 교체할지 정합니다.",
    ),
    "risk": (
        "비용·위험 기준",
        "실행 비용과 결과를 제한하는 위험 기준을 정합니다.",
    ),
}

_VARIANT_LABELS = {
    "Annual": "연간 재무 기준",
    "Quarterly": "분기 재무 기준",
    "Snapshot": "기존 스냅샷",
}


class SettingsValidationError(ValueError):
    """Raised when a submitted settings draft cannot become an execution payload."""

    def __init__(self, errors: Mapping[str, str]):
        self.errors = dict(errors)
        super().__init__("설정값을 확인해 주세요.")


def _option(value: object, label: str | None = None) -> dict[str, object]:
    return {"value": deepcopy(value), "label": label or str(value)}


def _field(
    field_id: str,
    payload_key: str,
    label: str,
    control: str,
    default: object,
    help_text: str,
    **metadata: object,
) -> dict[str, object]:
    if control not in ALLOWED_CONTROLS:
        raise ValueError(f"지원하지 않는 설정 control입니다: {control}")
    result: dict[str, object] = {
        "field_id": field_id,
        "payload_key": payload_key,
        "label": label,
        "control": control,
        "value": deepcopy(default),
        "required": bool(metadata.pop("required", True)),
        "help": help_text,
    }
    result.update({key: deepcopy(value) for key, value in metadata.items()})
    return result


def _section(section_id: str, fields: Sequence[Mapping[str, object]]) -> dict[str, object]:
    title, description = _SECTION_METADATA[section_id]
    return {
        "section_id": section_id,
        "title": title,
        "description": description,
        "fields": [deepcopy(dict(item)) for item in fields],
        "disclosures": [],
    }


def _runtime_sequence(
    runtime_options: Mapping[str, object],
    key: str,
    fallback: Sequence[object],
) -> list[object]:
    candidate = runtime_options.get(key)
    if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes)):
        return list(candidate)
    return list(fallback)


def _preset_catalog(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> dict[str, list[str]]:
    all_presets = runtime_options.get("presets")
    if not isinstance(all_presets, Mapping):
        return {"기본 구성": []}
    strategy_presets = all_presets.get(strategy_choice)
    if not isinstance(strategy_presets, Mapping):
        return {"기본 구성": []}
    return {
        str(name): [str(ticker) for ticker in members]
        for name, members in strategy_presets.items()
        if isinstance(members, Sequence) and not isinstance(members, (str, bytes))
    } or {"기본 구성": []}


def _date_fields(*, start: str = "2016-01-01") -> list[dict[str, object]]:
    return [
        _field(
            "start",
            "start",
            "검증 시작일",
            "date",
            start,
            "전략 계산을 시작할 날짜입니다.",
        ),
        _field(
            "end",
            "end",
            "검증 종료일",
            "date",
            "2026-07-18",
            "전략 계산에 포함할 마지막 날짜입니다.",
        ),
    ]


def _standard_universe_fields(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> list[dict[str, object]]:
    presets = _preset_catalog(strategy_choice, runtime_options)
    preset_names = list(presets)
    tickers = [str(value) for value in _runtime_sequence(runtime_options, "tickers", [])]
    default_manual = list(next(iter(presets.values()), []))
    return [
        _field(
            "universe_mode",
            "universe_mode",
            "투자 대상 선택 방식",
            "segmented",
            "preset",
            "기본 구성 또는 직접 입력 중 하나를 선택합니다.",
            options=[
                _option("preset", "기본 구성"),
                _option("manual_tickers", "직접 입력"),
            ],
        ),
        _field(
            "preset_name",
            "preset_name",
            "기본 구성",
            "single_select",
            preset_names[0],
            "검증 목적에 맞는 기본 자산 구성을 선택합니다.",
            options=[_option(name) for name in preset_names],
            visible_when={"universe_mode": "preset"},
        ),
        _field(
            "tickers",
            "tickers",
            "직접 입력할 종목",
            "multi_select",
            default_manual,
            "직접 검증할 종목을 하나 이상 선택합니다.",
            options=[_option(ticker) for ticker in tickers],
            visible_when={"universe_mode": "manual_tickers"},
        ),
    ]


def _etf_risk_fields(
    runtime_options: Mapping[str, object],
) -> list[dict[str, object]]:
    benchmarks = [
        str(value)
        for value in _runtime_sequence(runtime_options, "benchmarks", ["SPY"])
    ]
    benchmark_default = benchmarks[0] if benchmarks else "SPY"
    return [
        _field(
            "min_price_filter",
            "min_price_filter",
            "최소 가격",
            "number",
            5.0,
            "이 가격보다 낮은 자산은 해당 시점 후보에서 제외합니다.",
            min=0.0,
            max=1000.0,
            step=1.0,
            advanced=True,
        ),
        _field(
            "transaction_cost_bps",
            "transaction_cost_bps",
            "거래비용(bps)",
            "number",
            10.0,
            "매매 때 반영할 편도 거래비용 가정입니다.",
            min=0.0,
            max=500.0,
            step=1.0,
        ),
        _field(
            "benchmark_ticker",
            "benchmark_ticker",
            "비교 기준 자산",
            "single_select",
            benchmark_default,
            "전략 결과와 비교할 대표 자산입니다.",
            options=[_option(value) for value in benchmarks] or [_option("SPY")],
        ),
        _field(
            "promotion_min_etf_aum_b",
            "promotion_min_etf_aum_b",
            "최소 ETF 운용자산($B)",
            "number",
            1.0,
            "현재 운용 가능성을 판단할 최소 ETF 운용자산 기준입니다.",
            min=0.0,
            max=1000.0,
            step=0.5,
            advanced=True,
        ),
        _field(
            "promotion_max_bid_ask_spread_pct",
            "promotion_max_bid_ask_spread_pct",
            "최대 호가 스프레드 비율",
            "number",
            0.005,
            "현재 매수·매도 호가 차이를 허용할 최대 비율입니다.",
            min=0.0,
            max=1.0,
            step=0.0005,
            advanced=True,
        ),
    ]


def _guardrail_fields() -> list[dict[str, object]]:
    return [
        _field(
            "underperformance_guardrail_enabled",
            "underperformance_guardrail_enabled",
            "상대성과 방어 규칙 사용",
            "toggle",
            False,
            "기준 자산보다 계속 약할 때 현금으로 물러나는 규칙입니다.",
            advanced=True,
        ),
        _field(
            "underperformance_guardrail_window_months",
            "underperformance_guardrail_window_months",
            "상대성과 확인 기간(개월)",
            "number",
            12,
            "상대성과 악화를 판단할 최근 개월 수입니다.",
            min=3,
            max=36,
            step=1,
            integer=True,
            advanced=True,
        ),
        _field(
            "underperformance_guardrail_threshold",
            "underperformance_guardrail_threshold",
            "상대성과 하한(%)",
            "number",
            -10.0,
            "기준 자산 대비 성과가 이 값 이하이면 방어 규칙을 적용합니다.",
            min=-50.0,
            max=0.0,
            step=1.0,
            payload_scale=0.01,
            advanced=True,
        ),
        _field(
            "drawdown_guardrail_enabled",
            "drawdown_guardrail_enabled",
            "낙폭 방어 규칙 사용",
            "toggle",
            False,
            "최근 낙폭이 깊어질 때 현금으로 물러나는 규칙입니다.",
            advanced=True,
        ),
        _field(
            "drawdown_guardrail_window_months",
            "drawdown_guardrail_window_months",
            "낙폭 확인 기간(개월)",
            "number",
            12,
            "전략과 기준 자산의 낙폭을 비교할 최근 개월 수입니다.",
            min=3,
            max=36,
            step=1,
            integer=True,
            advanced=True,
        ),
        _field(
            "drawdown_guardrail_strategy_threshold",
            "drawdown_guardrail_strategy_threshold",
            "전략 낙폭 하한(%)",
            "number",
            -35.0,
            "전략 낙폭이 이 값보다 깊으면 방어 규칙을 적용합니다.",
            min=-80.0,
            max=0.0,
            step=1.0,
            payload_scale=0.01,
            advanced=True,
        ),
        _field(
            "drawdown_guardrail_gap_threshold",
            "drawdown_guardrail_gap_threshold",
            "기준 대비 낙폭 차이(%)",
            "number",
            8.0,
            "전략 낙폭이 기준 자산보다 더 나쁜 허용 차이입니다.",
            min=0.0,
            max=50.0,
            step=1.0,
            payload_scale=0.01,
            advanced=True,
        ),
    ]


def _score_field(runtime_options: Mapping[str, object]) -> dict[str, object]:
    horizons = [
        int(value)
        for value in _runtime_sequence(
            runtime_options,
            "score_horizons",
            [1, 3, 6, 12],
        )
    ]
    return _field(
        "score_lookback_months",
        "score_lookback_months",
        "상대강도 계산 기간",
        "multi_select",
        [1, 3, 6, 12],
        "선택한 기간의 수익률을 같은 비중으로 점수에 반영합니다.",
        options=[_option(value, f"{value}개월") for value in horizons],
    )


def _standard_tactical_sections(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> list[dict[str, object]]:
    execution = _date_fields()
    universe = _standard_universe_fields(strategy_choice, runtime_options)
    rules: list[dict[str, object]] = []
    risk = _etf_risk_fields(runtime_options)

    if strategy_choice == "Equal Weight":
        execution.append(
            _field(
                "rebalance_interval",
                "rebalance_interval",
                "리밸런싱 간격(개월)",
                "number",
                12,
                "선택 비중을 다시 맞추는 개월 간격입니다.",
                min=1,
                max=36,
                step=1,
                integer=True,
            )
        )
    elif strategy_choice == "GTAA":
        execution.extend(
            [
                _field(
                    "top",
                    "top",
                    "보유 자산 수",
                    "number",
                    3,
                    "상대강도 상위 자산을 몇 개까지 보유할지 정합니다.",
                    min=1,
                    max=12,
                    step=1,
                    integer=True,
                ),
                _field(
                    "interval",
                    "interval",
                    "신호 갱신 간격(개월)",
                    "number",
                    1,
                    "상대강도와 위험회피 조건을 다시 계산하는 주기입니다.",
                    min=1,
                    max=12,
                    step=1,
                    integer=True,
                ),
            ]
        )
        regime_benchmarks = [
            str(value)
            for value in _runtime_sequence(
                runtime_options,
                "market_regime_benchmarks",
                ["SPY", "QQQ", "VTI", "IWM"],
            )
        ]
        rules.extend(
            [
                _score_field(runtime_options),
                _field(
                    "trend_filter_window",
                    "trend_filter_window",
                    "추세 확인 기간(거래일)",
                    "number",
                    200,
                    "후보 가격이 통과해야 하는 이동평균 기간입니다.",
                    min=20,
                    max=400,
                    step=10,
                    integer=True,
                ),
                _field(
                    "risk_off_mode",
                    "risk_off_mode",
                    "위험회피 전환 방식",
                    "single_select",
                    "cash_only",
                    "위험 구간에 현금 또는 방어 채권을 사용할지 정합니다.",
                    options=[
                        _option("cash_only", "현금 보유"),
                        _option("defensive_bond_preference", "방어 채권 우선"),
                    ],
                    advanced=True,
                ),
                _field(
                    "defensive_tickers",
                    "defensive_tickers",
                    "방어 자산",
                    "multi_select",
                    ["TLT", "IEF", "LQD"],
                    "위험 구간에서 사용할 방어 채권 후보입니다.",
                    options=[
                        _option(value)
                        for value in _runtime_sequence(
                            runtime_options,
                            "tickers",
                            ["TLT", "IEF", "LQD"],
                        )
                    ],
                    advanced=True,
                ),
                _field(
                    "market_regime_enabled",
                    "market_regime_enabled",
                    "시장 국면 필터 사용",
                    "toggle",
                    False,
                    "기준 자산의 추세로 위험 국면을 추가 확인합니다.",
                    advanced=True,
                ),
                _field(
                    "market_regime_window",
                    "market_regime_window",
                    "시장 국면 확인 기간",
                    "number",
                    200,
                    "시장 국면 기준 이동평균 기간입니다.",
                    min=20,
                    max=400,
                    step=10,
                    integer=True,
                    advanced=True,
                ),
                _field(
                    "market_regime_benchmark",
                    "market_regime_benchmark",
                    "시장 국면 기준 자산",
                    "single_select",
                    "SPY",
                    "위험 국면을 판단할 대표 자산입니다.",
                    options=[_option(value) for value in regime_benchmarks],
                    advanced=True,
                ),
                _field(
                    "crash_guardrail_enabled",
                    "crash_guardrail_enabled",
                    "급락 방어 규칙 사용",
                    "toggle",
                    False,
                    "최근 고점 대비 급락 시 위험 구간으로 전환합니다.",
                    advanced=True,
                ),
                _field(
                    "crash_guardrail_drawdown_threshold",
                    "crash_guardrail_drawdown_threshold",
                    "급락 판단 낙폭(%)",
                    "number",
                    15.0,
                    "최근 고점 대비 이 비율 이상 하락하면 급락으로 판단합니다.",
                    min=1.0,
                    max=80.0,
                    step=1.0,
                    payload_scale=0.01,
                    advanced=True,
                ),
                _field(
                    "crash_guardrail_lookback_months",
                    "crash_guardrail_lookback_months",
                    "급락 확인 기간(개월)",
                    "number",
                    12,
                    "최근 고점을 찾을 기간입니다.",
                    min=3,
                    max=36,
                    step=1,
                    integer=True,
                    advanced=True,
                ),
            ]
        )
        risk.insert(
            1,
            _field(
                "min_avg_dollar_volume_20d_m_filter",
                "min_avg_dollar_volume_20d_m_filter",
                "최근 20일 최소 평균 거래대금($M)",
                "number",
                0.0,
                "기준보다 거래대금이 낮은 ETF를 후보에서 제외합니다.",
                min=0.0,
                max=100000.0,
                step=5.0,
                advanced=True,
            ),
        )
        risk.extend(_guardrail_fields())
    elif strategy_choice == "Global Relative Strength":
        execution.extend(
            [
                _field(
                    "top",
                    "top",
                    "보유 자산 수",
                    "number",
                    4,
                    "상대강도 상위 자산을 몇 개까지 보유할지 정합니다.",
                    min=1,
                    max=12,
                    step=1,
                    integer=True,
                ),
                _field(
                    "interval",
                    "interval",
                    "신호 갱신 간격(개월)",
                    "number",
                    1,
                    "상대강도를 다시 계산하는 주기입니다.",
                    min=1,
                    max=12,
                    step=1,
                    integer=True,
                ),
            ]
        )
        rules.extend(
            [
                _field(
                    "cash_ticker",
                    "cash_ticker",
                    "방어 자산 ticker",
                    "text",
                    "BIL",
                    "추세 기준을 통과하지 못할 때 사용할 현금성 자산입니다.",
                    uppercase=True,
                ),
                _score_field(runtime_options),
                _field(
                    "trend_filter_window",
                    "trend_filter_window",
                    "추세 확인 기간(거래일)",
                    "number",
                    200,
                    "가격이 이 이동평균 아래이면 방어 자산으로 이동합니다.",
                    min=20,
                    max=400,
                    step=10,
                    integer=True,
                ),
            ]
        )
    elif strategy_choice == "Risk Parity":
        execution.extend(
            [
                _field(
                    "rebalance_interval",
                    "rebalance_interval",
                    "리밸런싱 간격(개월)",
                    "number",
                    1,
                    "목표 위험 비중을 다시 계산하는 주기입니다.",
                    min=1,
                    max=12,
                    step=1,
                    integer=True,
                ),
                _field(
                    "vol_window",
                    "vol_window",
                    "변동성 계산 기간(개월)",
                    "number",
                    6,
                    "자산별 위험을 추정할 최근 개월 수입니다.",
                    min=1,
                    max=24,
                    step=1,
                    integer=True,
                ),
            ]
        )
        risk.extend(_guardrail_fields())
    elif strategy_choice == "Dual Momentum":
        execution.extend(
            [
                _field(
                    "top",
                    "top",
                    "보유 자산 수",
                    "number",
                    1,
                    "절대·상대 모멘텀을 통과한 상위 자산 보유 수입니다.",
                    min=1,
                    max=5,
                    step=1,
                    integer=True,
                ),
                _field(
                    "rebalance_interval",
                    "rebalance_interval",
                    "리밸런싱 간격(개월)",
                    "number",
                    1,
                    "모멘텀 순위를 다시 계산하는 주기입니다.",
                    min=1,
                    max=12,
                    step=1,
                    integer=True,
                ),
            ]
        )
        risk.extend(_guardrail_fields())

    return [
        _section("execution", execution),
        _section("universe", universe),
        _section("rules", rules),
        _section("risk", risk),
    ]


def _risk_on_sections(runtime_options: Mapping[str, object]) -> list[dict[str, object]]:
    tickers = [str(value) for value in _runtime_sequence(runtime_options, "tickers", [])]
    execution = _date_fields(start="2021-06-01") + [
        _field(
            "start_balance",
            "start_balance",
            "시작 자산",
            "number",
            10_000.0,
            "백테스트를 시작할 가상 투자금입니다.",
            min=1_000.0,
            max=10_000_000.0,
            step=1_000.0,
        )
    ]
    universe = [
        _field(
            "universe_mode",
            "universe_mode",
            "투자 대상 범위",
            "segmented",
            "top1000",
            "DB 자산 범위 또는 직접 입력 종목을 선택합니다.",
            options=[
                _option("top1000", "미국 시가총액 상위 1,000"),
                _option("top2000", "미국 시가총액 상위 2,000"),
                _option("sp500", "S&P 500"),
                _option("manual_tickers", "종목 직접 입력"),
            ],
        ),
        _field(
            "tickers",
            "tickers",
            "직접 입력할 종목",
            "multi_select",
            ["NVDA", "MSFT", "AAPL", "AMZN", "META", "AVGO", "AMD", "TSLA"],
            "직접 검증할 종목을 하나 이상 선택합니다.",
            options=[_option(value) for value in tickers],
            visible_when={"universe_mode": "manual_tickers"},
        ),
    ]
    rules = [
        _field(
            "execution_mode",
            "execution_mode",
            "실행 기준",
            "single_select",
            "close_based",
            "종가 신호를 계산하고 다음 거래일에 실행합니다.",
            options=[_option("close_based", "종가 신호·다음 거래일 실행")],
        ),
        _field(
            "max_new_positions_per_day",
            "max_new_positions_per_day",
            "하루 최대 신규 편입 수",
            "number",
            3,
            "하루에 새로 편입할 수 있는 최대 종목 수입니다.",
            min=1,
            max=10,
            step=1,
            integer=True,
        ),
        _field(
            "max_total_positions",
            "max_total_positions",
            "최대 동시 보유 수",
            "number",
            3,
            "동시에 보유할 수 있는 최대 종목 수입니다.",
            min=1,
            max=20,
            step=1,
            integer=True,
        ),
        _field(
            "exit_mode",
            "exit_mode",
            "청산 기준",
            "segmented",
            "fixed_pct",
            "고정 손익률 또는 ATR 변동성 기준을 선택합니다.",
            options=[
                _option("fixed_pct", "고정 손익률"),
                _option("atr_based", "ATR 변동성"),
            ],
        ),
        _field(
            "max_holding_days",
            "max_holding_days",
            "최대 보유일",
            "number",
            5,
            "포지션을 유지할 최대 거래일 수입니다.",
            min=1,
            max=20,
            step=1,
            integer=True,
        ),
        _field(
            "stop_loss_pct",
            "stop_loss_pct",
            "손절 기준(%)",
            "number",
            -2.5,
            "진입가 대비 손실이 이 비율에 도달하면 청산합니다.",
            min=-50.0,
            max=0.0,
            step=0.5,
        ),
        _field(
            "take_profit_pct",
            "take_profit_pct",
            "익절 기준(%)",
            "number",
            5.0,
            "진입가 대비 수익이 이 비율에 도달하면 청산합니다.",
            min=0.5,
            max=100.0,
            step=0.5,
        ),
        _field(
            "atr_period",
            "atr_period",
            "ATR 계산 기간",
            "number",
            14,
            "변동성 청산 기준에 사용할 ATR 관찰 기간입니다.",
            min=2,
            max=100,
            step=1,
            integer=True,
            advanced=True,
        ),
        _field(
            "stop_atr_multiple",
            "stop_atr_multiple",
            "손절 ATR 배수",
            "number",
            1.0,
            "ATR 기반 손절에 적용할 배수입니다.",
            min=0.1,
            max=10.0,
            step=0.1,
            advanced=True,
        ),
        _field(
            "take_profit_atr_multiple",
            "take_profit_atr_multiple",
            "익절 ATR 배수",
            "number",
            2.0,
            "ATR 기반 익절에 적용할 배수입니다.",
            min=0.1,
            max=20.0,
            step=0.1,
            advanced=True,
        ),
        _field(
            "macro_filter_mode",
            "macro_filter_mode",
            "시장 필터 방식",
            "single_select",
            "hard_filter",
            "시장 조건 미충족 후보를 제외하거나 순위에서 감점합니다.",
            options=[
                _option("hard_filter", "조건 미충족 후보 제외"),
                _option("ranking_penalty", "순위 감점"),
                _option("off", "사용하지 않음"),
            ],
        ),
        _field("risk_on_min", "risk_on_min", "위험선호 최소 평균 Z", "number", 0.0, "위험선호 지표가 통과해야 하는 최소 값입니다.", step=0.1, advanced=True),
        _field("rate_pressure_max", "rate_pressure_max", "금리 압력 최대 평균 Z", "number", 1.0, "금리 압력 지표의 허용 최대 값입니다.", step=0.1, advanced=True),
        _field("dollar_pressure_max", "dollar_pressure_max", "달러 압력 최대 평균 Z", "number", 1.0, "달러 압력 지표의 허용 최대 값입니다.", step=0.1, advanced=True),
        _field("safe_haven_max", "safe_haven_max", "안전자산 선호 최대 평균 Z", "number", 1.0, "안전자산 선호 지표의 허용 최대 값입니다.", step=0.1, advanced=True),
        _field("rate_pressure_penalty_weight", "rate_pressure_penalty_weight", "금리 압력 감점", "number", 10.0, "순위 감점 방식에서 금리 압력에 적용할 가중치입니다.", min=0.0, max=100.0, step=1.0, advanced=True),
        _field("dollar_pressure_penalty_weight", "dollar_pressure_penalty_weight", "달러 압력 감점", "number", 10.0, "순위 감점 방식에서 달러 압력에 적용할 가중치입니다.", min=0.0, max=100.0, step=1.0, advanced=True),
        _field("safe_haven_penalty_weight", "safe_haven_penalty_weight", "안전자산 선호 감점", "number", 10.0, "순위 감점 방식에서 안전자산 선호에 적용할 가중치입니다.", min=0.0, max=100.0, step=1.0, advanced=True),
        _field("min_price", "min_price", "최소 주가", "number", 5.0, "이 가격보다 낮은 종목을 후보에서 제외합니다.", min=0.0, step=1.0, advanced=True),
        _field("min_avg_dollar_volume_20d_m", "min_avg_dollar_volume_20d_m", "최소 20일 평균 거래대금($M)", "number", 20.0, "후보가 통과해야 하는 최근 평균 거래대금입니다.", min=0.0, step=5.0, include_in_payload=False, advanced=True),
        _field("min_avg_volume_20d", "min_avg_volume_20d", "최소 20일 평균 거래량", "number", 500_000, "후보가 통과해야 하는 최근 평균 거래량입니다.", min=0, step=50_000, integer=True, advanced=True),
    ]
    risk = [
        _field("transaction_cost_bps", "transaction_cost_bps", "거래비용(bps)", "number", 0.0, "매수·매도에 반영할 거래비용입니다.", min=0.0, max=100.0, step=1.0),
        _field("slippage_bps", "slippage_bps", "슬리피지(bps)", "number", 0.0, "주문 가격과 실제 체결 가격의 차이 가정입니다.", min=0.0, max=100.0, step=1.0),
        _field("random_iterations", "random_iterations", "무작위 검증 반복 횟수", "number", 50, "후보 순위 민감도를 확인할 무작위 반복 횟수입니다.", min=0, max=100, step=5, integer=True, advanced=True),
        _field("scanner_top_n_per_day", "scanner_top_n_per_day", "일별 후보 저장 수", "number", 50, "근거 확인을 위해 날짜별로 보존할 상위 후보 수입니다.", min=1, max=200, step=5, integer=True, advanced=True),
        _field("run_comparison_suite", "run_comparison_suite", "비교 진단 함께 실행", "toggle", True, "기본 결과와 비교 진단을 함께 계산합니다.", advanced=True),
        _field("run_sensitivity_suite", "run_sensitivity_suite", "민감도 진단 함께 실행", "toggle", False, "주요 설정 변화에 대한 민감도 진단을 함께 계산합니다.", advanced=True),
    ]
    return [
        _section("execution", execution),
        _section("universe", universe),
        _section("rules", rules),
        _section("risk", risk),
    ]


def _generic_sections(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> list[dict[str, object]]:
    execution = _date_fields() + [
        _field(
            "rebalance_interval",
            "rebalance_interval",
            "리밸런싱 간격(개월)",
            "number",
            12,
            "선택 비중을 다시 맞추는 개월 간격입니다.",
            min=1,
            max=120,
            step=1,
            integer=True,
        )
    ]
    return [
        _section("execution", execution),
        _section("universe", _standard_universe_fields(strategy_choice, runtime_options)),
        _section("rules", []),
        _section("risk", _etf_risk_fields(runtime_options)),
    ]


def _strategy_sections(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> list[dict[str, object]]:
    if strategy_choice == "Risk-On Momentum 5D":
        return _risk_on_sections(runtime_options)
    if strategy_choice in {
        "Equal Weight",
        "GTAA",
        "Global Relative Strength",
        "Risk Parity",
        "Dual Momentum",
    }:
        return _standard_tactical_sections(strategy_choice, runtime_options)
    return _generic_sections(strategy_choice, runtime_options)


def _normalized_variant(strategy_choice: str, variant: str | None) -> str | None:
    if strategy_choice not in SINGLE_SETTINGS_CONCRETE_KEYS:
        raise ValueError(f"알 수 없는 전략입니다: {strategy_choice}")
    allowed_variants = SINGLE_SETTINGS_CONCRETE_KEYS[strategy_choice]
    if variant not in allowed_variants:
        raise ValueError(
            f"{strategy_choice}에서 사용할 수 없는 variant입니다: {variant}"
        )
    return variant


def _all_fields(workspace: Mapping[str, object]) -> list[dict[str, object]]:
    sections = workspace.get("sections")
    if not isinstance(sections, Sequence):
        return []
    fields: list[dict[str, object]] = []
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        section_fields = section.get("fields")
        if not isinstance(section_fields, Sequence):
            continue
        fields.extend(
            item if isinstance(item, dict) else dict(item)
            for item in section_fields
            if isinstance(item, Mapping)
        )
    return fields


def _effective_values(
    workspace: Mapping[str, object],
    submitted: Mapping[str, object],
) -> dict[str, object]:
    effective = {
        str(field["field_id"]): deepcopy(field.get("value"))
        for field in _all_fields(workspace)
    }
    effective.update({str(key): deepcopy(value) for key, value in submitted.items()})
    return effective


def _is_visible(field: Mapping[str, object], values: Mapping[str, object]) -> bool:
    visible_when = field.get("visible_when")
    if not isinstance(visible_when, Mapping):
        return True
    return all(values.get(str(key)) == expected for key, expected in visible_when.items())


def _option_values(field: Mapping[str, object]) -> list[object]:
    options = field.get("options")
    if not isinstance(options, Sequence) or isinstance(options, (str, bytes)):
        return []
    values = []
    for option in options:
        if isinstance(option, Mapping) and "value" in option:
            values.append(option["value"])
        else:
            values.append(option)
    return values


def _value_error(field: Mapping[str, object], value: object) -> str | None:
    if bool(field.get("required", True)) and (
        value is None or value == "" or value == []
    ):
        return "필수 설정입니다."

    control = str(field.get("control") or "")
    if value is None:
        return None
    if control == "date":
        if not isinstance(value, str):
            return "날짜 형식으로 입력해 주세요."
        try:
            date.fromisoformat(value)
        except ValueError:
            return "YYYY-MM-DD 날짜 형식으로 입력해 주세요."
    elif control == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "숫자로 입력해 주세요."
        minimum = field.get("min")
        maximum = field.get("max")
        if isinstance(minimum, (int, float)) and value < minimum:
            return f"최솟값 {minimum} 이상이어야 합니다."
        if isinstance(maximum, (int, float)) and value > maximum:
            return f"최댓값 {maximum} 이하여야 합니다."
    elif control in {"single_select", "segmented"}:
        if not isinstance(value, (str, int, float)) or isinstance(value, bool):
            return "선택 항목 형식으로 입력해 주세요."
        allowed = _option_values(field)
        if allowed and value not in allowed:
            return "선택할 수 없는 값입니다."
    elif control == "multi_select":
        if not isinstance(value, list):
            return "여러 항목은 목록으로 입력해 주세요."
        if len(value) != len({repr(item) for item in value}):
            return "중복 항목은 한 번만 선택해 주세요."
        allowed = _option_values(field)
        if allowed and any(item not in allowed for item in value):
            return "선택할 수 없는 값이 포함되어 있습니다."
    elif control == "toggle":
        if not isinstance(value, bool):
            return "켜기 또는 끄기로 선택해 주세요."
    elif control == "text" and not isinstance(value, str):
        return "문자열로 입력해 주세요."
    return None


def _payload_constants(
    strategy_choice: str,
    concrete_strategy_key: str,
    runtime_options: Mapping[str, object],
) -> dict[str, object]:
    constants: dict[str, object] = {
        "strategy_key": concrete_strategy_key,
        "timeframe": "1d",
        "option": "month_end",
    }
    if strategy_choice in {
        "GTAA",
        "Global Relative Strength",
        "Risk Parity",
        "Dual Momentum",
    }:
        policy_defaults = runtime_options.get("policy_defaults")
        supplied_policy = (
            dict(policy_defaults) if isinstance(policy_defaults, Mapping) else {}
        )
        constants.update(
            {
                "promotion_min_benchmark_coverage": supplied_policy.get(
                    "promotion_min_benchmark_coverage", 0.95
                ),
                "promotion_min_net_cagr_spread": supplied_policy.get(
                    "promotion_min_net_cagr_spread", -0.02
                ),
                "promotion_min_liquidity_clean_coverage": supplied_policy.get(
                    "promotion_min_liquidity_clean_coverage", 0.9
                ),
                "promotion_max_underperformance_share": supplied_policy.get(
                    "promotion_max_underperformance_share", 0.55
                ),
                "promotion_min_worst_rolling_excess_return": supplied_policy.get(
                    "promotion_min_worst_rolling_excess_return", -0.15
                ),
                "promotion_max_strategy_drawdown": supplied_policy.get(
                    "promotion_max_strategy_drawdown", -0.35
                ),
                "promotion_max_drawdown_gap_vs_benchmark": supplied_policy.get(
                    "promotion_max_drawdown_gap_vs_benchmark", 0.08
                ),
            }
        )
    if strategy_choice == "Global Relative Strength":
        constants["trend_filter_enabled"] = True
    if strategy_choice == "Risk-On Momentum 5D":
        constants["option"] = "close_based"
    return constants


def build_single_settings_workspace(
    strategy_choice: str,
    variant: str | None,
    values: Mapping[str, object] | None,
    runtime_options: Mapping[str, object] | None,
) -> dict[str, object]:
    """Build a JSON-ready settings read model without importing web/runtime modules."""

    normalized_variant = _normalized_variant(strategy_choice, variant)
    runtime = dict(runtime_options or {})
    sections = _strategy_sections(strategy_choice, runtime)
    concrete_strategy_key = _CONCRETE_STRATEGY_KEYS[
        (strategy_choice, normalized_variant)
    ]
    presets = _preset_catalog(strategy_choice, runtime)
    workspace: dict[str, object] = {
        "schema_version": SETTINGS_SCHEMA_VERSION,
        "strategy_choice": strategy_choice,
        "concrete_strategy_key": concrete_strategy_key,
        "draft_key": f"{strategy_choice}:{normalized_variant or 'default'}",
        "profile": deepcopy(_PROFILES[strategy_choice]),
        "variant": {
            "value": normalized_variant,
            "options": [
                {
                    "value": item,
                    "label": _VARIANT_LABELS.get(str(item), str(item)),
                }
                for item in SINGLE_SETTINGS_CONCRETE_KEYS[strategy_choice]
                if item is not None
            ],
        },
        "sections": sections,
        "evidence": {
            "universe_summary": "투자 대상 구성을 선택해 검증 범위를 고정합니다.",
            "universe_full_text": "",
            "technical_rows": [],
        },
        "action": {
            "id": "run_single_strategy",
            "label": "이 설정으로 백테스트 실행",
            "enabled": True,
        },
        "validation_errors": {},
        "payload_constants": _payload_constants(
            strategy_choice,
            concrete_strategy_key,
            runtime,
        ),
        "runtime_context": {
            "preset_members": deepcopy(presets),
        },
    }
    supplied = dict(values or {})
    for field in _all_fields(workspace):
        field_id = str(field["field_id"])
        if field_id in supplied:
            field["value"] = deepcopy(supplied[field_id])
    return deepcopy(workspace)


def validate_single_settings_draft(
    workspace: Mapping[str, object],
    values: Mapping[str, object] | None,
) -> dict[str, str]:
    """Validate submitted fields before any runner or persistence boundary is reached."""

    submitted = {str(key): value for key, value in dict(values or {}).items()}
    fields = _all_fields(workspace)
    field_by_id = {str(field["field_id"]): field for field in fields}
    effective = _effective_values(workspace, submitted)
    errors: dict[str, str] = {}

    for field_id in submitted:
        if field_id not in field_by_id:
            errors[field_id] = "허용되지 않은 설정입니다."

    for field_id, field in field_by_id.items():
        visible = _is_visible(field, effective)
        if field_id in submitted and not visible:
            errors[field_id] = "현재 조건에서는 사용할 수 없는 설정입니다."
            continue
        if not visible:
            continue
        message = _value_error(field, effective.get(field_id))
        if message:
            errors[field_id] = message
    return errors


def project_single_settings_payload(
    workspace: Mapping[str, object],
    values: Mapping[str, object] | None,
) -> dict[str, object]:
    """Project only validated visible fields and Python-owned constants into a payload."""

    submitted = dict(values or {})
    errors = validate_single_settings_draft(workspace, submitted)
    if errors:
        raise SettingsValidationError(errors)

    effective = _effective_values(workspace, submitted)
    payload_constants = workspace.get("payload_constants")
    payload: dict[str, object] = (
        deepcopy(dict(payload_constants))
        if isinstance(payload_constants, Mapping)
        else {}
    )
    for field in _all_fields(workspace):
        if not _is_visible(field, effective):
            continue
        if field.get("include_in_payload") is False:
            continue
        field_id = str(field["field_id"])
        payload_key = str(field["payload_key"])
        value = deepcopy(effective.get(field_id))
        scale = field.get("payload_scale")
        if isinstance(scale, (int, float)) and isinstance(value, (int, float)):
            value = round(float(value) * float(scale), 12)
        if field.get("integer") is True and isinstance(value, (int, float)):
            value = int(value)
        if field.get("uppercase") is True and isinstance(value, str):
            value = value.strip().upper()
        payload[payload_key] = value

    strategy_choice = str(workspace.get("strategy_choice") or "")
    universe_mode = str(effective.get("universe_mode") or "")
    runtime_context = workspace.get("runtime_context")
    context = dict(runtime_context) if isinstance(runtime_context, Mapping) else {}
    preset_members = context.get("preset_members")
    presets = dict(preset_members) if isinstance(preset_members, Mapping) else {}
    if strategy_choice == "Risk-On Momentum 5D":
        universe_contract = {
            "top1000": ("Top1000", 1000),
            "top2000": ("Top2000", 2000),
            "sp500": ("S&P 500", 500),
            "manual_tickers": (None, len(list(effective.get("tickers") or []))),
        }
        preset_name, universe_limit = universe_contract[universe_mode]
        payload["tickers"] = (
            list(effective.get("tickers") or [])
            if universe_mode == "manual_tickers"
            else []
        )
        payload["preset_name"] = preset_name
        payload["universe_limit"] = universe_limit
        payload["macro_filter_enabled"] = (
            str(effective.get("macro_filter_mode") or "") != "off"
        )
        payload["min_avg_dollar_volume_20d"] = float(
            effective.get("min_avg_dollar_volume_20d_m") or 0.0
        ) * 1_000_000.0
    else:
        preset_name = effective.get("preset_name")
        payload["tickers"] = (
            list(presets.get(str(preset_name), []))
            if universe_mode == "preset"
            else list(effective.get("tickers") or [])
        )
        payload["preset_name"] = (
            str(preset_name) if universe_mode == "preset" else None
        )

    if strategy_choice in {"GTAA", "Global Relative Strength"}:
        months = [int(value) for value in list(effective.get("score_lookback_months") or [])]
        return_columns = [f"{month}MReturn" for month in months]
        payload["score_return_columns"] = return_columns
        payload["score_weights"] = {column: 1.0 for column in return_columns}
    return payload


__all__ = [
    "ALLOWED_CONTROLS",
    "SETTINGS_SCHEMA_VERSION",
    "SINGLE_SETTINGS_CONCRETE_KEYS",
    "SettingsValidationError",
    "build_single_settings_workspace",
    "project_single_settings_payload",
    "validate_single_settings_draft",
]
