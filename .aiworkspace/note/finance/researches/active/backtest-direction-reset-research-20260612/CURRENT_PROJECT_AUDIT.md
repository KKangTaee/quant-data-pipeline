# Current Project Audit

Status: Active
Last Updated: 2026-06-12 KST

## Summary

현재 Backtest 제품의 올바른 중심은 `전략 실행 / 비교 / 후보 source 생성 / replay 가능성 확인`이다. Evidence, governance, diagnostics는 중요하지만 Backtest Analysis의 첫 화면 목적이 아니다.

Backtest workflow는 아래처럼 읽어야 한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

Backtest Analysis는 후보 source를 만든다. Practical Validation은 데이터 / provider / macro / robustness / realism evidence와 `NOT_RUN` 차단을 소유한다. Final Review는 selected-route gate와 decision dossier를 소유한다. Portfolio Monitoring은 선정 이후 read-only scenario update와 monitoring evidence를 소유한다.

## Current Product Promise

`finance`는 backtest 숫자를 바로 투자 판단으로 받아들이지 않고, DB-backed runtime, point-in-time / survivorship awareness, Practical Validation, Final Review, read-only monitoring을 통해 후보를 단계적으로 검증하는 quant research workspace다.

이 promise를 Backtest Analysis 안에서 모두 해결하려 하면 화면이 무거워진다. Backtest Analysis는 "좋아 보이는 전략을 찾는 곳"이지만 "투자 가능하다고 승인하는 곳"은 아니다.

## Local Evidence

