# 미국 인플레이션·FOMC 정책·국채 저항선 경로 분석 설계

Status: Approved
Approved: 2026-08-02
Scope: `finance` package and Finance Streamlit `Market Research > 경제 사이클`

## 이걸 하는 이유?

사용자는 다음과 같은 투자자 관점의 역산 과정을 반복 가능하고 검증 가능한 기능으로 만들고 싶다.

```text
10년물의 중요한 전고점·저항선
  -> 그 구간에 도달할 수 있는 정책금리 경로
  -> 그 정책 경로를 정당화할 수 있는 Core PCE 경로
  -> 남은 달에 허용되거나 필요한 월별 Core PCE
  -> 다음 물가 발표 전에 준비할 조건
  -> 채권·주식시장 조건부 스트레스
```

이 사고방식은 유효한 분석 출발점이지만, `10년물 4.7%`, `Core PCE 0.4% 한 번`,
`2~3회 인상`을 고정된 인과관계로 사용하면 오판할 수 있다. 이 설계는 사용자의 원래
질문 순서를 보존하면서 다음을 보강한다.

- 단일 숫자 대신 확률분포를 사용한다.
- `4.7%`를 영구 기준이 아니라 시점별 동적 저항 후보로 바꾼다.
- 점도표와 물가 전망의 익명 분포를 개인별로 임의 연결하지 않는다.
- 월별 PCE를 단순 합산하지 않고 지수 수준에서 연말 `Q4/Q4` 경로를 계산한다.
- 10년물 상승을 정책 기대, 실질금리, 기대인플레이션, 기간 프리미엄으로 분해한다.
- 기존 경제 사이클 확률을 재사용하지 않고, 침체는 원자료 기반 신규 모델로 격리한다.
- 모든 예측은 point-in-time 백테스트와 공개 게이트를 통과한 경우에만 숫자 확률로 노출한다.

## 승인된 결정

- 분석 대상은 미국으로 한정한다.
- 엔진은 해석 가능한 규칙·경제 관계와 통계 모델을 결합한 혼합형을 사용한다.
- 인플레이션은 연말 Core PCE 연속 확률분포를 우선 결과로 하고 다섯 상태를 파생한다.
- 순방향 분석과 10년물 목표에서 출발하는 역산 분석을 모두 제공한다.
- 국채 저항선은 단기·경기·구조 기간의 전고점 군집에서 동적으로 계산한다.
- 자동 추천 기준과 사용자가 저장한 기준을 명확히 구분한다.
- 금리 인상 횟수와 10년물 변화를 기계적으로 `25bp 대 25bp`로 연결하지 않는다.
- SEP의 금리 점과 물가 전망은 분포 단위로만 사용하고 개인별 대응관계를 주장하지 않는다.
- 현재 구현 중인 기존 경제 사이클 확률과 그 현재·1개월·2개월 전망은 이 기능의 입력,
  보조값, fallback 또는 검증 정답으로 사용하지 않는다.
- 침체 모델은 별도 원자료와 별도 검증 계약으로 새로 만들며, 검증 전에는
  `NOT_AVAILABLE`로 취급한다.
- S&P 500 숫자는 확정 목표가가 아니라 금리·이익·배수 조건을 가진 스트레스 범위로 표시한다.
- UI는 provider를 직접 호출하지 않고 `Ingestion -> DB -> Loader -> Service -> UI`를 따른다.

## 2026년 분석에서 보존할 것과 수정할 것

2026년 6월 SEP와 7월 FOMC는 이 기능을 설계하게 된 실제 사례지만, 아래 값은 모델의
영구 상수가 아니라 해당 시점의 분석 snapshot이다.

### 보존할 질문

- 현재 10년물의 중요한 전고점은 어디인가?
- 그 저항선을 돌파하려면 시장이 몇 회의 인상을 반영해야 하는가?
- 그 정도 정책 경로가 현실화되려면 연말 Core PCE가 어느 수준이어야 하는가?
- 남은 달의 월별 Core PCE가 어느 정도면 그 경로에 도달하는가?
- 다음 PCE가 `0.1~0.2%` 또는 `0.4~0.5%`일 때 각 경로의 확률이 얼마나 바뀌는가?
- 그 조합에서 채권과 주식의 스트레스 범위는 어떻게 달라지는가?

### 수정할 해석

- 2026년 6월 SEP의 연말 정책금리 분포에서 현 수준 대비 2회 인상은 5명,
  3회 인상은 1명이다. 따라서 `2~3회 인상`은 합계 6명이며 5명이 아니다.
- Core PCE `3.5~3.6%` 구간의 참가자 수와 높은 금리 점의 참가자 수가 비슷하더라도,
  공개 SEP만으로 동일 인물이라고 연결할 수 없다.
- `0.4~0.5%` 한 번의 월별 Core PCE는 인상 확률을 높일 수 있지만 자동 인상 신호는 아니다.
  발생 월, 이후 경로, 물가 확산도, 노동시장과 FOMC 반응을 함께 봐야 한다.
