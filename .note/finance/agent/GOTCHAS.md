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
