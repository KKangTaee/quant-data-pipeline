# Overview Market Context US Stock Turnaround Analysis V1 Risks

Last Updated: 2026-07-15

## Open Risks

1. **Cumulative duration facts can create false quarters.**
   - H1/9M/FY subtraction, primary-period ownership, comparative non-overwrite를 real-like tests로 먼저 고정한다.
2. **Concept tags differ by issuer and over time.**
   - canonical family priority와 same-filing fallback만 허용하고 missing을 다른 concept/period로 합성하지 않는다.
3. **Gross profit is often absent as a direct fact.**
   - same-quarter revenue minus cost only when unit/filing/fiscal identity matches.
4. **Reported OCF can be lifted by working capital or SBC.**
   - two consecutive TTM OCF positives를 요구하고 normalized OCF를 불완전 facts로 합성하지 않는다.
5. **Market cap can be stale.**
   - 7-day freshness gate를 통과하지 못하면 numeric EV multiple을 숨긴다.
6. **Debt components can be double-counted.**
   - direct total debt priority와 mutually exclusive component family를 사용한다.
7. **Split changes can fake dilution or per-share jumps.**
   - PIT split-neutral shares and no-future-split regression을 추가한다.
8. **Sequential stage can imply false causality.**
   - milestone rail은 independent status이며 prior stages를 자동 pass하지 않는다.
9. **Sector-specific firms need different valuation methods.**
   - financial institutions/REIT/specialized sectors는 generic router numeric conclusion을 막는다.
10. **Turnaround screen can be mistaken for a screener or signal.**
    - selected-company V1, no ranking, no target price, no buy/sell language를 유지한다.
11. **Adding a second analysis can slow every selected-stock render.**
    - one-symbol bounded queries and cache를 측정하고 actual latency evidence가 필요할 때만 lazy loading을 검토한다.
12. **Current S&P/PER UI can regress during React split.**
    - existing payload and focused/browser regressions을 각 차수 completion gate로 둔다.

## Deferred Risks

- peer cohort survivorship/PIT correctness
- historical enterprise-value snapshot
- normalized working-capital/SBC cash conversion
- all-stock discovery performance and materialization
