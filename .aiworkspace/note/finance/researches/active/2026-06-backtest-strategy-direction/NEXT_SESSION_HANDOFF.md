# Next Session Handoff

Status: Active
Last Verified: 2026-06-08

## Recommended New Session Prompt

```text
2차 research bundle `.aiworkspace/note/finance/researches/active/2026-06-backtest-strategy-direction/`를 읽고,
3A `Strategy Evidence Inventory / Direction Panel` 구현 task를 열어줘.

범위:
- Backtest 전략별 maturity / evidence / next action을 read-only로 보여준다.
- registry / saved JSONL / run history는 수정하지 않는다.
- Risk-On Momentum 5D governance, quarterly maturation, ETF current-candidate rerun은 이번 task에서 구현하지 않는다.
```

## Start Here

1. `.aiworkspace/note/finance/docs/INDEX.md`
2. `.aiworkspace/note/finance/docs/ROADMAP.md`
3. `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
4. `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md`
5. `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
6. This bundle:
   - `RECOMMENDATION.md`
   - `STRATEGY_INVENTORY.md`
   - `WEAKNESS_MATRIX.md`
   - `CURRENT_PROJECT_AUDIT.md`

## Suggested 3A Scope

### Purpose

Backtest Analysis에서 전략별 성숙도와 다음 행동을 확인할 수 있게 한다.

### Candidate Files

| Area | Files |
| --- | --- |
| Strategy catalog | `app/web/backtest_strategy_catalog.py` |
| Read model | new or existing `app/services/backtest_*` helper |
| Backtest UI | `app/web/backtest_analysis.py`, `app/web/backtest_single_strategy.py`, or related `app/web/backtest_*` surface |
| Reference / docs link | optional contextual help only if narrow |
| Tests | `tests/test_service_contracts.py` or focused Streamlit-free service tests |

### Implementation Boundary

- Read-only display only.
- No strategy runtime behavior changes.
- No DB schema changes.
- No provider fetch.
- No registry / saved setup writes.
- No generated artifact commit.

### Acceptance Criteria

- Strategy maturity rows exist for all catalog strategies.
- Risk-On Momentum 5D is clearly labeled as Backtest Analysis research lane with governance deferred.
- Strict quarterly prototypes are clearly labeled as prototype / contract-smoke maturity.
- Strict annual 3종 and GTAA / Equal Weight are surfaced as first evidence-mature candidate group.
- Tests cover the read model without importing Streamlit.
- Browser QA is run if Streamlit UI changes.

## Suggested 3B Scope After 3A

Strict Annual + GTAA / Equal Weight Portfolio Bridge:

- show component role / target use
- show current anchor / weakness
- show required Practical Validation evidence
- keep final selection and monitoring read-only

## Explicitly Deferred

- Risk-On Momentum Practical Validation module
- Risk-On Momentum Final Review route
- Portfolio Monitoring daily signal policy
- GRS / Risk Parity / Dual Momentum current candidate search
- quarterly candidate lifecycle
- external benchmark research
- live trading / broker integration / auto rebalance

## Closeout Reminder

After any 3차 implementation:

- run targeted tests
- run `git diff --check`
- run Browser QA if UI changed
- update relevant durable docs via `finance-doc-sync`
- avoid staging generated artifacts unless explicitly requested
