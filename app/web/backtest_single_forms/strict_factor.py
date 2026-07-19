from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill
from app.web.backtest_single_settings_workspace import single_settings_section


def _render_strict_factor_data_readiness_note(
    *,
    family_label: str,
    statement_freq: str,
    mode_label: str,
    prototype: bool = False,
    combined_factor: bool = False,
    inline: bool = False,
) -> None:
    freq_label = str(statement_freq).strip().lower()
    status_label = "research-only prototype" if prototype else "public candidate"
    coverage_note = (
        "quality + value factor가 동시에 필요하므로 usable history를 더 보수적으로 봅니다."
        if combined_factor
        else "선택 universe의 statement shadow factor coverage가 실제 시작 가능 구간을 결정합니다."
    )
    def render_note() -> None:
        st.markdown(
            f"- **가격**: `Daily Market Update` 또는 OHLCV 수집이 먼저 필요합니다.\n"
            f"- **재무제표**: `Extended Statement Refresh`를 **{freq_label}** 기준으로 준비합니다.\n"
            "- **Factor**: 저장된 statement shadow factor를 읽고, 리밸런싱 시점에 사용 가능한 종목만 평가합니다.\n"
            f"- **상태**: `{family_label}`은 현재 **{status_label}** 경로입니다.\n"
            f"- **주의**: {coverage_note}"
        )
        st.caption(f"계산 계약: `{mode_label}`")

    if inline:
        render_note()
        return
    with st.expander("데이터 준비 기준", expanded=False):
        render_note()


def _strict_factor_date_input(label: str, *, default: date, key: str) -> date:
    value = "today" if key in st.session_state else default
    return st.date_input(label, value=value, key=key)


def _render_strict_factor_core_inputs(
    *,
    section_label: str,
    key_prefix: str,
    default_start: date,
    top_default: int,
    top_max: int,
    top_help: str,
) -> tuple[date, date, int]:
    """Render the period and selection count before the universe decision."""

    with single_settings_section(
        section_label,
        "검증 기간과 최종 보유 종목 수를 먼저 정합니다.",
    ):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "시작일",
                default=default_start,
                key=f"{key_prefix}_start",
            )
        with col2:
            end_date = _strict_factor_date_input(
                "종료일",
                default=DEFAULT_BACKTEST_END_DATE,
                key=f"{key_prefix}_end",
            )
        with col3:
            top_n = int(
                st.number_input(
                    "최종 보유 종목 수",
                    min_value=1,
                    max_value=top_max,
                    value=top_default,
                    step=1,
                    help=top_help,
                    key=f"{key_prefix}_top_n",
                )
            )
        st.caption("월말에 후보를 다시 평가하고 기본적으로 같은 비중으로 보유합니다.")
    return start_date, end_date, top_n


