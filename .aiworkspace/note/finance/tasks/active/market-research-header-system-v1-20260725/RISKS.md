# Risks

## Open

- 네 화면은 독립 Vite bundle이므로 공통 source import가 각 build와 static distribution에 모두 포함되는지 검증해야 한다.
- 심리의 긴 headline과 선물매크로 action 2개가 420px에서 충돌하지 않는지 actual Browser QA가 필요하다.
- 일정은 기존 두 카드 hero를 한 shell로 바꾸므로 count grid와 다음 command panel 사이의 여백 회귀를 확인해야 한다.
- 경제사이클 payload에서 월중 추정 여부를 상단 meta에 투영할 때 기존 의미를 확장하거나 새 판단을 만들지 않아야 한다.

## Guardrails

- 계산, scoring, validation, provider fetch, DB / loader는 변경하지 않는다.
- 기존 action id와 Python dispatch 경계를 유지한다.
- 색상만으로 상태를 전달하지 않는다.
- generated `.superpowers/`와 기존 사용자 변경은 commit하지 않는다.
