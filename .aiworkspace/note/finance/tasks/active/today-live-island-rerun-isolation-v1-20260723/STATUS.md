# Today Live Island Rerun Isolation V1 Status

Status: Written specification review pending
Roadmap: 0/2 implementation stages complete
Last Updated: 2026-07-23

## Completed

- actual `main-dev` browser와 source를 대조해 15초 전체 Today fragment와 1초 top-level React clock state를 분리 진단했다.
- static cache, portfolio live island, separate API/push의 세 접근을 비교했다.
- 사용자가 portfolio live island 방향을 승인했다.
- `DESIGN.md`에 static shell, clock child, conditional heartbeat, portfolio island, failure/test 계약을 고정했다.

## Next

- 사용자가 written specification을 확인하면 `writing-plans`로 TDD implementation plan을 작성한다.
- plan 승인 뒤 1/2차 전체 rerun 제거부터 구현한다.