def _render_strict_factor_universe_inputs(
    *,
    section_label: str,
    key_prefix: str,
    presets: dict[str, list[str]],
    default_preset: str,
    help_text: str,
    strict_labels: bool,
    show_historical_caption: bool,
    show_preset_status: bool,
) -> tuple[str, str | None, list[str]]:
    """Render a Korean-first preset/manual choice with compact ticker evidence."""

    with single_settings_section(
        section_label,
        "검증할 후보군을 선택하고 상세 종목과 데이터 계약은 근거에서 확인합니다.",
    ):
        universe_mode = st.radio(
            "투자 대상 선택",
            options=["Preset", "Manual"],
            format_func=lambda value: "목적별 기본 구성" if value == "Preset" else "종목 직접 입력",
            horizontal=True,
            help=help_text,
            key=f"{key_prefix}_universe_mode",
        )
        preset_name: str | None = None
        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "기본 구성",
                options=list(presets.keys()),
                format_func=lambda value: (
                    strict_preset_display_label(value) if strict_labels else value
                ),
                index=list(presets.keys()).index(default_preset),
                key=f"{key_prefix}_preset",
            )
            tickers = list(presets[preset_name])
            _render_ticker_preview(tickers)
            if show_historical_caption:
                _render_historical_universe_caption()
            if show_preset_status:
                _render_strict_preset_status_note(preset_name, tickers)
        else:
            manual_tickers = st.text_input(
                "검증할 종목",
                value="AAPL,MSFT,GOOG",
                help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
                key=f"{key_prefix}_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)
            _render_ticker_preview(tickers)
    return universe_mode, preset_name, tickers


def _render_quality_snapshot_form() -> None:
    _apply_single_strategy_prefill("quality_snapshot")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="qs",
        default_start=date(2016, 1, 1),
        top_default=2,
        top_max=20,
        top_help="Quality 점수 상위에서 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="qs",
        presets=QUALITY_BROAD_PRESETS,
        default_preset=next(iter(QUALITY_BROAD_PRESETS)),
        help_text="저장된 과거 실행을 재현할 stock 중심 후보군입니다.",
        strict_labels=False,
        show_historical_caption=False,
        show_preset_status=False,
    )
    _render_quality_family_guide("quality_broad")
    with st.expander("Universe 근거", expanded=False):
        st.markdown(
            "- 가격과 기존 legacy factor row가 모두 있는 종목만 재현할 수 있습니다.\n"
            "- 신규 연구는 Strict Annual 또는 Quality + Value Strict Annual을 사용합니다.\n"
            "- 이 경로는 저장된 과거 결과 호환을 위해서만 유지합니다."
        )
        st.caption("재현 계약: `legacy_broad_yfinance`")

    with st.form("quality_snapshot_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "Quality 지표를 합산해 월말마다 상위 후보를 같은 비중으로 선택합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="qs_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="qs_option")
            factor_freq = st.selectbox(
                "재무 지표 주기",
                options=["annual"],
                format_func=lambda _: "연간",
                index=0,
                key="qs_factor_freq",
            )
            quality_factors = st.multiselect(
                "Quality 지표",
                options=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                default=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                key="qs_quality_factors",
                help="수익성은 높을수록, 부채비율은 낮을수록 좋은 방향으로 표준화합니다.",
            )
            snapshot_mode = st.selectbox(
                "재현 방식",
                options=["broad_research"],
                format_func=lambda _: "저장된 broad 연구 스냅샷",
                index=0,
                key="qs_snapshot_mode",
            )
        with single_settings_section(
            "비용·위험 기준",
            "이 legacy 재현 경로는 저장된 기본 비용 계약을 그대로 사용합니다.",
        ):
            st.caption("비용과 위험 기준을 새로 조정하려면 Strict Annual 경로를 사용합니다.")
        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    if start_date > end_date:
        validation_errors.append("시작일은 종료일보다 늦을 수 없습니다.")
    if not quality_factors:
        validation_errors.append("Quality 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "factor_freq": factor_freq,
        "rebalance_freq": "monthly",
        "snapshot_mode": snapshot_mode,
        "quality_factors": quality_factors,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot")

def _render_quality_snapshot_strict_annual_form() -> None:
    _apply_single_strategy_prefill("quality_snapshot_strict_annual")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="qss",
        default_start=_default_strict_factor_start_date(),
        top_default=2,
        top_max=20,
        top_help="연간 Quality 점수 기준으로 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="qss",
        presets=QUALITY_STRICT_PRESETS,
        default_preset=STRICT_ANNUAL_SINGLE_DEFAULT_PRESET,
        help_text="연간 재무제표 coverage가 검증된 미국 주식 구성을 기본으로 사용합니다.",
        strict_labels=True,
        show_historical_caption=True,
        show_preset_status=True,
    )
    with st.expander("Universe 근거", expanded=False):
        _render_strict_factor_data_readiness_note(
            family_label="Quality Snapshot (Strict Annual)",
            statement_freq="annual",
            mode_label="strict_statement_annual + shadow_factors",
            inline=True,
        )
        universe_contract, dynamic_candidate_tickers, dynamic_target_size = _render_strict_universe_contract_setup(
            key="qss_universe_contract",
            tickers=tickers,
            preset_name=preset_name,
            statement_freq="annual",
        )
        _render_strict_factor_prerun_preview(
            tickers=tickers,
            strategy_label="Quality Snapshot (Strict Annual)",
            preset_name=preset_name,
            universe_contract=universe_contract,
            statement_freq="annual",
        )

    with st.form("quality_snapshot_strict_annual_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "연간 Quality 지표, 추세 필터, 비중과 방어 규칙을 정합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="qss_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="qss_option")
            rebalance_interval = st.number_input(
                "리밸런싱 간격(개월)",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qss_rebalance_interval",
            )
            quality_factors = st.multiselect(
                "Quality 지표",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qss_quality_factors",
                help="기본은 coverage-first 팩터 조합입니다. 필요하면 예전 quality factor도 다시 포함할 수 있습니다.",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("추세·시장 필터", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### 추세 필터")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "추세 필터 사용",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "추세 판단 기간",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qss_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qss",
                    label_prefix="",
                )
            with st.expander("비중·방어 규칙", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality",
                )
        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 비교 기준, 유동성 조건과 중단 기준을 정합니다.",
        ):
            with st.expander("거래 비용과 승격 기준", expanded=False):
                (
                    benchmark_contract,
                    min_price_filter,
                    min_history_months_filter,
                    min_avg_dollar_volume_20d_m_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_benchmark_coverage,
                    promotion_min_net_cagr_spread,
                    promotion_min_liquidity_clean_coverage,
                    promotion_max_underperformance_share,
                    promotion_min_worst_rolling_excess_return,
                    promotion_max_strategy_drawdown,
                    promotion_max_drawdown_gap_vs_benchmark,
                ) = _render_strict_annual_real_money_inputs(
                    key_prefix="qss",
                )
            with st.expander("중단·경고 기준", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                ) = _render_underperformance_guardrail_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality ",
                )
                (
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_drawdown_guardrail_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality ",
                )
                guardrail_reference_ticker = _render_guardrail_reference_ticker_input(
                    key_prefix="qss",
                    benchmark_ticker=benchmark_ticker,
                    default_guardrail_reference_ticker=st.session_state.get("qss_guardrail_reference_ticker"),
                    underperformance_guardrail_enabled=underperformance_guardrail_enabled,
                    drawdown_guardrail_enabled=drawdown_guardrail_enabled,
                )

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality Snapshot (Strict Annual)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Quality 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "quality_factors": quality_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "guardrail_reference_ticker": guardrail_reference_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot (Strict Annual)")

def _render_quality_snapshot_strict_quarterly_prototype_form() -> None:
    _apply_single_strategy_prefill("quality_snapshot_strict_quarterly_prototype")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="qsqp",
        default_start=_default_strict_factor_start_date(),
        top_default=2,
        top_max=20,
        top_help="분기 Quality 점수 기준으로 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="qsqp",
        presets=QUALITY_STRICT_PRESETS,
        default_preset=STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
        help_text="분기 재무제표 검증 비용을 고려해 100종목 구성을 기본으로 사용합니다.",
        strict_labels=True,
        show_historical_caption=True,
        show_preset_status=False,
    )
    with st.expander("Universe 근거", expanded=False):
        _render_strict_quarterly_productionization_note(family_label="Quality Snapshot (Strict Quarterly)")
        _render_strict_factor_data_readiness_note(
            family_label="Quality Snapshot (Strict Quarterly)",
            statement_freq="quarterly",
            mode_label="strict_statement_quarterly + shadow_factors + post_run_readiness",
            inline=True,
        )
        _render_strict_price_freshness_preflight(
            tickers=tickers,
            end_value=st.session_state.get("qsqp_end", DEFAULT_BACKTEST_END_DATE),
            timeframe=st.session_state.get("qsqp_timeframe", "1d"),
            strategy_label="Quality Snapshot (Strict Quarterly)",
        )
        _render_statement_shadow_coverage_preview(
            tickers=tickers,
            freq="quarterly",
            strategy_label="Quality Snapshot (Strict Quarterly)",
        )
        universe_contract_label = _render_strict_universe_contract_selectbox(
            "Universe 계약",
            key="qsqp_universe_contract",
            help=STRICT_UNIVERSE_CONTRACT_HELP,
        )
        universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
        dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
            universe_contract=universe_contract,
            tickers=tickers,
            preset_name=preset_name,
            statement_freq="quarterly",
        )

    with st.form("quality_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "분기 Quality 지표와 월말 선택·방어 규칙을 정합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="qsqp_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="qsqp_option")
            rebalance_interval = st.number_input(
                "리밸런싱 간격(개월)",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qsqp_rebalance_interval",
            )
            quality_factors = st.multiselect(
                "Quality 지표",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qsqp_quality_factors",
                help="first-pass quarterly strict도 quality strict와 같은 coverage-first 팩터 조합을 기본값으로 사용합니다.",
            )
            _render_advanced_group_caption(
                "Quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("추세·시장 필터", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### 추세 필터")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "추세 필터 사용",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qsqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "추세 판단 기간",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qsqp_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality ",
                )
            with st.expander("비중·방어 규칙", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality",
                )
                st.caption(
                    "이 contract들은 quarterly payload와 replay surface에 저장됩니다. "
                    "실제 데이터 문제는 Run 이후 Factor Readiness에서 가격 / statement 기준으로 다시 확인합니다."
                )

        with single_settings_section(
            "비용·위험 기준",
            "분기 검증 경로는 저장된 기본 거래 비용을 사용하며 방어 규칙은 위 설정에 포함됩니다.",
        ):
            st.caption("실행 후 실제 coverage와 비용 영향은 결과의 Factor Readiness에서 확인합니다.")
        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality Snapshot (Strict Quarterly)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Quality 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "quality_factors": quality_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot (Strict Quarterly)")

