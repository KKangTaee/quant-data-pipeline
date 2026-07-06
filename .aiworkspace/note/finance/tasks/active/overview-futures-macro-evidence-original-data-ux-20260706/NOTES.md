# Futures Macro Evidence / Original Data UX Notes

## 2026-07-06

- Existing React workbench already owns command strip, brief, scores, 1W / 1M flow, validation state, and evidence drawer.
- Existing lower expander still uses `근거 해석 / 원본 데이터`, repeats current evidence framing when React is available, then shows historical validation summary, data management, and raw tables.
- User concern is not lack of a guide. The target is to make the information itself carry enough context: what the row/section is, what it says, and how it connects to current interpretation.
- Phase 2 wording decision: avoid treating occurrence count as a signal. Use `비슷한 과거 상태` for historical frequency and explicitly say whether 5D directional consistency is applicable.
- Phase 3 raw table decision: preserve every dataframe, but rename disclosures around calculation steps so the user can connect current score, score contributors, actual daily moves, and historical sample tables.
- Phase 4 React linkage decision: keep evidence item metadata compact. The drawer shows score label / symbol / z-score as a meta line, while the detailed dataframe remains the source for full raw values.
- Follow-up decision: the top daily date should not read like a stale KST calendar date. Label it as `CME/yfinance 일봉 세션 기준` wherever the React command / data-basis card exposes the latest futures daily date.
- Follow-up decision: score signs are directional macro-pressure scores, not universal good/bad ratings. React score chips now include compact polarity hints per score family, e.g. risk-on `+` means stronger risk appetite while rate pressure `+` means higher rate burden.
- Follow-up decision: add `1D` to the React flow tabs and make it the default period. `1D` uses raw recent 1-trading-day percentage moves, while the top score remains the latest 1D move standardized by recent volatility; showing both helps explain cases where the current score differs from 1W / 1M context.
- Historical validation follow-up decision: use `오늘과 비슷했던 과거 상태 확인` as the core user meaning. This is not exact 16-symbol pattern matching and not a forecast; it maps the current 16-futures daily score state to the same historical classification process, then reports whether similar historical states support directional reading or only conservative interpretation.
- Historical validation graph decision: do not render charts in this pass. Prepare lightweight payload metadata only. Similar-state frequency can be charted for mixed / directional states; forward-return distribution should only be charted when directional hit-rate is applicable and sample exists.
- Historical validation component split decision: keep one Streamlit custom component / iframe boundary for Futures Macro. Split `HistoricalValidationPanel.tsx` as an internal React subcomponent, and keep `MetricTile` local to that file until the same tile pattern is reused elsewhere.
- Historical validation layout decision: user intended an on-screen section split, not only file-level component extraction. Treat `과거 점검` as its own executable section card between recent flow and current evidence, with copy / status / CTA / result tiles grouped together.
