# Overview Market Context US Stock Turnaround Analysis V1 Risks

Last Updated: 2026-07-15

## Guarded Risks

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
    - one-symbol bounded queries와 cache를 적용했다. actual latency는 `1.7s~7.2s`였으므로 selected-company V1에는 유지하되 broad discovery로 확장할 때는 별도 materialization/lazy-loading 설계가 필요하다.
12. **Current S&P/PER UI can regress during React split.**
    - existing payload value equality, focused regression, AMD/AAPL actual, desktop/browser regressions을 completion gate로 통과했다.

## Open Risks

1. **Actual lifecycle CIK gap blocks raw repair.**
   - RIVN/LCID/PLTR/AMD/AAPL의 stored analysis는 계산됐지만 QA 시점 lifecycle identity에는 SEC CIK가 없었다.
   - collection plan은 `BLOCKED/CIK_MISSING`으로 두어 분석을 보존한다. 실제 보강 전에는 lifecycle CIK 연결을 먼저 검증해야 한다.
2. **Read-time calculation is not a screener architecture.**
   - AAPL cold read가 `7.231s`까지 걸렸다. all-stock discovery/ranking은 현재 loader를 반복 호출하지 말고 PIT universe와 materialization 비용을 별도로 설계해야 한다.
3. **Repository-wide unrelated contract drift remains.**
   - isolated full regression `1,073/1,077`이며 Practical Validation 2건, Market Movers 1건, Sentiment 1건이 기존 상태로 실패한다. 이번 task 소유 파일과 무관해 수정하지 않았다.
4. **External collection path was not exercised against providers.**
   - read-only actual QA와 identity preflight까지 검증했다. 명시 action은 CIK가 준비된 selected symbol에서만 별도 실행할 수 있다.

## Deferred Risks

- peer cohort survivorship/PIT correctness
- historical enterprise-value snapshot
- normalized working-capital/SBC cash conversion
- all-stock discovery performance and materialization
