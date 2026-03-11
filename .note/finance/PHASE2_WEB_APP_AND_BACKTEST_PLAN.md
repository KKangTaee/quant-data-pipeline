# Phase 2 Web App And Backtest Plan

## 목적
이 문서는 현재 완성된 1차 내부용 수집 웹 앱 이후, `finance` 프로젝트를
실제 운영 가능한 데이터 수집 콘솔에서 백테스트 실행 플랫폼으로 확장하기 위한
2차 개발 계획을 단계별로 정리한 문서다.

이번 단계의 핵심 방향은 다음 두 가지다.

- 수집 운영을 더 안정적이고 반복 가능하게 만든다
- DB 기반 백테스트 실행으로 넘어갈 준비를 한다

---

## 현재 기준점

현재 1차 구현으로 이미 가능한 것:

- Streamlit 기반 내부 운영 웹 앱
- 개별 수집 실행
  - OHLCV
  - fundamentals
  - factors
  - asset profile
  - financial statements
- Core Market Data Pipeline 실행
- 입력 검증
- 실행 이력 저장
- 로그 / 실패 CSV 확인
- 대량 실행 경고
- 실행 중 전역 잠금
- OHLCV 대량 실행 진행률 표시

즉, 지금부터는 “기본 UI 만들기”가 아니라
“운영 고도화 + 백테스트 준비” 단계로 넘어간다.

---

## 2차 최종 목표

2차 종료 시점에 확보하고 싶은 상태:

1. 주기별 운영 파이프라인이 정의되어 있다
2. 버튼 실행과 미래 자동 실행이 같은 코드 경로를 쓴다
3. 설정값이 코드 하드코딩에서 일부 분리된다
4. 백테스트용 DB loader 계층이 정의된다
5. 최소 1개 전략을 웹에서 실행할 준비가 된다

---

## 전체 단계

1. 실행 이력 및 운영 상태 고도화
2. 운영 파이프라인 분리
3. 설정 외부화
4. 백테스트 데이터 조회 계층 설계 및 구현
5. 전략 실행 인터페이스 1차 구현

권장 구현 순서도 위 순서를 그대로 따른다.

---

## Phase 2-1. 실행 이력 및 운영 상태 고도화

### 목표
실행 이력을 나중에 다시 봤을 때,
무슨 입력으로 어떤 job을 돌렸고 어떤 결과가 나왔는지 재구성 가능하게 만든다.

### 작업 항목
- 실행 이력 JSONL에 입력 파라미터 저장
- 실행 이력에 symbol source 종류 저장
- 실패 메시지와 예외 메시지 구조 정리
- pipeline step별 결과를 더 쉽게 재활용할 수 있는 형태로 정리
- 필요하면 최근 성공/실패 통계 요약 추가

### 산출물
- 개선된 실행 이력 스키마
- 웹 UI에 표시 가능한 운영 요약 정보

### 검증 기준
- 이력 한 줄만 봐도:
  - 어떤 job인지
  - 어떤 입력값인지
  - 어떤 소스로 symbols를 불러왔는지
  - 얼마나 처리했는지
  - 실패가 있었는지
  를 알 수 있어야 한다

### 우선순위
- 높음

---

## Phase 2-2. 운영 파이프라인 분리

### 목표
수집 job을 “기술 함수”가 아니라 “운영 단위”로 다시 묶는다.

현재 Core Pipeline은 개발용으로는 충분하지만,
실제 운영에서는 daily / weekly / monthly 성격이 분리되어야 한다.

### 추천 파이프라인

#### 1. Daily Market Update
- 목적:
  - 가격 데이터 최신화
- 포함:
  - OHLCV Collection
- 기본 대상:
  - NYSE Stocks 또는 필터된 운영 유니버스

#### 2. Weekly Fundamental Refresh
- 목적:
  - 요약 fundamentals와 factors 갱신
- 포함:
  - Fundamentals Ingestion
  - Factor Calculation

#### 3. Extended Statement Refresh
- 목적:
  - 상세 financial statements 갱신
- 포함:
  - Financial Statement Ingestion