- 10년물 `4.7%`는 2025~2026년 시장에서 의미 있는 전고점 군집이 될 수 있지만,
  인플레이션을 판정하는 절대선은 아니다.
- 장기금리는 정책금리 기대뿐 아니라 실질 성장 기대와 기간 프리미엄만으로도 상승할 수 있다.

## 제품 범위

### 포함

- 월별 Core PCE와 연말 `Q4/Q4` 확률분포
- 인플레이션 다섯 상태와 SEP·사용자 목표 수준 도달 확률
- 다음 FOMC와 연말 목표금리 구간 확률
- 동결·1회·2회·3회 이상 인상 또는 인하 경로
- 2년물·10년물·실질금리·기대인플레이션·기간 프리미엄 해석
- 동적 저항 구간과 접근·돌파·안착·실패 상태
- 금리 목표에서 필요한 정책·물가 경로를 찾는 역산 기능
- 조건부 S&P 500 스트레스와 차년도 EPS·AI 수익화 촉매
- 별도 검증을 거치는 신규 침체 확률 모듈
- 모든 결과의 기준시각, 데이터 신선도, 모델 버전, 근거와 과거 replay

### 제외

- 기존 경제 사이클 모델 확률 또는 파생 상태의 재사용
- SEP 참가자의 익명 금리 점과 익명 물가 전망을 개인별로 연결하는 추정
- NBER의 공식 침체 선언처럼 보이는 표현
- 단일 PCE 발표치로 자동 금리 결정을 확정하는 규칙
- 10년물 저항선 돌파를 인플레이션 재가속으로 자동 분류하는 규칙
- 목표가격, 매수·매도 지시, 자동 주문 또는 포트폴리오 리밸런싱
- 화면 렌더링 중 FRED·BEA·Federal Reserve·CME 등 외부 호출
- 검증에 실패한 확률을 마지막 정상값으로 대체해 최신 결과처럼 표시하는 동작

## 전체 사용자 흐름

```text
저장된 최신 원자료와 공개시각
  -> Core PCE 월별 확률 경로
  -> 연말 Core PCE 연속분포와 5상태
  -> FOMC 회의·연말 정책 경로 분포
  -> 국채금리 구성요소별 경로
  -> 동적 저항선 도달·돌파·안착 확률
  -> 주식시장 조건부 스트레스

사용자 선택 저항선·목표금리
  -> 목표를 만족하는 국채금리 simulation 경로를 추출
  -> 해당 경로의 정책 횟수 분포를 역산
  -> 해당 정책 경로와 부합하는 Core PCE 경로를 역산
  -> 남은 달의 필요 월별 물가와 다음 발표 임계값을 제시

신규 침체 원자료
  -> 별도 침체 모델과 검증 게이트
  -> 통과 전에는 다른 엔진과 결합하지 않음
```

## 데이터 계약

모든 입력과 결과에는 최소한 다음 시각을 분리해 저장한다.

- `observation_date`: 값이 설명하는 경제 시점
- `released_at`: 시장과 모델이 실제로 알 수 있게 된 시각
- `collected_at`: 시스템이 수집한 시각
- `as_of_at`: 계산 cutoff

`as_of_at` 이후 공개된 값은 참조월이 과거여도 사용할 수 없다. 예를 들어 7월 FOMC
결정을 계산할 때 다음 날 공개된 6월 PCE는 입력에 포함하지 않는다.

### 재사용하는 저장 구조

기존 `macro_series_vintage_observation`과 ALFRED 기반 as-of loader는 시계열의 빈티지·공개일
요건을 만족하는 범위에서 재사용한다. 기존 경제 사이클 snapshot, 확률, factor 또는
artifact는 재사용하지 않는다.

### 신규 저장 구조

#### `fomc_sep_distribution`

SEP 표를 참가자 분포 그대로 저장한다.

- SEP 회의일과 실제 공개시각
- 전망 대상 연도와 장기 전망 여부
- 변수: 연방기금금리, 실질 GDP, 실업률, PCE, Core PCE
- 점 또는 전망 구간
- 해당 구간 참가자 수
- 단위, 원문 URL, 수집시각, parser 버전

금리 점과 물가 분포의 행을 연결하는 `participant_id`는 만들지 않는다.

#### `fomc_policy_decision`

- 회의일과 발표시각
- 결정 전·후 목표금리 하단과 상단
- 총 투표, 찬성, 반대
- 반대표가 선호한 방향과 폭
- 성명서 source identity와 직전 성명 대비 변경 근거
- 수집시각과 parser 버전

#### `inflation_policy_model_artifact`

- 모델 버전과 학습 cutoff
- feature·transform·상태 정의 버전
- 학습 기간과 forecast horizon
- component와 ensemble weight
- rolling-origin 검증 지표
- calibration artifact
- `READY | LIMITED | FAILED` 공개 상태와 사유

#### `inflation_policy_snapshot`

