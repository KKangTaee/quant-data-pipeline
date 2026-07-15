# Overview Market Context Turnaround Stage Semantics Fix V1 Status

Last Updated: 2026-07-16

## Current Stage

- 전체 roadmap: 1차~3차
- 현재: detailed TDD implementation plan complete, 1차 RED 시작 전
- 구현 완료 차수: 0/3

## Completed

- AAPL actual DB와 current code를 read-only로 추적했다.
- EPS 누락의 직접 원인을 duration unit allowlist의 `USD per share` 누락으로 확정했다.
- 파일 수정 없이 unit 하나만 허용한 재계산에서 TTM EPS `7.90`, `PER_READY` 복구를 확인했다.
- data-only/minimal, selected semantic display, backend taxonomy rewrite 세 접근을 비교하고 중간안을 승인 방향으로 선택했다.
- 사용자가 written spec을 승인했다.
- loader/evidence, React semantics, actual/Browser QA의 3개 task와 RED/GREEN/commit 단위를 `PLAN.md`에 고정했다.
- linked `codex/sub-dev` worktree와 focused baseline 100/100 pass를 확인했다.

## Next Action

- 1차 public-loader `USD per share` RED test부터 실행한다.
