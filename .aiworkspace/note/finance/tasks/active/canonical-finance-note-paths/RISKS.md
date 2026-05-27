# Risks

- 기존 `.note/finance`에만 새로 생성된 local artifact가 있다면 자동 병합하지 않는다. 이번 작업은 참조 경로 전환만 수행한다.
- `registries/`와 `saved/` JSONL은 source-of-truth이므로 코드 검증 중 새 row를 쓰지 않는다.
- 남은 `.note` 문자열은 `quant-research` 외부 research source reference이며, finance app registry/saved/runtime 경로는 아니다.
