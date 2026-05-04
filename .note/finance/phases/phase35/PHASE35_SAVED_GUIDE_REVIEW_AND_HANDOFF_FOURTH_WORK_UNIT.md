# Phase 35 Saved Guide Review And Handoff Fourth Work Unit

## 목적

Phase35 네 번째 작업은 기록된 operating guide를 다시 읽고,
기본 포트폴리오 선정 흐름이 어디까지 완성됐는지 확인하는 것이다.

## 쉽게 말하면

운영 가이드를 만든 뒤 다시 열어 보고,
"이 후보는 선정 기록과 운영 기준이 연결된 상태"인지 확인한다.

## 왜 필요한가

- 운영 기준은 한 번 저장하고 끝나는 값이 아니라, 이후 실제 운영 전 계속 다시 읽어야 한다.
- 저장된 guide가 source final decision과 연결되어야 나중에 왜 이 기준이 나왔는지 추적할 수 있다.
- Phase35 이후 live approval이나 monitoring tracker로 갈 때도 guide가 먼저 기준점이 된다.

## 구현한 내용

- `기록된 운영 가이드 확인` section을 추가했다.
- saved guide table에는 Guide ID, Source Decision, Source, Components, Weight Total, Guide Route, Handoff를 표시한다.
- 선택한 saved guide에서 component table과 operating policy, raw JSON을 확인할 수 있다.
- handoff route:
  - `POST_SELECTION_OPERATING_GUIDE_READY`

## 결과

Phase35 구현 완료 시점의 기본 흐름은
`백테스트 -> 후보 검토 -> 포트폴리오 제안 -> 최종 선정 -> 운영 가이드`까지 이어진다.

이 흐름은 실전 후보 포트폴리오를 찾고 운영 기준까지 정리하는 기본 제품 흐름이며,
아직 live approval, 주문 실행, 자동매매는 아니다.
