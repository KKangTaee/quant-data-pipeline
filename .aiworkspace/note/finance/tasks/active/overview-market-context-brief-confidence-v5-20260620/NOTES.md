# Notes

## Decision

Events / 자료 신뢰도는 market movement 자체가 아니라 `오늘의 시장 브리프를 얼마나 강하게 읽을지`에 대한 confidence modifier다.

따라서 이 정보는 `오늘의 시장 브리프` 3행 안에 섞지 않고, 바로 아래 `브리프 신뢰도`로 분리한다.

## UX Interpretation

- `오늘의 시장 브리프`: 오늘 무엇이 움직였고, 그 움직임이 확산인지 집중인지, Futures/Macro 배경이 어떤지 읽는다.
- `브리프 신뢰도`: 이벤트 자료와 선물 자료 상태 때문에 위 브리프를 어느 정도 조심해서 읽어야 하는지 보여준다.
- `근거: 자료 기준 / 출처 상태`: 더 긴 source ledger와 보강 위치는 하단 disclosure에서 확인한다.

## Compatibility

`context_findings` / `next_checks`는 이전 task와 테스트 호환을 위해 payload에 남긴다. 다만 기본 UI가 이를 action checklist나 별도 findings rail로 다시 표시하면 이번 V5 결정과 충돌한다.
