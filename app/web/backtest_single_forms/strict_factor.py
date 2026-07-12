from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill


def _render_strict_factor_data_readiness_note(
    *,
    family_label: str,
    statement_freq: str,
    mode_label: str,
    prototype: bool = False,
    combined_factor: bool = False,
) -> None:
    freq_label = str(statement_freq).strip().lower()
    status_label = "research-only prototype" if prototype else "public candidate"
    coverage_note = (
        "quality + value factor가 동시에 필요하므로 usable history를 더 보수적으로 봅니다."
        if combined_factor
        else "선택 universe의 statement shadow factor coverage가 실제 시작 가능 구간을 결정합니다."
    )
    with st.expander("데이터 준비 기준", expanded=False):
        st.markdown(
            f"- **가격**: `Daily Market Update` 또는 OHLCV 수집이 먼저 필요합니다.\n"
            f"- **재무제표**: `Extended Statement Refresh`를 **{freq_label}** 기준으로 준비합니다.\n"
            "- **Factor**: 저장된 statement shadow factor를 읽고, 리밸런싱 시점에 사용 가능한 종목만 평가합니다.\n"
            f"- **상태**: `{family_label}`은 현재 **{status_label}** 경로입니다.\n"
            f"- **주의**: {coverage_note}"
        )
        st.caption(f"Current mode: `{mode_label}`")


def _strict_factor_date_input(label: str, *, default: date, key: str) -> date:
    value = "today" if key in st.session_state else default
    return st.date_input(label, value=value, key=key)