| Area | Local source | Evidence label | What it proves |
| --- | --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Evidence-first / DB-backed / no-live-trading product boundary. |
| Roadmap state | `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | 4C reset completed; 5A/5B runtime contracts completed without new panels; no active phase. |
| Project ownership | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Backtest Analysis, Practical Validation, Final Review, Operations boundaries and file ownership. |
| Runtime flow | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | Documented | Single, Compare, Saved replay, Risk-On runtime paths and result bundle contract. |
| Strategy flow | `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` | Documented | ETF, strict annual, strict quarterly, Risk-On strategy family contracts. |
| Backtest UI flow | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Documented | Backtest Analysis first renders execution/compare, while validation/review/monitoring own downstream gates. |
| 4C status | `.aiworkspace/note/finance/tasks/active/backtest-analysis-direction-reset-20260609/STATUS.md` | Documented | 3A~4B panels were demoted behind `전략 개발 참고`. |
| 5A status | `.aiworkspace/note/finance/tasks/active/global-relative-strength-5a-20260609/STATUS.md` | Documented | GRS runtime/result bundle was hardened without adding a new panel. |
| 5B status | `.aiworkspace/note/finance/tasks/active/risk-parity-dual-momentum-5b-20260610/STATUS.md` | Documented | Risk Parity / Dual Momentum runtime/result bundle contracts were hardened without new panels. |
| Backtest Analysis render | `app/web/backtest_analysis.py` | Observed | Single Strategy / Portfolio Mix Builder render first; reference panels appear only after a checkbox. |
| Research board service | `app/services/backtest_analysis_research_board.py` | Observed | 3A~4B panels are hidden-by-default, non-writing strategy development references. |
| Strategy catalog | `app/services/backtest_strategy_catalog.py` | Observed | Current catalog includes ETF, strict annual, strict quarterly prototype, and Risk-On strategies. |
| Candidate replay | `app/runtime/candidate_library.py` | Observed | Candidate Library replay supports ETF keys and strict annual keys, not strict quarterly or Risk-On as candidate lifecycle. |
| History scope copy | `app/web/backtest_history_helpers.py` | Observed | Quarterly prototype and Risk-On have explicit deferred / research-lane interpretations. |

## Surface Role Classification

| Surface | Role | What Belongs Here | What Should Move Elsewhere |
| --- | --- | --- | --- |
| Backtest > Backtest Analysis | User-facing product surface with a research/reference tail | Run a strategy, compare strategies, build weighted mix, replay saved mix, create candidate source, inspect compact runtime warnings. | Provider collection, validation result save, final selected-route decision, monitoring signal, large governance workbench by default. |
| Backtest Analysis `전략 개발 참고` | Mixed / advanced reference | Maturity inventory, bridge notes, Risk-On governance notes, ETF evidence gap, session-only rerun matrix. | Default first screen or required candidate workflow. |
| Backtest > Practical Validation | User-facing evidence gate | Source traits, module plan, replay, provider/macro/robustness/realism evidence, Final Review gate. | Strategy ideation, broad strategy maturity catalog, live approval. |
| Backtest > Final Review | User-facing decision support | Gate-passed candidates, decision cockpit, selected-route decision record, dossier. | Backtest execution, provider fetch, auto monitoring. |
| Operations > Portfolio Monitoring | User-facing monitoring | Read-only selected strategy scenarios, explicit scenario update, continuity, review signals. | Broker orders, account sync, auto rebalance, strategy research workbench. |
| Operations > Backtest Run History / Candidate Library | Support / archive / replay | Inspect previous runs, restore payloads, replay supported candidates. | Primary product decision flow or broad governance explanation. |

## Branch Direction Diagnosis

### 3A~4B: Useful evidence, wrong default gravity

3A~4B created real knowledge: strategy maturity inventory, strict annual / ETF bridge, Risk-On governance readiness, ETF evidence expansion, current-anchor checks, and session-only rerun matrix. The issue was not that these were false. The issue was that they competed with the basic product task.

Why the flow became heavy:

- The first screen started to feel like a governance console rather than a strategy runner.
- Read-only diagnostics looked adjacent to action, even when they did not write registries or validation results.
- Strategy maturity, provider readiness, rerun scenarios, and governance blockers were all placed near the same stage, blurring ownership with Practical Validation and Final Review.
- The user had to parse too many "what this does not do" boundaries before doing the main job.

### 4C: Correct reset, but incomplete product answer

4C solved the immediate UX drift by rendering Single Strategy / Portfolio Mix Builder first and demoting panels behind `전략 개발 참고`. This should be kept.

What it did not fully solve:

- It did not redefine the higher-level product model for replay, saved setup, history, validation handoff, and maturity gates.
- It preserved the reference material but did not decide whether those references should eventually live in Reference / reports instead of Backtest Analysis.
- It did not answer whether quarterly prototypes should be matured next or paused behind a stricter gate.

### 5A / 5B: Valuable direction, keep the pattern

5A/5B are the strongest post-reset work because they improved strategy runtime/result bundle contracts without adding new panels.

Keep:

- GRS ownership of rebalance cadence, cash proxy, benchmark contract, concentration metadata, and score-window metadata.
- Risk Parity volatility window / eligible universe / inverse-vol / cash-only / low-vol overweight diagnostics.
- Dual Momentum raw top-N / trend rejected / cash-retained slot / concentration / whipsaw diagnostics.
- Reuse of existing Selection History and result bundle surfaces.

Reason: this makes Backtest Analysis better at its primary job: producing interpretable run results and replayable candidate sources.

### 5C Strict Quarterly Prototype: Defer

Strict Quarterly Prototype work should not be the immediate next build unless the user explicitly chooses a prototype-maturation slice. It needs evidence gates before it can leave prototype status:

- quarterly PIT / filing lag evidence
- history and saved replay parity
- Candidate Library lifecycle decision
- Practical Validation module fit
- clear label that runtime success is not candidate readiness

## Strategy Maturity Model

| Maturity | Meaning | Required Gate | Strategies Today |
| --- | --- | --- | --- |
| Candidate-ready source | Can be run/replayed and has enough durable evidence to enter Practical Validation, but still needs validation gate before Final Review. | Runtime/result bundle contract, replay support, strategy hub/current anchor, known weakness, Practical Validation source fit. | Quality Strict Annual, Value Strict Annual, Quality + Value Strict Annual, GTAA as tactical sleeve; Equal Weight as baseline/sleeve only. |
| Runtime-hardened but evidence-expansion needed | Runtime/result contract is meaningful, but current candidate evidence is not deep enough for first-class promotion. | Current anchor report, rerun matrix interpretation, provider/cost/benchmark evidence, weakness report. | Global Relative Strength, Risk Parity Trend, Dual Momentum. |
| Research lane | Produces valuable research evidence but uses a different cadence or artifact model that needs governance before downstream handoff. | Domain-specific Practical Validation module, Final Review selected-route rule, monitoring cadence, artifact storage boundary. | Risk-On Momentum 5D. |
| Prototype / contract-smoke | Runtime exists to test a contract, not to imply investment readiness. | PIT / filing lag review, replay lifecycle, validation compatibility, explicit prototype label. | Quality Strict Quarterly Prototype, Value Strict Quarterly Prototype, Quality + Value Strict Quarterly Prototype. |
| Legacy / compatibility | Kept for compatibility or comparison, not first-line product direction. | None until explicitly re-scoped. | Broad Quality Snapshot. |

## Strategy Group Findings

| Strategy Group | Current Interpretation | Keep / Defer / Rework |
| --- | --- | --- |
| Strict Annual 3종 | Best candidate-ready factor group, with annual PIT framing and existing replay support. | Keep as first candidate-ready group, but still gate through Practical Validation. |
| Strict Quarterly Prototype 3종 | Runtime-supported prototype, not an annual-equivalent candidate. | Defer; do not remove label. Improve replay/runtime contracts later only as prototype work. |
| ETF: GTAA | Evidence-mature tactical ETF sleeve. | Keep as bridge-ready sleeve. |
| ETF: Equal Weight | Useful baseline / exposure sleeve, weak standalone alpha claim. | Keep as baseline/sleeve, not standalone winner. |
| ETF: GRS | Runtime/replay recently improved, current anchor still thin. | Keep 5A contract; Next evidence-expansion candidate. |
| ETF: Risk Parity Trend | Runtime contract now explains defensive mechanics, but evidence hub is thin. | Keep 5B contract; Next evidence-expansion candidate. |
| ETF: Dual Momentum | Runtime contract now exposes concentration/whipsaw/cash retention, but evidence hub is thin. | Keep 5B contract; Next evidence-expansion candidate. |
| Risk-On Momentum 5D | Strong daily swing research lane, but not downstream-ready. | Keep as research lane; governance design before validation/review/monitoring. |

## Current Weak Points

- Backtest Analysis still contains advanced reference panels; even hidden, their existence can invite future panel growth.
- The product does not yet have a single compact handoff contract that says: "this result can go to Practical Validation because X, not because CAGR is high."
- Strategy maturity is present in services/docs, but not yet elevated into a product-level decision rule outside the heavy panel model.
- Saved replay and history replay are valuable but should be framed as reproducibility, not validation.
- Quarterly prototypes and Risk-On Momentum are especially likely to be over-promoted if performance looks attractive.

## Weaknesses

The main weakness is workflow gravity, not lack of raw capability. The branch has many useful pieces, but the user can still be pulled from "run and compare a strategy" into maturity/governance/provider/readiness interpretation too early. That makes Backtest Analysis feel heavier than its product role.

Secondary weaknesses:

- Candidate readiness and replayability are not yet expressed as one compact handoff contract.
- ETF strategies after GTAA have improved runtime metadata but still thin durable candidate evidence.
- Strict quarterly prototypes and Risk-On Momentum need stronger labels and gates to prevent accidental promotion.

## Data And Validation Risks

- Point-in-time correctness and filing lag are still decisive for fundamental strategies, especially quarterly variants.
- Survivorship and universe assumptions are decisive for Risk-On Momentum and dynamic equity universes.
- Provider / holdings / liquidity evidence belongs in DB-backed ingestion and Practical Validation, not in Backtest Analysis direct fetches.
- `NOT_RUN` remains a blocker, not a pass.
- Backtest result bundle metadata should be evidence for reproducibility and warnings, not automatic investability approval.

## Audit Conclusion

The next direction should preserve 4C and 5A/5B while resisting the 3A~4B default-screen pull.

In short:

- Keep Backtest Analysis execution-first.
- Keep 5A/5B runtime/result bundle hardening as the right pattern.
- Move broad maturity/governance work toward Reference / reports / compact read models rather than more Backtest panels.
- Treat Practical Validation as the first real evidence gate.
- Treat Final Review and Portfolio Monitoring as downstream decision support and monitoring only.
- Defer strict quarterly formalization and Risk-On downstream integration until their separate gates are approved.