def _render_value_snapshot_strict_quarterly_prototype_form() -> None:
    _apply_single_strategy_prefill("value_snapshot_strict_quarterly_prototype")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="vsqp",
        default_start=_default_strict_factor_start_date(),
        top_default=10,
        top_max=50,
        top_help="분기 Value 점수 기준으로 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="vsqp",
        presets=VALUE_STRICT_PRESETS,
        default_preset=STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
        help_text="분기 재무제표 검증 비용을 고려해 100종목 구성을 기본으로 사용합니다.",
        strict_labels=True,
        show_historical_caption=True,
        show_preset_status=False,
    )
    with st.expander("Universe 근거", expanded=False):
        _render_strict_quarterly_productionization_note(family_label="Value Snapshot (Strict Quarterly)")
        _render_strict_factor_data_readiness_note(
            family_label="Value Snapshot (Strict Quarterly)",
            statement_freq="quarterly",
            mode_label="strict_statement_quarterly + shadow_factors + post_run_readiness",
            inline=True,
        )
        _render_strict_price_freshness_preflight(
            tickers=tickers,
            end_value=st.session_state.get("vsqp_end", DEFAULT_BACKTEST_END_DATE),
            timeframe=st.session_state.get("vsqp_timeframe", "1d"),
            strategy_label="Value Snapshot (Strict Quarterly)",
        )
        _render_statement_shadow_coverage_preview(
            tickers=tickers,
            freq="quarterly",
            strategy_label="Value Snapshot (Strict Quarterly)",
        )
        universe_contract_label = _render_strict_universe_contract_selectbox(
            "Universe 계약",
            key="vsqp_universe_contract",
            help=STRICT_UNIVERSE_CONTRACT_HELP,
        )
        universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
        dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
            universe_contract=universe_contract,
            tickers=tickers,
            preset_name=preset_name,
            statement_freq="quarterly",
        )

    with st.form("value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "분기 Value 지표와 월말 선택·방어 규칙을 정합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="vsqp_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="vsqp_option")
            rebalance_interval = st.number_input(
                "리밸런싱 간격(개월)",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="vsqp_rebalance_interval",
            )
            value_factors = st.multiselect(
                "Value 지표",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vsqp_value_factors",
                help="quarterly strict도 yield / book-to-market 중심의 coverage-first 기본 조합을 사용합니다.",
            )
            _render_advanced_group_caption(
                "Quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("추세·시장 필터", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### 추세 필터")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "추세 필터 사용",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="vsqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "추세 판단 기간",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="vsqp_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value ",
                )
            with st.expander("비중·방어 규칙", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value",
                )
                st.caption(
                    "이 contract들은 quarterly payload와 replay surface에 저장됩니다. "
                    "실제 데이터 문제는 Run 이후 Factor Readiness에서 가격 / statement 기준으로 다시 확인합니다."
                )

        with single_settings_section(
            "비용·위험 기준",
            "분기 검증 경로는 저장된 기본 거래 비용을 사용하며 방어 규칙은 위 설정에 포함됩니다.",
        ):
            st.caption("실행 후 실제 coverage와 비용 영향은 결과의 Factor Readiness에서 확인합니다.")
        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Value Snapshot (Strict Quarterly)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not value_factors:
        validation_errors.append("Value 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "value_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "snapshot_source": "shadow_factors",
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Value Snapshot (Strict Quarterly)")

def _render_value_snapshot_strict_annual_form() -> None:
    _apply_single_strategy_prefill("value_snapshot_strict_annual")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="vss",
        default_start=_default_strict_factor_start_date(),
        top_default=10,
        top_max=50,
        top_help="연간 Value 점수 기준으로 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="vss",
        presets=VALUE_STRICT_PRESETS,
        default_preset=STRICT_ANNUAL_SINGLE_DEFAULT_PRESET,
        help_text="연간 재무제표 coverage가 검증된 미국 주식 구성을 기본으로 사용합니다.",
        strict_labels=True,
        show_historical_caption=True,
        show_preset_status=True,
    )
    with st.expander("Universe 근거", expanded=False):
        _render_strict_factor_data_readiness_note(
            family_label="Value Snapshot (Strict Annual)",
            statement_freq="annual",
            mode_label="strict_statement_annual + shadow_factors",
            inline=True,
        )
        universe_contract, dynamic_candidate_tickers, dynamic_target_size = _render_strict_universe_contract_setup(
            key="vss_universe_contract",
            tickers=tickers,
            preset_name=preset_name,
            statement_freq="annual",
        )
        _render_strict_factor_prerun_preview(
            tickers=tickers,
            strategy_label="Value Snapshot (Strict Annual)",
            preset_name=preset_name,
            universe_contract=universe_contract,
            statement_freq="annual",
        )

    with st.form("value_snapshot_strict_annual_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "연간 Value 지표, 추세 필터, 비중과 방어 규칙을 정합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="vss_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="vss_option")
            rebalance_interval = st.number_input(
                "리밸런싱 간격(개월)",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="vss_rebalance_interval",
            )
            value_factors = st.multiselect(
                "Value 지표",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vss_value_factors",
                help="높을수록 좋은 yield / book-to-market 계열과 낮을수록 좋은 inverse multiple 계열을 함께 지원합니다.",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("추세·시장 필터", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### 추세 필터")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "추세 필터 사용",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="vss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "추세 판단 기간",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="vss_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="vss",
                    label_prefix="",
                )
            with st.expander("비중·방어 규칙", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value",
                )
        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 비교 기준, 유동성 조건과 중단 기준을 정합니다.",
        ):
            with st.expander("거래 비용과 승격 기준", expanded=False):
                (
                    benchmark_contract,
                    min_price_filter,
                    min_history_months_filter,
                    min_avg_dollar_volume_20d_m_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_benchmark_coverage,
                    promotion_min_net_cagr_spread,
                    promotion_min_liquidity_clean_coverage,
                    promotion_max_underperformance_share,
                    promotion_min_worst_rolling_excess_return,
                    promotion_max_strategy_drawdown,
                    promotion_max_drawdown_gap_vs_benchmark,
                ) = _render_strict_annual_real_money_inputs(
                    key_prefix="vss",
                )
            with st.expander("중단·경고 기준", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                ) = _render_underperformance_guardrail_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value ",
                )
                (
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_drawdown_guardrail_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value ",
                )
                guardrail_reference_ticker = _render_guardrail_reference_ticker_input(
                    key_prefix="vss",
                    benchmark_ticker=benchmark_ticker,
                    default_guardrail_reference_ticker=st.session_state.get("vss_guardrail_reference_ticker"),
                    underperformance_guardrail_enabled=underperformance_guardrail_enabled,
                    drawdown_guardrail_enabled=drawdown_guardrail_enabled,
                )

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Value Snapshot (Strict Annual)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not value_factors:
        validation_errors.append("Value 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "value_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "snapshot_source": "shadow_factors",
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "guardrail_reference_ticker": guardrail_reference_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Value Snapshot (Strict Annual)")

def _render_quality_value_snapshot_strict_quarterly_prototype_form() -> None:
    _apply_single_strategy_prefill("quality_value_snapshot_strict_quarterly_prototype")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="qvqp",
        default_start=_default_strict_factor_start_date(),
        top_default=10,
        top_max=30,
        top_help="분기 Quality + Value 종합 점수 기준으로 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="qvqp",
        presets=QUALITY_STRICT_PRESETS,
        default_preset=STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
        help_text="분기 재무제표 검증 비용을 고려해 100종목 구성을 기본으로 사용합니다.",
        strict_labels=True,
        show_historical_caption=True,
        show_preset_status=False,
    )
    with st.expander("Universe 근거", expanded=False):
        _render_strict_quarterly_productionization_note(family_label="Quality + Value Snapshot (Strict Quarterly)")
        _render_strict_factor_data_readiness_note(
            family_label="Quality + Value Snapshot (Strict Quarterly)",
            statement_freq="quarterly",
            mode_label="strict_statement_quarterly + shadow_factors + quality_value_blend + post_run_readiness",
            combined_factor=True,
            inline=True,
        )
        _render_strict_price_freshness_preflight(
            tickers=tickers,
            end_value=st.session_state.get("qvqp_end", DEFAULT_BACKTEST_END_DATE),
            timeframe=st.session_state.get("qvqp_timeframe", "1d"),
            strategy_label="Quality + Value Snapshot (Strict Quarterly)",
        )
        _render_statement_shadow_coverage_preview(
            tickers=tickers,
            freq="quarterly",
            strategy_label="Quality + Value Snapshot (Strict Quarterly)",
        )
        universe_contract_label = _render_strict_universe_contract_selectbox(
            "Universe 계약",
            key="qvqp_universe_contract",
            help=STRICT_UNIVERSE_CONTRACT_HELP,
        )
        universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
        dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
            universe_contract=universe_contract,
            tickers=tickers,
            preset_name=preset_name,
            statement_freq="quarterly",
        )

    with st.form("quality_value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "분기 Quality + Value 지표와 월말 선택·방어 규칙을 정합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="qvqp_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="qvqp_option")
            rebalance_interval = st.number_input(
                "리밸런싱 간격(개월)",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qvqp_rebalance_interval",
            )
            quality_factors = st.multiselect(
                "Quality 지표",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvqp_quality_factors",
            )
            value_factors = st.multiselect(
                "Value 지표",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvqp_value_factors",
            )
            _render_advanced_group_caption(
                "Quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("추세·시장 필터", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### 추세 필터")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "추세 필터 사용",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qvqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "추세 판단 기간",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qvqp_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor ",
                )
            with st.expander("비중·방어 규칙", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor",
                )
                st.caption(
                    "이 contract들은 quarterly payload와 replay surface에 저장됩니다. "
                    "실제 데이터 문제는 Run 이후 Factor Readiness에서 가격 / statement 기준으로 다시 확인합니다."
                )

        with single_settings_section(
            "비용·위험 기준",
            "분기 검증 경로는 저장된 기본 거래 비용을 사용하며 방어 규칙은 위 설정에 포함됩니다.",
        ):
            st.caption("실행 후 실제 coverage와 비용 영향은 결과의 Factor Readiness에서 확인합니다.")
        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality + Value Snapshot (Strict Quarterly)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Quality 지표를 한 개 이상 선택해 주세요.")
    if not value_factors:
        validation_errors.append("Value 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_value_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "snapshot_source": "shadow_factors",
        "quality_factors": quality_factors,
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Quarterly)")