#### 4. Metadata Refresh
- 목적:
  - profile / universe 메타데이터 갱신
- 포함:
  - Asset Profile Collection

### 작업 항목
- 기존 wrapper를 조합한 운영용 pipeline wrapper 추가
- 웹 앱에서 운영 파이프라인 버튼 분리
- 각 pipeline의 목적 / 주기 / 선행조건 설명 추가

### 산출물
- daily / weekly / monthly 성격의 pipeline 정의
- pipeline 실행 wrapper
- 웹 버튼 또는 섹션

### 검증 기준
- 사용자가 “오늘은 뭘 눌러야 하지?”를 고민하지 않아야 한다
- 운영 목적별로 버튼이 분리되어 있어야 한다

### 우선순위
- 매우 높음

---

## Phase 2-3. 설정 외부화

### 목표
운영 관련 기본값을 코드 수정 없이 조정 가능한 구조로 만든다.

### 외부화 후보
- DB 접속정보
- symbol preset
- 기본 symbol source
- period / freq 기본값
- large-run warning threshold
- progress 표시 threshold
- chunk size

### 추천 방식

1차 권장:
- 프로젝트 내 설정 파일
- 예: `config/finance_web_app.toml`

나중 확장:
- 환경변수 + 설정 파일 혼합

### 작업 항목
- 현재 하드코딩된 상수 목록 정리
- 설정 로더 작성
- 웹 앱과 wrapper가 같은 설정을 보도록 연결

### 산출물
- 설정 파일 1개
- 설정 로더 모듈

### 검증 기준
- preset / threshold / 기본 period를 설정 파일만 수정해서 바꿀 수 있어야 한다

### 우선순위
- 높음

---

## Phase 2-4. 백테스트 데이터 조회 계층 설계 및 구현

### 목표
전략 코드가 DB 테이블을 직접 만지지 않고,
표준 loader 계층을 통해 입력 데이터를 가져가게 만든다.

이 단계가 실제로 “수집 도구”에서 “퀀트 실행 플랫폼”으로 넘어가는 핵심이다.

### 필요한 loader 종류

#### 1. Price Loader
- 대상:
  - `finance_price.nyse_price_history`
- 반환:
  - 심볼/날짜 기준 가격 DataFrame

#### 2. Fundamentals Loader
- 대상:
  - `finance_fundamental.nyse_fundamentals`
- 반환:
  - period_end 기준 fundamentals DataFrame

#### 3. Factor Loader
- 대상:
  - `finance_fundamental.nyse_factors`
- 반환:
  - factor matrix 형태 DataFrame

#### 4. Detailed Financial Statement Loader
- 대상:
  - `finance_fundamental.nyse_financial_statement_labels`
  - `finance_fundamental.nyse_financial_statement_values`
- 반환:
  - 계정 라벨 사전
  - period/filer 기준 상세 재무제표 long-form 또는 pivot DataFrame

### 왜 이 loader가 필요한가
- `nyse_fundamentals`와 `nyse_factors`는 현재 `yfinance` 기반 요약 데이터다
- 이 데이터는 현재 프로젝트 기준으로 과거 시계열 범위가 제한적이며,
  대략 최근 4년 수준까지만 안정적으로 확보되는 것으로 이해한다
- 예를 들어 지금이 2026년이면, 실질적으로 2022년 전후 이후 데이터 중심으로만 존재할 수 있다
- 반면 `nyse_financial_statement_labels`와 `nyse_financial_statement_values`는
  컬럼 구조는 덜 정제되어 있어도,
  더 이전 시기의 데이터와 더 세부적인 계정 수준 데이터를 확보하기 위한 원장 역할을 한다

즉 이 상세 재무제표 테이블들은
- 단순 보조 테이블이 아니라
- 장기 백테스트 확장과 세부 팩터 재계산의 원천 데이터 계층으로 봐야 한다

향후에는 아래 용도로 사용될 수 있다.
- 4년보다 더 긴 재무 시계열 확보
- 기존 `nyse_fundamentals`에 없는 세부 계정 기반 커스텀 팩터 계산
- 특정 회계 항목의 과거 추적
- point-in-time 기준 재무 데이터 재구성 고도화

