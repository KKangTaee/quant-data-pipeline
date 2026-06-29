# Internal Benchmarks

Status: Active
Last Verified: 2026-06-08

## Scope Note

이번 2차 작업은 외부 상용 서비스 benchmark가 아니라, 현재 repository 안에 누적된 strategy report와 runtime smoke를 기준으로 한 internal benchmark다.

외부 benchmark가 필요한 경우 별도 3차 전 research로 열 수 있다.
현재 목적은 "무엇을 먼저 개발할지"를 결정하는 것이므로, 이미 검증된 local evidence를 우선한다.

Evidence labels:

- `Observed`: code or local report directly shows the behavior.
- `Documented`: durable docs or strategy report describe the pattern.
- `Inferred`: synthesis from multiple supported local facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Internal benchmark | Category | Evidence | Relevant pattern | Product implication |
| --- | --- | --- | --- | --- |
| Strict Annual current candidates | Factor equity | Documented | Value / Quality / Quality+Value each have current anchor or alternative notes | Best starting point for candidate evidence hardening |
| GTAA current candidate | ETF tactical allocation | Documented | Low-MDD ETF paper candidate with practical route | Useful defensive / tactical component for portfolio bridge |
| Equal Weight sleeve | ETF static basket | Documented | Standalone winner is weak, but mix with GTAA improves portfolio shape | Treat as sleeve / exposure tool, not alpha engine |
| Global Relative Strength smoke | ETF relative strength | Observed | Core/runtime/UI/replay path is connected | Needs strategy hub and current candidate search before promotion |
| Quarterly strict runtime smoke | Factor equity prototype | Observed | Runtime contract and meta preservation work | Needs candidate lifecycle and investment evidence before promotion |
| Risk-On Momentum 5D V2 | Daily swing research | Documented | V2 analysis, ATR exit, macro penalty, comparison suite exist | Needs separate governance before validation / monitoring integration |

## Key Findings

### 1. Mature strategy families already exist

The strongest evidence is concentrated in strict annual family reports and GTAA / Equal Weight ETF notes.
This argues for consolidating and productizing existing candidates before adding another core strategy.

### 2. Runtime support is broader than durable strategy evidence

The product can execute more strategies than it can confidently explain as candidate families.
Global Relative Strength, Risk Parity Trend, Dual Momentum, quarterly prototypes, and Risk-On Momentum need different follow-up work.

### 3. Strategy maturity should be a first-class product signal

The UI and reports should distinguish:

- executable research strategy
- replayable candidate
- Practical Validation-ready source
- Final Review-eligible candidate
- Portfolio Monitoring-ready selected strategy

Without this maturity layer, users can confuse "runs successfully" with "ready for monitoring".

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| Strategy evidence is uneven | Strict annual has rich reports; Risk Parity / Dual Momentum do not | Build an inventory / weakness matrix before implementation |
| Risk-On governance is deferred | Roadmap explicitly keeps it outside validation / monitoring | Open separate approved Daily Swing governance scope |
| Quarterly remains prototype | Runtime smoke checks contract, not investment readiness | Do not promote quarterly candidates until replay / validation evidence matures |
| ETF strategy family lacks unified anchor view | GTAA / EW are documented; GRS is mostly smoke-validated | Add ETF family evidence normalization before candidate promotion |
