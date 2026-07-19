# Design

## 범위

- `PortfolioMonitoringWorkbench.tsx`: pointer/focus 상태, guide line, active point, tooltip 렌더링
- `workbenchState.ts`: 가장 가까운 유효 관측치와 tooltip 위치를 계산하는 순수 함수
- `style.css`: hover 시각 표현과 모든 px 기반 font-size +1px
- 관련 React/Python 계약 테스트와 built static distribution

## hover 계약

- 좁은 점 자체가 아니라 차트 plot 전체를 투명 hit area로 사용한다.
- pointer x좌표와 가장 가까운, `total`이 존재하는 관측치를 선택한다.
- tooltip은 오른쪽 끝에서는 점의 왼쪽으로 전환하고 상하 plot 경계를 넘지 않는다.
- point focus는 동일한 active 상태를 사용해 키보드 접근성을 유지한다.

## 경계

- 차트 수치 계산, valuation, DB row, macro/diagnosis 판정은 바꾸지 않는다.
- tooltip은 주문·리밸런싱 신호가 아니라 저장된 portfolio value 관측치 확인 기능이다.
