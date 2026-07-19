# Futures Macro Asset Outlook Layout Fix Design

## 이걸 하는 이유?

`자산별 확인 포인트`의 각 미래 행은 `기간 / 자산별 방향 / 전체 전망 상태`를 한 줄의 세 열로 배치한다. `전체 전망 · PROVISIONAL` 문구가 추가된 뒤 다섯 열 카드의 제한된 너비에서 상태 badge가 대부분의 공간을 차지했고, `우위 미확인`과 `상방 우세`가 글자 단위로 줄바꿈되는 회귀가 발생했다.

전체 전망 상태는 자산마다 독립적으로 계산한 품질 상태가 아니다. 같은 5D 또는 20D 조건부 체제 전망의 publication status를 모든 자산 보조 경로가 공유한다. 따라서 각 카드에 같은 badge를 반복하는 것보다 섹션이 horizon별 전체 상태를 한 번 소유하는 편이 의미와 레이아웃 모두 정확하다.

## 확인된 현재 의미

- `PROVISIONAL`은 정상 스펙이다. 계산은 가능하지만 확률과 경로의 시간순 검증 기준을 모두 충족하지 못한 미래 분포다.
- `우위 미확인`은 자료 부족이나 전체 상태 복제가 아니다. 자산 family의 과거 유사 episode 향후 중앙값이 표준화 기준 `-0.25 < z < +0.25`일 때 표시한다.
- 실제 2026-07-17 snapshot의 5D 중앙값은 다섯 family 모두 중립 구간이다. 20D는 주식 위험선호만 `+0.482`로 `상방 우세`이고 나머지는 중립 구간이다.

## 검토한 접근

### A. 섹션이 전체 전망 상태를 소유 — 채택

- 섹션 heading 아래 또는 우측 status rail에 `다음 5D 전체 전망 · PROVISIONAL`, `다음 20D 전체 전망 · PROVISIONAL`을 한 번씩 표시한다.
- 자산 카드의 미래 행은 `다음 5D / 우위 미확인`, `다음 20D / 상방 우세`처럼 자산별 방향만 표시한다.
- 5D와 20D 상태가 나중에 달라져도 각 horizon badge는 독립적으로 표시한다.

의미의 소유자가 정확하고, 반복이 줄며, 카드 방향 문구가 충분한 너비를 확보한다.

### B. 카드마다 badge를 다음 줄로 이동 — 제외

줄바꿈 회귀는 해결하지만 같은 전체 상태를 카드마다 열 번 반복하고 카드 높이를 불필요하게 늘린다.

### C. 카드 badge를 `PROVISIONAL`로 축약 — 제외

폭은 줄지만 status가 자산별 검증인지 전체 체제 검증인지 다시 모호해진다.

## UI 계약

### 섹션 상태 rail

- `자산별 확인 포인트` heading 영역에 두 horizon 상태를 함께 표시한다.
- 표시 문구는 영어 상태값을 유지한다: `5D 전체 전망 · PROVISIONAL`, `20D 전체 전망 · PROVISIONAL`.
- `VERIFIED`, `PROVISIONAL`, `UNAVAILABLE`별 기존 badge 색상 의미를 유지한다.
- 좁은 화면에서는 두 badge가 자연스럽게 다음 줄로 wrap되며 화면 가로 overflow를 만들지 않는다.

### 자산 카드

- 카드 header의 `관측 완료 / 일부 관측 / 관측 불가`는 유지한다.
- 1D / 5D / 20D 현재 관측 블록은 변경하지 않는다.
- 미래 행은 두 열 `기간 / 자산별 방향`만 사용한다.
- 방향 문구는 글자 단위로 깨지지 않게 한 줄을 우선 보장한다.
- `우위 미확인`, `상방 우세`, `하방 우세`, `검증 부족`의 계산 및 문구는 변경하지 않는다.

## 데이터와 상태 계약

- React payload의 `five_day_status`, `twenty_day_status`는 그대로 사용한다.
- 섹션 status rail은 첫 pathway에서 두 horizon status를 읽는다. pathway가 없으면 rail을 표시하지 않는다.
- 현재/미래 상태 분리, 자산 median threshold `±0.25`, 5D·20D publication gate, 10년 snapshot 계약은 변경하지 않는다.
- 이번 수정은 React 구조와 CSS 배치만 바꾸며 Python service, DB, provider, materialization을 수정하지 않는다.

## 파일 범위

- `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- `tests/test_service_contracts.py`
- `app/web/streamlit_components/futures_macro_workbench/component_static/`
- 기존 Futures Macro active task의 closeout 문서

## 검증 계약

1. source contract는 섹션 status rail에 5D·20D 전체 전망 상태가 각각 한 번만 존재하도록 요구한다.
2. 카드의 미래 행에는 status badge가 없고 기간과 자산별 방향만 남는다.
3. 현재 관측 status와 payload의 future status 필드는 계속 유지된다.
4. focused RED/GREEN contract, 기존 Futures Macro regression, Vite production build를 통과한다.
5. 실제 desktop에서 `우위 미확인 / 상방 우세`가 글자 단위로 줄바꿈되지 않는다.
6. 420px에서도 status rail과 카드가 가로 overflow를 만들지 않고 browser console error가 없다.

## 제외 범위

- `PROVISIONAL`을 다른 상태로 승격하거나 한글화
- `우위 미확인` threshold 또는 계산식 변경
- 자산별 독립 publication gate 추가
- 확률·경로 모델, DB schema, provider, ingestion 변경
- 다른 Overview 섹션의 UI 재설계
