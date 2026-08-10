# Overview 시장 심리 기간별 변화 3차 설계

## 목적

현재 `기간별 심리 경로`는 검증된 estimator가 없어서 1W·1M 모두 `검증 전 비공개`로 표시된다. 이 fail-closed 정책은 정상이나, 사용자는 같은 안내만 반복해서 보고 기간별로 실제 심리가 어떻게 변했는지 확인할 수 없다.

3차에서는 미래 확률 전망 대신 저장된 CNN·AAII 관측을 이용한 `기간별 심리 변화`를 제공한다. 사용자는 1W·1M 카드에서 두 심리 축의 시작값, 현재값, 변화량과 두 축의 관계가 유지됐는지 바뀌었는지를 확인한다.

## 제품 계약

- 이 영역은 미래 예측, 가격 전망, 매매 신호가 아니다.
- CNN과 AAII를 하나의 합성점수로 만들지 않는다.
- 1W는 CNN 최근 5개 관측 간격과 AAII 최근 1개 주간 관측 간격을 비교한다.
- 1M은 CNN 최근 20개 관측 간격과 AAII 최근 4개 주간 관측 간격을 비교한다.
- source별 발표 주기가 다르므로 각 metric에 실제 시작일과 종료일을 별도로 표시한다.
- 충분한 관측이 없으면 변화량을 임의 생성하지 않고 해당 metric을 `관측 부족`으로 표시한다.
- 기존 `outlook`의 estimator/validation gate는 유지한다. 검증된 전망이 없는 상태에서 확률을 공개하지 않는다.

## 화면 순서

기존 화면 순서를 다음처럼 바꾼다.

1. 종합 판정 Hero
2. CNN·AAII 현재 근거
3. CNN 고정 + AAII 전환 이력 그래프
4. 1W·1M `기간별 심리 변화`
5. 다음 관찰 조건
6. 방법·원시 근거 disclosure

## 기간 카드

각 카드는 다음을 제공한다.

- 기간 label: `1W / 최근 5거래일`, `1M / 최근 20거래일`
- 비교 기준: CNN 관측 간격과 AAII 주간 관측 간격
- CNN metric: 시작값, 현재값, 변화량, 실제 날짜 범위, 현재 상태
- AAII Spread metric: 시작값, 현재값, 변화량, 실제 날짜 범위, 현재 방향
- 관계 변화: 기간 시작의 두 축 관계와 현재 두 축 관계

기간 시작과 현재의 상위 관계와 두 축 방향이 모두 같으면 `이어짐`, 상위 관계가 달라지면 `A에서 B로 바뀜`으로 설명한다. 상위 관계가 같아도 CNN·AAII 방향 구성이 달라지면 `같은 관계 안에서 축 구성이 바뀜`으로 구분한다. 한 축이라도 시작값이 부족하면 관계 변화를 단정하지 않는다.

## 서비스 계약

`app/services/overview/sentiment.py`가 계산의 source of truth다.

- history는 날짜순으로 정렬하고 같은 series/date의 중복은 `collected_at` 최신 row 하나만 사용한다. 최신 version 값이 결측이면 이전 유효 version으로 후퇴하지 않는다.
- 시작·종료 날짜가 모두 유효하고 시작일이 종료일보다 빠를 때만 source 변화량을 공개한다.
- CNN은 `cnn_fear_greed_index`, AAII는 `aaii_bull_bear_spread`를 사용한다.
- 변화량은 `현재값 - 시작값`이며 CNN은 point, AAII Spread는 percentage point 단위다.
- current 관계는 기존 `_build_sentiment_cross_read` 계약을 재사용한다.
- 시작 관계도 같은 CNN bucket과 AAII `+10pp / -10pp` 규칙으로 계산한다.
- `period_changes.status`는 두 기간이 모두 정상일 때 `AVAILABLE`, 일부만 정상일 때 `PARTIAL`, 모두 부족할 때 `UNAVAILABLE`이다.

## Payload와 React 경계

`app/web/overview/sentiment_helpers.py`는 서비스 결과를 `period_changes`로 직렬화한다. `sentiment_react_workbench_v2` schema와 기존 refresh/reload action 경계는 바꾸지 않는다.

React는 계산을 재구현하지 않고 다음만 수행한다.

- `SentimentPeriodChangeSection`에서 1W·1M 카드를 렌더링한다.
- 양수/음수/보합을 표현하되 숫자와 상태 label을 항상 함께 표시한다.
- 관측 부족 metric은 빈 숫자 대신 설명을 표시한다.
- 기존 `SentimentOutlookSection`은 화면에서 제거한다.
- rolling reload 호환을 위해 payload의 legacy `outlook`은 당분간 유지할 수 있으나 화면에는 노출하지 않는다.

## 결측과 오류 처리

- 필요한 CNN 관측 수는 1W 6개, 1M 21개다.
- 필요한 AAII Spread 관측 수는 1W 2개, 1M 5개다.
- 한 source만 충분하면 그 metric은 표시하고 기간 상태는 `PARTIAL`이다.
- 두 source의 시작값이 모두 있어야 관계 변화를 표시한다.
- 값이 부족해도 현재 Hero, 이력 graph, 다음 관찰 조건은 숨기지 않는다.

## 제외 범위

- 신규 provider, DB schema, ingestion job
- 미래 수익률 target 또는 estimator
- 확률, episode count, baseline 대비 우위 공개
- monitoring, validation, trading signal

## 검증

- 서비스 regression으로 1W·1M lag, 단위, 날짜, 관계 전환, 결측을 검증한다.
- payload regression으로 service 결과가 React 계약에 보존되는지 검증한다.
- React source contract와 Vite production build를 검증한다.
- 실제 Streamlit desktop/420px Browser QA에서 카드, 날짜, 변화량, 관계 문장, overflow, console error를 확인한다.
