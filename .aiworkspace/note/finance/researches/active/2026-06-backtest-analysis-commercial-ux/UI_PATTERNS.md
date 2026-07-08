# UI Patterns

Status: Active
Last Updated: 2026-06-29 KST

## Summary

Backtest Analysis should become a compact workbench:

```text
Choose strategy / mix
  -> Run
  -> Read result summary
  -> Decide next action
  -> Drill into details only when needed
```

The target is not a prettier guide page.
The target is fewer default blocks, clearer status, and lower decision burden.

## Pattern Catalog

### Pattern 1. Workbench Header Instead Of Usage Guide

- Seen in: Koyfin summary snapshots, IBKR PortfolioAnalyst dashboard framing.
- User problem: The current top expander explains too much before the user acts.
- Interaction shape:
  - one compact header row under `Backtest`
  - stage stepper: `1 Backtest Analysis`, `2 Practical Validation`, `3 Final Review`
  - right side: current task / last run state / next action
  - no bullet guide
- Data required:
  - active panel
  - latest run exists?
  - current Practical Validation source exists?
  - last selected strategy / mix state
- Fit:
  - High. It directly replaces `Backtest 사용 안내`.
- Risk:
  - If too much status is added, it becomes another dashboard. Limit to 3-4 facts.

### Pattern 2. Action-First Backtest Analysis

- Seen in: Portfolio123 idea -> ranking -> test flow, current 4C reset.
- User problem: Reference and strategy-development panels distract from execution.
- Interaction shape:
  - top segmented choice: `Single Strategy` / `Portfolio Mix Builder`
  - a compact strategy selector with maturity chip
  - form grouped as `필수 설정` and `고급 설정`
  - run button visible near the essential settings
- Data required:
  - strategy catalog
  - maturity label
  - strategy-specific defaults
- Fit:
  - High. Current mode selector exists, but copy and panels should be simplified.
- Risk:
  - Maturity chip must not become a full strategy inventory table.

### Pattern 3. Result Overview / Details Split

- Seen in: TradingView Strategy Tester and QuantConnect result page.
- User problem: Latest Run repeats many checklists before showing the actual strategy result.
- Interaction shape:
  - `Run Overview`: metrics, curve, data state, next action in one row/section.
  - `Performance`: summary metrics and chart.
  - `Holdings / Selection`: selection history only for relevant strategies.
  - `Assumptions`: Data Trust, settings, benchmark, costs.
  - `Raw`: result table / meta.
- Data required:
  - existing bundle summary, chart, result_df, meta, warnings.
- Fit:
  - Very high. Existing tabs can be reorganized.
- Risk:
  - Need to preserve data warnings while making them less noisy.

### Pattern 4. Validation Handoff Eligibility, Not Candidate Score

- Seen in: Composer caution model and this project's Practical Validation boundary.
- User problem: Candidate Readiness score can look like a pseudo-investment rating.
- Interaction shape:
  - Replace score with three states:
    - `검증으로 보낼 수 있음`
    - `보낼 수 있지만 확인 필요`
    - `아직 보낼 수 없음`
  - Explain one reason and one action.
  - Keep detailed criteria in disclosure.
- Data required:
  - result rows / curve exists
  - supported strategy for Practical Validation
  - replay/source contract exists
  - warnings/review signals
- Fit:
  - Very high. This directly addresses the user's concern.
- Risk:
  - If too permissive, weak candidates enter Practical Validation. Mitigate by preserving review signal and downstream gate.

### Pattern 5. Reference Content Relocation

- Seen in: commercial products keep help/docs separate from main workflow.
- User problem: Reference help in Backtest Analysis is not part of the job.
- Interaction shape:
  - remove `render_reference_contextual_help("backtest_analysis")` from Backtest Analysis.
  - keep Reference page or a small global help entry if needed.
  - remove hidden research board table from default product path.
- Data required:
  - none for core workflow.
- Fit:
  - High.
- Risk:
  - Some useful internal strategy maturity information becomes less discoverable. Keep it in research/report docs.

### Pattern 6. Strategy Maturity As Chip, Not Panel

- Seen in: stage/status labels in analytics tools.
- User problem: Users must know prototype/research/candidate-ready, but not read a large table.
- Interaction shape:
  - strategy selector shows one maturity chip.
  - result overview shows one line: `역할`, `다음 가능 행동`, `주의`.
- Data required:
  - strategy key to maturity mapping.
- Fit:
  - High.
- Risk:
  - Mapping can drift. Put it in Streamlit-free service and test it.

### Pattern 7. Detail Disclosures For Developer Payload / Raw Meta

- Seen in: QuantConnect logs/project files/downloads as secondary sections.
- User problem: Developer payload and raw meta are useful for debugging but noisy for normal use.
- Interaction shape:
  - keep `Developer Payload`, `Meta`, raw tables under `Raw / Debug` tab or expander.
  - default view never starts with raw JSON or long caveats.
- Data required:
  - existing payload/meta.
- Fit:
  - High.
- Risk:
  - Debug convenience decreases slightly. Acceptable for commercial UX.

## Patterns That Conflict With Current Boundaries

| Pattern | Conflict | Handling |
|---|---|---|
| Broker-like launch / trade flow | live approval / order / account sync is out of scope | Keep all copy as candidate / validation / monitoring only |
| Strategy marketplace browsing | distracts from local data correctness | Parking lot |
| More guide expanders | violates user intent | Explicitly reject in acceptance criteria |
| UI direct provider refresh | breaks Ingestion -> DB -> Loader -> UI | Do not implement in Backtest Analysis |
| Turning Risk-On into monitoring signal | governance not approved | keep research lane |

## Product Copy Rules

- Use Korean-first labels.
- Avoid `Promotion Policy Signal` as a primary visible phrase. Prefer `다음 단계 가능성`, `검증 전 확인`, `보류 사유`.
- Avoid "추천", "승인", "투자 가능" in Backtest Analysis.
- Use `후보 source`, `검증 대상`, `관찰 후보` to separate stage semantics.
- Keep caveats short and action-linked.
