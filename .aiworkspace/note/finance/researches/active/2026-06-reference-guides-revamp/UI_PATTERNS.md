# UI And Workflow Patterns

## Product Goal

Make `Reference` the user's operating manual for the finance console:

- answer "where should I go next?"
- explain "what does this status/metric mean?"
- show "what record was created or read?"
- clarify "when should I stop rather than proceed?"
- keep product boundaries visible without turning the page into a wall of documentation

## Pattern 1. Task-First Reference Landing

- First viewport should start from user intent, not a long explanatory hero.
- Recommended entry cards:
  - `시장 / 데이터 상태 보기`: Overview, Futures Monitor, sentiment, events.
  - `데이터 갱신 / 복구`: Ingestion, System / Data Health, provider snapshot, stale data.
  - `후보 만들기`: Backtest Analysis, single strategy, compare, saved mix.
  - `검증 / 최종 판단`: Practical Validation, Final Review, Go / Review / Stop.
  - `선정 후 모니터링`: Portfolio Monitoring, scenario update, selected decision handoff.
  - `문제 해결`: stale Overview/Futures, provider gap, `NOT_RUN`, blocked gate, archive recovery.
- Each card should show `owner screen`, `what you can do`, `what this does not do`, and `next action`.

## Pattern 2. Journey Guides Instead Of One Universal Flow

- Keep the current portfolio-selection flow as `Journey: 후보를 모니터링 후보로 보내기`.
- Add separate journeys:
  - `Daily Market Context`: Overview refresh, futures monitor, event calendar, sentiment context.
  - `Data Freshness Repair`: Ingestion source, Data Health triage, run artifacts.
  - `Candidate Creation`: Backtest Analysis route and source handoff.
  - `Evidence Review`: Practical Validation / Final Review status interpretation.
  - `Monitoring After Selection`: Portfolio Monitoring setup, scenario update, drift / review signals.
- Each journey should have `when to use`, `screens`, `records`, `go/review/stop`, and `common failure states`.

## Pattern 3. Searchable Concepts And Status Dictionary

- Provide a compact search/filter over terms and statuses:
  `Data Trust`, `Promotion Policy Signal`, `NOT_RUN`, `REVIEW`, `BLOCKED`,
  `Provider Coverage`, `Look-through Exposure`, `selection_gate_policy_snapshot`,
  `deployment_readiness_policy_snapshot`, `Portfolio Monitoring Scenario`.
- Each row should include:
  `plain Korean meaning`, `owner screen`, `pass/fail implication`, `where to fix`, `record/source`.
- This can reuse the existing Glossary page later, but the Guides landing should expose a subset immediately.

## Pattern 4. Records And Data Source Map

- Add a table or drawer that answers:
  "이 화면에서 생긴 기록은 어디에 남고, 어떤 화면이 다시 읽는가?"
- Required rows:
  - MySQL price / provider / macro / sentiment tables
  - `PORTFOLIO_SELECTION_SOURCES.jsonl`
  - `PRACTICAL_VALIDATION_RESULTS.jsonl`
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
  - `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`
  - run history / run artifacts
- Mark generated/local artifacts as not normally committed.

## Pattern 5. Troubleshooting Playbooks

- Add short, action-oriented playbooks:
  - `Overview / Futures data가 stale일 때`
  - `Ingestion은 성공했는데 UI가 갱신되지 않을 때`
  - `Practical Validation에 NOT_RUN이 있을 때`
  - `Final Review 후보가 안 보일 때`
  - `Portfolio Monitoring scenario가 stale일 때`
  - `Archive에서 과거 run을 복원해야 할 때`
- Each playbook should show:
  `symptom`, `likely owner screen`, `first check`, `safe action`, `stop condition`, `where evidence lives`.

## Pattern 6. Contextual Cross-Links

- Other product screens should point back to Reference only at the exact interpretation point.
- Examples:
  - Backtest result `Promotion Policy Signal` caption -> Reference concept row.
  - Practical Validation `NOT_RUN` -> troubleshooting playbook.
  - Overview stale badge -> data freshness playbook.
  - Portfolio Monitoring scenario mismatch -> monitoring replay guide.
- Phase 1 can prepare anchors in Reference; later phases can wire links from other screens.

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Troubleshooting playbooks | Could become action runners if overloaded | Keep Reference read-only; link to owner screens instead of executing jobs. |
| Report-like Reference content | Could be confused with durable source-of-truth | Mark docs as guide only; source of truth remains DB / registry / saved setup. |
| Portfolio monitoring guide | Could sound like live approval / rebalance | Repeat no broker order, no auto rebalance, no account sync in journey header. |
| Searchable glossary | Could duplicate `Reference > Glossary` | Start with curated status dictionary; later merge or cross-link with Glossary. |
| External benchmark-inspired UI | Could over-polish Streamlit into a marketing page | Keep dense operational layout, compact controls, no hero-heavy landing. |
