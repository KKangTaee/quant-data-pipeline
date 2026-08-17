# Institutional Holdings Metric Clarity Design

Status: Approved Design — Written Spec Review
Last Updated: 2026-08-17

## Why This Change

Institutional Holdings의 분기 리뷰와 기관 보유 랭킹은 계산값 자체는 제공하지만, 화면의
레이블과 단위가 계산 의미를 충분히 설명하지 않는다.

- `기여 상위 / 기여 하위`의 숫자가 비중 변화인지, 종목 수익률인지, 포트폴리오 수익
  기여인지 구분하기 어렵다.
- 포트폴리오 기여는 수익률의 퍼센트포인트인데 현재 `%`로 표시된다.
- `기여 하위`는 현재 단순 오름차순이어서 모든 종목이 상승한 경우에도 양수 종목을
  손실 기여처럼 읽을 수 있다.
- 화면 하단의 13F 한계가 영어 문장과 여러 chip으로 중복되어 첫 화면을 방해한다.
- 기관 보유 랭킹의 `31.4B` 같은 값은 통화와 지표명이 없어 시가총액이나 거래량으로
  오해할 수 있다.

이번 개선은 계산식이나 데이터 수집 범위를 바꾸지 않고, 사용자가 값의 의미와 다음
해석을 즉시 이해하도록 표시 계약을 명확히 한다.

## Confirmed Meanings

### 포트폴리오 수익 기여

분기 리뷰의 종목별 기여는 다음 식을 사용한다.

```text
포트폴리오 수익 기여(%p) = 이전 보고 포트폴리오 비중(%) × 종목 기간 수익률(%) / 100
```

예를 들어 이전 보고 비중 20%인 종목의 기간 수익률이 +10%이면 해당 종목은 가정
포트폴리오 수익률에 `+2.0%p` 기여한다. 이는 비중 증가도, 종목 자체 수익률도 아니다.

### 기관 보유 랭킹 금액

랭킹의 금액은 같은 CUSIP을 보유한 기관들이 해당 보고 분기의 13F에 신고한
`보고 보유가액 합계`다.

- 시가총액이 아니다.
- 거래량이나 거래대금이 아니다.
- 현재 보유액이 아니라 지연 공개된 분기 말 보고값이다.
- 랭킹은 `보유 기관 수` 내림차순이 1차 기준이고, 기관 수가 같을 때
  `보고 보유가액 합계`가 2차 기준이다.
- 집계는 현재 loader 계약대로 put/call row를 제외하고 distinct CIK 기관 수와 같은
  CUSIP의 reported value 합계를 사용한다.

## Approved User Experience

### 1. 분기 리뷰 기여 영역

기존 `기여 상위 / 기여 하위`를 다음 두 의미로 분리한다.

- `수익 기여 상위`: `contribution_pct > 0`인 종목 중 큰 순서
- `손실 기여 상위`: `contribution_pct < 0`인 종목 중 작은 값부터, 즉 손실 영향이 큰 순서

양수 또는 음수 행이 없으면 반대 부호 행을 대신 채우지 않고 각각
`수익 기여 종목 없음`, `손실 기여 종목 없음`을 표시한다. 0 기여 행은 어느 목록에도
포함하지 않는다.

두 목록 위에는 다음 읽기 안내를 한 번만 둔다.

```text
포트폴리오 수익 기여 = 이전 보고 비중 × 종목 수익률
예: 비중 20% × 수익률 +10% = 포트폴리오 수익률 +2.0%p 기여
```

각 종목 행은 다음 세 지표를 명시한다.

```text
AAPL · Apple Inc.
이전 보고 비중 20.0% | 종목 수익률 +10.0% | 포트폴리오 기여 +2.0%p
```

분기 변화 table도 `기여도`를 `수익 기여(%p)`로 바꾸고 값에 `%p` 단위를 사용한다.
`이전 비중 / 현재 비중`과 `ADD / REDUCE`는 기존 보고 수량 기반 변화 의미를 유지한다.

