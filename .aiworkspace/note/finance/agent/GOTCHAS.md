# Finance Codex Gotchas

Status: Active
Last Verified: 2026-05-12

이 문서는 반복될 가능성이 높은 실수만 짧게 남긴다.

## Rules

- `registries/*.jsonl`, `run_history/*.jsonl`, runtime artifact, temp CSV는 사용자가 명시 요청하지 않으면 커밋하지 않는다.
- `saved/*.jsonl`은 사용자가 저장한 reusable setup이므로 문서 정리 과정에서 삭제하지 않는다.
- Practical Validation에서 `NOT_RUN`은 pass가 아니다. 데이터나 구현이 없어 실행하지 못했다는 뜻이다.
- UI에서 provider / FRED를 직접 fetch하지 않는다. Ingestion -> DB -> Loader -> UI 흐름을 유지한다.
- Final Review와 Selected Portfolio Dashboard는 live approval, broker order, auto rebalance가 아니다.
- 문서 정리 중 기존 대형 문서를 그대로 새 `docs/`로 복붙하지 않는다. 장기 지식만 짧게 승격한다.
- 새 backtest report는 phase 폴더가 아니라 `.aiworkspace/note/finance/reports/backtests/runs/YYYY/`부터 시작한다.
- backtest report는 사람이 읽는 근거 문서다. `registries/`와 `saved/`의 JSONL source-of-truth를 대체하지 않는다.
- `research/` 폴더를 삭제하기 전에는 코드가 읽는 reference data가 없는지 확인한다. Practical Validation stress window JSON처럼 런타임이 읽는 파일은 먼저 새 위치로 옮기고 코드 경로를 바꾼다.
- `support_tracks/`의 과거 plugin / skill / automation 계획을 active 기준처럼 읽지 않는다. 현재 기준은 `AGENTS.md`, `docs/runbooks/`, 실제 설치된 skill이다.