#### 5. Universe Loader
- 대상:
  - `nyse_stock`
  - `nyse_etf`
  - `nyse_asset_profile`
- 반환:
  - 전략 실행 대상 심볼 집합

### 작업 항목
- loader 모듈 추가
- 입력 파라미터 표준화
  - symbols
  - universe source
  - start
  - end
  - freq
- point-in-time 주의사항을 API 설계에 반영

### 산출물
- `finance` 또는 `app` 하위 loader 모듈
- 표준 loader 함수 집합

### 검증 기준
- 전략 코드가 테이블명/SQL을 직접 몰라도 되도록 만들 것
- 같은 loader를 웹 UI와 전략 엔진 둘 다 사용할 수 있을 것

### 우선순위
- 매우 높음

---

## Phase 2-5. 전략 실행 인터페이스 1차 구현

### 목표
웹에서 최소 1개 전략을 실행하고 결과를 확인할 수 있는 첫 진입점을 만든다.

### 1차 범위 권장
- 전략 1개 또는 2개만 연결
- 예:
  - value factor ranking
  - quality factor ranking
- 입력:
  - universe source
  - 기간
  - rebalance frequency
  - top N
- 출력:
  - 누적 수익률
  - CAGR
  - MDD
  - 승률 또는 기간별 요약

### 작업 항목
- 웹 UI에 전략 실행 섹션 추가
- 기존 `finance` 전략 계층과 연결
- 결과 요약 표 / 그래프 추가

### 산출물
- 전략 실행 UI 초안
- 최소 1개 전략 실행 가능 상태

### 검증 기준
- 웹에서 전략 파라미터를 넣고 실행 가능해야 한다
- 결과가 재현 가능해야 한다

### 우선순위
- 중간

---

## 권장 실제 개발 순서

가장 현실적인 순서는 아래다.

1. Phase 2-2 운영 파이프라인 분리
2. Phase 2-1 실행 이력 고도화
3. Phase 2-3 설정 외부화
4. Phase 2-4 백테스트 loader 계층 구현
5. Phase 2-5 전략 실행 UI 1차

이 순서를 권장하는 이유:

- 지금 당장 운영 가치를 가장 많이 올리는 것은 pipeline 분리다
- 그 다음이 운영 추적성 확보다
- 백테스트 UI는 loader 계층 없이 들어가면 구조가 약해진다

---

## 다음 바로 시작할 작업

다음 실제 구현 시작점으로는 아래를 권장한다.

### 추천 시작 작업
- `Daily Market Update`
- `Weekly Fundamental Refresh`
- `Extended Statement Refresh`
- `Metadata Refresh`

이 4개 운영 파이프라인을 먼저 정의하고,
웹 앱에 버튼 단위로 분리한다.

### 이유
- 현재 앱은 기능별 버튼은 잘 되어 있다
- 하지만 운영 관점의 버튼 구조는 아직 약하다
- 이 단계를 먼저 해야 추후 자동화와 스케줄링도 자연스럽게 붙는다

---

## 완료 판정 기준

2차 계획 전체가 잘 진행되고 있는지 판단하는 기준:

- 운영자가 daily / weekly / monthly 성격의 작업을 명확히 구분해서 실행할 수 있는가
- 실행 기록만 보고도 무슨 입력으로 어떤 결과가 났는지 알 수 있는가
- 전략 실행 코드가 DB 세부 구현에 직접 의존하지 않는가
- 웹 UI가 데이터 수집 콘솔에서 전략 실행 콘솔로 자연스럽게 확장되는가

---

## 결론

2차의 본질은 UI를 화려하게 만드는 것이 아니라,
운영 파이프라인을 구조화하고 백테스트 입력 계층을 정리하는 것이다.

즉 다음 단계의 가장 중요한 질문은 이것이다.

- “어떤 기능을 더 넣을까?”가 아니라
- “운영 단위와 전략 실행 단위를 어떤 구조로 연결할까?”

현재 기준으로 가장 먼저 할 일은
운영 파이프라인을 daily / weekly / monthly 관점으로 재구성하는 것이다.
