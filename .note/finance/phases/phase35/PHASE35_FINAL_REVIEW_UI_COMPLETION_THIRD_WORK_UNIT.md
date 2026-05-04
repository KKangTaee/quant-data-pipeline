# Phase 35 Final Review UI Completion Third Work Unit

## 목적

세 번째 작업은 Final Review 안에서 최종 판단 완료 상태를 충분히 확인할 수 있게 UI를 보강하는 것이다.

## 쉽게 말하면

사용자가 final decision을 저장한 뒤,
저장된 기록에서 투자 가능 여부와 실행 경계를 바로 확인할 수 있어야 한다.

## 왜 필요한가

- 별도 후속 탭을 제거했기 때문에 Final Review의 saved decision review가 더 중요해졌다.
- 최종 선정과 실제 주문은 다르므로, `Live Approval / Order` disabled 경계가 계속 보여야 한다.
- 사용자는 최종 판단 route를 내부 코드가 아니라 쉬운 말로 읽어야 한다.

## 구현한 내용

- saved final decision table에 `투자 가능성`을 추가했다.
- route detail panel title을 `Final Review Status`로 읽게 했다.
- selected final decision detail에 아래 badge를 보여준다.
  - Decision
  - 투자 가능성
  - Source
  - Observation
  - Live Approval
  - Order
- `Post-Selection Guide 열기` 버튼을 제거했다.
- `Live Approval / Order` disabled button만 남겨 실행 경계를 분명히 했다.

## 결과

Final Review는 최종 판단 저장과 저장된 판단 확인을 모두 담당한다.
별도 후속 가이드 없이도 사용자가 최종 상태를 읽을 수 있다.
