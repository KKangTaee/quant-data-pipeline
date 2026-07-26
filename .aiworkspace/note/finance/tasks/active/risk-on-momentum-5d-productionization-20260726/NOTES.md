# Risk-On Momentum 5D Productionization Notes

## Decisions

- Label-only promotion is unsafe because maturity currently gates Level2 handoff.
- Core strategy behavior is treated as an existing contract; optimization must prove parity.
- Standard execution should be a useful candidate review, while 50-random plus sensitivity
  belongs to an explicit deep-research mode.
- Full trade/scanner rows stay generated; downstream uses compact evidence only.
- Current universe membership must not be presented as historical PIT membership.
- Standard는 20개 simulation request 중 behaviorally distinct 16개만 실행하며 4개를 cache에서 재사용한다.
- Daily Swing history record는 analysis intensity와 compact evidence를 보존하고 Practical Validation replay는 전략 규칙을 유지하되 Quick intensity를 강제한다.
- production maturity는 자동 신호나 주문을 의미하지 않는다. selected route는 장 마감 후 수동 검토, 1 market day stale, manual recheck를 기본으로 한다.

## Durable Doc Sync

- `docs/ROADMAP.md`: Daily Swing governance 후보를 Decision Queue에서 제거하고 implemented baseline으로 승격
- `docs/flows/BACKTEST_UI_FLOW.md`: production maturity, compact evidence와 Level2 fail-closed 흐름 반영
- `docs/architecture/BACKTEST_RUNTIME_FLOW.md`: prepared/cache/intensity와 downstream route 반영
- `docs/architecture/SCRIPT_STRUCTURE_MAP.md`, `SYSTEM_BOUNDARIES.md`, `STRATEGY_IMPLEMENTATION_FLOW.md`: 새 runtime evidence / validation / policy owner 반영
- `docs/PRODUCT_DIRECTION.md`, `docs/PROJECT_MAP.md`, `docs/INDEX.md`: 제품 약속, high-level surface, 문서 탐색 구조 변화가 없어 변경하지 않음

## Existing Dirty Worktree

The following pre-existing user/runtime files are out of scope and must not be staged:

- `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl`
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`
- `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`
- `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`
- existing generated QA images and `.superpowers/`

## Baseline Test Gap

The broader evidence-inventory suite currently has one pre-existing drift failure:
`test_backtest_ui_uses_catalog_defaults_for_primary_strategy_surfaces` searches the current
Single Strategy source for the old literal `statement annual`. Risk-On core and governance
tests are green. This drift should be handled only if the owning contract is touched.
