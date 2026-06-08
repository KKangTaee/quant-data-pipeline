# UI And Workflow Patterns

Status: Draft
Last Updated: 2026-06-08

## Summary

현재 제품은 단계가 이미 간결하다. 필요한 개선은 단계를 늘리는 것이 아니라 각 단계의 "판단 효력"을 높이는 것이다. UI도 더 많은 버튼보다, 어떤 evidence가 충분하고 어떤 evidence가 부족해서 선택을 막거나 보류해야 하는지 한눈에 보이게 해야 한다.

## Pattern Catalog

### 1. Evidence Packet Before Decision

- Seen in: Bloomberg PORT reporting, IBKR PortfolioAnalyst reports, Portfolio Lab PDF / saved portfolio claims.
- User problem: Final Review에서 많은 근거를 보더라도 나중에 "왜 이 후보를 선택했는지"를 재현하기 어렵다.
- Interaction shape: Final Review 상단에 `Decision Packet` 상태를 보여준다. 항목은 Backtest Contract, Data Validation, Provider Look-through, Benchmark Parity, Robustness, Stress / Simulation, Paper Observation, Monitoring Plan, Assumption Disclosure로 나눈다.
- Data required: validation result, diagnostic rows, provider coverage, curve provenance, benchmark parity, strategy config, data snapshot ids, source URLs / source types, operator reason.
- Why it matters: 투자 판단은 하나의 점수보다 evidence bundle의 완성도가 중요하다.
- Fit for this project: 매우 높음. 이미 registry와 validation result에 대부분의 재료가 있다.
- Risks: packet을 너무 크게 만들면 Final Review가 무거워진다. 첫 구현은 compact summary + expandable details가 적합하다.

### 2. Missing Evidence As A Gate, Not A Decoration

- Seen in: Bloomberg data validation pattern, FINRA / SEC automated tool disclosure, current project `NOT_RUN is not pass` rule.
- User problem: `REVIEW` / `NOT_RUN`이 많아도 사용자는 최종 선택을 눌러도 되는지 헷갈린다.
- Interaction shape: `Critical Gaps` panel을 Final Review 저장 버튼 바로 위에 둔다. critical `NOT_RUN`, stale provider, benchmark parity REVIEW, runtime period gap, leveraged ETF suitability gap은 selected route를 기본 차단하거나 explicit waiver를 요구한다.
- Data required: diagnostic status, critical domain list, review gaps, provider coverage status, benchmark parity, period coverage, strategy family risk class.
- Why it matters: 검증 효력은 "실행한 검사 수"가 아니라 "실행하지 못한 중요 검사 처리"에서 나온다.
- Fit for this project: 높음. `not_run_critical_domains`, `paper_tracking_gaps`, `review_gaps`가 이미 존재한다.
- Risks: 너무 엄격하면 초기 workflow가 자주 막힌다. waiver가 있더라도 사유와 만료일을 저장해야 한다.

### 3. Look-Through Exposure Board

- Seen in: Morningstar Portfolio X-Ray, IBKR Portfolio Checkup.
- User problem: ETF tickers만 보면 실제 자산군, 섹터, 국가, top holding overlap, 비용, 레버리지 노출을 알기 어렵다.
- Interaction shape: Practical Validation의 Provider Coverage를 `Look-through Board`로 승격한다. 구성: coverage %, missing ETF, top holdings overlap, asset class / sector / country exposure, expense / AUM / spread, leverage / inverse objective, source age.
- Data required: `etf_holdings_snapshot`, `etf_exposure_snapshot`, `etf_operability_snapshot`, source map status, collected_at, coverage_status.
- Why it matters: 실전 투자는 portfolio가 실제로 무엇을 들고 있는지 확인해야 한다.
- Fit for this project: 높음. P2 provider connector foundation과 잘 맞다.
- Risks: provider coverage가 partial이면 UI가 빈칸이 많아질 수 있다. 빈칸은 `NOT_RUN / missing source map`으로 보여줘야 한다.

### 4. Robustness Lab Attached To Validation

- Seen in: CFA backtesting / simulation, QuantConnect optimization, Portfolio Lab Monte Carlo.
- User problem: 하나의 backtest curve가 좋아도 parameter, period, rebalance date, benchmark, cost assumption이 조금 바뀌면 무너질 수 있다.
- Interaction shape: Backtest Analysis에서 실험을 만들고, Practical Validation에서 `Robustness Lab` 결과를 읽는다. 기본 세트는 walk-forward window, train/test split, parameter perturbation, drop-one component, rebalancing cadence, cost/slippage sensitivity, Monte Carlo/bootstrap, historical stress windows.
- Data required: strategy config, parameter grid, run set id, run result summary, cost model, rebalance policy, out-of-sample windows, result degradation metrics.
- Why it matters: overfit / data snooping 방어는 실전 투자 가능성 판단의 핵심이다.
- Fit for this project: 중간-높음. 일부 stress / sensitivity는 이미 있으나 experiment registry가 필요하다.
- Risks: 계산 비용과 UI 복잡도가 크다. 첫 구현은 selected source 1개에 대한 small default test suite가 좋다.