- 계산 기준시각과 모델 버전
- 월별 Core PCE path quantile
- 연말 Core PCE 분포와 다섯 상태 확률
- SEP·사용자 목표 수준 도달 확률
- 다음 회의와 연말 정책금리 확률
- 인상·인하 횟수 분포
- 국채금리와 저항선 돌파 확률
- top evidence, 데이터 신선도, 경고
- forward와 reverse scenario의 compact 결과

전체 simulation path는 모델 artifact 또는 별도 DB artifact에 두고 UI snapshot에는 요약값만 둔다.

#### `yield_resistance_definition`

- 기준 소유자: `AUTO | USER`
- 대상 instrument
- lookback과 pivot 확인 규칙
- zone 하단·상단과 buffer
- 인플레이션 확인 profile: breakeven·실질금리·기간 프리미엄 확인조건
- 생성 기준시각과 알고리즘 버전
- 사용자 기준이면 이름, 활성 여부, 저장시각

자동 기준은 시점별 snapshot으로 보존하고 과거 값을 현재 기준으로 재작성하지 않는다.

#### `yield_resistance_snapshot`

- definition identity와 계산 기준시각
- 현재 금리와 zone까지의 거리
- `APPROACH | ATTEMPT | CONFIRMED | HOLD | FAILED` 상태
- zone strength, timeframe confluence, touch·rejection 근거
- breakout과 hold의 조건부 확률
- 주도 요인 분류와 품질 상태

## 필수 매크로 입력

### 실제 물가

- PCE, Core PCE index와 월별 변화율
- CPI, Core CPI와 주요 bridge component
- Dallas Fed Trimmed Mean PCE
- 주거 제외 서비스 또는 이용 가능한 서비스 세부 항목
- 상품·서비스 확산도와 trimmed/winsorized breadth

### 물가 선행 입력

- 평균 시간당 임금, 고용비용지수, 단위노동비용
- PPI와 수입물가
- 임대료·주거 선행지표
- 유가와 주요 상품가격
- 단기·장기 기대인플레이션
- Cleveland Fed Inflation Nowcasting은 외부 비교 기준으로 사용

### 정책과 위원회

- FOMC 결정, 성명, 투표와 반대 방향
- SEP 금리·성장·실업·PCE·Core PCE 분포
- 정책금리 목표 범위
- CME FedWatch는 가용할 때만 사용하는 선택적 시장 prior

### 노동·성장 원자료

- 실업률, 비농업고용, 신규실업수당, 근로시간, 임시직
- 실질 개인소득, 실질 소비, 산업생산, 실질 판매
- 성장과 고용 입력은 기존 경제 사이클 확률로 대체하지 않는다.

### 금리와 금융여건

- 2년물·10년물 명목 국채금리
- 10년 실질금리와 10년 breakeven
- 2s10s 등 curve slope
- New York Fed ACM term premium
- 신용 spread와 금융여건은 정책·침체 보조 원자료로만 사용

## Core PCE 경로 엔진

### 연말 값 계산

SEP의 연간 PCE 전망은 `Q4/Q4` 의미로 해석한다. 월별 변화율의 단순 합이나 12월
전년비로 대체하지 않는다.

월별 index path는 다음처럼 재귀 계산한다.

```text
P_t = P_(t-1) * (1 + m_t / 100)

Q4/Q4 = (
  mean(P_Oct, P_Nov, P_Dec) /
  mean(P_prev_Oct, P_prev_Nov, P_prev_Dec)
  - 1
) * 100
```

특정 연말 목표에 필요한 남은 월 평균은 위 식을 만족하는 월별 변화율을 수치적으로
역산한다. 그러므로 `1~4월 누적치 + 남은 달 합계`는 빠른 설명용 근사치로만 제공하고
모델 계산에는 사용하지 않는다.

2026년 6월 Core PCE index까지 알려진 시점에서 동일한 월별 변화율을 7~12월에 가정한
설명용 예시는 다음과 같다. 실제 모델은 동일 경로 가정이 아니라 월별 확률분포를 사용한다.

| 7~12월 가정 | 예상 연말 Core PCE `Q4/Q4` |
| --- | ---: |
| 매월 0.20% | 약 3.17% |
| 매월 0.25% | 약 3.43% |
| 매월 약 0.264% | 약 3.50% |
| 매월 0.30% | 약 3.68% |
| 한 번 0.40%, 나머지 0.20% | 발생 월에 따라 약 3.24~3.37% |
| 한 번 0.50%, 나머지 0.20% | 발생 월에 따라 약 3.27~3.48% |

이 예시는 `0.4~0.5% 한 번이면 연말 3.5%와 금리 인상`이라는 boolean 규칙이 성립하지
않음을 보여준다. 반대로 작은 월별 상승도 여러 달 지속되면 연말 분포의 상단 질량을
의미 있게 높일 수 있다.

### 혼합형 월별 nowcast

월별 Core PCE 분포는 다음 component를 결합한다.

1. 해석 가능한 bridge
   - Core PCE 자기시차
   - 공개된 CPI component에서 PCE component로의 bridge
   - 임금·서비스·생산자·수입물가·기대인플레이션
