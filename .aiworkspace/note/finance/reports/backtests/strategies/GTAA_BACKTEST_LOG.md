# GTAA Backtest Log

## 목적

이 문서는 `GTAA` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 `GTAA`를 어떤 universe / score horizon / top / interval / benchmark 조합으로 돌렸고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `GTAA` run만 append 한다
- 실험 목적과 핵심 입력값을 같이 남긴다
- 결과는 최소한 아래를 남긴다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`
- `SPY` 비교가 핵심이면 그 비교 결과도 같이 적는다

## 기록

### 2026-04-20 - expanded universe follow-up search

- 목표:
  - 기존 `SPY / QQQ / GLD / IEF` compact 후보가 ticker 수가 부족하다는 사용자 피드백을 반영해,
    `GTAA` 안에서 더 넓은 ETF universe를 다시 테스트한다.
  - ticker를 늘렸을 때도 `real_money_candidate`가 유지되는지, 아니면 watchlist-only로 내려가는지 확인한다.
- 전략:
  - `GTAA`
- 기간 / universe:
  - `2016-01-01 ~ latest DB`
  - effective result window: `2016-01-29 ~ 2026-04-17`
  - manual expanded ETF universe search
- 핵심 설정:
  - `Option = month_end`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
  - `Min ETF AUM = 1.0B`
  - `Max Bid-Ask Spread = 0.50%`
  - `Market Regime = off`
  - `Crash Guardrail = off`
  - `Defensive Tickers = TLT, IEF, LQD, BIL`
- 신규 확장 후보:
  - `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `Top Assets = 1`
  - `Signal Interval = 8`
  - `Score Horizons = 1M / 3M / 6M`
  - `Risk-Off Mode = cash_only` 또는 `defensive_bond_preference`
- 결과:
  - `CAGR = 21.4953%`
  - `MDD = -6.4936%`
  - `Sharpe = 3.6601`
  - `Benchmark CAGR = 13.5612%`
  - `Net CAGR Spread = +7.9341%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
  - `Rolling Review = normal`
  - `Out-Of-Sample Review = normal`
- Top-2 확장 대안:
  - `SPY, QQQ, GLD, IEF, LQD, TLT`, `Top = 2`, `Interval = 4`, `1M / 3M / 6M`
  - `CAGR = 16.7945%`
  - `MDD = -8.3917%`
  - `Sharpe = 3.0086`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = watchlist_only`
  - `Validation = watch`
- 해석:
  - `TLT`를 추가한 6개 clean ETF universe는 ticker 부족 문제를 보강하는 방향으로 타당하다.
  - 다만 `Top = 2`를 유지하면 아직 `real_money_candidate`가 아니라 `watchlist_only`다.
  - 실전 기본값은 기존 `SPY / QQQ / GLD / IEF`, `Top = 2` 후보를 유지하고,
    신규 6개 universe `Top = 1`은 공격형 paper probation 후보로 추가한다.
- cadence follow-up:
  - 사용자 지적처럼 `Interval = 6` 또는 `8`은 tactical allocation 기준으로 느린 리밸런싱이다.
  - 확장 6 ETF core sensitivity에서는 monthly / quarterly cadence가 `hold`였고,
    `Top = 1 / Interval = 4`와 `Top = 1 / Interval = 8`만 `real_money_candidate`였다.
  - 따라서 `Interval = 8` 후보는 숫자가 강해도 기본 대표 후보가 아니라 느린 저회전 공격형 paper 후보로만 본다.
- 관련 문서:
  - [GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md)

### 2026-04-18 - real-money candidate compact ETF search

- 목표:
  - 기존 preset에 국한하지 않고 GTAA ETF universe를 다시 탐색해 `Promotion = hold`가 아닌 실제 투자 가능 후보를 찾는다.
  - current runtime의 ETF operability / validation / deployment metadata를 유지한 채 `real_money_candidate`가 나오는지 확인한다.
- 전략:
  - `GTAA`
- 기간 / universe:
  - `2016-01-01 ~ latest DB`
  - effective result window: `2016-01-29 ~ 2026-03-31`
  - manual ETF universe search
- 핵심 설정:
  - `Option = month_end`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
  - `Min ETF AUM = 1.0B`
  - `Max Bid-Ask Spread = 0.50%`
  - `Market Regime = off`
- 추천 후보:
  - `SPY, QQQ, GLD, IEF`
  - `Top Assets = 2`
  - `Signal Interval = 4`
  - `Score Horizons = 1M / 3M`
  - `Risk-Off Mode = defensive_bond_preference`
