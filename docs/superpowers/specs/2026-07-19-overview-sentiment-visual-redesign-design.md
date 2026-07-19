# Overview 시장 심리 시각 개편 설계

## 목적

기존 CNN·AAII 두 축 판정과 데이터 계약은 유지하면서 Overview의 시장 심리 화면을 Market Context·Futures Macro와 같은 서사형 판단 화면으로 개편한다.

사용자는 한 화면에서 다음을 끝낼 수 있어야 한다.

1. 현재 시장 행동과 개인투자자 인식이 같은 방향인지 엇갈리는지 파악한다.
2. CNN과 AAII의 현재값과 판정 근거를 같은 깊이로 확인한다.
3. 과거 관측의 꺾임과 심리 전환 시점을 원본 관측값 기준으로 읽는다.
4. 검증된 경우에만 1주·1개월 조건부 전망을 확인하고, 검증이 부족하면 다음 관찰 조건으로 전환한다.

이 설계는 기존 `sentiment_react_workbench_v2`의 판정 규칙을 바꾸지 않는다. CNN은 시장 행동, AAII는 개인투자자 설문이며 두 값을 하나의 합성점수로 만들지 않는다.

## 승인된 화면 순서

화면은 다음 순서로 구성한다.

1. 종합 판정 Hero
2. CNN·AAII 현재 근거
3. 과거 그래프
4. 1W·1M 조건부 전망
5. 다음 관찰 조건
6. 방법·원시 근거 disclosure

첫 화면의 주인공은 운영 상태나 저장 row가 아니라 종합 판정 문장이다.

## 1. 종합 판정 Hero

Hero는 Market Context·Futures Macro와 같은 큰 제목, 여유 있는 패딩, 절제된 gradient를 사용한다.

- eyebrow: `Market psychology · cross read`
- headline 예시: `시장 행동은 공포지만, 개인투자자의 기대는 낙관적입니다.`
- transition 문장: 두 심리 축이 같은 방향인지 엇갈리는지 설명한다.
- summary: 현재 해석과 단정할 수 없는 범위를 설명한다.
- 우측에는 CNN과 AAII 현재 판정을 작은 읽기 블록으로 배치한다.
- 하단 metadata에는 각 기준일, 합성점수 없음, 매수·매도 신호 아님을 표시한다.
- refresh와 reload action은 Hero 상단의 compact action으로 유지한다.

별도의 cross-read 카드를 다시 만들지 않는다. 종합 해석은 Hero에서 한 번만 설명한다.

## 2. CNN·AAII 현재 근거

Hero 아래에 같은 너비와 정보 밀도의 source box 두 개를 둔다.

### CNN 시장 행동

- Fear & Greed 현재값과 상태
- 직전 관측 대비 변화
- 탐욕·중립·공포 구성요소 수
- 7개 구성요소가 현재 headline을 얼마나 지지하는지 한 문장

### AAII 투자자 설문

- Bull–Bear Spread 현재값과 낙관·중립·비관 상태
- 직전 주 대비 변화
- Bullish·Neutral·Bearish 현재 비율
- 장기평균 및 최근 관측 범위와 비교한 한 문장

### box 장식 규칙

- box 상단의 갈색·녹청색 라운드 선은 사용하지 않는다.
- 상단 선은 출처를 구분하는 장식 외의 기능이 없으므로 제거한다.
- 출처는 label, 값, 그래프 색, 상태 badge로 구분한다.
- box border와 radius는 Market Context·Futures Macro의 중립 surface 문법을 따른다.

## 3. 색상 체계

출처색과 상태색을 분리한다.

- CNN 고정 출처색: warm brown 계열
- AAII 고정 출처색: teal 계열
- neutral 구조: blue-gray 계열
- fear·optimistic 같은 상태: 작은 badge, dot, 문구로 표시

출처색은 장기간 고정한다. 현재 상태가 바뀌어도 CNN과 AAII 그래프 색은 바뀌지 않는다. 색상만으로 의미를 전달하지 않고 label과 선 형태를 함께 사용한다.

AAII 응답 내부 series는 다음처럼 구분한다.

- Bullish: AAII teal 실선
- Neutral: neutral gray 파선
- Bearish: muted berry 점선

## 4. 과거 그래프

화면에는 동시에 두 개의 graph panel만 표시한다.

### CNN 고정 panel

- CNN Fear & Greed 그래프는 항상 표시한다.
- y축은 0~100으로 고정한다.
- 공포·중립·탐욕 band는 옅은 배경으로 표시한다.
- 현재값과 판정 label을 마지막 관측점에 직접 표시한다.
- 최근 관측 수와 현재값을 panel header에 표시한다.