2. 정규화 통계 모델
   - 선형·비선형 관계를 별도 추정하되 시계열 표본 크기에 맞게 regularization
   - 결측과 release lag를 feature 자체로 관리
3. 시나리오 component
   - 사용자가 다음 발표치 또는 월별 경로를 직접 입력한 경우 확정 입력으로 분기

component weight는 rolling-origin 성과로 정하며 고정된 수동 평균을 사용하지 않는다.
월별 predictive residual과 calibration error를 simulation에 포함해 연말 분포가 지나치게
좁아지지 않게 한다.

### 다섯 상태

연말 Core PCE 연속분포가 source of truth이고 상태는 표현 layer다.

| 상태 | 의미 |
| --- | --- |
| 빠른 둔화 | SEP 중심보다 뚜렷하게 낮고 최근 momentum·breadth도 하락 |
| 완만한 둔화 | 물가가 낮아지지만 목표 복귀 속도는 완만 |
| 고착 | 높은 수준이 유지되며 둔화·재가속 증거가 엇갈림 |
| 재가속 | SEP 상단 또는 정책 반응 구간으로 상승하며 확산도 확인 |
| 충격성 재가속 | 상단 꼬리 수준과 이례적 월별 충격·확산이 함께 나타남 |

2026년 6월 SEP를 기준으로 한 초기 표현 구간은 `2.9 / 3.1 / 3.5 / 3.9%`를 후보
경계로 사용한다. 이 값은 전역 상수가 아니다. 최신 SEP 분포, 연준 목표와의 거리,
rolling-origin 예측오차, 정책 반응이 변하는 구간으로 매 SEP 이후 상태 정의 버전을
재산정한다. `3.4%`, `3.5%`, `3.6%`처럼 사용자가 보는 중요 수준의 도달 확률은 상태와
별도로 항상 조회할 수 있다.

### 단일 발표치 처리

- `0.1~0.2%`: 둔화·동결 posterior를 높일 수 있으나 한 번으로 확정하지 않는다.
- `0.3%`: 기존 연말 경로와 surprise 방향에 따라 중립 또는 고착 증거가 된다.
- `0.4~0.5%`: 재가속·인상 posterior를 높이되 지속성·breadth가 없으면 shock flag로만 남긴다.
- 효과는 발표 월, 이전 path, consensus surprise, 남은 개월 수와 함께 계산한다.

## FOMC 정책 경로 엔진

정책금리 확률은 세 component와 하나의 선택 component를 결합한다.

### 1. 경제 반응함수

- Core PCE level, momentum, breadth와 목표 gap
- 실업률, 고용, 신규실업수당, 성장·소비 원자료
- 실질 정책금리와 금융여건
- 단일 Taylor rule 값이 아니라 여러 투명한 정책규칙의 범위

### 2. 위원회 prior

- 최신 SEP 금리 점 분포
- SEP Core PCE·PCE·성장·실업 분포
- 최근 결정, 성명 변화, 투표와 반대 방향
- 익명 분포 사이에 존재하지 않는 개인별 joint mapping은 만들지 않음

### 3. 통계 component

- 당시 공개된 입력만으로 다음 회의 결정과 연말 target band를 학습
- meeting별 rolling-origin 분류와 확률 보정
- 급격한 체제 변화에 한 component가 전체 확률을 독점하지 못하도록 weight 제한

### 4. 선택적 시장 prior

CME FedWatch가 수집·검증된 경우에만 별도 prior로 사용한다. 없거나 stale이면 경제·위원회·
통계 component만 재정규화하고 전체 결과를 실패시키지 않는다. 시장 확률과 모델 확률은
사용자가 차이를 볼 수 있도록 분리 표시한다.

### 출력

- 다음 회의: `CUT | HOLD | HIKE` 확률과 가능한 폭
- 연말: 각 target range 또는 midpoint bin 확률
- 남은 기간: 순인하·동결·1회·2회·3회 이상 인상 확률
- 각 정책 경로에서 연말 Core PCE와 주요 노동 입력의 조건부 범위
- SEP, 시장 prior, 경제 반응함수 사이의 차이

## 동적 국채 저항선 엔진

### 후보 생성

- 전술 구간: 63거래일
- 경기 구간: 252거래일
- 구조 구간: 504거래일
- 각 기간에서 확인 가능한 pivot high를 찾는다.
- 비슷한 pivot은 `max(5bp, 최근 63일 일간 절대변화 중앙값)` tolerance로 군집화한다.
- touch 수, rejection 크기, 최근성, 여러 timeframe의 중첩으로 zone strength를 계산한다.

pivot을 확인하는 데 오른쪽 관측치가 필요하면 pivot 날짜에 알았던 것처럼 기록하지 않는다.
해당 pivot은 확인 조건을 충족한 날짜부터만 사용 가능하다. 이 계약은 backtest와 과거
replay에서 동일하게 적용한다.

### 상태 전이

