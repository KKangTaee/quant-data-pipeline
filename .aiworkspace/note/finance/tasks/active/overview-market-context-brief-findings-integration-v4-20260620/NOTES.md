# Notes

## UX Decision

- `맥락 검토 결과`는 별도 section으로 두면 사용자가 다시 또 다른 체크 결과를 읽는 느낌이 강했다.
- 가격 움직임과 Futures / Macro는 이미 상단 headline, tape, brief rows에 들어가 있으므로 별도 반복하지 않는다.
- Events / 자료 신뢰도는 시장 결론을 바꾸는 신호가 아니라 현재 브리프를 읽을 때의 caveat이므로, `오늘의 시장 브리프` 안에서 같은 흐름으로 읽게 한다.

## Data Boundary

- `context_findings`와 `next_checks`는 compatibility payload로 유지했다.
- 기본 renderer는 이 payload를 별도 user-facing rail로 자동 표시하지 않는다.
- `extra_context_findings`가 명시적으로 들어온 경우에만 기존 rail helper가 추가 근거 메모로 표시할 수 있다.
