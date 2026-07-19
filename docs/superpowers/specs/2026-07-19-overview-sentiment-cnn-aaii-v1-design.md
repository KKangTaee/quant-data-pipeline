# Overview Sentiment CNN·AAII 균형 개선 설계

## 목표

Overview의 심리 탭을 CNN 중심의 반복적인 정보 화면에서 다음 질문에 빠르게 답하는 판단 화면으로 바꾼다.

1. 시장 가격과 거래가 보여주는 심리는 공포인가, 탐욕인가?
2. 개인투자자 설문 심리는 낙관인가, 비관인가?
3. 두 축은 같은 방향인가, 엇갈리는가?
4. 현재 판단을 만든 근거와 앞으로 확인할 조건은 무엇인가?

1차에서는 CNN과 AAII 저장 데이터만 사용한다. 신규 공급자, 합성 심리지수, 1주·1개월 확률 예측은 추가하지 않는다.

## 제품 원칙

- CNN은 `시장 행동 심리`, AAII는 `개인투자자 인식 심리`로 정의한다.
- 두 축은 서로 다른 척도와 빈도를 가지므로 하나의 숫자로 합성하지 않는다.
- CNN 구성요소는 세 번째 독립 심리 축이 아니라 CNN headline의 내부 근거와 확신도를 설명한다.
- 첫 화면은 run, row, missing count가 아니라 현재 판단과 사용자가 확인할 다음 조건을 중심으로 구성한다.
- 원본 row와 갱신 세부 상태는 보존하되 접힌 상세 근거로 내린다.
- 현재 데이터로 검증할 수 없는 확률과 미래 수익률은 표시하지 않는다.

## 사용자 흐름

### 1. 문장형 현재 판단

Hero는 합성점수 대신 두 축을 함께 읽은 결론을 보여준다.

- 예: `시장 행동은 공포, 개인투자자 설문은 낙관 — 심리가 엇갈립니다.`
- phase badge는 `행동 공포 · 설문 낙관`처럼 두 방향을 그대로 표시한다.
- summary는 엇갈림의 의미와 현재 판단의 제한을 한두 문장으로 설명한다.
- 기준일과 새로고침 action은 compact metadata로 유지하고 별도 운영 진단 panel로 확장하지 않는다.

### 2. 동등한 두 축

Hero 아래에 같은 크기와 정보 밀도의 source card 두 개를 둔다.

#### CNN 시장 행동 카드

- 현재 Fear & Greed 점수와 상태
- 직전 관측 대비 변화
- 저장된 최근 이력 내 percentile과 범위
- 7개 구성요소의 공포·중립·탐욕 개수
- 내부 구성요소가 headline을 지지하는지, 혼합인지에 대한 한 줄 설명

#### AAII 개인투자자 설문 카드

- Bullish, Neutral, Bearish 비중
- Bull-Bear Spread와 낙관·중립·비관 상태
- 직전 주 대비 변화
- Bullish, Neutral, Bearish 각각의 장기평균 대비 차이
- 설문 응답이 어느 쪽으로 기울었는지에 대한 한 줄 설명

두 카드는 desktop에서 2열, 좁은 iframe과 mobile에서 1열로 배치한다.

### 3. 교차 해석

두 source card 아래에 하나의 cross-read panel을 둔다.

- CNN과 AAII가 같은 방향이면 `심리 일치`
- CNN과 AAII가 반대 방향이면 `뚜렷한 엇갈림`
- 한쪽이 중립이고 다른 한쪽이 방향성을 가지면 `부분 엇갈림`
- 둘 다 중립이면 `중립 일치`

panel은 `현재 판정`, `그 의미`, `다음 확인 조건`을 구분한다. CNN 구성요소 혼합 여부는 cross-read의 세 번째 투표가 아니라 CNN 판정의 내부 확신도 문장에만 반영한다.

### 4. 상세 근거

상세 근거는 중복 없이 두 영역으로 구성한다.