| 상태 | 운영 의미 |
| --- | --- |
| 접근 | 현재 금리가 zone buffer 안으로 진입 |
| 돌파 시도 | zone 상단을 일시적으로 상회했으나 확인 부족 |
| 돌파 확인 | 최근 5일 중 3일 종가가 상단+buffer 위이거나 주간 종가 확인 |
| 안착 | 확인 이후 설정한 유지 기간 동안 zone 위를 보존 |
| 실패 | 상회 후 zone 아래로 복귀하고 재진입 조건을 잃음 |

확인 일수와 buffer는 definition에 versioning한다. 최초 기본값은 위 규칙을 사용하되,
instrument별 historical false-break rate 검증을 통해 별도 version으로만 변경한다.

### 적용 instrument

- 2년물 명목금리
- 10년물 명목금리
- 10년물 실질금리
- 10년 breakeven
- 2s10s slope
- ACM term premium

### 상승 원인 분류

두 분해 lens를 별도로 사용하며 component를 중복 합산하지 않는다.

1. 정책·기간 lens: 기대 단기금리 경로와 기간 프리미엄
2. 실질·물가 lens: 10년 실질금리와 10년 breakeven

결과는 `인플레이션 주도 | 정책 주도 | 실질금리·성장 주도 | 기간 프리미엄 주도 | 혼합`으로
분류한다. 10년물 단독 돌파는 인플레이션 상태의 입력 근거가 아니라 결과 확인 신호다.

### 인플레이션 확인 기준

사용자가 질문한 `10년물의 어떤 값이 인플레이션 신호인가`에 대해 값 하나를 답으로
사용하지 않는다. 자동 추천 profile은 다음 증거의 조건부 결합을 평가한다.

- 10년물이 해당 시점의 자동 또는 사용자 저항 zone을 `CONFIRMED` 이상으로 돌파
- 10년 breakeven이 자체 동적 zone 또는 검증된 상승 momentum을 확인
- 10년 실질금리 상승만으로 명목금리 움직임이 설명되지 않음
- ACM term premium 단독 급등이 주원인이 아님
- Core PCE의 `재가속 + 충격성 재가속` posterior가 발표 전보다 상승하거나 정책 반응
  임계 구간에 진입

결과는 `미확인 | 혼합 | 인플레이션 확인`과 함께 `인플레이션 주도 돌파 확률`로 제공한다.
정확한 결합 weight와 확률은 historical event rolling-origin으로 보정한다. 사용자는 자동
profile을 복사해 breakeven 확인 여부, term-premium 제외 조건, 돌파 확인 기간을 바꿔
저장할 수 있다. 사용자 profile은 자동 추천 기준을 덮어쓰지 않으며 결과에 소유자를 표시한다.

## 순방향·역산 simulation

### 순방향

1. 남은 달의 Core PCE path를 확률적으로 생성한다.
2. 각 path에서 연말 `Q4/Q4`와 인플레이션 상태를 계산한다.
3. FOMC 엔진으로 회의별 정책 경로를 생성한다.
4. 정책·실질금리·breakeven·기간 프리미엄 조건으로 국채금리 path를 생성한다.
5. 각 path가 자동 또는 사용자 저항선을 접근·돌파·안착하는지 평가한다.
6. 조건을 만족한 path의 비율과 신뢰구간을 결과 확률로 제공한다.

### 역산

1. 사용자가 instrument, 목표 zone, horizon, `도달 | 돌파 | 안착` 조건을 고른다.
2. 순방향 simulation 중 목표 조건을 만족하는 path를 likelihood에 따라 재가중한다.
3. 재가중된 path에서 정책금리 횟수와 target band 분포를 계산한다.
4. 그 path와 부합하는 연말 Core PCE와 남은 월 평균 MoM 분포를 계산한다.
5. 다음 PCE가 `0.1~0.5%`일 때 목표 도달 posterior가 어떻게 바뀌는지 보여준다.

역산 결과는 유일한 필요조건이 아니라 `그 목표와 부합하는 경로들의 조건부분포`로 표시한다.
`10년물 4.7%에는 3회 인상이 필요하다`처럼 단일 인과 문장으로 축약하지 않는다.

## 신규 침체 모듈

침체 기능은 필요하지만 기존 경제 사이클 결과를 재사용하지 않는다. 신규 모듈은 다음 다섯
상태를 별도 확률로 계산한다.

| 상태 | 의미 |
| --- | --- |
| 확장 | 활동·고용·소득·소비가 폭넓게 증가 |
| 성장 둔화 | 증가세가 약해지지만 폭넓은 수축은 아님 |
| 침체 경계 | 선행·동행 원자료에서 수축 위험이 임계 수준에 접근 |
| 침체 | 깊이·확산·지속성을 가진 실물 수축 가능성이 높음 |
| 회복 전환 | 수축 이후 breadth와 momentum이 저점 통과 |

현재, 3개월, 6개월, 12개월 horizon을 별도 평가한다. NBER 침체 날짜는 사후 평가 label로만
사용하며 현재 공식 판정처럼 표시하지 않는다.

