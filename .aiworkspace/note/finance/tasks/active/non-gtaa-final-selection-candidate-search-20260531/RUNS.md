# Runs

| Time | Command / Check | Outcome |
|---|---|---|
| 2026-05-31 | Task setup | Opened non-GTAA candidate search task. No registry writes performed. |
| 2026-05-31 | Non-GTAA Compare dry-run: Equal Weight, Risk Parity Trend, Dual Momentum, Global Relative Strength | Single-strategy candidates did not pass selected-route. Stronger EW variants passed replay but were blocked by critical Final Review review groups, especially Risk Contribution for single-component sources. |
| 2026-05-31 | Weighted mix dry-run: EW Dividend / EW Core / Risk Parity / Dual Momentum / GRS variants | Several mixes reached Practical Validation `READY_FOR_FINAL_REVIEW`, but selected-route blocked on Backtest Realism and Component Role / Weight. No V2 Final Decision write. |
| 2026-05-31 | Growth / sector / gold dry-run | Best mix: `EW GrowthSectorGold 50 + RiskParity 25 + GRS 25`, actual replay CAGR 13.01%, MDD -13.66%, Sharpe 1.21, Practical Validation score 9.1. Final Review selected-route still blocked by Backtest Realism and Component Role / Weight plus review-required groups. |
| 2026-05-31 | Historical lifecycle ETF mix dry-run: SPY / SOXX / IEF / TLT | Best growth mix examples produced high replay CAGR, e.g. `SOXX60 SPY25 IEF10 TLT5` at 28.66% CAGR / -38.40% MDD / 1.10 Sharpe and `SOXX40 SPY30 IEF15 TLT15` at 24.55% CAGR / -36.38% MDD / 1.06 Sharpe. Selected-route still blocked by realism, component rationale, and review-required risk/provider/validation groups. |
| 2026-05-31 | Legacy Final Review V1 registry scan | Found non-GTAA selected row `final_quality_current_candidate_cov100_top10_aor_ma250_paper_only_20260507_e08bac`: Quality Coverage 100 Top-10 AOR MA250 paper-only candidate, route `SELECT_FOR_PRACTICAL_PORTFOLIO`, selected true, 100% Quality, CAGR 14.38%, MDD -14.56%. |
| 2026-05-31 | `build_selected_dashboard_handoff_review([legacy_quality_row])` dry-run | Handoff route `HANDOFF_READY`; dashboard row count 1; monitorable count 1; live approval/order/auto rebalance all false. This proves the row shape can feed the dashboard, but the current dashboard loader still reads V2, which has 0 rows. |
| 2026-05-31 | `load_final_selected_portfolio_dashboard(limit=None)` | Current V2 dashboard source has final decision count 0, selected decision count 0, dashboard row count 0. |