def _render_quality_value_snapshot_strict_annual_form() -> None:
    _apply_single_strategy_prefill("quality_value_snapshot_strict_annual")
    start_date, end_date, top_n = _render_strict_factor_core_inputs(
        section_label="핵심 실행 설정",
        key_prefix="qvss",
        default_start=_default_strict_factor_start_date(),
        top_default=10,
        top_max=30,
        top_help="연간 Quality + Value 종합 점수 기준으로 최종 보유할 종목 수입니다.",
    )
    universe_mode, preset_name, tickers = _render_strict_factor_universe_inputs(
        section_label="투자 대상 Universe",
        key_prefix="qvss",
        presets=QUALITY_STRICT_PRESETS,
        default_preset=STRICT_ANNUAL_SINGLE_DEFAULT_PRESET,
        help_text="연간 재무제표 coverage가 검증된 미국 주식 구성을 기본으로 사용합니다.",
        strict_labels=True,
        show_historical_caption=True,
        show_preset_status=True,
    )
    with st.expander("Universe 근거", expanded=False):
        _render_strict_factor_data_readiness_note(
            family_label="Quality + Value Snapshot (Strict Annual)",
            statement_freq="annual",
            mode_label="strict_statement_annual + shadow_factors + quality_value_blend",
            combined_factor=True,
            inline=True,
        )
        universe_contract, dynamic_candidate_tickers, dynamic_target_size = _render_strict_universe_contract_setup(
            key="qvss_universe_contract",
            tickers=tickers,
            preset_name=preset_name,
            statement_freq="annual",
        )
        _render_strict_factor_prerun_preview(
            tickers=tickers,
            strategy_label="Quality + Value Snapshot (Strict Annual)",
            preset_name=preset_name,
            universe_contract=universe_contract,
            statement_freq="annual",
        )

    with st.form("quality_value_snapshot_strict_annual_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "연간 Quality + Value 지표, 추세 필터, 비중과 방어 규칙을 정합니다.",
        ):
            timeframe = st.selectbox("가격 간격", options=["1d"], index=0, key="qvss_timeframe")
            option = st.selectbox("선정 시점", options=["month_end"], index=0, key="qvss_option")
            rebalance_interval = st.number_input(
                "리밸런싱 간격(개월)",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qvss_rebalance_interval",
            )
            quality_factors = st.multiselect(
                "Quality 지표",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvss_quality_factors",
            )
            value_factors = st.multiselect(
                "Value 지표",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvss_value_factors",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("추세·시장 필터", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### 추세 필터")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "추세 필터 사용",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qvss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "추세 판단 기간",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qvss_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qvss",
                    label_prefix="",
                )
            with st.expander("비중·방어 규칙", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor",
                )
        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 비교 기준, 유동성 조건과 중단 기준을 정합니다.",
        ):
            with st.expander("거래 비용과 승격 기준", expanded=False):
                (
                    benchmark_contract,
                    min_price_filter,
                    min_history_months_filter,
                    min_avg_dollar_volume_20d_m_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_benchmark_coverage,
                    promotion_min_net_cagr_spread,
                    promotion_min_liquidity_clean_coverage,
                    promotion_max_underperformance_share,
                    promotion_min_worst_rolling_excess_return,
                    promotion_max_strategy_drawdown,
                    promotion_max_drawdown_gap_vs_benchmark,
                ) = _render_strict_annual_real_money_inputs(
                    key_prefix="qvss",
                )
            with st.expander("중단·경고 기준", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                ) = _render_underperformance_guardrail_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor ",
                )
                (
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_drawdown_guardrail_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor ",
                )
                guardrail_reference_ticker = _render_guardrail_reference_ticker_input(
                    key_prefix="qvss",
                    benchmark_ticker=benchmark_ticker,
                    default_guardrail_reference_ticker=st.session_state.get("qvss_guardrail_reference_ticker"),
                    underperformance_guardrail_enabled=underperformance_guardrail_enabled,
                    drawdown_guardrail_enabled=drawdown_guardrail_enabled,
                )

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality + Value Snapshot (Strict Annual)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Quality 지표를 한 개 이상 선택해 주세요.")
    if not value_factors:
        validation_errors.append("Value 지표를 한 개 이상 선택해 주세요.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_value_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "snapshot_source": "shadow_factors",
        "quality_factors": quality_factors,
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "guardrail_reference_ticker": guardrail_reference_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Annual)")

__all__ = [name for name in globals() if not name.startswith("__")]
