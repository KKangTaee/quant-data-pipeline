# Overview Sentiment Period Metric UI Polish Design

## Goal

Market Research > 심리의 1W·1M 기간 변화 카드에서 장식적인 source별 상단 컬러선을 제거하고, 각 기간의 차이를 실제 변화량 중심으로 즉시 읽을 수 있게 한다.

## Confirmed Interpretation

- 1W와 1M의 `end_value`가 같은 것은 정상이다. 두 기간 모두 source별 최신 관측을 종료점으로 사용한다.
- 기간별로 달라져야 하는 값은 `start_value`, `start_date`, `lag_observations`, `change`다.
- 현재 UI는 공통 `end_value`를 가장 큰 숫자로 표시해 두 기간이 같은 정보처럼 보이게 한다. 계산 문제가 아니라 presentation hierarchy 문제다.

## Approved UI

- CNN·AAII metric box의 source별 `border-top`을 제거한다.
- 두 metric box는 동일한 중립 border와 background를 사용한다.
- source 구분은 source명 왼쪽의 작은 원형 marker로만 표시한다.
  - CNN marker: 기존 warm brown
  - AAII marker: 기존 teal
- metric의 primary 숫자는 `change`로 표시한다.
  - 예: `+15.5pt`, `+25.4pt`
- 공통 최신값은 `현재 66.3pt`처럼 secondary 정보로 표시한다.
- 기존 source별 실제 날짜와 `start_value → end_value` 문장은 유지한다.
- 현재 상태 label과 두 축 관계 문장은 유지한다.

## Scope And Ownership

- React markup owner: `app/web/streamlit_components/sentiment_workbench/src/SentimentPeriodChangeSection.tsx`
- Visual owner: `app/web/streamlit_components/sentiment_workbench/src/style.css`
- Regression owner: `tests/test_service_contracts.py`
- Generated production bundle: `app/web/streamlit_components/sentiment_workbench/component_static/`
- Service와 payload 계약은 변경하지 않는다.

## Empty State

metric이 unavailable이면 기존 `관측 부족` 또는 fail-closed reason을 primary로 유지하고, 현재값은 제공된 경우에만 secondary로 표시한다. 변화량을 임의 생성하지 않는다.

## Verification

- source-contract test는 period metric에 source별 top border가 없고 marker 규칙이 있는지 확인한다.
- React source-contract test는 변화량이 primary, 현재값이 secondary인지 확인한다.
- Vite production build를 다시 생성한다.
- actual Streamlit Browser QA에서 1W·1M의 primary 변화량이 서로 다르게 보이고, source marker·날짜 범위·관계 문장이 유지되는지 확인한다.
- desktop과 420px에서 overflow와 stacking을 확인한다.

## Non-goals

- 1W·1M 계산식, observation lag, source별 최신 기준일 변경
- sentiment service 또는 payload schema 변경
- 미래 전망, 확률, estimator 추가
- 다른 Market Research surface의 카드 스타일 일괄 개편
