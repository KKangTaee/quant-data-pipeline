# Phase 35 Operating Guide UI Third Work Unit

## 목적

Phase35 세 번째 작업은 운영 가이드를 실제로 작성하고 기록할 수 있는 UI를 만드는 것이다.

## 쉽게 말하면

최종 선정 후보를 고른 뒤,
사용자가 "언제 리밸런싱하고, 언제 줄이고, 언제 멈추고, 언제 다시 볼지"를 화면에서 정리한다.

## 왜 필요한가

- 실전 후보 포트폴리오는 선정 판단만으로 충분하지 않다.
- 리밸런싱 / 축소 / 중단 / 재검토 기준이 있어야 감정적 판단을 줄일 수 있다.
- 이 UI는 주문 버튼이 아니라 운영 기준표 작성 화면이어야 한다.

## 구현한 내용

- `Backtest > Post-Selection Guide` workflow panel을 추가했다.
- 입력 항목:
  - Guide ID
  - Capital Mode
  - Rebalancing Cadence
  - 자본 / 승인 경계
  - 리밸런싱 기준
  - 축소 기준
  - 중단 기준
  - 재검토 기준
  - 운영 메모
- action:
  - `운영 가이드 기록`
- disabled action:
  - `Live Approval / Order`

## 결과

운영 기준이 준비되면 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`에 append-only로 기록된다.
이 기록도 live approval이나 broker order가 아니다.
