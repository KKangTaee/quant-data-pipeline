# Phase 35 Final Guide Preview UI Third Work Unit

## 목적

Phase35 세 번째 작업은 운영 전 지침을 저장하지 않고 화면에서 확인할 수 있는 UI를 만드는 것이다.

## 쉽게 말하면

최종 선정 후보를 고른 뒤,
사용자가 "이 후보는 투자 가능 후보로 볼 수 있는가, 언제 리밸런싱하고, 언제 줄이고, 언제 멈추고, 언제 다시 볼 것인가"를 확인한다.

## 왜 필요한가

- 실전 후보 포트폴리오는 선정 판단만으로 충분하지 않다.
- 리밸런싱 / 축소 / 중단 / 재검토 기준이 있어야 감정적 판단을 줄일 수 있다.
- 다만 Final Review에서 이미 최종 판단을 저장했으므로, 이 UI가 또 저장 버튼을 만들 필요는 없다.

## 구현한 내용

- `Backtest > Post-Selection Guide` workflow panel을 보정했다.
- preview 항목:
  - Capital Mode
  - Rebalancing Cadence
  - 자본 / 승인 경계
  - 리밸런싱 기준
  - 축소 기준
  - 중단 기준
  - 재검토 기준
  - 운영 메모
- action:
  - `추가 저장 없음` disabled action
- disabled action:
  - `Live Approval / Order`
- preview:
  - `최종 지침 Preview`

## 결과

운영 전 기준은 화면에서 확인하고,
최종 판단 원본은 Final Review의 final selection decision으로 유지한다.

Phase35는 새 `.jsonl` 파일을 만들지 않는다.
