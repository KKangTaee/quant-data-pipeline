# 경제사이클 자산별 정보 중복 제거·글자 크기 조정 설계

Status: Approved Direction
Last Updated: 2026-07-25

## 배경

`자산별 확인 포인트`의 금·달러 카드에서는 같은 문장이 서로 다른 위치에서 반복된다.

1. 카드 상단 `narrative`가 `현재 수준`과 `전망 여건`을 포함한다.
2. 바로 아래 `사이클 판단의 공통 경제 배경`이 같은 `economic_state.summary`를 다시 표시한다.
3. 금·달러에는 별도 `current_interpretation`이 없어 React가 `narrative`를 `현재 해석`에 다시 사용한다.

2026-07-25 실제 DB read model에서도 금·달러의 상단 문장 앞부분과
`economic_state.summary`가 완전히 같고 `current_interpretation`은 비어 있었다.

## 목표

- 공통 경제 배경은 카드마다 한 번만 표시한다.
- 금·달러의 상단 요약과 현재 해석은 해당 자산의 측정 경로·실제 가격·자료 한계에 집중한다.
- `자산별 확인 포인트` 영역의 모든 표시 글자를 기존보다 `1px` 크게 만든다.
- 데이터 계산, 확률, 방향 enum, 가격 기간, DB/provider 경계는 바꾸지 않는다.

## 검토한 방식

### A. 공통 경제 배경 블록만 숨김

React에서 금·달러의 `EconomicStateBlock`만 숨길 수 있다. 변경은 작지만 다른 자산
카드와 구조가 달라지고, 상단 요약과 `현재 해석`이 같은 `narrative`를 반복하는 문제는
남는다.

### B. 자산 고유 문구와 공통 경제 배경을 데이터에서 분리 — 채택

금·달러 context가 별도 `summary`와 `current_interpretation`을 제공한다.
`economic_state`는 기존 블록에서 한 번만 표시한다. React는 명시 필드를 우선 사용하고
legacy payload에만 기존 fallback을 유지한다.

장점은 문구의 역할이 payload부터 분명하고 Python 단위 테스트로 회귀를 막을 수 있다는
점이다. 사용자 승인 방향과도 일치한다.

### C. 모든 자산 카드의 문구 구조를 전면 재설계

채권·주식·원자재까지 summary/economic state/current interpretation을 새로 정의하면
일관성은 높일 수 있지만 이번에 확인된 실제 중복 범위를 넘는다. 별도 UX 과제로 둔다.

## 사용자 화면

### 금·달러 카드 순서

1. 카드 제목과 데이터 범위
2. 자산 고유 한 줄 요약
3. `사이클 판단의 공통 경제 배경`
4. `현재 움직임`
5. `함께 관찰된 경로`
6. `현재 해석`
7. `향후 1·2개월 확인 조건`

### 자산 고유 요약

공통 경제 상태 문장을 제외하고 다음만 요약한다.

- 금: 실질금리·달러·단기금리·위험회피 경로, 금 가격 방향, 인과 확정 금지
- 달러: 미국 명목·실질금리·위험회피 경로, 달러지수 방향, 해외 상대금리 결측,
  인과 확정 금지

### 현재 해석

상단 요약문 전체를 반복하지 않는다. 측정 경로, 실제 가격, 중요한 자료 한계를 각각
짧은 항목으로 제공한다. 공통 경제 배경 문장은 이 목록에 넣지 않는다.

### 글자 크기

React의 `자산별 확인 포인트` section에 전용 class를 두고 다음 표시 계층을 모두 기존보다
`1px` 크게 한다.

- section eyebrow, 제목, 보조 문구
- 자산 카드 제목·요약·coverage
- 공통 경제 배경 제목·본문·배지
- 현재 움직임·경로·해석·확인 조건의 제목·본문·수치·상태
- tooltip/mobile detail, 자료 부족·현재 데이터 범위 밖 문구
- 원자재 내부 자산 카드 문구

레이아웃 폭·padding·grid·색상·행간은 유지한다. 420px에서 줄바꿈과 가로 overflow를
다시 확인한다.

## 코드 경계

- `finance/economic_cycle_asset_pathways.py`
  - 공통 경제 상태를 포함하지 않는 금·달러 자산 고유 summary와 interpretation 생성
  - 기존 `economic_state`, pathway, price, limitation 값 유지
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
  - 명시적 summary/current interpretation 사용
  - 자산별 section class 추가
  - legacy fallback 보존
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
  - 자산별 section에 한정된 `+1px` typography
- `tests/test_economic_cycle_asset_pathways.py`
  - 공통 summary 비포함과 금·달러 고유 interpretation 계약
- `tests/test_market_context_economic_cycle.py`
  - React 구조와 scoped typography 계약

## 변경하지 않는 범위

- 경제사이클 factor·확률·publication gate
- `economic_state` 계산과 네 factor 문구
- 금·달러 가격·경로 산식 및 5/21/63거래일 기준
- DB schema, ingestion, loader, provider 호출
- 채권·주식·원자재의 정보 구조 전면 개편
- 가격 원인 추론, 수익률 예측, 매매 신호

## 오류와 호환성

- 새 summary/current interpretation이 없는 legacy payload는 기존 narrative fallback으로
  표시한다.
- 가격이나 경로가 부족하면 기존 `UNAVAILABLE`/coverage 의미를 유지하고 방향을 만들지
  않는다.
- common economic state는 데이터가 부족해도 기존 자료 부족 배지를 그대로 표시한다.

## 검증

- Python regression에서 금·달러 summary/current interpretation에
  `현재 수준:`·`전망 여건:`이 들어가지 않는지 확인한다.
- 공통 `economic_state.summary`와 기존 pathway/price enum이 불변인지 확인한다.
- React source contract에서 자산별 section class, fallback, scoped `+1px` 규칙을 확인한다.
- focused Python tests와 Vite production build를 실행한다.
- 실제 Streamlit을 desktop과 420px에서 확인하고 중복 문장, 줄바꿈, 가로 overflow,
  console warning/error를 점검한다.

## 완료 조건

- 금·달러에서 공통 경제 배경 문장이 한 번만 보인다.
- 상단 요약과 현재 해석이 같은 전체 문장을 반복하지 않는다.
- 금·달러 자산 고유 경로·가격·자료 한계는 손실 없이 읽을 수 있다.
- 자산별 확인 포인트의 모든 표시 글자가 기존보다 `1px` 크다.
- 기존 데이터·모델·provider 경계와 다른 화면의 typography는 바뀌지 않는다.
