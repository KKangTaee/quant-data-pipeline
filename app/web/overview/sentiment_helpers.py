from __future__ import annotations

from typing import Any

from app.web.overview import legacy_dashboard as _legacy


def render_sentiment_header() -> None:
    _legacy.st.markdown("### 시장 심리 컨텍스트")


def render_sentiment_controls() -> None:
    control_cols = _legacy.st.columns([1.1, 1, 1], gap="small", vertical_alignment="bottom")
    if control_cols[0].button(
        "시장 심리 갱신",
        key="overview_market_sentiment_refresh",
        use_container_width=True,
        type="primary",
    ):
        with _legacy.st.spinner("Refreshing CNN Fear & Greed / AAII sentiment..."):
            _legacy._store_overview_job_result(
                "overview_market_sentiment_result",
                _legacy.run_overview_market_sentiment(),
            )
            _legacy.load_overview_market_sentiment_snapshot.clear()
        _legacy.st.rerun()
    if control_cols[1].button(
        "화면 새로고침",
        key="overview_market_sentiment_reload",
        use_container_width=True,
    ):
        _legacy.load_overview_market_sentiment_snapshot.clear()
        _legacy.st.rerun()
    control_cols[2].caption("CNN / AAII 저장 데이터 기준")


def render_sentiment_job_result() -> None:
    _legacy._render_market_job_result("overview_market_sentiment_result")


def load_sentiment_snapshot() -> dict[str, Any]:
    return _legacy.load_overview_market_sentiment_snapshot()


def render_sentiment_snapshot_overview(snapshot: dict[str, Any]) -> None:
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    _legacy._render_sentiment_analysis_panel(analysis)
    _legacy._render_sentiment_analysis_steps(analysis)
    _legacy.render_status_card_grid(_sentiment_status_cards(snapshot, coverage, analysis))
    for warning in snapshot.get("warnings") or []:
        _legacy.st.warning(str(warning))


def has_sentiment_rows(snapshot: dict[str, Any]) -> bool:
    rows = snapshot.get("rows")
    return isinstance(rows, _legacy.pd.DataFrame) and not rows.empty


def render_sentiment_empty_state() -> None:
    _legacy.st.info("Stored sentiment rows are not available yet. Run Market Sentiment refresh first.")


def render_sentiment_detail_sections(snapshot: dict[str, Any]) -> None:
    analysis = dict(snapshot.get("analysis") or {})
    rows = snapshot.get("rows")
    component_rows = snapshot.get("component_rows")
    history_rows = snapshot.get("history_rows")

    _legacy._render_sentiment_driver_groups(analysis)
    _legacy._render_sentiment_component_learning_cards(analysis)
    _legacy._render_sentiment_next_checks(analysis)

    trend_tab, components_tab, table_tab = _legacy.st.tabs(["추세 근거", "CNN 구성 상세", "원천 테이블"])
    with trend_tab:
        _legacy.st.altair_chart(
            _legacy._sentiment_trend_chart(
                history_rows if isinstance(history_rows, _legacy.pd.DataFrame) else _legacy.pd.DataFrame()
            ),
            width="stretch",
        )
    with components_tab:
        _legacy.st.altair_chart(
            _legacy._sentiment_component_chart(
                component_rows if isinstance(component_rows, _legacy.pd.DataFrame) else _legacy.pd.DataFrame()
            ),
            width="stretch",
        )
        if isinstance(component_rows, _legacy.pd.DataFrame) and not component_rows.empty:
            _legacy.st.dataframe(component_rows, width="stretch", hide_index=True)
    with table_tab:
        _legacy.st.dataframe(rows, width="stretch", hide_index=True)


def _sentiment_status_cards(
    snapshot: dict[str, Any],
    coverage: dict[str, Any],
    analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "title": "데이터 신뢰도",
            "value": dict(analysis.get("data_confidence") or {}).get("status") or snapshot.get("status") or "-",
            "detail": f"{coverage.get('missing_count') or 0} missing · {coverage.get('stale_count') or 0} stale",
            "tone": _legacy._sentiment_tone(
                dict(analysis.get("data_confidence") or {}).get("tone") or snapshot.get("status")
            ),
        },
        {
            "title": "CNN Fear & Greed",
            "value": "-" if coverage.get("cnn_score") is None else f"{float(coverage['cnn_score']):.1f}",
            "detail": str(coverage.get("cnn_rating") or "-"),
            "tone": "positive"
            if _legacy._safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) >= 55
            else "warning"
            if _legacy._safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) < 45
            else "neutral",
        },
        {
            "title": "AAII Bearish",
            "value": "-" if coverage.get("aaii_bearish") is None else f"{float(coverage['aaii_bearish']):.1f}%",
            "detail": "weekly bearish sentiment",
            "tone": "warning"
            if _legacy._safe_float(coverage.get("aaii_bearish")) is not None
            and float(coverage["aaii_bearish"]) >= 40
            else "neutral",
        },
        {
            "title": "Bull-Bear Spread",
            "value": "-"
            if coverage.get("aaii_bull_bear_spread") is None
            else f"{float(coverage['aaii_bull_bear_spread']):+.1f} pp",
            "detail": "AAII bullish minus bearish",
            "tone": "positive"
            if _legacy._safe_float(coverage.get("aaii_bull_bear_spread")) is not None
            and float(coverage["aaii_bull_bear_spread"]) > 0
            else "warning"
            if _legacy._safe_float(coverage.get("aaii_bull_bear_spread")) is not None
            else "neutral",
        },
    ]