- 결과:
  - `CAGR = 17.4612%`
  - `MDD = -8.3917%`
  - `Sharpe = 3.0717`
  - `Benchmark CAGR = 12.6486%`
  - `Net CAGR Spread = +4.8126%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
  - `Rolling Review = normal`
  - `Out-Of-Sample Review = normal`
- 대안:
  - 공격형: `SPY, QQQ, GLD, LQD`, `Top = 1`, `Interval = 4`, `1M / 3M / 6M`, `CAGR = 20.6161%`, `MDD = -10.6744%`, `real_money_candidate`
  - 낮은 MDD: `SPY, QQQ, GLD, IEF, LQD`, `Top = 2`, `Interval = 6`, `1M / 3M`, `CAGR = 15.9664%`, `MDD = -4.7476%`, `real_money_candidate`
- 해석:
  - 기존 Phase 13 reference는 `production_candidate / watchlist_only`였지만,
    이번 compact ETF 변형은 `Validation = normal`을 회복해 `real_money_candidate`까지 올라갔다.
  - broader universe는 raw CAGR이 높아도 ETF profile / AUM / spread coverage 때문에 `hold`가 반복되어 최종 추천에서 제외했다.
  - 현재 deployment는 여전히 `paper_only`이므로 바로 live allocation이 아니라 paper probation 후보로 본다.
- 관련 문서:
  - [GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md)

### 2026-04-10 - practical non-hold reference

- 목표:
  - `Promotion != hold`, `Deployment != blocked`, `SPY` 대비 `CAGR / MDD` 우위를 동시에 만족하는 GTAA practical reference 확보
- 전략:
  - `GTAA`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-02`
  - custom ETF set
- 핵심 설정:
  - `Option = month_end`
  - `Top Assets = 2`
  - `Signal Interval = 3`
  - `Score Horizons = 1M / 3M`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
  - `Min ETF AUM = 0.0`
  - `Max Bid-Ask Spread = 100.0`
  - `Market Regime = off`
- factor / ticker:
  - `SPY, QQQ, GLD, LQD`
- 결과:
  - `CAGR = 14.7671%`
  - `MDD = -11.5626%`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = watchlist_only`
- 해석:
  - `hold`는 벗어났고 `blocked`도 아니다
  - 동일 sampled benchmark surface 기준 `SPY`보다 `CAGR / MDD`가 모두 더 좋았다
  - 다만 아직 `real_money_candidate`는 아니므로 실전형 후보라기보다 practical reference에 가깝다
- 다음 액션:
  - ETF operability / coverage interpretation이 완화되면 더 공격형 universe를 다시 비교한다
- 관련 문서:
  - [GTAA.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/GTAA.md)
  - [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/runs/2026/strategy_search/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)

### 2026-04-30 - clean-6 AOR current candidate reset run

- 목표:
  - fresh registry reset 이후 7단계 `단일 후보 직행 평가 또는 Portfolio Proposal 초안 작성`까지 도달 가능한 GTAA 후보를 찾는다.
- 전략:
  - `GTAA Clean-6 AOR Top-1`
- 기간 / universe:
  - input: `2016-01-01 ~ 2026-04-01`
  - effective result window: `2016-01-29 ~ 2026-04-01`
  - universe: `SPY, QQQ, GLD, IEF, LQD, TLT`
- 핵심 설정:
  - `Option = month_end`
  - `Top Assets = 1`
  - `Signal Interval = 2`
  - `Score Horizons = 3M / 12M`
  - `Trend Filter = MA200`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = AOR`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