### 5. Assumption And Limitation Disclosure

- Seen in: FINRA / SEC automated tool alerts, Morningstar report disclosures, IBKR disclosures.
- User problem: backtest / simulation / provider snapshot이 무엇을 보장하지 않는지 화면에 남지 않으면 과신하기 쉽다.
- Interaction shape: Final Review packet에 `Assumptions & Limits` section을 고정한다. "hypothetical backtest", "not investment advice", "current snapshot", "provider partial", "no broker order", "ALFRED vintage not implemented" 같은 항목을 자동 생성하고 operator가 확인한다.
- Data required: source provenance, data coverage, strategy assumptions, model limitations, no-live boundary.
- Why it matters: 실전 투자 판단 전 가장 중요한 안전장치다.
- Fit for this project: 매우 높음. docs와 code에 이미 boundary text가 많다.
- Risks: 문구만 많아지면 사용자가 무시한다. critical limitation만 decision-level로 묶어야 한다.

### 6. Persistent Monitoring Timeline

- Seen in: IBKR PortfolioAnalyst reports / allocation goals, Bloomberg reporting orchestration.
- User problem: Selected Dashboard에서 현재 상태를 볼 수 있어도, 시간이 지나며 어떤 trigger가 발생했고 어떤 결정을 했는지 누적되지 않는다.
- Interaction shape: Selected Portfolio Dashboard에 `Monitoring Timeline`을 둔다. 사용자가 월간/리밸런싱 주기마다 snapshot을 저장하면 benchmark delta, drawdown, drift, provider staleness, review signal, operator action이 append-only로 남는다.
- Data required: selected decision id, recheck result, target/current allocation, benchmark, provider coverage refresh status, review trigger status, operator note.
- Why it matters: 실전 투자는 "선정"보다 "선정 이후 관리"가 더 길다.
- Fit for this project: 높음. `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` 경계가 이미 있다.
- Risks: account holding 자동 연결 없이 current allocation은 수동 / virtual input이다. 이 경계를 분명히 해야 한다.

### 7. Source-Of-Truth Breadcrumb

- Seen in: institutional reporting workflows and current project registry model.
- User problem: legacy registry, V2 registry, saved portfolio, run history가 섞이면 무엇을 믿어야 하는지 헷갈린다.
- Interaction shape: 모든 주요 화면 상단에 `Source chain`을 compact breadcrumb로 표시한다: `selection_source_id -> validation_id -> decision_id -> monitoring_snapshot_id`.
- Data required: registry ids and source references.
- Why it matters: 재현성과 사용자 신뢰를 높인다.
- Fit for this project: 높음. id들이 이미 존재한다.
- Risks: legacy source를 함께 표시할 때 복잡해질 수 있다.

## Patterns That Conflict With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Broker integration and automated rebalancing | current product boundary says no live approval, broker order, auto rebalance | Parking Lot. Monitoring log and manual allocation input만 먼저 강화한다. |
| AI-generated deployable trading strategies | Composer-like products go from idea to execution | Do not adopt execution. Possible future: AI-assisted checklist / report narrative only. |
| Account aggregation | IBKR-like external account linking needs credentials and privacy/security work | Out of scope. Use manual current value / allocation input until product boundary changes. |
| Institutional multi-asset risk model | Bloomberg PORT-like model is too broad | Use scenario families and data validation pattern, not full risk engine clone. |
| Full licensed holdings database | Morningstar-like coverage requires data licensing | Use provider snapshot connectors and explicit coverage gaps. |

## Patterns That Should Remain Internal / Ops Only

| Pattern | Keep internal because | Product-facing alternative |
| --- | --- | --- |
| Provider source map discovery buttons | source mapping is operational and sometimes noisy | Show provider coverage and missing source reason in Practical Validation. |
| Raw ingestion logs / failure CSV | useful for debugging, not investment judgment | Summarize data freshness, missing fields, and collection status. |
| Run artifact browsing | local runtime artifact can be large and unstable | Link to evidence packet / report summary. |
| Schema sync / DB maintenance | operator task, not user workflow | Data validation summary with stale / missing / partial states. |

## Candidate Questions For Feature Opportunity

- Should critical `NOT_RUN` block `SELECT_FOR_PRACTICAL_PORTFOLIO`, or allow explicit waiver?
- What is the minimum Decision Packet required before Final Review selection?
- Which look-through fields are mandatory for ETF portfolios: holdings coverage, expense ratio, AUM, ADV, spread, leverage objective?
- Should Robustness Lab start as a default small suite or as user-configurable advanced validation?
- What exact monitoring snapshot should be appended after a portfolio is selected?