- CNN: 7개 구성요소를 한 번만 렌더링하고 각 항목의 점수, 상태, 무엇을 측정하는지, 현재 의미를 제공한다.
- AAII: 세 응답 비중을 장기평균과 나란히 비교하고 현재값과 평균 차이를 같은 카드 안에서 제공한다.

기존의 `방향별 CNN 그룹`, `CNN 구성요소 상세`, `CNN 구성요소 변화` 반복 block은 하나의 CNN evidence 영역으로 통합한다. 변화량은 각 구성요소 행의 보조 정보로 포함한다.

### 5. 그래프

서로 다른 단위와 빈도를 같은 y축에 올리지 않는다.

#### CNN 그래프

- 0~100 고정 y축
- 공포·중립·탐욕 해석 구간을 배경 band로 표시
- 일간 관측을 실제 날짜 간격으로 배치
- 현재값과 직전값을 tooltip에서 표시

#### AAII 응답 그래프

- Bullish, Neutral, Bearish 비중을 0~100% 축으로 표시
- 주간 관측만 연결
- tooltip에 세 비중과 기준일을 표시

#### AAII Spread 그래프

- Bull-Bear Spread를 독립된 pp 축으로 표시
- 0pp 기준선을 강조
- +10pp와 -10pp 판정선을 보조선으로 표시

그래프는 `CNN 행동`, `AAII 응답`, `AAII Spread` tab으로 전환한다. x좌표는 ordinal index가 아니라 observation date의 timestamp 비율로 계산한다.

## 판정 규칙

### CNN 방향

기존 CNN score bucket을 유지한다. source의 headline 점수와 rating을 우선 사용하고 구성요소 분포는 내부 근거로만 사용한다.

### AAII 방향

Bull-Bear Spread를 주 방향 판정으로 사용한다.

- spread가 `+10pp 이상`: `optimistic`
- spread가 `-10pp 이하`: `pessimistic`
- 그 사이: `neutral`
- spread 결측: `unavailable`이며 방향 판정을 보류

Bullish 38.0%, Neutral 31.5%, Bearish 30.5% 장기평균 대비 차이는 판정을 설명하는 근거다. 장기평균 차이가 spread 방향과 충돌하면 그 충돌을 설명하되 별도 방향 투표로 계산하지 않는다.

### 교차 판정

CNN의 `greed`는 AAII의 `optimistic`, CNN의 `fear`는 AAII의 `pessimistic`과 같은 방향으로 매핑한다.

| CNN | AAII | 결과 |
|---|---|---|
| greed | optimistic | 심리 일치 · 위험선호 |
| fear | pessimistic | 심리 일치 · 방어 우위 |
| greed | pessimistic | 뚜렷한 엇갈림 |
| fear | optimistic | 뚜렷한 엇갈림 |
| neutral | neutral | 중립 일치 |
| neutral | directional | 부분 엇갈림 |
| directional | neutral | 부분 엇갈림 |

한 source가 결측이면 종합 판정을 만들지 않고 `한 축만 확인 가능`으로 표시한다.

## Read-model과 파일 경계

### `app/services/overview/sentiment.py`

- CNN axis, AAII axis, cross-read를 만드는 deterministic helper를 둔다.
- 각 axis는 현재값, 직전값, 변화, 최근 범위, 방향, 설명, 근거를 반환한다.
- AAII 세 비중의 장기평균 차이와 history를 만든다.
- 사용자 문구와 판정은 service에서 만들고 React가 임의로 재판정하지 않게 한다.

### `app/web/overview/sentiment_helpers.py`

React payload schema를 `sentiment_react_workbench_v2`로 올린다.

- `summary`: 문장형 교차 판정과 기준일
- `axes.market_behavior`: CNN source card 계약
- `axes.investor_survey`: AAII source card 계약
- `cross_read`: 일치·엇갈림, 의미, 내부 확신도
- `evidence.cnn_components`: 통합된 CNN 상세 근거
- `evidence.aaii_comparison`: 세 응답과 장기평균 비교
- `charts.cnn`, `charts.aaii_responses`, `charts.aaii_spread`: 단위별 분리 series
- `watch_conditions`: 미래 예측이 아닌 확인 조건
- `raw_evidence`: 접힌 원본 row

