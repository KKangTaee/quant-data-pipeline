# Inflation Policy Yield Path Integration

- Worktree: `codex/sub-dev`
- 단계별 독립 커밋과 테스트 gate를 유지한다.
- 사용자 소유 registry, research bundle, run history와 기존 QA 이미지는 stage하지 않는다.
- 구현 순서: data -> engines -> workbench -> equity stress -> recession risk.
- 1차 데이터 task는 실제 2026 source와 2026-07-29 PIT cutoff를 통과했다.
- 2차 엔진은 `finance/loaders/inflation_policy.py` bundle과 새 model artifact만 입력으로
  사용하고 `economic_cycle_*` 결과를 import/query/fallback하지 않는다.