### AAII 전환 panel

AAII는 한 panel 안에서 다음 두 tab을 전환한다.

1. `AAII 응답` — 기본 선택
2. `AAII Spread`

`AAII 응답`은 Bullish·Neutral·Bearish 비율을 0~100% 축에 표시한다. `AAII Spread`는 독립된 percentage-point 축을 사용하고 0pp 및 ±10pp 판정선을 표시한다.

두 panel은 desktop에서 같은 폭과 같은 중간 높이를 사용한다. 기존 compact 시안보다 plot 높이를 늘리되, 첨부된 기존 대형 chart처럼 한 graph가 viewport 전체를 점유하지 않게 한다. mobile에서는 plot 높이를 줄이고 tab control을 header 아래로 감싼다.

### 선 연결 규칙

모든 graph는 원본 관측값 사이를 직선으로 연결한다.

- spline, bezier, curve smoothing을 사용하지 않는다.
- CNN 일간, AAII 주간 관측의 실제 날짜 간격을 x좌표에 반영한다.
- 선형 보간은 시각적 연결에만 사용하며 중간 날짜의 값을 새 관측으로 만들지 않는다.
- hover 시 가장 가까운 실제 관측점의 날짜와 원본 값을 표시한다.
- CNN hover는 score와 상태를 표시한다.
- AAII 응답 hover는 세 응답 비율을 함께 표시한다.
- AAII Spread hover는 spread와 판정 구간을 표시한다.

## 5. 1W·1M 조건부 전망

전망은 Futures Macro의 기간 카드 문법을 사용한다.

- 1W: 다음 5거래일
- 1M: 다음 20거래일
- 각 기간은 독립 card다.
- card는 우세 경로, 경로별 확률, 표본 수, 기준 확률 대비 차이, 검증 상태를 표시한다.
- 검증 상태는 `VERIFIED`, `PROVISIONAL`, `UNAVAILABLE` 중 하나다.

가능한 경로는 현재 두 축의 관계를 기준으로 정의한다.

- 엇갈림 유지
- CNN 공포 완화 또는 탐욕 약화
- AAII 낙관 후퇴 또는 비관 완화

확률은 point-in-time 유사 구간과 시계열 분리 검증을 통과했을 때만 표시한다. 검증 기준을 충족하지 못하면 임의 확률을 만들지 않고 `통계적 판단 불가`와 다음 관찰 조건을 표시한다.

시각 mockup의 확률은 layout 검토용 데모였으며 production 값으로 사용하지 않는다.

### 단계 경계

이번 시각 개편은 전망 card의 화면 계약과 unavailable 상태를 구현할 수 있다. 실제 확률 산출기는 장기 이력 품질과 point-in-time 검증을 완료한 별도 차수에서 제공한다. 검증된 estimator가 없으면 두 card 모두 확률을 숨기거나 `UNAVAILABLE`로 표시한다.

## 6. 다음 관찰 조건과 상세 근거

전망 가능 여부와 관계없이 다음 세 경로를 제공한다.

- confirm: CNN 반등과 AAII 낙관 유지
- reverse: AAII 낙관의 빠른 후퇴
- persist: 두 축 괴리 지속

방법, 표본, 검증 기준, 원시 관측값, 출처 기준은 기본 접힘 disclosure로 둔다. refresh job, 저장 row, raw status는 첫 화면에 독립 panel로 만들지 않는다.

## 컴포넌트 경계

### `app/services/overview/sentiment.py`

- CNN·AAII 방향과 교차 판정의 source of truth를 유지한다.
- React가 방향을 재계산하지 않도록 문장과 상태를 반환한다.
- 조건부 전망이 연결되면 기간별 status, probabilities, baseline, episode count, validation evidence를 반환한다.
- 검증된 전망이 없으면 명시적인 unavailable payload를 반환한다.

### `app/web/overview/sentiment_helpers.py`

- 기존 v2 payload를 visual redesign contract로 변환한다.
- graph는 `cnn`, `aaii_responses`, `aaii_spread`의 독립 series를 유지한다.
- optional `outlook.horizons`는 1W·1M card state를 제공한다.
- refresh/reload action id와 `python_dispatch_only` boundary를 유지한다.

### React workbench

기능을 다음 단위로 분리한다.

