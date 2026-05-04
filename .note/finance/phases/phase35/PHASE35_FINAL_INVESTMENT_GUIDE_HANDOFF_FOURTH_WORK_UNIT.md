# Phase 35 Final Investment Guide Handoff Fourth Work Unit

## 목적

Phase35 네 번째 작업은 반복 저장 UX를 제거하고,
기본 포트폴리오 선정 흐름이 어디까지 완성됐는지 확인하는 것이다.

## 쉽게 말하면

운영 가이드를 또 저장하는 대신,
"최종 판단 기록과 운영 전 기준이 한 화면에서 연결되어 보이는가"를 확인한다.

## 왜 필요한가

- 저장 버튼이 phase마다 반복되면 사용자는 무엇이 원본 판단인지 헷갈린다.
- Final Review의 final decision이 원본 기록이고, Phase35는 그 기록을 읽는 마지막 확인 화면이어야 한다.
- Phase35 이후 live approval이나 monitoring tracker로 가더라도, 먼저 실행 경계가 선명해야 한다.

## 구현한 내용

- `기록된 운영 가이드 확인` section을 제거했다.
- saved guide table과 saved guide JSON review를 제거했다.
- `추가 저장 없음` disabled action을 추가했다.
- preview JSON에 `preview_only = true`, `live_approval = false`, `order_instruction = false`가 보이게 했다.
- handoff route:
  - `FINAL_INVESTMENT_GUIDE_READY`

## 결과

Phase35 구현 완료 시점의 기본 흐름은
`백테스트 -> 후보 검토 -> 포트폴리오 제안 -> 최종 선정 -> 최종 투자 지침 확인`까지 이어진다.

이 흐름은 실전 후보 포트폴리오를 찾고 운영 전 기준까지 확인하는 기본 제품 흐름이며,
아직 live approval, 주문 실행, 자동매매는 아니다.
