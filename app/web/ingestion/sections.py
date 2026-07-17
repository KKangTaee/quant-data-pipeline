"""Collection workbench section renderers for Workspace > Ingestion."""

from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from app.web.ingestion.registry import (
    INGESTION_COLLECTION_MANUAL,
    INGESTION_COLLECTION_OPERATIONAL,
    INGESTION_COLLECTION_RECORDS,
)


def _bind_page_globals() -> None:
    from app.web.ingestion import page

    globals().update(
        {
            name: getattr(page, name)
            for name in dir(page)
            if not name.startswith("__")
        }
    )


def render_operational_section() -> Any:
    _bind_page_globals()
    current_progress_callback = None
    st.info(
        "일상 운영 / 검증 데이터: 백테스트와 Practical Validation, Overview가 DB에서 읽을 데이터를 채웁니다. "
        "수집 결과가 부분 성공이면 downstream 화면에서도 coverage gap으로 남을 수 있습니다."
    )

    with st.expander("일별 가격 업데이트", expanded=True):
        _render_job_brief("daily_market_update")
        st.caption("권장 주기: 매 거래일 장 마감 후 또는 다음 backtest/data sync 전에 실행합니다.")
        st.caption(
            "권장 source: 평소 운영은 `Profile Filtered Stocks + ETFs`를 사용합니다. "
            "raw `NYSE Stocks + ETFs`는 넓은 universe를 다시 훑어야 할 때만 사용하세요."
        )
        st.caption("기본값: `Profile Filtered Stocks + ETFs`, `1d`, `1d`.")
        st.caption("저장 테이블: `finance_price.nyse_price_history`")
        daily_symbol_result = _render_symbol_source_inputs(
            "daily_market",
            "Daily Market Symbols",
            default_source_mode="Profile Filtered Stocks + ETFs",
        )
        daily_symbols_input = daily_symbol_result["symbols"]
        daily_source_mode = daily_symbol_result.get("source_mode") or "Manual"
        daily_raw_source_modes = {"NYSE Stocks", "NYSE ETFs", "NYSE Stocks + ETFs"}
        daily_filter_non_plain = st.checkbox(
            "Exclude special share-class / non-plain symbols",
            value=True,
            key="daily_filter_non_plain_symbols",
            help=(
                "When raw NYSE universes are selected, exclude symbols such as preferred/unit/special share classes. "
                "This usually reduces noisy provider failures and wasted requests."
            ),
        )
        daily_filtered_symbols: list[str] = list(daily_symbols_input)
        daily_excluded_symbols: list[str] = []
        if daily_filter_non_plain and daily_source_mode in daily_raw_source_modes:
            daily_filtered_symbols, daily_excluded_symbols = filter_non_plain_symbols(daily_symbols_input)
            if daily_excluded_symbols:
                st.info(
                    "provider 안정성을 위해 특수 share-class / non-plain symbol을 제외했습니다: "
                    f"`{len(daily_excluded_symbols)}`개 제외, `{len(daily_filtered_symbols)}`개 실행 대상."
                )
                st.caption(f"제외 sample: {', '.join(daily_excluded_symbols[:10])}")
        daily_symbols_input = daily_filtered_symbols
        daily_col1, daily_col2 = st.columns(2)
        daily_period_input = daily_col1.selectbox("Daily Period", PERIOD_PRESETS, index=0, key="daily_period_input")
        daily_interval_input = daily_col2.selectbox("Daily Interval", ["1d", "1wk", "1mo"], index=0, key="daily_interval_input")
        daily_col3, daily_col4 = st.columns(2)
        daily_start_input = daily_col3.text_input("Daily Start", value="", key="daily_start_input")
        daily_end_input = daily_col4.text_input("Daily End", value="", key="daily_end_input")
        daily_resolved_period, daily_resolved_start, daily_resolved_end = _normalize_ohlcv_window(
            daily_period_input,
            daily_start_input,
            daily_end_input,
        )
        daily_execution_profile, daily_profile_caption = _resolve_daily_market_execution_profile(
            daily_source_mode,
            period=daily_resolved_period,
            start=daily_resolved_start,
            end=daily_resolved_end,
            interval=daily_interval_input,
        )
        st.caption(daily_profile_caption)
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", _format_symbol_source_label(daily_source_mode)),
                ("대상 수", f"{len(daily_symbols_input):,} symbols"),
                (
                    "기간",
                    _format_contract_window(
                        period=daily_resolved_period,
                        start=daily_resolved_start,
                        end=daily_resolved_end,
                    ),
                ),
                ("Interval", daily_interval_input),
                ("Execution profile", daily_execution_profile),
            ],
            note=(
                "이 설정으로 가격 row를 저장합니다. 저장 row 수가 있어도 요청 기간 전체 coverage를 뜻하지는 않으므로 "
                "결과 해석과 DB coverage quick check를 함께 보세요."
            ),
        )
        _render_price_window_preflight(
            symbols=daily_symbols_input,
            start=daily_resolved_start,
            end=daily_resolved_end,
            timeframe=daily_interval_input,
        )
        daily_symbol_check = check_symbol_input(daily_symbols_input)
        _render_check_result(daily_symbol_check)
        daily_run_allowed = _render_large_run_guard(
            prefix="daily_market",
            job_name="daily_market_update",
            symbols=daily_symbols_input,
        )
        daily_collection_params = _build_ohlcv_collection_params(
            symbols=daily_symbols_input,
            start=daily_resolved_start,
            end=daily_resolved_end,
            period=daily_resolved_period,
            interval=daily_interval_input,
            execution_profile=daily_execution_profile,
            excluded_symbols=daily_excluded_symbols,
        )
        if st.button(
            "일별 가격 업데이트 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(daily_symbol_check) or not daily_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "daily_market_update",
                    "job_name": "daily_market_update",
                    "spinner_text": "Running daily market update...",
                    "params": daily_collection_params,
                    "run_metadata": _job_metadata(
                        pipeline_type="daily_market_update",
                        execution_mode="operational",
                        symbol_source=daily_symbol_result.get("source_mode"),
                        symbol_count=len(daily_symbols_input),
                        execution_context=(
                            "Routine daily price-history refresh for the selected operating universe. "
                            "Managed universes use managed execution profiles; raw NYSE sweeps use the heavy profile."
                        ),
                        input_params={
                            "start": daily_resolved_start,
                            "end": daily_resolved_end,
                            "period": daily_resolved_period,
                            "interval": daily_interval_input,
                            "execution_profile": daily_execution_profile,
                            "exclude_non_plain_symbols": daily_filter_non_plain,
                            "excluded_symbols": daily_excluded_symbols,
                        },
                    ),
                }
            )
        if _is_running_action("daily_market_update"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Daily Market Update",
            )
        _render_inline_last_completed_result("daily_market_update")

    with st.expander("선물 OHLCV 수집", expanded=False):
        _render_job_brief("collect_futures_ohlcv")
        st.caption("Overview Futures Monitor에서 사용할 선물 캔들 데이터를 수집합니다.")
        st.caption("기본값은 주요 지수 / 금리 / 원자재 / FX 선물이며, 저장 테이블은 `finance_price.futures_ohlcv`입니다.")
        futures_symbols_text = st.text_area(
            "Futures Symbols",
            value=", ".join(DEFAULT_CORE_FUTURES_SYMBOLS),
            key="futures_ohlcv_symbols_input",
            help="Yahoo/yfinance futures ticker를 쉼표 또는 줄바꿈으로 입력합니다.",
        )
        futures_symbols_input = [
            item.strip().upper()
            for item in futures_symbols_text.replace("\n", ",").split(",")
            if item.strip()
        ]
        futures_col1, futures_col2, futures_col3 = st.columns(3)
        futures_period_input = futures_col1.selectbox(
            "Futures Period",
            ["1d", "5d", "7d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=0,
            key="futures_ohlcv_period_input",
        )
        futures_interval_input = futures_col2.selectbox(
            "Futures Interval",
            ["1m", "2m", "5m", "15m", "1h", "1d"],
            index=0,
            key="futures_ohlcv_interval_input",
        )
        futures_max_symbols = int(
            futures_col3.number_input(
                "Max Symbols",
                min_value=1,
                max_value=24,
                value=min(24, max(1, len(futures_symbols_input))),
                step=1,
                key="futures_ohlcv_max_symbols",
            )
        )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", "yfinance pilot"),
                (
                    "대상 수",
                    f"{min(len(futures_symbols_input), futures_max_symbols):,} / {len(futures_symbols_input):,} symbols",
                ),
                ("기간", futures_period_input),
                ("Interval", futures_interval_input),
                ("Cadence", "manual"),
            ],
            note=(
                "이 수집은 선물 시장 컨텍스트용입니다. 무료 provider 지연 / 누락 가능성이 있어 "
                "Overview에서 stale / failed 상태를 함께 확인해야 합니다."
            ),
        )
        futures_symbol_check = check_symbol_input(futures_symbols_input)
        _render_check_result(futures_symbol_check)
        if st.button(
            "선물 OHLCV 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(futures_symbol_check),
        ):
            _schedule_job(
                {
                    "action": "collect_futures_ohlcv",
                    "job_name": "collect_futures_ohlcv",
                    "spinner_text": "Running futures OHLCV collection...",
                    "params": {
                        "symbols": futures_symbols_input,
                        "period": futures_period_input,
                        "interval": futures_interval_input,
                        "cadence_mode": "manual",
                        "max_symbols": futures_max_symbols,
                        "batch_size": 6,
                        "sleep_sec": 0.1,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="overview_futures_market_monitor",
                        execution_mode="manual",
                        symbol_source="manual_futures_watchlist",
                        symbol_count=min(len(futures_symbols_input), futures_max_symbols),
                        execution_context="Manual futures OHLCV refresh for Overview Futures Monitor.",
                        input_params={
                            "period": futures_period_input,
                            "interval": futures_interval_input,
                            "max_symbols": futures_max_symbols,
                        },
                    ),
                }
            )
        _render_inline_last_completed_result("collect_futures_ohlcv")
        if _is_running_action("collect_futures_ohlcv"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Futures OHLCV Collection",
            )

    with st.expander("시장 심리 수집", expanded=False):
        _render_job_brief("collect_market_sentiment")
        st.caption("저장 테이블: `finance_meta.macro_series_observation`")
        sentiment_cols = st.columns(2)
        include_cnn = sentiment_cols[0].checkbox(
            "CNN Fear & Greed",
            value=True,
            key="market_sentiment_include_cnn",
        )
        include_aaii = sentiment_cols[1].checkbox(
            "AAII Sentiment Survey",
            value=True,
            key="market_sentiment_include_aaii",
        )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("CNN", "enabled" if include_cnn else "disabled"),
                ("AAII", "enabled" if include_aaii else "disabled"),
                ("저장 위치", "finance_meta.macro_series_observation"),
            ],
            note=(
                "이 수집은 Overview 시장 심리 context용입니다. source 차단이나 partial result는 "
                "Overview Sentiment / Data Health에 그대로 남깁니다."
            ),
        )
        if st.button(
            "시장 심리 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or not (include_cnn or include_aaii),
        ):
            _schedule_job(
                {
                    "action": "collect_market_sentiment",
                    "job_name": "collect_market_sentiment",
                    "spinner_text": "Running market sentiment collection...",
                    "params": {
                        "include_cnn": bool(include_cnn),
                        "include_aaii": bool(include_aaii),
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="overview_market_sentiment",
                        execution_mode="manual",
                        symbol_source="CNN Fear & Greed / AAII Sentiment Survey",
                        symbol_count=int(bool(include_cnn)) + int(bool(include_aaii)),
                        execution_context="Manual market sentiment refresh for Overview Sentiment.",
                        input_params={
                            "include_cnn": bool(include_cnn),
                            "include_aaii": bool(include_aaii),
                        },
                    ),
                }
            )
        if _is_running_action("collect_market_sentiment"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Market Sentiment",
            )
        _render_inline_last_completed_result("collect_market_sentiment")

    with st.expander("EDGAR 재무제표 갱신", expanded=False):
        _render_job_brief("extended_statement_refresh")
        st.caption("권장 주기: 월 1회 또는 긴 기간 factor research / backtest 준비 전에 실행합니다.")
        st.caption("권장 source: `Profile Filtered Stocks`나 statement coverage preset부터 시작하세요.")
        st.caption(
            "새 재무제표 coverage와 strict factor 준비는 이 EDGAR refresh에서 시작합니다. "
            "수동 `Financial Statement Ingestion` card는 복구 / 진단용으로 남아 있습니다."
        )
        st.caption(
            "symbol preset dropdown에는 관리용 coverage preset도 있습니다: "
            "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, and `US Statement Coverage 1000`."
        )
        st.caption("기본값: `Profile Filtered Stocks`, `annual`, `0 periods (all available)`.")
        st.caption("SEC fair access를 위해 `SEC_USER_AGENT`와 pacing을 확인한 뒤 대량 실행하세요.")
        st.caption(
            "저장 테이블: "
            "`finance_fundamental.nyse_financial_statement_filings`, "
            "`finance_fundamental.nyse_financial_statement_labels`, "
            "`finance_fundamental.nyse_financial_statement_values`, "
            "`finance_fundamental.nyse_fundamentals_statement`, "
            "`finance_fundamental.nyse_factors_statement`"
        )
        ext_symbol_result = _render_symbol_source_inputs(
            "extended_statement",
            "EDGAR Statement Symbols",
            default_source_mode="Profile Filtered Stocks",
        )
        ext_symbols_input = ext_symbol_result["symbols"]
        ext_col1, ext_col2 = st.columns(2)
        ext_period_input = ext_col1.selectbox("EDGAR Statement Period Type", ["annual", "quarterly"], index=0, key="ext_period_input")
        ext_periods_input = ext_col2.number_input(
            "EDGAR Statement Periods",
            min_value=0,
            max_value=80,
            value=0,
            step=1,
            key="ext_periods_input",
            help="`0` means collect all available statement periods from the source. Use this for PIT recovery and quarterly history hardening.",
        )
        st.caption("`freq`는 선택한 `Period Type`에 자동으로 맞춰 실행됩니다.")
        st.caption("Tip: `0 = all available periods`. 짧은 rolling refresh를 의도할 때만 양수를 입력하세요.")
        ext_symbol_check = check_symbol_input(ext_symbols_input)
        _render_check_result(ext_symbol_check)
        ext_run_allowed = _render_large_run_guard(
            prefix="extended_statement",
            job_name="extended_statement_refresh",
            symbols=ext_symbols_input,
        )
        if st.button(
            "EDGAR 재무제표 갱신 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(ext_symbol_check) or not ext_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "extended_statement_refresh",
                    "job_name": "extended_statement_refresh",
                    "spinner_text": "Running EDGAR statement refresh...",
                    "params": {
                        "symbols": ext_symbols_input,
                        "freq": ext_period_input,
                        "periods": int(ext_periods_input),
                        "period": ext_period_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="extended_statement_refresh",
                        execution_mode="operational",
                        symbol_source=ext_symbol_result.get("source_mode"),
                        symbol_count=len(ext_symbols_input),
                        execution_context="Primary EDGAR financial statement refresh and statement shadow rebuild.",
                        input_params={
                            "freq": ext_period_input,
                            "periods": int(ext_periods_input),
                            "period": ext_period_input,
                        },
                    ),
                }
            )
        if _is_running_action("extended_statement_refresh"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="EDGAR Statement Refresh",
            )
        _render_inline_last_completed_result("extended_statement_refresh")

    with st.expander("SEC Form 13F 데이터셋 수집", expanded=False):
        _render_job_brief("collect_sec_13f_dataset")
        st.caption(
            "SEC 공식 Form 13F quarterly data set zip을 DB에 저장해 `Workspace > Institutional Portfolios`에서 읽습니다. "
            "13F는 분기 지연 공시이며 현재 매매 의도를 뜻하지 않습니다."
        )
        st.caption(
            "저장 테이블: `finance_meta.institutional_13f_manager`, "
            "`finance_meta.institutional_13f_filing`, `finance_meta.institutional_13f_holding`, "
            "`finance_meta.institutional_13f_refresh_status`"
        )
        sec13f_default_url = (
            "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/"
            "01mar2026-31may2026_form13f.zip"
        )
        sec13f_cols = st.columns(2)
        sec13f_dataset_label = sec13f_cols[0].text_input(
            "Dataset Label",
            value="2026-march-april-may",
            key="sec13f_dataset_label",
            help="DB source_dataset에 저장할 사람이 읽는 label입니다.",
        )
        sec13f_user_agent = sec13f_cols[1].text_input(
            "SEC User-Agent Override",
            value="",
            key="sec13f_user_agent",
            help="선택 사항입니다. 비워두면 SEC_USER_AGENT 환경변수 또는 collector 기본값을 사용합니다.",
        )
        sec13f_url = st.text_input(
            "SEC 13F Dataset URL",
            value=sec13f_default_url,
            key="sec13f_dataset_url",
            help="SEC Form 13F Data Sets 페이지의 official zip 링크를 입력합니다.",
        )
        sec13f_local_path = st.text_input(
            "Local Zip Path",
            value="",
            key="sec13f_local_zip_path",
            help="이미 내려받은 zip 파일이 있으면 이 경로를 우선 사용합니다. 입력하면 URL download를 하지 않습니다.",
        )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", "SEC Form 13F official data set"),
                ("Dataset", sec13f_dataset_label or "-"),
                ("Input", "local zip path" if sec13f_local_path.strip() else "SEC URL"),
                ("저장 위치", "finance_meta institutional_13f_* tables"),
            ],
            note=(
                "이 수집은 대용량 quarterly zip을 처리할 수 있습니다. UI는 결과만 읽고, full holdings row는 DB에 남깁니다. "
                "CUSIP-symbol mapping은 별도 mapping table이 보강되기 전까지 partial입니다."
            ),
        )
        if st.button(
            "SEC Form 13F 데이터셋 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or not (sec13f_local_path.strip() or sec13f_url.strip()),
        ):
            _schedule_job(
                {
                    "action": "collect_sec_13f_dataset",
                    "job_name": "collect_sec_13f_dataset",
                    "spinner_text": "Collecting SEC Form 13F data set...",
                    "params": {
                        "dataset_url": None if sec13f_local_path.strip() else sec13f_url.strip(),
                        "dataset_zip_path": sec13f_local_path.strip() or None,
                        "source_dataset": sec13f_dataset_label.strip() or None,
                        "user_agent": sec13f_user_agent.strip() or None,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="institutional_13f_dataset_collection",
                        execution_mode="operational_low_frequency",
                        symbol_source="SEC Form 13F official data set",
                        symbol_count=None,
                        execution_context=(
                            "Institutional Portfolios Workspace가 읽을 SEC 13F filing / holdings snapshot을 DB에 저장합니다."
                        ),
                        input_params={
                            "dataset_url": None if sec13f_local_path.strip() else sec13f_url.strip(),
                            "dataset_zip_path": sec13f_local_path.strip() or None,
                            "source_dataset": sec13f_dataset_label.strip() or None,
                        },
                    ),
                }
            )
        if _is_running_action("collect_sec_13f_dataset"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="SEC Form 13F Data Set",
            )
        _render_inline_last_completed_result("collect_sec_13f_dataset")

    with st.expander("종목 메타데이터 업데이트", expanded=False):
        _render_job_brief("metadata_refresh")
        st.caption("권장 주기: 주 1회 또는 tracked universe / profile filter가 바뀐 뒤 실행합니다.")
        st.caption("권장 scope: 한쪽만 갱신할 의도가 아니라면 `stock`과 `etf`를 함께 선택하세요.")
        st.caption("저장 테이블: `finance_meta.nyse_asset_profile`")
        metadata_kind_options = st.multiselect(
            "Metadata Refresh Kinds",
            options=["stock", "etf"],
            default=["stock", "etf"],
            key="metadata_kind_options",
        )
        metadata_kinds = tuple(metadata_kind_options) if metadata_kind_options else ()
        metadata_check = check_asset_profile_prerequisites(metadata_kinds)
        _render_check_result(metadata_check)
        if st.button(
            "종목 메타데이터 업데이트 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(metadata_check),
        ):
            _schedule_job(
                _build_asset_profile_job(
                    action="metadata_refresh",
                    job_name="metadata_refresh",
                    spinner_text="Running metadata refresh...",
                    kinds=metadata_kinds,
                    pipeline_type="metadata_refresh",
                    execution_mode="operational",
                    execution_context="Routine metadata refresh for tracked stock and ETF asset profiles.",
                )
            )
        if _is_running_action("metadata_refresh"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Metadata Refresh",
            )
        _render_inline_last_completed_result("metadata_refresh")

    with st.expander("S&P 500 실제 EPS 등록", expanded=False):
        _render_job_brief("import_sp500_index_earnings_xlsx")
        st.write(
            "경제 사이클의 `실제 TTM EPS`에 사용할 S&P 500 완료 분기 실적을 등록합니다. "
            "공식 S&P 500 페이지에서 `Index Earnings` 파일을 내려받은 뒤 그대로 업로드하세요."
        )
        st.link_button(
            "S&P 500 공식 페이지에서 Index Earnings 받기",
            "https://www.spglobal.com/spdji/en/indices/equity/sp-500/",
            use_container_width=True,
        )
        st.caption(
            "앱은 actual/estimate 상태와 As-Reported/Operating 구분이 명시된 분기만 반영합니다. "
            "경제 사이클의 현재·전년 TTM 비교에는 실제 As-Reported 분기 8개가 필요합니다."
        )
        sp500_eps_file = st.file_uploader(
            "S&P Index Earnings XLSX",
            type=["xlsx"],
            key="sp500_index_earnings_xlsx",
            help="S&P 공식 페이지의 Documents 영역에 있는 Index Earnings XLSX를 선택합니다.",
        )
        sp500_eps_release_date = st.date_input(
            "자료 발표일",
            value=date.today(),
            key="sp500_index_earnings_release_date",
            help="이 파일을 확인하거나 내려받은 날짜가 아니라 S&P가 이 자료를 공개한 날짜를 입력합니다.",
        )
        if st.button(
            "실제 EPS 반영",
            use_container_width=True,
            disabled=_has_running_job() or sp500_eps_file is None,
        ):
            _schedule_job(
                {
                    "action": "import_sp500_index_earnings_xlsx",
                    "job_name": "import_sp500_index_earnings_xlsx",
                    "spinner_text": "S&P 500 실제 EPS 분기를 검증하고 등록하는 중입니다...",
                    "params": {
                        "workbook_content": sp500_eps_file.getvalue(),
                        "source_release_date": str(sp500_eps_release_date),
                        "source_name": sp500_eps_file.name,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="sp500_index_earnings_registration",
                        execution_mode="manual_official_file_import",
                        symbol_source="S&P Dow Jones Indices official Index Earnings XLSX",
                        symbol_count=None,
                        execution_context=(
                            "S&P 공식 Index Earnings workbook의 명시적 actual As-Reported 분기를 "
                            "경제 사이클 실제 TTM EPS 입력으로 등록합니다."
                        ),
                        input_params={
                            "source_release_date": str(sp500_eps_release_date),
                            "source_name": sp500_eps_file.name,
                        },
                    ),
                }
            )
        _render_inline_last_completed_result("import_sp500_index_earnings_xlsx")

    with st.expander("시장 이벤트 캘린더 수집", expanded=False):
        st.write("Overview Events 탭에서 읽을 시장 이벤트 캘린더를 공식 무료 소스에서 수집합니다.")
        st.caption(
            "현재 구현 대상: Federal Reserve FOMC, BLS/BEA macro release schedule, "
            "Nasdaq/Cboe/Russell market-structure calendar, yfinance + Nasdaq cross-check 기반 earnings estimate."
        )
        st.caption("저장 테이블: `finance_meta.market_event_calendar`")
        fomc_tab, macro_event_tab, market_structure_tab, earnings_tab = st.tabs(
            ["FOMC 일정", "매크로 발표", "시장 구조 일정", "실적 발표"]
        )
        with fomc_tab:
            _render_job_brief("collect_fomc_calendar")
            current_year = date.today().year
            fomc_year_options = list(range(current_year - 1, current_year + 3))
            fomc_years = st.multiselect(
                "FOMC Years",
                options=fomc_year_options,
                default=[current_year, current_year + 1],
                key="overview_fomc_calendar_years",
                help="비워두면 Fed 페이지에서 파싱 가능한 모든 연도 row를 수집합니다.",
            )
            if st.button(
                "FOMC 일정 수집",
                use_container_width=True,
                disabled=_has_running_job(),
            ):
                _schedule_job(
                    {
                        "action": "collect_fomc_calendar",
                        "job_name": "collect_fomc_calendar",
                        "spinner_text": "Collecting FOMC calendar from the official Fed page...",
                        "params": {
                            "years": tuple(fomc_years) if fomc_years else None,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational",
                            symbol_source="Federal Reserve official FOMC calendar",
                            symbol_count=None,
                            execution_context=(
                                "Overview Events 탭에서 사용할 FOMC meeting calendar를 Fed 공식 HTML에서 파싱해 DB에 저장합니다."
                            ),
                            input_params={
                                "years": tuple(fomc_years) if fomc_years else None,
                            },
                        ),
                    }
                )
        with macro_event_tab:
            _render_job_brief("collect_macro_calendar")
            current_year = date.today().year
            macro_year_options = list(range(current_year - 1, current_year + 3))
            macro_years = st.multiselect(
                "Macro Calendar Years",
                options=macro_year_options,
                default=[current_year, current_year + 1],
                key="overview_macro_calendar_years",
                help="BLS는 선택 연도별 schedule page를, BEA는 full release schedule에서 일치하는 연도를 수집합니다.",
            )
            macro_source_cols = st.columns(5, gap="small")
            macro_include_bls = macro_source_cols[0].checkbox(
                "BLS inflation / labor",
                value=True,
                key="overview_macro_include_bls",
            )
            macro_include_bea = macro_source_cols[1].checkbox(
                "BEA GDP / PCE",
                value=True,
                key="overview_macro_include_bea",
            )
            macro_include_census = macro_source_cols[2].checkbox(
                "Census indicators",
                value=True,
                key="overview_macro_include_census",
            )
            macro_include_ism = macro_source_cols[3].checkbox(
                "ISM PMI",
                value=True,
                key="overview_macro_include_ism",
            )
            macro_include_treasury = macro_source_cols[4].checkbox(
                "Treasury auctions",
                value=True,
                key="overview_macro_include_treasury",
            )
            st.caption(
                "공식 source request는 네트워크/정책에 따라 차단될 수 있습니다. 실패하면 job result와 Data Health에서 확인합니다."
            )
            if st.button(
                "공식 매크로 발표 일정 수집",
                use_container_width=True,
                disabled=_has_running_job()
                or not (
                    macro_include_bls
                    or macro_include_bea
                    or macro_include_census
                    or macro_include_ism
                    or macro_include_treasury
                ),
            ):
                _schedule_job(
                    {
                        "action": "collect_macro_calendar",
                        "job_name": "collect_macro_calendar",
                        "spinner_text": "Collecting official macro and Treasury calendar dates...",
                        "params": {
                            "years": tuple(macro_years) if macro_years else None,
                            "include_bls": macro_include_bls,
                            "include_bea": macro_include_bea,
                            "include_census": macro_include_census,
                            "include_ism": macro_include_ism,
                            "include_treasury": macro_include_treasury,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational_low_frequency",
                            symbol_source="official macro and Treasury calendar sources",
                            symbol_count=None,
                            execution_context=(
                                "Overview Events 탭에서 사용할 BLS / BEA / Census / ISM / Treasury calendar를 공식 source에서 파싱해 DB에 저장합니다."
                            ),
                            input_params={
                                "years": tuple(macro_years) if macro_years else None,
                                "include_bls": macro_include_bls,
                                "include_bea": macro_include_bea,
                                "include_census": macro_include_census,
                                "include_ism": macro_include_ism,
                                "include_treasury": macro_include_treasury,
                            },
                        ),
                    }
                )
            st.divider()
            _render_job_brief("import_bls_macro_calendar_ics")
            bls_ics_file = st.file_uploader(
                "BLS Calendar .ics File",
                type=["ics"],
                key="overview_macro_bls_ics_file",
                help="BLS 공식 release schedule 캘린더 파일을 브라우저에서 내려받은 뒤 업로드합니다.",
            )
            if st.button(
                "BLS 공식 .ics 일정 가져오기",
                use_container_width=True,
                disabled=_has_running_job() or bls_ics_file is None,
            ):
                try:
                    bls_ics_text = bls_ics_file.getvalue().decode("utf-8-sig", errors="replace")
                except Exception as exc:
                    st.error(f"BLS .ics file could not be read: {exc}")
                else:
                    _schedule_job(
                        {
                            "action": "import_bls_macro_calendar_ics",
                            "job_name": "import_bls_macro_calendar_ics",
                            "spinner_text": "Importing BLS CPI / PPI / Jobs release dates from the uploaded .ics file...",
                            "params": {
                                "ics_text": bls_ics_text,
                                "years": tuple(macro_years) if macro_years else None,
                                "source_name": bls_ics_file.name,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="overview_macro_calendar_collection",
                                execution_mode="manual_official_file_import",
                                symbol_source="BLS official release schedule ICS file",
                                symbol_count=None,
                                execution_context=(
                                    "BLS backend request 차단 시 사용자가 내려받은 공식 .ics 파일에서 CPI, PPI, Employment Situation 일정을 파싱해 DB에 저장합니다."
                                ),
                                input_params={
                                    "years": tuple(macro_years) if macro_years else None,
                                    "source_name": bls_ics_file.name,
                                },
                            ),
                        }
                    )
        with market_structure_tab:
            _render_job_brief("collect_market_structure_calendar")
            current_year = date.today().year
            structure_year_options = list(range(current_year - 1, current_year + 3))
            structure_years = st.multiselect(
                "Market Structure Calendar Years",
                options=structure_year_options,
                default=[current_year, current_year + 1],
                key="overview_market_structure_calendar_years",
                help="Nasdaq Trader holiday calendar, Cboe standard options expiration calendar, FTSE Russell reconstitution schedule을 수집합니다.",
            )
            structure_source_cols = st.columns(3, gap="small")
            structure_include_holidays = structure_source_cols[0].checkbox(
                "Holidays / early closes",
                value=True,
                key="overview_market_structure_include_holidays",
            )
            structure_include_options = structure_source_cols[1].checkbox(
                "Options expiration",
                value=True,
                key="overview_market_structure_include_options",
            )
            structure_include_russell = structure_source_cols[2].checkbox(
                "Russell reconstitution",
                value=True,
                key="overview_market_structure_include_russell",
            )
            st.caption(
                "이 일정은 거래 신호가 아니라 휴장, 조기폐장, 만기, 지수 재구성처럼 일정 밀도와 자료 상태를 설명하는 시장 배경입니다."
            )
            if st.button(
                "시장 구조 일정 수집",
                use_container_width=True,
                disabled=_has_running_job()
                or not (
                    structure_include_holidays
                    or structure_include_options
                    or structure_include_russell
                ),
            ):
                _schedule_job(
                    {
                        "action": "collect_market_structure_calendar",
                        "job_name": "collect_market_structure_calendar",
                        "spinner_text": "Collecting market-structure calendar dates from official sources...",
                        "params": {
                            "years": tuple(structure_years) if structure_years else None,
                            "include_holidays": structure_include_holidays,
                            "include_options_expiration": structure_include_options,
                            "include_russell": structure_include_russell,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational_low_frequency",
                            symbol_source="official market-structure calendar sources",
                            symbol_count=None,
                            execution_context=(
                                "Overview Events 탭에서 일정 밀도 근거로 사용할 휴장, 조기폐장, options expiration, Russell reconstitution calendar를 저장합니다."
                            ),
                            input_params={
                                "years": tuple(structure_years) if structure_years else None,
                                "include_holidays": structure_include_holidays,
                                "include_options_expiration": structure_include_options,
                                "include_russell": structure_include_russell,
                            },
                        ),
                    }
                )
        with earnings_tab:
            _render_job_brief("collect_earnings_calendar")
            earnings_source_mode = st.selectbox(
                "Symbol Source",
                [
                    "Latest S&P 500 Movers",
                    "S&P 500 Universe Batch",
                    "Large-cap Top1000 Batch",
                    "Large-cap Top2000 Batch",
                    "Manual Symbols",
                ],
                index=0,
                key="overview_earnings_symbol_source",
            )
            earnings_cols = st.columns(4, gap="small")
            earnings_top_movers_limit = int(
                earnings_cols[0].number_input(
                    "Top Movers",
                    min_value=5,
                    max_value=100,
                    value=20,
                    step=5,
                    key="overview_earnings_top_movers_limit",
                    disabled=earnings_source_mode != "Latest S&P 500 Movers",
                )
            )
            earnings_lookahead_days = int(
                earnings_cols[1].number_input(
                    "Lookahead Days",
                    min_value=7,
                    max_value=365,
                    value=120 if earnings_source_mode == "Latest S&P 500 Movers" else 30,
                    step=7,
                    key="overview_earnings_lookahead_days",
                )
            )
            earnings_max_symbols = int(
                earnings_cols[2].number_input(
                    "Max Symbols",
                    min_value=5,
                    max_value=200,
                    value=50 if earnings_source_mode == "Latest S&P 500 Movers" else 100,
                    step=5,
                    key="overview_earnings_max_symbols",
                )
            )
            earnings_batch_offset = int(
                earnings_cols[3].number_input(
                    "Batch Offset",
                    min_value=0,
                    max_value=2000,
                    value=0,
                    step=50,
                    key="overview_earnings_batch_offset",
                    disabled=earnings_source_mode in {"Latest S&P 500 Movers", "Manual Symbols"},
                )
            )
            earnings_validation_cols = st.columns(2, gap="small")
            earnings_validate_with_nasdaq = earnings_validation_cols[0].checkbox(
                "Nasdaq cross-check",
                value=True,
                key="overview_earnings_validate_with_nasdaq",
                help="Cross-check yfinance earnings dates against Nasdaq's free earnings calendar endpoint when possible.",
            )
            earnings_request_sleep_sec = float(
                earnings_validation_cols[1].number_input(
                    "Ticker Cooldown Sec",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.1 if earnings_source_mode != "Latest S&P 500 Movers" else 0.0,
                    step=0.1,
                    key="overview_earnings_request_sleep_sec",
                )
            )
            manual_earnings_text = ""
            if earnings_source_mode == "Manual Symbols":
                manual_earnings_text = st.text_area(
                    "Symbols",
                    value="AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA",
                    key="overview_earnings_manual_symbols",
                )
            st.caption(
                "Latest movers uses the latest stored S&P 500 intraday snapshot. S&P 500 and large-cap batch modes are low-frequency sweeps; keep Max Symbols bounded and use Batch Offset to continue later."
            )
            if st.button(
                "실적 발표 예상 일정 수집",
                use_container_width=True,
                disabled=_has_running_job(),
            ):
                manual_symbols = _parse_csv_items(manual_earnings_text)
                symbol_source = {
                    "Latest S&P 500 Movers": "latest_movers",
                    "S&P 500 Universe Batch": "sp500_universe",
                    "Large-cap Top1000 Batch": "top1000",
                    "Large-cap Top2000 Batch": "top2000",
                    "Manual Symbols": "manual",
                }[earnings_source_mode]
                earnings_universe_code = {
                    "top1000": "TOP1000",
                    "top2000": "TOP2000",
                }.get(symbol_source, "SP500")
                earnings_universe_limit = {
                    "top1000": 1000,
                    "top2000": 2000,
                }.get(symbol_source)
                _schedule_job(
                    {
                        "action": "collect_earnings_calendar",
                        "job_name": "collect_earnings_calendar",
                        "spinner_text": "Collecting earnings dates from yfinance calendar and optional Nasdaq cross-check...",
                        "params": {
                            "symbols": manual_symbols if symbol_source == "manual" else None,
                            "symbol_source": symbol_source,
                            "universe_code": earnings_universe_code,
                            "universe_limit": earnings_universe_limit,
                            "top_movers_limit": earnings_top_movers_limit,
                            "lookahead_days": earnings_lookahead_days,
                            "max_symbols": earnings_max_symbols,
                            "batch_offset": earnings_batch_offset,
                            "validate_with_nasdaq": earnings_validate_with_nasdaq,
                            "request_sleep_sec": earnings_request_sleep_sec,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational_low_frequency",
                            symbol_source=symbol_source,
                            symbol_count=len(manual_symbols) if symbol_source == "manual" else earnings_max_symbols,
                            execution_context=(
                                "Overview Events 탭에서 사용할 upcoming earnings calendar estimate를 무료 provider source로 수집하고 source validation metadata를 저장합니다."
                            ),
                            input_params={
                                "symbol_source": symbol_source,
                                "universe_code": earnings_universe_code,
                                "universe_limit": earnings_universe_limit,
                                "top_movers_limit": earnings_top_movers_limit,
                                "lookahead_days": earnings_lookahead_days,
                                "max_symbols": earnings_max_symbols,
                                "batch_offset": earnings_batch_offset,
                                "validate_with_nasdaq": earnings_validate_with_nasdaq,
                                "request_sleep_sec": earnings_request_sleep_sec,
                            },
                        ),
                    }
                )
        event_progress_labels = {
            "collect_fomc_calendar": "FOMC Calendar Collection",
            "collect_macro_calendar": "Macro Calendar Collection",
            "collect_market_structure_calendar": "Market Structure Calendar Collection",
            "import_bls_macro_calendar_ics": "BLS Calendar ICS Import",
            "collect_earnings_calendar": "Earnings Calendar Collection",
        }
        for event_action, event_label in event_progress_labels.items():
            if _is_running_action(event_action):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label=event_label,
                )
        _render_inline_last_completed_result(
            "collect_fomc_calendar",
            "collect_macro_calendar",
            "collect_market_structure_calendar",
            "import_bls_macro_calendar_ics",
            "collect_earnings_calendar",
        )

    with st.expander("Practical Validation 검증 데이터 보강", expanded=False):
        st.write("Practical Validation에서 포트폴리오를 검토할 때 사용할 provider snapshot 데이터를 수집합니다.")
        st.caption(
            "ETF의 운용 가능성, ETF 내부 구성, 시장 환경 데이터를 DB에 저장해 둡니다. "
            "이후 Practical Validation은 저장된 snapshot을 읽어서 비용 / 유동성, 자산배분, 집중도, 시장 국면 판단의 근거로 사용합니다."
        )
        st.caption(
            "전체 저장 대상: `finance_meta.etf_provider_source_map`, `finance_meta.etf_operability_snapshot`, "
            "`finance_meta.etf_holdings_snapshot`, `finance_meta.etf_exposure_snapshot`, "
            "`finance_meta.macro_series_observation`, `finance_meta.nyse_symbol_lifecycle`"
        )
        source_map_tab, provider_tab, holdings_tab, macro_tab, lifecycle_tab = st.tabs(
            [
                "ETF 소스 매핑",
                "ETF 운용성",
                "ETF 구성 / 노출",
                "FRED 시장환경",
                "상장 / 상폐 근거",
            ]
        )

        with source_map_tab:
            _render_job_brief("discover_etf_provider_source_map")
            st.caption(
                "`nyse_etf`와 ETF asset profile을 기준으로 운용사와 공식 endpoint 후보를 찾고 검증합니다. "
                "이 테이블이 채워져야 새 ETF도 holdings / exposure 수집 대상인지 자동으로 판단할 수 있습니다."
            )
            st.caption("저장 테이블: `finance_meta.etf_provider_source_map`")
            source_map_symbols_text = st.text_area(
                "ETF Symbols",
                value=P2_PROVIDER_SOURCE_MAP_SYMBOLS,
                key="p2_provider_source_map_symbols_input",
                help="비워두면 DB의 `nyse_etf` 전체를 대상으로 source map 후보를 만듭니다. 처음에는 현재 검증 ETF부터 실행하는 것을 권장합니다.",
            )
            source_map_symbols = _parse_csv_items(source_map_symbols_text)
            source_map_cols = st.columns(2)
            source_map_limit = int(
                source_map_cols[0].number_input(
                    "Universe Limit",
                    min_value=0,
                    max_value=5000,
                    value=0,
                    step=50,
                    key="p2_provider_source_map_limit",
                    help="0이면 제한 없이 실행합니다. 전체 NYSE ETF를 한 번에 탐색하기 전에 작은 값으로 smoke 확인할 수 있습니다.",
                )
            )
            source_map_verify = source_map_cols[1].checkbox(
                "Verify Official URLs",
                value=True,
                key="p2_provider_source_map_verify",
                help="공식 URL / 다운로드 endpoint가 실제 응답하는지 확인한 row만 verified로 저장합니다.",
            )
            if source_map_symbols:
                _render_check_result(check_symbol_input(source_map_symbols))
            else:
                st.info("심볼 입력을 비우면 `nyse_etf` 전체를 대상으로 source map을 탐색합니다.")
            if st.button(
                "ETF 공식 소스 매핑 발견 실행",
                use_container_width=True,
                disabled=_has_running_job(),
            ):
                _schedule_job(
                    {
                        "action": "discover_etf_provider_source_map",
                        "job_name": "discover_etf_provider_source_map",
                        "spinner_text": "Discovering ETF provider source map...",
                        "params": {
                            "symbols": source_map_symbols or None,
                            "limit": source_map_limit or None,
                            "verify": bool(source_map_verify),
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_provider_source_map",
                            execution_mode="operational",
                            symbol_source="nyse_etf / nyse_asset_profile",
                            symbol_count=len(source_map_symbols) if source_map_symbols else None,
                            execution_context=(
                                "Practical Validation에서 ETF holdings / exposure connector를 자동 판정할 수 있도록 "
                                "운용사 공식 URL과 parser mapping을 발견하고 검증합니다."
                            ),
                            input_params={
                                "symbols": source_map_symbols or None,
                                "limit": source_map_limit or None,
                                "verify": bool(source_map_verify),
                            },
                        ),
                    }
                )
            if _is_running_action("discover_etf_provider_source_map"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="Provider Source Map Discovery",
                )
            _render_inline_last_completed_result("discover_etf_provider_source_map")

        with provider_tab:
            _render_job_brief("collect_etf_operability_provider")
            st.caption(
                "ETF가 현재 실전 운용 대상으로 적절한지 확인하기 위한 비용, 규모, 유동성, 가격 괴리, 레버리지 / 인버스 정보를 수집합니다. "
                "Practical Validation에서는 거래 가능성, 비용 부담, 레버리지 / 인버스 상품 여부를 판단하는 근거로 사용합니다."
            )
            st.caption(
                "저장 테이블: `finance_meta.etf_operability_snapshot`"
            )
            operability_symbols_text = st.text_area(
                "ETF Symbols",
                value=P2_PROVIDER_OPERABILITY_SYMBOLS,
                key="p2_operability_symbols_input",
                help="초기 공식 provider 수집 지원 대상: AOR, IEF, TLT, SPY, BIL, GLD, QQQ.",
            )
            operability_symbols = _parse_csv_items(operability_symbols_text)
            operability_cols = st.columns(4)
            operability_provider = operability_cols[0].selectbox(
                "Provider",
                ["official", "auto", "db_bridge", "ishares", "ssga", "invesco"],
                index=0,
                key="p2_operability_provider",
            )
            operability_as_of = operability_cols[1].text_input(
                "As Of Date",
                value="",
                key="p2_operability_as_of",
                help="선택 사항입니다. YYYY-MM-DD 형식으로 입력합니다. 비워두면 provider 또는 DB의 최신 기준일을 사용합니다.",
            )
            operability_lookback = int(
                operability_cols[2].number_input(
                    "Bridge Lookback Days",
                    min_value=5,
                    max_value=252,
                    value=60,
                    step=5,
                    key="p2_operability_lookback",
                )
            )
            operability_timeframe = operability_cols[3].selectbox(
                "Bridge Timeframe",
                ["1d", "1wk", "1mo"],
                index=0,
                key="p2_operability_timeframe",
            )
            operability_check = check_symbol_input(operability_symbols)
            _render_check_result(operability_check)
            if st.button(
                "ETF 운용성 스냅샷 수집",
                use_container_width=True,
                disabled=_has_running_job() or _is_blocking(operability_check),
            ):
                _schedule_job(
                    {
                        "action": "collect_etf_operability_provider",
                        "job_name": "collect_etf_operability_provider",
                        "spinner_text": "Running ETF operability provider snapshot...",
                        "params": {
                            "symbols": operability_symbols,
                            "as_of_date": operability_as_of or None,
                            "provider": operability_provider,
                            "lookback_days": operability_lookback,
                            "timeframe": operability_timeframe,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_provider_operability",
                            execution_mode="operational",
                            symbol_source="Practical Validation provider source map",
                            symbol_count=len(operability_symbols),
                            execution_context=(
                                "Practical Validation에서 비용 / 유동성 / 거래 가능성을 판단할 때 사용할 ETF operability snapshot을 수집합니다."
                            ),
                            input_params={
                                "provider": operability_provider,
                                "as_of_date": operability_as_of or None,
                                "lookback_days": operability_lookback,
                                "timeframe": operability_timeframe,
                            },
                        ),
                    }
                )
            if _is_running_action("collect_etf_operability_provider"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="ETF Operability Snapshot",
                )
            _render_inline_last_completed_result("collect_etf_operability_provider")

        with holdings_tab:
            _render_job_brief("collect_etf_holdings_exposure")
            st.caption(
                "ETF 안에 무엇이 들어있는지와 자산군 / 섹터 / 국가 / 통화 노출이 어떻게 나뉘는지 수집합니다. "
                "Practical Validation에서는 포트폴리오 자산배분, 집중도, 중복 노출을 판단하는 근거로 사용합니다. "
                "`GLD`의 row-level holdings는 아직 수집 대기 상태라 기본 목록에는 넣지 않습니다."
            )
            st.caption(
                "저장 테이블: `finance_meta.etf_holdings_snapshot`, `finance_meta.etf_exposure_snapshot`"
            )
            holdings_symbols_text = st.text_area(
                "ETF Symbols",
                value=P2_PROVIDER_HOLDINGS_SYMBOLS,
                key="p2_holdings_symbols_input",
                help="초기 row-level holdings 수집 지원 대상: AOR, IEF, TLT, SPY, BIL, QQQ.",
            )
            holdings_symbols = _parse_csv_items(holdings_symbols_text)
            holdings_cols = st.columns(3)
            holdings_provider = holdings_cols[0].selectbox(
                "Provider",
                ["official", "ishares", "ssga", "invesco"],
                index=0,
                key="p2_holdings_provider",
            )
            holdings_as_of = holdings_cols[1].text_input(
                "As Of Date",
                value="",
                key="p2_holdings_as_of",
                help="선택 사항입니다. YYYY-MM-DD 형식으로 입력합니다. 비워두면 provider 최신 holdings와 최신 저장 holdings를 사용해 exposure를 집계합니다.",
            )
            holdings_include_aggregates = holdings_cols[2].checkbox(
                "Provider Aggregate Sectors",
                value=True,
                key="p2_holdings_include_aggregates",
                help="provider가 공식 sector aggregate를 제공하면 함께 저장합니다. 현재는 SPY / QQQ에서 사용합니다.",
            )
            holdings_check = check_symbol_input(holdings_symbols)
            _render_check_result(holdings_check)
            if st.button(
                "ETF 구성 / 노출 스냅샷 수집",
                use_container_width=True,
                disabled=_has_running_job() or _is_blocking(holdings_check),
            ):
                _schedule_job(
                    {
                        "action": "collect_etf_holdings_exposure",
                        "job_name": "collect_etf_holdings_exposure",
                        "spinner_text": "Running ETF holdings and exposure snapshots...",
                        "params": {
                            "symbols": holdings_symbols,
                            "as_of_date": holdings_as_of or None,
                            "provider": holdings_provider,
                            "include_provider_aggregates": bool(holdings_include_aggregates),
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_provider_holdings_exposure",
                            execution_mode="operational",
                            symbol_source="Practical Validation provider source map",
                            symbol_count=len(holdings_symbols),
                            execution_context=(
                                "Practical Validation에서 자산배분 / 집중도 / 중복 노출을 판단할 때 사용할 ETF holdings와 exposure snapshot을 수집합니다."
                            ),
                            input_params={
                                "provider": holdings_provider,
                                "as_of_date": holdings_as_of or None,
                                "include_provider_aggregates": bool(holdings_include_aggregates),
                            },
                        ),
                    }
                )
            if _is_running_action("collect_etf_holdings_exposure"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="ETF Holdings / Exposure Snapshot",
                )
            _render_inline_last_completed_result("collect_etf_holdings_exposure")

        with macro_tab:
            _render_job_brief("collect_macro_market_context")
            st.caption(
                "VIX, 금리곡선, 신용스프레드 같은 시장 환경 데이터를 수집합니다. "
                "Practical Validation에서는 현재 시장 국면과 risk-on / risk-off 환경을 해석하는 근거로 사용합니다."
            )
            st.caption(
                "저장 테이블: `finance_meta.macro_series_observation`"
            )
            macro_series_text = st.text_area(
                "Macro Series IDs",
                value=P2_PROVIDER_MACRO_SERIES,
                key="p2_macro_series_input",
                help="기본 수집 series: VIXCLS, T10Y3M, BAA10Y.",
            )
            macro_series = _parse_csv_items(macro_series_text)
            macro_cols = st.columns(3)
            macro_start = macro_cols[0].text_input("Start", value="2016-01-01", key="p2_macro_start")
            macro_end = macro_cols[1].text_input("End", value=date.today().isoformat(), key="p2_macro_end")
            macro_source_mode = macro_cols[2].selectbox(
                "Source Mode",
                ["auto", "csv", "api"],
                index=0,
                key="p2_macro_source_mode",
                help="`auto`는 `FRED_API_KEY`가 있으면 FRED API를 사용하고, 없으면 FRED 공식 CSV download를 사용합니다.",
            )
            macro_check = check_symbol_input(macro_series)
            _render_check_result(macro_check)
            if st.button(
                "FRED 시장환경 수집",
                use_container_width=True,
                disabled=_has_running_job() or _is_blocking(macro_check),
            ):
                _schedule_job(
                    {
                        "action": "collect_macro_market_context",
                        "job_name": "collect_macro_market_context",
                        "spinner_text": "Running macro market-context snapshot...",
                        "params": {
                            "series_ids": macro_series,
                            "start": macro_start or None,
                            "end": macro_end or None,
                            "source_mode": macro_source_mode,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_macro_market_context",
                            execution_mode="operational",
                            symbol_source="FRED market-context source map",
                            symbol_count=len(macro_series),
                            execution_context=(
                                "Practical Validation에서 시장 국면과 risk-on / risk-off 환경을 해석할 때 사용할 FRED market-context observations를 수집합니다."
                            ),
                            input_params={
                                "series_ids": macro_series,
                                "start": macro_start or None,
                                "end": macro_end or None,
                                "source_mode": macro_source_mode,
                            },
                        ),
                    }
                )
            if _is_running_action("collect_macro_market_context"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="Macro Context Snapshot",
                )
            _render_inline_last_completed_result("collect_macro_market_context")

        with lifecycle_tab:
            _render_data_quality_callout(
                "상장 / 상폐 근거 해석 기준",
                "상장 / 상폐 근거는 Data Coverage Audit의 survivorship 해석을 보강합니다. "
                "current snapshot 계열은 historical membership PASS 근거가 아니며, 실제 historical source나 delisting source와 구분해서 봅니다.",
                tone="warning",
            )
            form25_tab, symdir_tab, sec_cik_tab, computed_tab = st.tabs(
                ["SEC Form 25", "Nasdaq 현재 상장", "SEC CIK 교차확인", "반복 관찰 요약"]
            )

            with form25_tab:
                _render_job_brief("collect_sec_form25_delistings")
                st.caption(
                    "SEC Form 25 / 25-NSE filing metadata를 읽어 delisting / withdrawal evidence를 저장합니다. "
                    "Data Coverage Audit의 survivorship / delisting control 근거를 보강하는 용도입니다."
                )
                st.caption(
                    "저장 테이블: `finance_meta.nyse_symbol_lifecycle` "
                    "(`source_type=delisting_feed`, `coverage_status=actual`)"
                )
                st.caption(
                    "Form 25가 없다는 사실은 active listing proof가 아닙니다. "
                    "complete historical universe membership은 별도 historical listing source가 필요합니다."
                )
                sec_form25_symbols_text = st.text_area(
                    "Symbols",
                    value=SEC_FORM25_DEFAULT_SYMBOLS,
                    key="sec_form25_symbols_input",
                    help="SEC ticker / CIK mapping으로 조회할 심볼을 입력합니다. 예: 과거 delisting이 의심되는 후보 ticker 목록.",
                )
                sec_form25_symbols = _parse_csv_items(sec_form25_symbols_text)
                sec_form25_user_agent = st.text_input(
                    "SEC User-Agent Override",
                    value="",
                    key="sec_form25_user_agent",
                    help="선택 사항입니다. 비워두면 `SEC_USER_AGENT` 환경변수 또는 collector 기본값을 사용합니다.",
                )
                sec_form25_cols = st.columns(2)
                sec_form25_include_archive = sec_form25_cols[0].checkbox(
                    "Search Archived Filing Files",
                    value=True,
                    key="sec_form25_include_archive",
                    help="recent filing 목록 밖의 archive JSON 파일도 일부 확인합니다.",
                )
                sec_form25_max_archive = int(
                    sec_form25_cols[1].number_input(
                        "Max Archive Files",
                        min_value=0,
                        max_value=20,
                        value=5,
                        step=1,
                        key="sec_form25_max_archive_files",
                    )
                )
                sec_form25_check = check_symbol_input(sec_form25_symbols)
                _render_check_result(sec_form25_check)
                if st.button(
                    "SEC Form 25 상폐 근거 수집",
                    width="stretch",
                    disabled=_has_running_job() or _is_blocking(sec_form25_check),
                ):
                    _schedule_job(
                        {
                            "action": "collect_sec_form25_delistings",
                            "job_name": "collect_sec_form25_delistings",
                            "spinner_text": "Running SEC Form 25 delisting evidence collection...",
                            "params": {
                                "symbols": sec_form25_symbols,
                                "user_agent": sec_form25_user_agent or None,
                                "include_archive_files": bool(sec_form25_include_archive),
                                "max_archive_files": sec_form25_max_archive,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_delisting_evidence",
                                execution_mode="operational",
                                symbol_source="SEC EDGAR company_tickers / submissions API",
                                symbol_count=len(sec_form25_symbols),
                                execution_context=(
                                    "Data Coverage Audit의 survivorship / delisting control을 보강하기 위해 "
                                    "SEC Form 25 / 25-NSE delisting evidence를 DB lifecycle table에 수집합니다."
                                ),
                                input_params={
                                    "include_archive_files": bool(sec_form25_include_archive),
                                    "max_archive_files": sec_form25_max_archive,
                                    "user_agent_override": bool(sec_form25_user_agent),
                                },
                            ),
                        }
                    )
                if _is_running_action("collect_sec_form25_delistings"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="SEC Form 25 Delisting Evidence",
                    )
                _render_inline_last_completed_result("collect_sec_form25_delistings")

            with symdir_tab:
                _render_job_brief("collect_symbol_directory_snapshots")
                st.caption(
                    "Nasdaq public Symbol Directory의 현재 listing 관찰치를 partial lifecycle evidence로 저장합니다. "
                    "이 row는 historical membership proof가 아니라 current observation입니다."
                )
                symdir_sources = st.multiselect(
                    "수집 파일",
                    options=["nasdaqlisted", "otherlisted"],
                    default=["nasdaqlisted", "otherlisted"],
                    key="symbol_directory_sources",
                    help="nasdaqlisted는 Nasdaq-listed, otherlisted는 NYSE/NYSE American 등 other-listed current file입니다.",
                )
                symdir_cols = st.columns(3)
                symdir_snapshot_date = symdir_cols[0].text_input(
                    "Snapshot Date",
                    value="",
                    key="symbol_directory_snapshot_date",
                    help="선택 사항입니다. 비워두면 source file creation date 또는 오늘 날짜를 사용합니다.",
                )
                symdir_include_test = symdir_cols[1].checkbox(
                    "Include Test Issues",
                    value=False,
                    key="symbol_directory_include_test_issues",
                )
                symdir_user_agent = symdir_cols[2].text_input(
                    "User-Agent Override",
                    value="",
                    key="symbol_directory_user_agent",
                )
                if st.button(
                    "Nasdaq 상장 관찰치 수집",
                    width="stretch",
                    disabled=_has_running_job() or not symdir_sources,
                ):
                    _schedule_job(
                        {
                            "action": "collect_symbol_directory_snapshots",
                            "job_name": "collect_symbol_directory_snapshots",
                            "spinner_text": "Collecting Nasdaq Symbol Directory current snapshots...",
                            "params": {
                                "sources": tuple(symdir_sources),
                                "user_agent": symdir_user_agent or None,
                                "include_test_issues": bool(symdir_include_test),
                                "snapshot_date": symdir_snapshot_date or None,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_lifecycle_current_snapshot",
                                execution_mode="operational",
                                symbol_source="Nasdaq public Symbol Directory",
                                symbol_count=None,
                                execution_context=(
                                    "Nasdaq public Symbol Directory current files를 partial listing_observed lifecycle evidence로 저장합니다."
                                ),
                                input_params={
                                    "sources": tuple(symdir_sources),
                                    "include_test_issues": bool(symdir_include_test),
                                    "snapshot_date": symdir_snapshot_date or None,
                                    "user_agent_override": bool(symdir_user_agent),
                                },
                            ),
                        }
                )
                if _is_running_action("collect_symbol_directory_snapshots"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="Symbol Directory Snapshot Collection",
                    )
                _render_inline_last_completed_result("collect_symbol_directory_snapshots")

            with sec_cik_tab:
                _render_job_brief("collect_sec_company_ticker_crosscheck")
                st.caption(
                    "SEC current CIK / ticker / exchange association을 identity cross-check로 저장합니다. "
                    "심볼 입력을 비우면 SEC file 전체를 대상으로 합니다."
                )
                sec_cik_symbols_text = st.text_area(
                    "Symbols",
                    value="",
                    key="sec_cik_crosscheck_symbols_input",
                    help="선택 사항입니다. 특정 심볼만 확인하려면 쉼표로 입력합니다.",
                )
                sec_cik_symbols = _parse_csv_items(sec_cik_symbols_text)
                if sec_cik_symbols:
                    sec_cik_check = check_symbol_input(sec_cik_symbols)
                    _render_check_result(sec_cik_check)
                else:
                    sec_cik_check = {"status": "ok", "message": "전체 SEC current association file을 대상으로 실행합니다."}
                    st.info(sec_cik_check["message"])
                sec_cik_cols = st.columns(2)
                sec_cik_snapshot_date = sec_cik_cols[0].text_input(
                    "Snapshot Date",
                    value="",
                    key="sec_cik_snapshot_date",
                )
                sec_cik_user_agent = sec_cik_cols[1].text_input(
                    "SEC User-Agent Override",
                    value="",
                    key="sec_cik_user_agent",
                )
                if st.button(
                    "SEC CIK / 티커 교차확인 수집",
                    width="stretch",
                    disabled=_has_running_job() or _is_blocking(sec_cik_check),
                ):
                    _schedule_job(
                        {
                            "action": "collect_sec_company_ticker_crosscheck",
                            "job_name": "collect_sec_company_ticker_crosscheck",
                            "spinner_text": "Collecting SEC CIK / ticker / exchange crosscheck evidence...",
                            "params": {
                                "symbols": sec_cik_symbols or None,
                                "user_agent": sec_cik_user_agent or None,
                                "snapshot_date": sec_cik_snapshot_date or None,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_lifecycle_identity_crosscheck",
                                execution_mode="operational",
                                symbol_source="SEC company_tickers_exchange.json",
                                symbol_count=len(sec_cik_symbols) if sec_cik_symbols else None,
                                execution_context=(
                                    "SEC current CIK / ticker / exchange association을 partial identity lifecycle evidence로 저장합니다."
                                ),
                                input_params={
                                    "symbols": sec_cik_symbols or None,
                                    "snapshot_date": sec_cik_snapshot_date or None,
                                    "user_agent_override": bool(sec_cik_user_agent),
                                },
                            ),
                        }
                )
                if _is_running_action("collect_sec_company_ticker_crosscheck"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="SEC CIK / Ticker Crosscheck",
                    )
                _render_inline_last_completed_result("collect_sec_company_ticker_crosscheck")

            with computed_tab:
                _render_job_brief("collect_computed_snapshot_lifecycle")
                st.caption(
                    "이미 저장된 current listing snapshot rows를 읽어 반복 관찰 window를 partial lifecycle evidence로 요약합니다. "
                    "상폐나 historical membership을 증명하지 않습니다."
                )
                computed_symbols_text = st.text_area(
                    "Symbols",
                    value="",
                    key="computed_lifecycle_symbols_input",
                    help="선택 사항입니다. 비워두면 기존 current snapshot rows 전체를 요약합니다.",
                )
                computed_symbols = _parse_csv_items(computed_symbols_text)
                if computed_symbols:
                    computed_check = check_symbol_input(computed_symbols)
                    _render_check_result(computed_check)
                else:
                    computed_check = {"status": "ok", "message": "전체 current snapshot rows를 대상으로 실행합니다."}
                    st.info(computed_check["message"])
                computed_min_observations = int(
                    st.number_input(
                        "Minimum Observation Dates",
                        min_value=2,
                        max_value=10,
                        value=2,
                        step=1,
                        key="computed_lifecycle_min_observation_dates",
                        help="서로 다른 관찰일이 이 값 이상인 symbol만 partial summary row를 만듭니다.",
                    )
                )
                if st.button(
                    "반복 관찰 lifecycle 요약 생성",
                    width="stretch",
                    disabled=_has_running_job() or _is_blocking(computed_check),
                ):
                    _schedule_job(
                        {
                            "action": "collect_computed_snapshot_lifecycle",
                            "job_name": "collect_computed_snapshot_lifecycle",
                            "spinner_text": "Computing conservative lifecycle evidence from current snapshots...",
                            "params": {
                                "symbols": computed_symbols or None,
                                "min_observation_dates": computed_min_observations,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_lifecycle_computed_snapshot",
                                execution_mode="operational",
                                symbol_source="finance_meta.nyse_symbol_lifecycle current snapshots",
                                symbol_count=len(computed_symbols) if computed_symbols else None,
                                execution_context=(
                                    "기존 current snapshot rows의 반복 관찰 window를 partial computed lifecycle evidence로 요약합니다."
                                ),
                                input_params={
                                    "symbols": computed_symbols or None,
                                    "min_observation_dates": computed_min_observations,
                                },
                            ),
                        }
                )
                if _is_running_action("collect_computed_snapshot_lifecycle"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="Computed Snapshot Lifecycle",
                    )
                _render_inline_last_completed_result("collect_computed_snapshot_lifecycle")
    return current_progress_callback


