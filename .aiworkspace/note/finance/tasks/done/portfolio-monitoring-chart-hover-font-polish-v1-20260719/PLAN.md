# Portfolio Monitoring Chart Hover / Font Polish V1

## 이걸 하는 이유?

종합 가치곡선의 날짜별 값을 마우스로 바로 확인할 수 없고, Portfolio Monitoring React 화면의 글자가 전반적으로 작아 실제 모니터링 시 읽기 부담이 있다.

## 목표

- 가치곡선 전체 영역에서 가장 가까운 관측일의 날짜와 평가 금액을 hover/focus로 표시한다.
- Portfolio Monitoring React 탭의 명시적 `font-size`를 기존보다 정확히 `1px` 높인다.
- 기존 데이터 계약, DB, 등록 workflow는 변경하지 않는다.

## 전체 roadmap

1. hover / font 계약을 회귀 테스트로 고정한다.
2. React SVG tooltip과 탭 전역 +1px 폰트 변경을 구현한다.
3. 테스트, 빌드, desktop Browser QA로 실제 화면을 확인한다.

## 완료 조건

- 차트에서 날짜·총 평가금액 tooltip과 강조점이 보인다.
- 키보드 focus에서도 같은 값이 노출된다.
- 탭 stylesheet의 모든 px 기반 `font-size`가 정확히 1px 증가한다.
- React/Python 계약 테스트, typecheck, production build, Browser QA가 통과한다.