### 2. 기관 보유 랭킹

랭킹 상단 설명은 정렬 기준과 금액 의미를 함께 설명한다.

```text
보유 기관 수가 많은 종목 순입니다. 금액은 해당 분기에 기관들이 13F로 보고한
보유가액 합계이며, 시가총액이나 거래량이 아닙니다.
```

각 row는 익명 숫자 대신 명시적 레이블을 사용한다.

```text
1  AAPL · Apple Inc.
   보유 기관 1,284개
   13F 보고 보유가액 합계 $31.4B
```

금액은 미국 달러임을 `$`로 표시한다. 기존 `B / M / K` compact formatting은 유지한다.
현재 분기 내 랭킹 의미만 명확히 하며, 과거 분기 간 절대 금액 비교 기능은 추가하지
않는다.

### 3. 13F 자료 해석 안내

분기 리뷰 아래의 영어 caveat와 페이지 하단의 영문 chip 묶음을 동시에 노출하지 않는다.
페이지 하단에 기본 접힘 상태인 `13F 자료 해석 시 주의` disclosure 하나만 둔다.

접힘 summary에는 `지연 공시 · 실시간 매매 신호 아님`을 표시하고, 펼쳤을 때 다음 세
항목을 한글로 제공한다.

1. 분기 종료 후 최대 45일 뒤 공개되는 지연 자료이며 실시간 매매 신호가 아니다.
2. 공매도, 현금, 일부 파생상품, 헤지, 수수료와 분기 중 매매는 반영되지 않는다.
3. 수정 신고, 비공개 처리, 원천 추출과 CUSIP-symbol 연결 상태에 따라 표시 내용이
   달라질 수 있다.

원천/ingestion의 영어 caveat 상수는 내부 source limitation 기록으로 유지할 수 있지만,
사용자 화면에는 localized compact disclosure만 투영한다.

## Architecture And Ownership

### Calculation service

`app/services/institutional_quarter_review.py`

- 기여 계산식과 covered-sleeve return 계산은 변경하지 않는다.
- `top_contributors`는 양수 기여만, `top_detractors`는 음수 기여만 제공한다.
- 정렬 방향과 최대 5개 계약을 focused test로 고정한다.
- 영문 quarter-review caveat를 사용자 화면에 직접 노출하지 않도록 localized 의미로
  정리하거나 presentation projection에서 흡수한다.

### Workbench read model

`app/services/institutional_portfolios.py`

- popularity row에 `$`가 포함된 명시적 `13F 보고 보유가액 합계` 표시값을 제공한다.
- title/subtitle/caveat는 랭킹이 기관 수 기준이고 금액은 13F 보고 합계임을 설명한다.
- 화면용 13F disclosure는 한글 summary와 세 개의 compact item으로 제공한다.
- 기존 raw source caveat와 수집/DB 계약은 변경하지 않는다.

### React presentation

`app/web/streamlit_components/institutional_portfolios_workbench/src/QuarterReviewPanel.tsx`

- percent와 percentage-point formatter를 분리한다.
- 기여 안내, 세 지표 row와 정확한 empty state를 표시한다.
- table의 수익률은 `%`, 포트폴리오 기여는 `%p`로 표시한다.
- 중복된 quarter-review 영문 note를 제거한다.

`app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`

- popularity row에 `보유 기관`과 `13F 보고 보유가액 합계` 레이블을 표시한다.
- 하단 caveat chip 목록을 semantic `details / summary` 한글 disclosure로 교체한다.

`app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`

- 기존 content-first surface와 맞는 compact metric row와 disclosure 스타일을 제공한다.
- 색상만으로 수익/손실을 구분하지 않고 제목, 부호와 레이블을 함께 사용한다.
- 모바일에서도 레이블과 값이 겹치지 않도록 row가 자연스럽게 wrap된다.

`app/web/streamlit_components/institutional_portfolios_workbench/component_static/`