def render_manual_section() -> Any:
    _bind_page_globals()
    current_progress_callback = None
    st.info(
        "수동 복구 / 진단: 특정 심볼 재수집, 저수준 파이프라인 확인, PIT inspection 같은 보조 작업입니다. "
        "정기 운영보다 느리거나 실험적인 작업은 이곳에서 필요한 범위만 좁혀 실행합니다."
    )
    with st.expander("가격 이력 수동 수집", expanded=False):
        _render_job_brief("collect_ohlcv")
        st.caption(
            "`Symbols` 입력을 사용합니다. Factors 계산 전에 가격 row를 좁은 범위로 보강할 때 적합합니다. "
            "date-range가 애매하면 `period` 기반 실행이 더 단순합니다."
        )
        st.caption("저장 테이블: `finance_price.nyse_price_history`")
        ohlcv_symbol_result = _render_symbol_source_inputs("ohlcv", "OHLCV Symbols")
        ohlcv_symbols_input = ohlcv_symbol_result["symbols"]
        ohlcv_col1, ohlcv_col2 = st.columns(2)
        ohlcv_period_input = ohlcv_col1.selectbox("OHLCV Period", PERIOD_PRESETS, index=3, key="ohlcv_period_input")
        ohlcv_interval_input = ohlcv_col2.selectbox("OHLCV Interval", ["1d", "1wk", "1mo"], index=0, key="ohlcv_interval_input")
        ohlcv_col3, ohlcv_col4 = st.columns(2)
        ohlcv_start_input = ohlcv_col3.text_input("OHLCV Start", value="", key="ohlcv_start_input")
        ohlcv_end_input = ohlcv_col4.text_input("OHLCV End", value="", key="ohlcv_end_input")
        ohlcv_resolved_period, ohlcv_resolved_start, ohlcv_resolved_end = _normalize_ohlcv_window(
            ohlcv_period_input,
            ohlcv_start_input,
            ohlcv_end_input,
        )
        if ohlcv_period_input == "7d" and not ohlcv_start_input and not ohlcv_end_input:
            st.caption(
                f"`7d`는 rolling date window로 변환됩니다: start=`{ohlcv_resolved_start}`, end=`{ohlcv_resolved_end}`."
            )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", _format_symbol_source_label(ohlcv_symbol_result.get("source_mode") or "Manual")),
                ("대상 수", f"{len(ohlcv_symbols_input):,} symbols"),
                (
                    "기간",
                    _format_contract_window(
                        period=ohlcv_resolved_period,
                        start=ohlcv_resolved_start,
                        end=ohlcv_resolved_end,
                    ),
                ),
                ("Interval", ohlcv_interval_input),
            ],
            note="수동 OHLCV 수집은 요청 범위 보강용입니다. 실행 후 missing / no-data / rate-limit payload를 확인하세요.",
        )
        _render_price_window_preflight(
            symbols=ohlcv_symbols_input,
            start=ohlcv_resolved_start,
            end=ohlcv_resolved_end,
            timeframe=ohlcv_interval_input,
        )
        ohlcv_symbol_check = check_symbol_input(ohlcv_symbols_input)
        _render_check_result(ohlcv_symbol_check)
        ohlcv_run_allowed = _render_large_run_guard(
            prefix="ohlcv",
            job_name="collect_ohlcv",
            symbols=ohlcv_symbols_input,
        )
        ohlcv_collection_params = _build_ohlcv_collection_params(
            symbols=ohlcv_symbols_input,
            start=ohlcv_resolved_start,
            end=ohlcv_resolved_end,
            period=ohlcv_resolved_period,
            interval=ohlcv_interval_input,
        )
        if st.button(
            "가격 이력 수동 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(ohlcv_symbol_check) or not ohlcv_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "collect_ohlcv",
                    "job_name": "collect_ohlcv",
                    "spinner_text": "Running OHLCV collection...",
                    "params": ohlcv_collection_params,
                    "run_metadata": _job_metadata(
                        pipeline_type="manual_ohlcv_collection",
                        execution_mode="manual",
                        symbol_source=ohlcv_symbol_result.get("source_mode"),
                        symbol_count=len(ohlcv_symbols_input),
                        execution_context="Manual OHLCV ingestion for the selected symbols or universe source.",
                        input_params={
                            "start": ohlcv_resolved_start,
                            "end": ohlcv_resolved_end,
                            "period": ohlcv_resolved_period,
                            "interval": ohlcv_interval_input,
                        },
                    ),
                }
            )
        if _is_running_action("collect_ohlcv"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="OHLCV Collection",
            )
        _render_inline_last_completed_result("collect_ohlcv")

    with st.expander("자산 프로필 수동 수집", expanded=False):
        _render_job_brief("collect_asset_profiles")
        st.caption(
            "`Symbols` 입력은 사용하지 않습니다. 선택한 `Asset Profile Kinds`와 MySQL의 "
            "`nyse_stock` / `nyse_etf` universe table을 기준으로 실행합니다."
        )
        st.caption("저장 테이블: `finance_meta.nyse_asset_profile`")
        profile_kind_options = st.multiselect(
            "Asset Profile Kinds",
            options=["stock", "etf"],
            default=["stock", "etf"],
            key="profile_kind_options",
        )
        kinds = tuple(profile_kind_options) if profile_kind_options else ()
        asset_profile_check = check_asset_profile_prerequisites(kinds)
        _render_check_result(asset_profile_check)
        if st.button(
            "자산 프로필 수동 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(asset_profile_check),
        ):
            _schedule_job(
                _build_asset_profile_job(
                    action="collect_asset_profiles",
                    job_name="collect_asset_profiles",
                    spinner_text="Running asset profile collection...",
                    kinds=kinds,
                    pipeline_type="manual_asset_profile_collection",
                    execution_mode="manual",
                    execution_context="Manual asset profile refresh for selected stock / ETF universe kinds.",
                )
            )
        if _is_running_action("collect_asset_profiles"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Asset Profile Collection",
            )
        _render_inline_last_completed_result("collect_asset_profiles")

    with st.expander("상세 재무제표 수동 수집", expanded=False):
        _render_job_brief("collect_financial_statements")
        st.caption(
            "`Symbols` 입력을 사용합니다. normalized fundamentals보다 느리고, issuer별 실패가 있으면 partial success가 될 수 있습니다."
        )
        st.caption(
            "이 card는 낮은 수준의 수동 수집입니다. 일상적인 statement history 복구와 quarterly coverage 보강은 "
            "위의 `Extended Statement Refresh`를 우선 사용하세요."
        )
        st.caption(
            "strict annual 운영 run에는 symbol preset dropdown의 "
            "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, `US Statement Coverage 1000`도 사용할 수 있습니다."
        )
        st.caption("저장 테이블: `finance_fundamental.nyse_financial_statement_filings`, `finance_fundamental.nyse_financial_statement_labels`, `finance_fundamental.nyse_financial_statement_values`")
        fs_symbol_result = _render_symbol_source_inputs("fs", "Financial Statement Symbols")
        fs_symbols_input = fs_symbol_result["symbols"]
        fs_col1, fs_col2 = st.columns(2)
        fs_mode_input = fs_col1.selectbox(
            "Statement Mode",
            ["annual", "quarterly"],
            index=0,
            key="fs_mode_input",
            help="일반 운영에서는 annual/quarterly 중 하나를 고르면 내부적으로 freq와 EDGAR period request를 같은 값으로 맞춰 실행합니다.",
        )
        fs_periods_input = fs_col2.number_input(
            "Financial Statement Periods",
            min_value=0,
            max_value=80,
            value=0,
            step=1,
            key="fs_periods_input",
            help="`0`이면 각 symbol에 대해 EDGAR에서 가능한 모든 statement period를 수집합니다.",
        )
        st.caption("Tip: `0 = all available periods`. quarterly strict coverage를 다시 채울 때 권장합니다.")
        st.caption(
            "`Statement Mode`는 operator용 단일 입력입니다. "
            "내부적으로는 `freq`와 `period`를 같은 값으로 맞춰 실행합니다."
        )
        fs_symbol_check = check_symbol_input(fs_symbols_input)
        _render_check_result(fs_symbol_check)
        fs_run_allowed = _render_large_run_guard(
            prefix="financial_statements",
            job_name="collect_financial_statements",
            symbols=fs_symbols_input,
        )
        if st.button(
            "상세 재무제표 수동 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(fs_symbol_check) or not fs_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "collect_financial_statements",
                    "job_name": "collect_financial_statements",
                    "spinner_text": "Running financial statement ingestion...",
                    "params": {
                        "symbols": fs_symbols_input,
                        "freq": fs_mode_input,
                        "periods": int(fs_periods_input),
                        "period": fs_mode_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="manual_financial_statement_ingestion",
                        execution_mode="manual",
                        symbol_source=fs_symbol_result.get("source_mode"),
                        symbol_count=len(fs_symbols_input),
                        execution_context="Manual detailed financial statement ingestion for the selected symbols or universe source.",
                        input_params={
                            "statement_mode": fs_mode_input,
                            "freq": fs_mode_input,
                            "periods": int(fs_periods_input),
                            "period": fs_mode_input,
                        },
                    ),
                }
            )
        if _is_running_action("collect_financial_statements"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Financial Statement Ingestion",
            )
        _render_inline_last_completed_result("collect_financial_statements")

    with st.expander("재무제표 shadow 재구성", expanded=False):
        _render_job_brief("rebuild_statement_shadow")
        st.caption(
            "`Statement Shadow Coverage Preview`가 `raw_statement_present_but_shadow_missing`라고 표시할 때 사용합니다. "
            "raw statement row가 이미 있으면 이 경로가 더 빠릅니다."
        )
        st.caption("저장 테이블: `finance_fundamental.nyse_fundamentals_statement`, `finance_fundamental.nyse_factors_statement`")
        shadow_symbol_result = _render_symbol_source_inputs(
            "shadow_rebuild",
            "Shadow Rebuild Symbols",
            default_source_mode="Manual",
        )
        shadow_symbols_input = shadow_symbol_result["symbols"]
        shadow_freq_input = st.selectbox(
            "Shadow Rebuild Frequency",
            ["annual", "quarterly"],
            index=1,
            key="shadow_rebuild_freq_input",
            help="이미 저장된 raw statement row를 사용해 선택한 statement frequency의 shadow table을 재구성합니다.",
        )
        shadow_symbol_check = check_symbol_input(shadow_symbols_input)
        _render_check_result(shadow_symbol_check)
        shadow_run_allowed = _render_large_run_guard(
            prefix="shadow_rebuild",
            job_name="rebuild_statement_shadow",
            symbols=shadow_symbols_input,
        )
        if st.button(
            "재무제표 shadow 재구성 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(shadow_symbol_check) or not shadow_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "rebuild_statement_shadow",
                    "job_name": "rebuild_statement_shadow",
                    "spinner_text": "Running statement shadow rebuild...",
                    "params": {
                        "symbols": shadow_symbols_input,
                        "freq": shadow_freq_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="statement_shadow_rebuild",
                        execution_mode="manual",
                        symbol_source=shadow_symbol_result.get("source_mode"),
                        symbol_count=len(shadow_symbols_input),
                        execution_context="Manual rebuild of statement shadow tables using already stored raw statement ledgers.",
                        input_params={"freq": shadow_freq_input},
                    ),
                }
            )
        if _is_running_action("rebuild_statement_shadow"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Statement Shadow Rebuild Only",
            )
        _render_inline_last_completed_result("rebuild_statement_shadow")

    with st.expander("가격 stale 원인 진단", expanded=False):
        _render_price_stale_diagnosis_card()
    if _is_running_action("diagnose_price_stale"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Price Stale Diagnosis",
        )

    with st.expander("재무제표 universe coverage QA", expanded=False):
        _render_statement_universe_coverage_qa_card()
    if _is_running_action("diagnose_statement_universe_coverage"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Statement Universe Coverage QA",
        )

    with st.expander("재무제표 coverage 원인 진단", expanded=False):
        _render_statement_coverage_diagnosis_card()
    if _is_running_action("diagnose_statement_coverage"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Statement Coverage Diagnosis",
        )

    with st.expander("재무제표 PIT inspection", expanded=False):
        _render_statement_pit_inspection_card()
    if _is_running_action("inspect_statement_pit"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Statement PIT Inspection",
        )
    return current_progress_callback


def render_selected_section(selected_collection_section: str) -> Any:
    _bind_page_globals()
    if selected_collection_section == INGESTION_COLLECTION_OPERATIONAL:
        return _render_ingestion_operational_section()
    if selected_collection_section == INGESTION_COLLECTION_MANUAL:
        return _render_ingestion_manual_section()
    if selected_collection_section == INGESTION_COLLECTION_RECORDS:
        _render_ingestion_records_section()
    return None