기존 refresh/reload event contract와 Python dispatch boundary는 유지한다.

### React workbench

`SentimentWorkbench.tsx`는 v2 계약을 표현만 한다. 서비스에서 받은 방향·문장·tone을 다시 계산하지 않는다. 그래프의 날짜 좌표와 hover target 같은 표현 계산만 React가 담당한다.

`style.css`는 Market Context와 Futures Macro의 visual hierarchy를 따르되 기존 sentiment class namespace를 유지한다. source card, cross-read, evidence, charts, disclosure별 class를 분리한다.

## 결측과 오류 처리

- CNN과 AAII가 모두 없으면 기존 데이터 부족 화면과 refresh action을 유지한다.
- 한 source만 있으면 해당 source card는 정상 표시하고 다른 card는 `자료 없음` 상태로 표시한다.
- AAII 구성 비중 일부가 없으면 확보된 값만 표시하고 spread 판정이 불가능하면 중립으로 단정하지 않고 `판정 보류`로 표시한다.
- history가 2개 미만이면 변화와 선 그래프를 숨기고 `추이를 계산할 관측이 부족합니다`를 표시한다.
- stale warning은 현재 판단 옆 compact warning과 raw disclosure에만 표시한다.

## 접근성과 반응형

- tab button은 `role=tab`, `aria-selected`, 연결된 panel label을 제공한다.
- 색상만으로 방향을 표현하지 않고 모든 상태에 한국어 label을 함께 둔다.
- SVG에는 title/aria-label을 두고 tooltip이 없어도 최근값을 텍스트로 확인할 수 있게 한다.
- 420px viewport에서 horizontal overflow가 없어야 한다.
- raw table은 자체 scroll container 안에서만 가로 스크롤을 허용한다.

## 테스트 전략

### 서비스 회귀 테스트

- CNN fear + AAII spread +12pp는 `뚜렷한 엇갈림`이다.
- CNN greed + AAII spread +10pp 이상은 `심리 일치 · 위험선호`다.
- CNN fear + AAII spread -10pp 이하는 `심리 일치 · 방어 우위`다.
- 한 축 중립은 `부분 엇갈림`, 두 축 중립은 `중립 일치`다.
- AAII 장기평균 차이와 직전 주 변화가 정확히 계산된다.
- CNN 구성요소 혼합은 cross-read 방향을 바꾸지 않고 내부 확신도만 바꾼다.
- 한 source 또는 history가 부족한 경우 명시적 결측 상태를 반환한다.

### Payload 계약 테스트

- schema version과 v2 key가 고정된다.
- CNN·AAII source card가 같은 depth와 필수 field를 가진다.
- 세 그래프의 단위와 series가 섞이지 않는다.
- 기존 refresh/reload action id와 boundary가 유지된다.

### Frontend와 Browser QA

- TypeScript production build
- desktop에서 hero, 대칭 source card, cross-read, 세 그래프 확인
- 420px에서 1열 배치와 overflow 확인
- graph tab keyboard/click 전환과 tooltip 확인
- raw evidence가 기본 접힘인지 확인
- console error가 없는지 확인

## 범위 밖

- CFTC, Cboe, FRED 등 신규 데이터 수집
- CNN과 AAII를 합친 숫자형 종합점수
- 미래 시장 수익률 또는 심리의 1주·1개월 확률 예측
- DB schema와 ingestion job 변경
- 운영 진단 panel 또는 저장 row 중심 UI 추가
- 매수·매도 신호와 포트폴리오 action

## 전체 잠정 로드맵 연결

1. 이번 1차: CNN·AAII 판정, 균형 UI, 중복 제거, 그래프 분리
2. 2차: 장기 이력과 발표 당시 값의 축적·품질 점검
3. 3차: 예측 필요성이 유지될 때 CNN과 겹치지 않는 독립 데이터 후보 검토
4. 4차: point-in-time 검증 성능이 확인된 경우에만 1주·1개월 전망 제공

1차 완료는 2~4차 완료를 의미하지 않는다.