## 2026-06-08 Pattern Refresh

### 1. Main-Dev As Product Direction Console

- User problem: strategy research and product workflow decisions can become mixed if this session tries to evaluate both alpha quality and product structure.
- Interaction shape: `main-dev` should read as a product direction console. It audits local workflow, compares benchmarks, writes research bundles, and prepares future task / phase handoffs. It does not decide that a backtest-dev strategy is production-ready by itself.
- Output pattern: every broad direction request should produce a small roadmap: `1차 현재 제품 감사 -> 2차 외부 패턴 비교 -> 3차 개발 후보 우선순위 -> 4차 별도 개발 세션 handoff`.
- Fit: very high.

### 2. Strategy Promotion Contract

- Seen in: QuantConnect lifecycle, Portfolio123 ranking / simulation assumptions.
- User problem: backtest-dev can improve or add strategies, but main product needs a clear rule for when a strategy is eligible for Practical Validation / Final Review / Monitoring governance.
- Interaction shape: before a strategy enters product governance, show a promotion checklist:
  - strategy family / owner
  - universe and survivorship model
  - parameter set and optimization history
  - in-sample / out-of-sample / walk-forward evidence
  - cost / slippage / liquidity assumptions
  - benchmark / comparator policy
  - generated artifacts and replay contract
  - known failures and `NOT_RUN` evidence
- Data required: strategy config, run-set id, artifact ids, validation result ids, report path.
- Fit: high. It connects `backtest-dev` output to `main-dev` product governance without making this session a strategy-research worktree.

### 3. Monitoring Snapshot And Review Loop

- Seen in: Koyfin drift analysis, IBKR / Bloomberg reporting workflows.
- User problem: Portfolio Monitoring can show scenario results, but it does not yet create a durable review history by default.
- Interaction shape: add explicit `Save Monitoring Snapshot` / `Record Review` action after scenario update. Snapshot rows should capture selected decision id, portfolio id, strategy slot signature, benchmark delta, drift, provider freshness, review signals, open issues, operator note, and next review date.
- Data required: existing session scenario result, selected decision source chain, optional allocation input, provider freshness read model.
- Fit: very high. This is the most natural next user-facing improvement after the current monitoring-first UX.

### 4. Evidence Summary Before Evidence Detail

- Seen in: Bloomberg / Koyfin summary snapshots, current Operations Console pattern.
- User problem: Practical Validation and Final Review have many audit rows; users need a "what matters now" view first.
- Interaction shape: each stage starts with a compact action-oriented summary:
  - `Ready`: what can proceed now
  - `Must Fix`: blockers
  - `Open Review`: non-blocking but tracked risks
  - `Missing / Stale`: data gaps
  - `Next Owner`: Backtest, Ingestion, Validation, Final Review, Portfolio Monitoring, Archive
- Fit: high. Keep detailed evidence under expandable sections.

### 5. Archive / Recovery Demotion Instead Of Immediate Deletion

- Seen in: institutional separation between production workflow, reports, and archive.
- User problem: legacy tools still have audit value but can confuse the primary path.
- Interaction shape: Run History and Candidate Library stay available under `Operations > Archive / Recovery`, with copy that says "recover or audit old work; not a required selection stage."
- Fit: high. Deleting now could break handoff and evidence recovery.

### 6. Large-Surface Refactor After Direction Approval

- Seen locally: file-size audit, current roadmap carry-forward.
- User problem: product-facing changes in very large Streamlit/runtime files are riskier and harder to QA.
- Interaction shape: once a feature direction is approved, open a separate implementation session that splits one surface around a concrete feature boundary:
  - Portfolio Monitoring scenario / snapshot / detail panels
  - Portfolio Mix saved replay / weighted result / strategy form body
  - Robustness experiment read model / UI
- Fit: medium-high. It is not a product feature by itself, but it should accompany broad UX additions.

### 7. Product Copy Should Say Monitoring Candidate, Not Live-Ready Portfolio

- Seen in: Composer backtest disclosure and current project no-live boundary.
- User problem: "투자 가능 후보" can sound like approval to deploy real capital.
- Interaction shape: prefer labels like `모니터링 후보`, `관찰 후보`, `실전 검토 후보`, `선정 후 모니터링 대상`; reserve `live`, `deployment`, `order`, `rebalance` for explicit future scope only.
- Fit: very high.

### Updated Candidate Questions

- What exact conditions let a backtest-dev strategy enter main product governance?
- Which monitoring snapshot fields are mandatory for every selected strategy?
- Should monitoring snapshots be saved per strategy slot, per dashboard portfolio, or both?
- Which legacy surfaces can be hidden from primary navigation after archive semantics are stable?
- Which large surface should be split first if Monitoring Snapshot V2 is approved?