- automated test와 production build가 통과한 뒤 tracked bundle을 갱신한다.

## Data Flow And Boundaries

```text
13F holding rows + stored adjusted prices
  -> Python contribution calculation / popularity aggregation
  -> semantic labels and localized disclosure in workbench payload
  -> React renders weight, return, %p contribution and reported-value meaning
```

- provider fetch, SEC refresh, DB schema와 저장값을 변경하지 않는다.
- portfolio return, contribution formula, coverage calculation과 ranking sort priority를
  변경하지 않는다.
- current market cap, current institutional ownership와 trading volume을 새로 수집하지 않는다.
- 13F를 현재 매매 의도나 추천 신호로 해석하지 않는다.

## Empty And Error Behavior

- 가격 coverage가 없는 종목은 기존처럼 기여 계산에서 제외하고 0으로 대체하지 않는다.
- 양수 기여가 없으면 `수익 기여 종목 없음`, 음수 기여가 없으면
  `손실 기여 종목 없음`을 표시한다.
- popularity 금액이 누락되면 `$0`으로 오해시키지 않고 `보고가액 확인 불가`로 표시한다.
- popularity가 아직 load되지 않은 상태의 수동 `기관 보유 랭킹 불러오기` 흐름은 유지한다.
- disclosure는 자료가 없다는 오류 패널이 아니라 해석 범위를 설명하는 보조 정보로 둔다.

## Verification Contract

### Automated tests

- Python: 기여 계산식이 `weight × return / 100`을 유지한다.
- Python: positive contributors와 negative detractors가 부호별로 분리되고 0은 제외된다.
- Python: popularity의 primary sort가 holder count이고 표시 금액이 dollar-labeled
  reported-value aggregate임을 검증한다.
- React: 기여 행에 `이전 보고 비중`, `종목 수익률`, `포트폴리오 기여`와 `%p`가 보인다.
- React: popularity row에 `보유 기관`, `13F 보고 보유가액 합계`와 `$`가 보인다.
- React/source contract: 영문 caveat chip 목록이 사라지고 한글 disclosure가 존재한다.
- focused Python suite, Vitest, TypeScript typecheck, Vite build와 `git diff --check`를 통과한다.

### Browser QA

- 분기 리뷰에서 양수/음수 기여 목록과 세 지표의 의미를 확인한다.
- 변화 table에서 수익률 `%`와 기여 `%p`가 구분되는지 확인한다.
- 기관 보유 랭킹에서 기관 수와 보고 보유가액 합계가 명시되는지 확인한다.
- 하단 안내가 기본 접힘이고 펼치면 한글 세 항목만 나타나는지 확인한다.
- desktop과 390px viewport에서 overflow, 잘림과 레이블 충돌이 없는지 확인한다.
- console error 0건을 확인하고 최종 QA screenshot 1장을 generated artifact로 남긴다.

## Delivery Roadmap

### 1차 — 의미 계약 고정

- 목적: contribution 부호 분리, `%p`와 reported-value semantic payload를 고정한다.
- 완료 조건: focused Python tests가 계산식과 표시 read model을 검증한다.

### 2차 — 화면 표현 개선

- 목적: 분기 리뷰, 랭킹과 하단 disclosure를 승인된 한국어 UI로 교체한다.
- 완료 조건: React tests, typecheck와 production build가 통과한다.

### 3차 — 실제 화면 검증과 문서 정렬

- 목적: desktop/mobile Browser QA와 durable flow/task closeout을 완료한다.
- 완료 조건: screenshot, console error 0, focused regression과 문서 상태가 정렬된다.

## Out Of Scope

- 실시간 기관 보유액 또는 현재 시가총액 계산
- 거래량/거래대금 데이터 추가
- 13F popularity 집계의 새로운 ranking mode
- 과거 분기 간 절대 보고가액 비교
- ingestion, refresh cadence, DB schema와 가격 provider 변경
- 추천, 주문, 자동매매 또는 현재 투자 의도 추론