입력은 실업률, 고용, 근로시간, 임시직, 신규실업수당, 실질소득, 실질소비, 산업생산,
실질 판매, 신용 spread, curve와 금융여건의 point-in-time 원자료다. 기존 경제 사이클
확률·factor·snapshot은 입력과 label 모두에서 금지한다.

신규 침체 모델이 독립 검증 게이트를 통과하기 전에는 다음을 지킨다.

- UI 상태는 `NOT_AVAILABLE` 또는 `검증 중`이다.
- 정책 경로 ensemble weight에 포함하지 않는다.
- 인플레이션 상태를 변경하지 않는다.
- 침체 조건부 자산 시나리오를 숫자 확률로 제공하지 않는다.

## 주식시장 조건부 스트레스

주식 결과는 확정 지수 목표가가 아니라 조건부 분포다.

```text
Index level = forward EPS * forward valuation multiple
```

- 금리·실질금리·risk premium 경로가 valuation multiple에 미치는 역사적 조건부분포
- 올해와 차년도 EPS 전망 변화
- 인플레이션·침체 경로에 따른 margin과 이익 민감도
- AI 수익화와 생산성은 차년도 EPS revision 촉매로 별도 입력
- 사용자가 `S&P 500 6,400` 같은 수준을 입력하면 해당 수준 이하 도달 확률과 필요한
  EPS·multiple 조합을 역산

정책 발표와 금리 변화의 event study는 연관 범위를 제공할 뿐 인과를 확정하지 않는다.
AI 촉매도 물가 또는 정책 신호로 섞지 않는다.

## 확률 검증과 공개 게이트

모든 모델은 시간순 rolling-origin과 당시 공개 데이터만 사용한다. 전체 기간 random split은
정식 검증으로 인정하지 않는다.

### Core PCE

- 월별·연말 MAE/RMSE
- CRPS 또는 동등한 분포 score
- 50%·80%·95% prediction interval coverage
- 다섯 상태 Brier score, log loss, reliability
- carry-forward, 최근 평균, 최신 SEP, 외부 공식 nowcast와 비교

### FOMC

- 회의별 Brier score와 log loss
- class별 reliability와 calibration error
- 항상 동결, 직전 결정 유지, 최신 SEP, 선택적 시장 prior와 비교
- next-meeting과 year-end horizon을 분리 평가

### 저항선과 금리 path

- pivot 확인시각과 미래 누수 검사
- 접근 후 돌파·안착·실패의 empirical frequency
- 예측 확률의 calibration
- 단순 rolling high와 고정 buffer 기준 대비 개선
- 정책 repricing, 실질금리, breakeven, term premium driver 분류 안정성

### 침체

- recession event 단위 recall과 false alarm
- Brier score, PR-AUC, reliability
- turning point lead/lag와 평균 경보 지속시간
- 단순 Sahm-style rule, yield curve, 동행지표 breadth 기준과 비교

### 공개 상태

| 상태 | UI 동작 |
| --- | --- |
| `READY` | PIT, coverage, baseline, calibration 계약을 모두 통과해 숫자 확률 공개 |
| `LIMITED` | 방향·순위·넓은 범위만 제공하고 정밀 확률은 숨김 |
| `NOT_AVAILABLE` | critical data 또는 독립 검증이 없어 계산하지 않음 |
| `FAILED` | schema, probability sum, model artifact 또는 실행 오류로 결과 미사용 |

각 artifact는 사전에 고정한 baseline과 calibration threshold를 보관한다. 최종 holdout을 본 뒤
threshold를 바꾸면 새 모델 버전과 새 검증으로 취급한다. best baseline보다 분포 score가
나쁘거나 calibration이 무너지면 `READY`가 될 수 없다.

## 화면 설계

기존 `Market Research > 경제 사이클` 안에 내부 선택기를 둔다.

```text
경기 국면 | 물가·정책 경로
```

기존 `경기 국면` 화면과 모델은 변경하거나 신뢰 입력으로 재사용하지 않는다. 신규 기능은
`물가·정책 경로`의 독립 service·payload·component로 구현한다.

### 기본 판단 흐름

1. 현재 결론
   - 연말 Core PCE 중앙 경로와 uncertainty
   - 가장 가능성 높은 물가 상태
   - 다음 회의와 연말 정책 경로
   - 10년물의 가장 가까운 동적 저항선과 현재 상태
2. 물가 다섯 상태
   - 전체 확률을 합계 100%로 표시
   - 3.4·3.5·3.6%와 사용자 목표 도달 확률
3. 월별 사전 대비
   - 다음 Core PCE 발표치별 posterior 변화
   - 목표별 남은 월 필요 평균
   - one-off와 persistent path를 분리
4. 정책 경로
   - 동결·1·2·3회 이상 인상/인하
   - SEP·모델·선택적 시장 prior 차이
5. 금리와 저항선
   - 자동·사용자 zone
   - 접근·돌파·안착·실패
   - 상승 driver 분해와 인플레이션 확인 상태