def _render_quality_snapshot_form() -> None:
    st.markdown("### Quality Snapshot")
    st.caption(
        "Archived legacy broad yfinance compatibility path for saved/history replay only. "
        "For new research runs, start from `Quality Snapshot (Strict Annual)` or `Quality + Value / Strict Annual`."
    )
    _render_quality_family_guide("quality_broad")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- 이 archived path는 이미 존재하는 **`nyse_fundamentals` + `nyse_factors`** legacy rows가 있을 때만 재현용으로 사용합니다.\n"
            "- 새 factor 준비나 새 재무제표 source 수집은 `EDGAR annual 재무제표 갱신`과 statement shadow path를 사용하세요.\n"
            "- 첫 공개 버전은 **stock-oriented** 입니다. ETF 위주 유니버스는 quality factor snapshot이 비거나 의미가 약할 수 있습니다.\n"
            "- saved/history replay compatibility 때문에 실행 함수는 남아 있지만, 새 사용자 기본 선택지에서는 제외되어 있습니다."
        )
        st.caption("Archived mode: `legacy_broad_yfinance` (not strict PIT, not canonical financial statement source)")
    _apply_single_strategy_prefill("quality_snapshot")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="첫 factor strategy는 stock-only quality universe를 기준으로 시작하는 편이 안전합니다.",
        key="qs_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []

    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_BROAD_PRESETS.keys()),
            index=0,
            key="qs_preset",
        )
        tickers = QUALITY_BROAD_PRESETS[preset_name]
        _render_ticker_preview(tickers)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="Comma-separated stock tickers. Example: AAPL,MSFT,GOOG",
            key="qs_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    with st.form("quality_snapshot_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qs_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qs_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="Quality score 상위 종목 수입니다.",
                key="qs_top_n",
            )

        st.caption("Hidden defaults in this first pass: `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qs_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qs_option")
            factor_freq = st.selectbox(
                "Factor Frequency",
                options=["annual"],
                index=0,
                key="qs_factor_freq",
                help="첫 버전은 annual quality snapshot만 지원합니다.",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                default=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                key="qs_quality_factors",
                help="높을수록 좋은 factor와 낮을수록 좋은 factor를 내부 score rule로 함께 처리합니다.",
            )
            snapshot_mode = st.selectbox(
                "Snapshot Mode",
                options=["broad_research"],
                index=0,
                key="qs_snapshot_mode",
                help="첫 공개 버전은 broad-research snapshot을 사용합니다. strict PIT mode는 후속 단계로 남겨둡니다.",
            )

        submitted = st.form_submit_button("Run Quality Snapshot Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

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
    st.markdown("### Quality Snapshot (Strict Annual)")
    st.caption("Strict annual statement-driven quality strategy. This public candidate ranks annual statement shadow factors, then by default holds the top names equally between monthly rebalances.")
    _render_strict_factor_data_readiness_note(
        family_label="Quality Snapshot (Strict Annual)",
        statement_freq="annual",
        mode_label="strict_statement_annual + shadow_factors",
    )
    _apply_single_strategy_prefill("quality_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="Single Strategy에서는 annual statement coverage가 검증된 미국 주식 preset을 기본값으로 사용합니다.",
        key="qss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            format_func=strict_preset_display_label,
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="qss_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name, tickers)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

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

    with st.form("quality_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "Start Date",
                default=_default_strict_factor_start_date(),
                key="qss_start",
            )
        with col2:
            end_date = _strict_factor_date_input("End Date", default=DEFAULT_BACKTEST_END_DATE, key="qss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="strict annual quality 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement snapshots`, `monthly rebalance`, `equal-weight holding by default`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qss_rebalance_interval",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qss_quality_factors",
                help="기본은 coverage-first 팩터 조합입니다. 필요하면 예전 quality factor도 다시 포함할 수 있습니다.",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
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
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
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
            with st.expander("Promotion Policy Signal", expanded=False):
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
            with st.expander("Guardrails", expanded=False):
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

        submitted = st.form_submit_button("Run Strict Annual Quality Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality Snapshot (Strict Annual)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

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
    st.markdown("### Quality Snapshot (Strict Quarterly)")
    st.caption("Strict quarterly quality strategy. This formal path ranks quarterly statement shadow factors and keeps the top names equally between monthly rebalances.")
    _render_strict_quarterly_productionization_note(family_label="Quality Snapshot (Strict Quarterly)")
    _apply_single_strategy_prefill("quality_snapshot_strict_quarterly_prototype")

    _render_strict_factor_data_readiness_note(
        family_label="Quality Snapshot (Strict Quarterly)",
        statement_freq="quarterly",
        mode_label="strict_statement_quarterly + shadow_factors + post_run_readiness",
    )
    with st.expander("Quarterly data readiness", expanded=False):
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "Factor 기반 strict 전략은 실행 비용과 coverage 안정성을 위해 한 번에 최대 5년 범위로 실행합니다."
        )

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict first pass는 검증 비용을 낮추기 위해 `US Base Universe 100`을 기본 preset으로 둡니다.",
        key="qsqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            format_func=strict_preset_display_label,
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="qsqp_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qsqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

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

    with st.form("quality_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "Start Date",
                default=_default_strict_factor_start_date(),
                key="qsqp_start",
            )
        with col2:
            end_date = _strict_factor_date_input("End Date", default=DEFAULT_BACKTEST_END_DATE, key="qsqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="strict quarterly quality 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qsqp_top_n",
            )

        st.caption("Defaults: `quarterly statement snapshots`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qsqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qsqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qsqp_rebalance_interval",
            )
            universe_contract_label = _render_strict_universe_contract_selectbox(
                "Universe Contract",
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
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qsqp_quality_factors",
                help="first-pass quarterly strict도 quality strict와 같은 coverage-first 팩터 조합을 기본값으로 사용합니다.",
            )
            _render_advanced_group_caption(
                "Quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qsqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
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
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
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

        submitted = st.form_submit_button("Run Strict Quarterly Quality Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality Snapshot (Strict Quarterly)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

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
    st.markdown("### Value Snapshot (Strict Quarterly)")
    st.caption(
        "Strict quarterly value strategy. This Phase 8 path ranks quarterly statement shadow value factors and holds the cheapest names equally between monthly rebalances."
    )
    _render_strict_quarterly_productionization_note(family_label="Value Snapshot (Strict Quarterly)")
    _render_strict_factor_data_readiness_note(
        family_label="Value Snapshot (Strict Quarterly)",
        statement_freq="quarterly",
        mode_label="strict_statement_quarterly + shadow_factors + post_run_readiness",
    )
    with st.expander("Quarterly data readiness", expanded=False):
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "`US Base Universe 100` 기본 preset은 검증용 anchor일 뿐이고, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦게 열릴 수 있습니다."
        )
    _apply_single_strategy_prefill("value_snapshot_strict_quarterly_prototype")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict value는 검증 비용을 낮추기 위해 `US Base Universe 100`을 기본 preset으로 둡니다.",
        key="vsqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(VALUE_STRICT_PRESETS.keys()),
            format_func=strict_preset_display_label,
            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="vsqp_preset",
        )
        tickers = VALUE_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="vsqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

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

    with st.form("value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "Start Date",
                default=_default_strict_factor_start_date(),
                key="vsqp_start",
            )
        with col2:
            end_date = _strict_factor_date_input("End Date", default=DEFAULT_BACKTEST_END_DATE, key="vsqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="strict quarterly value 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="vsqp_top_n",
            )

        st.caption("Defaults: `quarterly statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="vsqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="vsqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="vsqp_rebalance_interval",
            )
            universe_contract_label = _render_strict_universe_contract_selectbox(
                "Universe Contract",
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
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vsqp_value_factors",
                help="quarterly strict도 yield / book-to-market 중심의 coverage-first 기본 조합을 사용합니다.",
            )
            _render_advanced_group_caption(
                "Quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="vsqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
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
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
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

        submitted = st.form_submit_button("Run Strict Quarterly Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Value Snapshot (Strict Quarterly)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

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
    st.markdown("### Value Snapshot (Strict Annual)")
    st.caption("Strict annual statement-driven value strategy. This public candidate ranks precomputed annual statement shadow factors and by default holds the cheapest names equally between monthly rebalances.")
    _render_strict_factor_data_readiness_note(
        family_label="Value Snapshot (Strict Annual)",
        statement_freq="annual",
        mode_label="strict_statement_annual + shadow_factors",
    )
    _apply_single_strategy_prefill("value_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="strict annual value도 annual coverage가 확인된 preset을 기본값으로 사용합니다.",
        key="vss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(VALUE_STRICT_PRESETS.keys()),
            format_func=strict_preset_display_label,
            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="vss_preset",
        )
        tickers = VALUE_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name, tickers)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="vss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

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

    with st.form("value_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "Start Date",
                default=_default_strict_factor_start_date(),
                key="vss_start",
            )
        with col2:
            end_date = _strict_factor_date_input("End Date", default=DEFAULT_BACKTEST_END_DATE, key="vss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="strict annual value 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="vss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement shadow factors`, `monthly rebalance`, `equal-weight holding by default`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="vss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="vss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="vss_rebalance_interval",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vss_value_factors",
                help="높을수록 좋은 yield / book-to-market 계열과 낮을수록 좋은 inverse multiple 계열을 함께 지원합니다.",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="vss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
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
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
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
            with st.expander("Promotion Policy Signal", expanded=False):
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
            with st.expander("Guardrails", expanded=False):
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

        submitted = st.form_submit_button("Run Strict Annual Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Value Snapshot (Strict Annual)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

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
    st.markdown("### Quality + Value Snapshot (Strict Quarterly)")
    st.caption(
        "Strict quarterly multi-factor strategy. This Phase 8 path blends quarterly quality and value shadow factors, then holds the combined top names equally between monthly rebalances."
    )
    _render_strict_quarterly_productionization_note(family_label="Quality + Value Snapshot (Strict Quarterly)")
    _render_strict_factor_data_readiness_note(
        family_label="Quality + Value Snapshot (Strict Quarterly)",
        statement_freq="quarterly",
        mode_label="strict_statement_quarterly + shadow_factors + quality_value_blend + post_run_readiness",
        combined_factor=True,
    )
    with st.expander("Quarterly data readiness", expanded=False):
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "`US Base Universe 100` 기본 preset은 검증 anchor이고, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦게 열릴 수 있습니다."
        )
    _apply_single_strategy_prefill("quality_value_snapshot_strict_quarterly_prototype")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict multi-factor는 검증 비용을 낮추기 위해 `US Base Universe 100`을 기본 preset으로 둡니다.",
        key="qvqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            format_func=strict_preset_display_label,
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="qvqp_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qvqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

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

    with st.form("quality_value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "Start Date",
                default=_default_strict_factor_start_date(),
                key="qvqp_start",
            )
        with col2:
            end_date = _strict_factor_date_input("End Date", default=DEFAULT_BACKTEST_END_DATE, key="qvqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                help="strict quarterly multi-factor 종합 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qvqp_top_n",
            )

        st.caption("Defaults: `quarterly statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qvqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qvqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qvqp_rebalance_interval",
            )
            universe_contract_label = _render_strict_universe_contract_selectbox(
                "Universe Contract",
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
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvqp_quality_factors",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvqp_value_factors",
            )
            _render_advanced_group_caption(
                "Quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qvqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
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
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
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

        submitted = st.form_submit_button("Run Strict Quarterly Quality + Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality + Value Snapshot (Strict Quarterly)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

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
    st.markdown("### Quality + Value Snapshot (Strict Annual)")
    st.caption(
        "Strict annual multi-factor strategy. This public candidate blends coverage-first quality signals "
        "with annual statement-driven valuation factors, then by default holds the combined top names equally between monthly rebalances."
    )
    _render_strict_factor_data_readiness_note(
        family_label="Quality + Value Snapshot (Strict Annual)",
        statement_freq="annual",
        mode_label="strict_statement_annual + shadow_factors + quality_value_blend",
        combined_factor=True,
    )
    _apply_single_strategy_prefill("quality_value_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="strict annual multi-factor도 annual coverage가 검증된 preset을 기본값으로 사용합니다.",
        key="qvss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            format_func=strict_preset_display_label,
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="qvss_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name, tickers)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qvss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

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

    with st.form("quality_value_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = _strict_factor_date_input(
                "Start Date",
                default=_default_strict_factor_start_date(),
                key="qvss_start",
            )
        with col2:
            end_date = _strict_factor_date_input("End Date", default=DEFAULT_BACKTEST_END_DATE, key="qvss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                help="strict annual multi-factor 종합 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qvss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement shadow factors`, `monthly rebalance`, `equal-weight holding by default`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qvss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qvss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qvss_rebalance_interval",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvss_quality_factors",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvss_value_factors",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qvss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
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
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
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
            with st.expander("Promotion Policy Signal", expanded=False):
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
            with st.expander("Guardrails", expanded=False):
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

        submitted = st.form_submit_button("Run Strict Annual Quality + Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    window_error = validate_strict_factor_backtest_window(
        start_date,
        end_date,
        strategy_label="Quality + Value Snapshot (Strict Annual)",
    )
    if window_error:
        validation_errors.append(window_error)
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

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