- 결과:
  - `CAGR = 15.3395%`
  - `MDD = -13.9675%`
  - `Sharpe = 1.6054`
  - `End Balance = 42,653.22`
  - `AOR CAGR = 5.4711%`
  - `AOR MDD = -20.3628%`
  - `AOR 대비 CAGR spread = +9.8684%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
- 비교 참고:
  - 같은 기간 `SPY` 기준으로도 full-period CAGR / MDD는 우위지만, rolling validation에서는 `worst_excess` 경고가 떠서 formal promotion benchmark로는 `hold`가 된다.
  - 같은 universe equal weight, interval 2는 `CAGR = 6.8786%`, `MDD = -23.0319%`, `Sharpe = 0.7597`였다.
- 저장:
  - `BACKTEST_RUN_HISTORY.jsonl`에 single strategy run 저장
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_52d5888e63ce`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `gtaa_current_candidate_clean6_aor_top1_i2_3m12m`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_gtaa_current_candidate_clean6_aor_top1_i2_3m12m`
- 해석:
  - 이 후보는 다중자산 GTAA 특성에 맞춰 `AOR`를 formal benchmark로 두면 Candidate Review, Pre-Live paper tracking, Portfolio Proposal 단일 후보 직행 평가까지 통과한다.
  - `SPY`는 reference benchmark로 계속 볼 수 있지만, formal gate로 쓰면 rolling 구간 부진 경고가 강해져 같은 후보가 hold로 내려간다.

### 2026-05-01 - clean-6 AOR top-2 interval-3 follow-up candidate

- 목표:
  - 추가 조건 `interval < 4`, `top = 2 / 3 / 4`, universe 6~15개 안에서 7단계까지 도달 가능한 GTAA 후보를 하나 더 찾는다.
- 전략:
  - `GTAA Clean-6 AOR Top-2`
- 기간 / universe:
  - input: `2016-01-01 ~ 2026-04-01`
  - effective result window: `2016-01-29 ~ 2026-04-01`
  - universe: `SPY, QQQ, GLD, IEF, LQD, TLT`
- 핵심 설정:
  - `Option = month_end`
  - `Top Assets = 2`
  - `Signal Interval = 3`
  - `Score Horizons = 1M / 3M / 6M`
  - `Trend Filter = MA200`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = AOR`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
- 결과:
  - `CAGR = 12.8073%`
  - `MDD = -11.5626%`
  - `Sharpe = 2.0147`
  - `End Balance = 34,032.54`
  - `AOR CAGR = 5.4711%`
  - `AOR MDD = -19.1037%`
  - `AOR 대비 CAGR spread = +7.3363%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
- 후보 선택 이유:
  - 같은 clean-6 universe의 `top=2 / interval=1 / 3M+6M+12M` 후보가 CAGR은 더 높았지만 MDD가 더 깊었다.
  - 이번 후보는 `interval=3`, `MDD=-11.5626%`, `Sharpe=2.0147`이라 추가 실습 후보로 더 안정적인 형태다.
- 저장:
  - `BACKTEST_RUN_HISTORY.jsonl`에 single strategy run 저장
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_a152594509dd`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`

### 2026-05-01 - clean-6 AOR high-CAGR top-2 candidate

- 목표:
  - 추가 조건을 유지하면서 `CAGR >= 15%`, `MDD 11~12%대 이하`인 GTAA 후보를 찾는다.
- 전략:
  - `GTAA Clean-6 AOR Top-2 High CAGR`
- 기간 / universe:
  - input: `2016-01-01 ~ 2026-04-01`
  - effective result window: `2016-01-29 ~ 2026-04-01`
  - universe: `SPY, QQQ, GLD, IEF, LQD, TLT`
- 핵심 설정:
  - `Option = month_end`
  - `Top Assets = 2`
  - `Signal Interval = 2`
  - `Score Horizons = 1M / 12M`
  - `Trend Filter = MA150`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = AOR`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
- 결과:
  - `CAGR = 15.2174%`
  - `MDD = -8.8783%`
  - `Sharpe = 1.9630`
  - `End Balance = 42,196.27`
  - `AOR CAGR = 5.4711%`
  - `AOR MDD = -20.3628%`
  - `AOR 대비 CAGR spread = +9.7464%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
- 후보 선택 이유:
  - 요청 조건 `top=2/3/4`, `interval<4`, universe 6~15개, `CAGR>=15%`, 낮은 MDD 목표를 모두 만족했다.
  - 이전 top-2 interval-3 후보보다 CAGR이 높고, MDD도 더 낮아 고CAGR 실습 후보로 적합하다.
- 저장:
  - `BACKTEST_RUN_HISTORY.jsonl`에 single strategy run 저장
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_d12013649150`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`

### 2026-05-05 - SPY benchmark 통과 후보 탐색

- 목표:
  - 기존 clean-6 후보처럼 `AOR`가 아니라 `SPY`를 formal benchmark로 두고 10단계 실습 후보가 될 수 있는 GTAA 후보를 찾는다.
  - 조건은 `top=2~4`, universe 6~12개, `interval<=3`이다.
- 탐색 요약:
  - 세 개의 병렬 탐색 track을 사용했다.
  - cross-asset / sector / style / defensive ETF universe를 나누어 확인했다.
  - `VGT`, `SMH`, `XLK`, `XLY`, `DIA`, `IWF` 일부 후보는 DB 가격 row가 짧아 장기 rolling validation 후보에서 제외했다.
- 가장 깔끔한 실습 후보:
  - 전략 이름: `GTAA SPY Benchmark Top-2 Style Momentum`
  - input: `2016-01-01 ~ 2026-05-01`
  - effective result window: `2016-01-29 ~ 2026-02-27`
  - universe: `QQQ, SOXX, MTUM, QUAL, USMV, IAU, IEF, TLT`
  - `Top Assets = 2`
  - `Signal Interval = 3`
  - `Score Horizons = 1M / 6M / 12M`
  - `Trend Filter = MA250`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
- 결과:
  - `CAGR = 18.9684%`
  - `MDD = -18.0974%`
  - `Sharpe = 2.0242`
  - `End Balance = 57,540.36`
  - `SPY CAGR = 13.3638%`
  - `SPY MDD = -15.9042%`
  - `SPY 대비 CAGR spread = +5.6046%p`
  - `Rolling underperformance share = 20.00%`
  - `Worst rolling excess = -9.8442%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `Validation = normal`
  - `ETF Operability = normal`