6. 역산
   - 목표 instrument·zone·시점·확인조건 선택
   - 필요한 정책·PCE·금리 component 조건부분포
7. 자산 스트레스
   - EPS·multiple·금리 조건과 지수 범위
   - AI 차년도 EPS 촉매
8. 침체
   - 신규 모델이 `READY`가 된 이후에만 확률 표시
9. 근거와 replay
   - 기준시각, 공개시각, 모델 버전, 과거 시점 재현

첫 화면은 job, 저장 row, raw status가 아니라 사용자의 현재 질문과 다음 확인 조건을 보여준다.
데이터와 모델 품질은 결론의 보조 근거로 배치한다.

## 서비스 조회 계약

UI는 compact read model 하나를 읽는다.

```text
as_of_at
model_version
publication_status
inflation
  q4q4_distribution
  state_probabilities[5]
  threshold_probabilities
  monthly_paths
  next_release_scenarios
policy
  next_meeting_probabilities
  year_end_target_bins
  net_move_probabilities
  sep_comparison
  optional_market_comparison
rates
  instruments
  resistance_zones
  breakout_probabilities
  driver_decomposition
reverse_scenario
  selected_target
  conditional_policy_paths
  conditional_pce_paths
  required_remaining_mom
equity_stress
recession
  publication_status
  horizon_probabilities_or_null
evidence
freshness
warnings
```

확률 배열은 유효 상태에서 합계 1을 만족해야 한다. 없는 선택 component는 `null`이며 0%로
위장하지 않는다.

## 오류와 제한 상태

- 필수 PCE 빈티지 누락: 연말 분포와 정책·역산 결과를 보류한다.
- SEP parser 일부 실패: 해당 SEP prior를 제외하고 이유를 표시한다.
- CME 미수집: 선택 component만 제외하고 나머지 모델은 재정규화한다.
- ACM term premium 미수집: term-premium driver를 `UNAVAILABLE`로 두고 다른 lens로 대체했다고
  주장하지 않는다.
- stale 입력: 영향받는 horizon과 마지막 공개시각을 표시하고 confidence를 자동 상향하지 않는다.
- probability·schema 검증 실패: 신규 snapshot을 current로 승격하지 않는다.
- 마지막 정상 snapshot은 과거 결과로 timestamp와 함께 열람할 수 있지만 최신 결과처럼 보이지 않는다.
- 침체 검증 미완료: `NOT_AVAILABLE`; 기존 사이클 값으로 채우지 않는다.
- reverse target을 만족하는 simulation이 너무 적으면 확률을 외삽하지 않고 조건을 완화하도록 안내한다.

## 테스트 계약

### 데이터·PIT

- observation, release, collection, as-of 시각 분리
- 발표 다음 날 데이터가 전날 FOMC 계산에 들어가지 않는지
- SEP 분포 parser의 participant count와 합계
- 금리 점과 물가 전망 사이에 participant mapping이 생성되지 않는지
- vintage revision replay와 이후 수정치 차단
- idempotent UPSERT와 partial failure rollback

### 계산

- index 기반 Core PCE `Q4/Q4` 공식과 root-finding
- 월별 path quantile과 상태 확률 합계
- 단일 `0.4~0.5%` 입력이 자동 인상 boolean으로 변환되지 않는지
- policy target bin과 net move 분포 일관성
- yield decomposition에서 서로 다른 lens를 중복 합산하지 않는지
- pivot의 known-at date와 breakout 상태 전이
- 10년물 단독 돌파가 인플레이션 확인으로 자동 승격되지 않는지
- 사용자 inflation-confirmation profile이 자동 profile을 덮어쓰지 않는지
- forward simulation과 reverse conditional reweighting
- 입력 target을 만족하는 path 부족 시 안전한 `NOT_AVAILABLE`
- 기존 경제 사이클 snapshot·probability를 import 또는 조회하지 않는 경계 테스트

### 검증·artifact

- rolling-origin만 정식 평가로 등록되는지
- baseline·calibration 미달 artifact가 `READY`가 되지 않는지
- model·feature·상태·저항선 definition version 보존
- stale 또는 failed snapshot이 current로 승격되지 않는지

### 서비스·UI

- optional component가 `null`일 때의 정상 렌더링
- 다섯 상태·정책 확률 합계와 라벨
- 자동 zone과 사용자 zone 시각적 구분
- forward·reverse 입력과 결과 연결
- 과거 replay가 당시 알려진 zone과 데이터만 사용하는지
- 기존 경제 사이클 payload와 화면 회귀 없음
- desktop·mobile React test/build와 Browser QA
- 페이지 오류, console error, horizontal overflow 0

## 예상 코드 경계

정확한 파일 분해는 구현 계획에서 현재 소유 구조와 충돌을 다시 확인하되 책임은 다음처럼 둔다.

