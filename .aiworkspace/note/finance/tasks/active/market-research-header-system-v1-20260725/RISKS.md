# Risks

## Resolved

- 네 독립 Vite bundle이 공통 source를 정상 포함하고 production build를 완료했다.
- 심리의 긴 headline과 선물매크로 action 2개는 420px에서 overflow 없이 stack된다.
- 일정의 header 이후 count / command 흐름과 경제사이클의 기존 payload 의미를 보존했다.
- fact box 좌측 강조선은 제거됐고 상태 점은 실제 상태 fact에만 표시된다.

## Known Unrelated Baseline

- broad service suite의 Backtest, AAII parser, 구형 선물 thermometer 관련 18개 실패는 이번 구현 이전부터 존재한 baseline이다.
- 사용자가 이번 범위에서 제외하도록 승인했으며 scoped 회귀는 모두 통과했다.

## Guardrails

- 계산, scoring, validation, provider fetch, DB / loader는 변경하지 않는다.
- 기존 action id와 Python dispatch 경계를 유지한다.
- 색상만으로 상태를 전달하지 않는다.
- generated `.superpowers/`와 기존 사용자 변경은 commit하지 않는다.