- `SentimentHero`
- `CurrentEvidenceSection`
- `SentimentHistorySection`
- `AaiiHistoryTabs`
- `SentimentOutlookSection`
- `WatchConditionsSection`
- `SentimentEvidenceDisclosure`

root component는 section 순서와 action dispatch만 담당한다. graph hover와 tab selection은 presentation state이며 Python round trip을 만들지 않는다.

## 결측과 오류 처리

- CNN과 AAII가 모두 없으면 데이터 부족 설명과 refresh action만 표시한다.
- 한 source만 있으면 Hero는 `한 축만 확인 가능`으로 표시하고 확보된 source box만 정상값을 보여준다.
- CNN history가 2개 미만이면 CNN panel에 관측 부족 상태를 표시한다.
- AAII 응답 또는 Spread history가 2개 미만이면 해당 tab에만 관측 부족 상태를 표시한다.
- 한 AAII tab의 결측이 다른 tab의 정상 graph를 숨기지 않는다.
- 전망 estimator 또는 검증 evidence가 없으면 확률을 렌더링하지 않는다.
- stale warning은 Hero metadata와 disclosure 안에서만 보조적으로 표시한다.

## 접근성과 반응형

- AAII tab은 `role=tab`, `aria-selected`, `aria-controls`, 연결된 `tabpanel`을 제공한다.
- keyboard focus와 좌우 이동 또는 표준 tab 이동으로 두 view를 전환할 수 있어야 한다.
- SVG마다 title 또는 aria-label을 제공한다.
- 최신값은 tooltip 없이도 header와 마지막 관측점 label에서 확인할 수 있어야 한다.
- 모든 상태는 색과 함께 한국어 label을 표시한다.
- 420px viewport에서 horizontal overflow가 없어야 한다.
- raw table만 자체 scroll container를 허용한다.

## 테스트와 QA

### 서비스·payload

- 기존 CNN·AAII 판정 matrix와 +10pp/-10pp 경계를 회귀 검증한다.
- 세 history series의 단위와 관측 날짜를 섞지 않는다.
- 전망 status가 unavailable이면 probability field가 비어 있거나 렌더링 금지 상태인지 검증한다.
- demo probability가 production payload에 존재하지 않는지 검증한다.

### React

- 종합 Hero가 source box보다 먼저 렌더링된다.
- CNN graph panel은 항상 보인다.
- AAII panel은 하나만 보이고 응답 tab이 기본값이다.
- 응답과 Spread tab 전환 시 panel 높이와 layout이 불필요하게 흔들리지 않는다.
- graph path가 spline command를 사용하지 않고 원본 관측점을 선형 연결한다.
- source box 상단에 colored rail이 렌더링되지 않는다.
- 기간 card는 verified/provisional/unavailable 상태를 구분한다.

### Browser QA

- desktop과 420px에서 Hero, source box, 두 graph panel, 기간 card, 관찰 조건을 확인한다.
- AAII tab click과 keyboard 전환을 확인한다.
- CNN·AAII hover가 실제 날짜와 값을 보여주는지 확인한다.
- graph 꺾임, 기준선, 마지막 값 label이 겹치거나 잘리지 않는지 확인한다.
- horizontal overflow와 console error가 0인지 확인한다.

## 범위 밖

- CNN·AAII 숫자형 합성점수
- 곡선 smoothing 또는 가상 중간 관측 생성
- 검증되지 않은 1W·1M 확률
- 신규 provider, DB schema, ingestion job
- refresh job 결과나 저장 row를 주인공으로 하는 운영 panel
- 매수·매도 신호와 포트폴리오 action

## 완료 조건

- Hero에서 현재 교차 판정을 한 번만 설명한다.
- CNN과 AAII current evidence가 균형 있게 보인다.
- source box 상단 colored rail이 없다.
- 화면에는 CNN graph와 AAII graph 두 개만 동시에 보인다.
- AAII 응답과 Spread가 한 panel에서 전환된다.
- 모든 시계열이 원본 관측점 사이의 직선으로 표시된다.
- 검증되지 않은 전망 확률을 만들지 않는다.
- desktop·420px Browser QA와 관련 service/frontend regression이 통과한다.

## 전체 로드맵 연결

1. 완료: CNN·AAII 두 축 판정과 v2 payload
2. 현재: 승인된 시각 개편과 graph interaction polish
3. 다음: 장기 이력·발표 당시 값 축적과 품질 점검
4. 이후: point-in-time 검증을 통과한 경우에만 1W·1M 확률 산출기 연결

현재 시각 개편 완료는 장기 이력과 전망 산출기 완료를 의미하지 않는다.