- schema: `finance/data/db/schema.py`
- SEP·FOMC·PCE·금리 수집: focused modules under `finance/data/`
- as-of read: focused modules under `finance/loaders/`
- Core PCE, policy, resistance, simulation, recession: 서로 분리된 focused `finance` domain modules
- orchestration·snapshot materialization: `app/jobs/` 또는 focused finance application boundary
- read model: 신규 service under `app/services/overview/`
- navigation bridge: `app/web/overview/`
- UI: 신규 독립 React view under `app/web/streamlit_components/economic_cycle_workbench/`
- tests: collector/schema/loader/domain/service/UI build와 Browser QA

기존 `finance/economic_cycle_*`, 기존 cycle snapshot 또는 기존 확률 service를 신규 예측 계산의
편의상 import하지 않는다. 공통으로 재사용할 수 있는 것은 일반 DB client, vintage observation,
날짜·품질 primitive와 UI shell뿐이다.

## 구현 로드맵

### 1차. 설계·공식 근거·데이터 계약

- 목적: 사용자의 분석 질문을 재현 가능한 계산 계약으로 고정
- 범위: 본 설계, 공식 source 정의, 기존 사이클 비재사용 경계
- 완료 조건: 사용자 승인, 자체검토, 설계 문서 커밋
- 다음 연결: 수집·schema·PIT fixture의 구현 계획

### 2차. 원자료 수집·DB·as-of loader

- 목적: SEP, FOMC, PCE, 금리·기간 프리미엄을 재현 가능하게 저장
- 범위: ingestion, schema, UPSERT, release timestamp, loader
- 완료 조건: fixture·DB·PIT 테스트와 실제 source smoke
- 다음 연결: 예측 엔진의 누수 없는 training panel

### 3차. Core PCE·정책·저항선 엔진과 백테스트

- 목적: 순방향 확률 경로와 동적 저항선 계산
- 범위: inflation ensemble, policy ensemble, zone detection, calibration artifact
- 완료 조건: baseline 비교와 공개 게이트, historical replay
- 다음 연결: 역산 simulation과 사용자 판단 화면

### 4차. 순방향·역산 UI

- 목적: 사용자가 다음 발표 전 조건과 목표 금리의 필요 경로를 판단
- 범위: read model, 물가·정책 경로 화면, custom criteria 저장
- 완료 조건: 실제 최신 DB 결과, desktop·mobile Browser QA, 기존 화면 회귀 없음
- 다음 연결: 자산과 침체의 독립 확장

### 5차. 주식시장·AI 수익성 스트레스

- 목적: 금리 경로를 EPS·multiple 조건부 범위와 연결
- 범위: S&P 500 stress, 사용자 지수 목표 역산, 차년도 EPS·AI catalyst
- 완료 조건: 연관과 가정을 표시한 PIT event study와 범위 검증
- 다음 연결: 통합 매크로 위험 요약

### 6차. 신규 침체 모듈

- 목적: 기존 엉터리 확률 없이 원자료에서 침체 위험을 새로 계산
- 범위: 신규 label·feature·model·0/3/6/12개월 검증
- 완료 조건: 독립 baseline·calibration gate 통과 전 `NOT_AVAILABLE` 유지
- 다음 연결: 통과한 경우에만 정책·자산 시나리오의 명시적 보조 조건으로 연결

## 완료 조건

- 사용자의 `전고점 -> 인상 횟수 -> 필요한 PCE 경로 -> 월별 대비 -> 주가 스트레스`
  질문을 순방향과 역산 양쪽에서 수행할 수 있다.
- `4.7%`, `3.5%`, `0.4~0.5%`, `S&P 500 6,400`이 영구 상수나 확정 인과로 코드에
  박히지 않는다.
- 기존 경제 사이클 확률이 신규 계산·fallback·침체 결과 어디에도 사용되지 않는다.
- SEP 익명 분포의 개인별 연결을 주장하지 않는다.
- 모든 과거 결과가 당시 공개된 빈티지와 당시 알려진 저항선만 사용한다.
- 검증 미통과 확률은 정밀 숫자로 공개되지 않는다.
- UI는 최신 결론, 다음 확인 조건, 역산 경로를 먼저 보여주고 운영 진단을 주인공으로 삼지 않는다.

## 공식 참고자료

- Federal Reserve, June 2026 SEP:
  <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm>
- Federal Reserve, July 29 2026 FOMC statement:
  <https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm>
- BEA, Personal Income and Outlays, June 2026:
  <https://www.bea.gov/news/2026/personal-income-and-outlays-june-2026>
- FRED, Core PCE Price Index:
  <https://fred.stlouisfed.org/series/PCEPILFE>
- FRED, 10-Year Treasury Constant Maturity Rate:
  <https://fred.stlouisfed.org/series/DGS10>
- New York Fed, Treasury term premia:
  <https://www.newyorkfed.org/research/data_indicators/term-premia-tabs>
- Cleveland Fed, Inflation Nowcasting:
  <https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting>
- Dallas Fed, Trimmed Mean PCE Inflation Rate:
  <https://www.dallasfed.org/research/pce>