- 비교 후보:
  - `SPY, QQQ, SOXX, XLE, XLU, XLV, IEF, IAU`, `top=2`, `interval=3`, `1M/3M/6M`, `MA200`은 `CAGR=20.86%`, `MDD=-13.04%`로 더 좋아 보였지만 `Deployment=review_required`였다.
  - 이유는 promotion은 통과했지만 recent rolling review / monitoring에서 manual review가 필요했기 때문이다.
- 해석:
  - `SPY`를 benchmark로 쓰면 GTAA가 AOR 기준보다 훨씬 엄격하게 평가된다.
  - 이번 후보는 CAGR이 SPY보다 높고, worst rolling excess가 `-10%` 안쪽에 있어 `Validation=normal`로 유지된 점이 핵심이다.
  - 아직 Candidate Library에는 자동 등록하지 않았다. 사용자가 원하면 Current Candidate Registry에 append한다.

### 2026-05-05 - SPY benchmark 저MDD 후보 재탐색

- 목표:
  - 위 SPY benchmark 후보보다 수익률을 조금 낮추더라도 MDD를 낮춘 GTAA 후보를 찾는다.
  - 조건은 `MDD <= 15%`, `CAGR >= 16~17%`, `top=2~4`, `interval<=3`, 10단계 실습 통과 가능 상태다.
- 가장 강한 저MDD 후보:
  - 전략 이름: `GTAA SPY Low-MDD Style Top-3`
  - input: `2016-01-01 ~ 2026-05-01`
  - effective result window: `2016-01-29 ~ 2026-02-27`
  - universe: `QQQ, SOXX, MTUM, QUAL, USMV, IAU, IEF, TLT`
  - `Top Assets = 3`
  - `Signal Interval = 3`
  - `Score Horizons = 1M / 6M`
  - `Trend Filter = MA250`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
- 결과:
  - `CAGR = 19.3479%`
  - `MDD = -11.0297%`
  - `Sharpe = 2.4188`
  - `End Balance = 59,437.88`
  - `SPY CAGR = 13.3638%`
  - `SPY MDD = -15.9042%`
  - `SPY 대비 CAGR spread = +5.9841%p`
  - `Rolling underperformance share = 3.33%`
  - `Worst rolling excess = -0.0209%`
  - `Rolling Review = normal`
  - `Monitoring = routine_review`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `Validation = normal`
  - `ETF Operability = normal`
- 비교 후보:
  - 같은 universe, `top=4`, `1M/6M`, `MA250`도 `CAGR=17.0098%`, `MDD=-10.9297%`, `Deployment=paper_only`로 매우 안정적이다.
  - 다만 `top=3` 후보가 CAGR, Sharpe, SPY 대비 spread가 더 높아 대표 후보로 더 적합하다.
- 해석:
  - 이전 `top=2 / 1M/6M/12M / MA250` 후보보다 MDD를 약 `18.10% -> 11.03%`로 크게 낮추면서 CAGR은 오히려 높게 유지했다.
  - `top=3`으로 분산을 조금 늘리고, 12M momentum을 빼서 최근 1M/6M 흐름을 더 민감하게 반영한 것이 drawdown 개선에 도움이 된 것으로 해석한다.
  - 사용자 요청에 따라 Candidate Library 노출용 Current Candidate Registry row를 append했다.
- 저장:
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `gtaa_current_candidate_spy_low_mdd_style_top3_i3_1m6m_ma250`
