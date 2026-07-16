# 미국 경제 사이클 국면·확률 예측 기능 설계

Status: Approved
Approved: 2026-07-16
Scope: `finance` package and Finance Streamlit `Workspace > Overview > 시장 맥락`

## 이걸 하는 이유?

사용자는 자신이 공부한 `회복 → 확장 → 둔화 → 침체` 경제 사이클을 현재 미국 경제에 적용하고, 과거 국면과 현재 위치, 향후 1개월·2개월의 가능한 이동을 한 화면에서 판단하고 싶다.

기존 학습 노트는 정책, 물가, 금리, 신용, 주식, 금, 달러, 원자재 사이의 투자자 관점 연결을 잘 포착한다. 이 설계는 그 논리를 버리지 않는다. 대신 실물경제 국면을 시장가격만으로 결정하지 않도록 역할을 분리하고, 실시간 빈티지와 확률 검증을 추가해 재현 가능한 제품 기능으로 확장한다.

## 승인된 결정

- 대상 경제는 미국으로 한정한다.
- 결과는 단일 확정 판정이 아니라 네 국면 전체 확률을 제공한다.
- 예측 지평은 현재, `+1개월`, `+2개월`이다.
- 예측 엔진은 `해석 가능한 요인 + 전환 제약 + 지평별 확률 보정` 혼합형을 사용한다.
- 화면은 C안인 `사이클 시계 + 과거 국면 리본` 혼합형을 사용한다.
- 실물 활동이 국면 정의의 중심이며, 금리·신용·금·달러·원자재는 시장 시사점과 선행 위험 근거로 분리한다.
- 숫자 확률은 rolling-origin 검증과 보정 기준을 통과한 경우에만 공개한다.
- 구현 순서는 빈티지 데이터 계약에서 시작하고, 검증되지 않은 차트 전용 UI를 먼저 만들지 않는다.

## 제품 범위

### 포함

- 과거 월별 미국 경제 사이클 판정과 국면 리본
- 현재 네 국면 확률 및 주요 근거
- 1개월·2개월 후 네 국면 확률 및 예상 이동 방향
- 실물 활동, 고용·소득, 물가·정책, 금융여건의 기여도
- 사용자의 학습 노트를 확장한 금리·주식·금·달러·원자재 시장 시사점
- 데이터 기준일, 모델 버전, 품질·신뢰도 상태
- 과거 시점 선택 시 당시 공개 데이터만 사용한 재현

### 제외

- 포트폴리오 배분, 매수·매도, risk-on/risk-off 지시
- NBER의 공식 선언처럼 보이는 표현
- 브로커 주문, 자동 리밸런싱, 실시간 투자 알림
- 화면 렌더링 경로에서 FRED·ALFRED 등 외부 소스 직접 호출
- 검증되지 않은 수동 국면 라벨 또는 임의 확률
- V1의 정량 재정충격 모델; 재정정책은 설명 가능한 이벤트 맥락으로 제한한다.

## 국면 의미

국면은 `활동 수준 × 변화 모멘텀 × 지표 확산도`로 정의한다. 경제의 방향과 경제 수준을 혼동하지 않는다.

| 국면 | 운영 정의 | 대표적인 이동 신호 |
| --- | --- | --- |
| 회복 | 활동 수준은 추세 아래지만 모멘텀과 확산도가 개선 | 수축 확률 하락, 고용·생산의 저점 통과 |
| 확장 | 활동이 추세 부근 이상이고 증가세가 폭넓게 유지 | 생산·고용·소득·소비의 동반 증가 |
| 둔화 | 전면적 수축은 아니지만 활동과 선행 모멘텀이 악화 | 확산도 하락, 금융·선행지표 악화 |
| 침체 | 생산·고용·소득·소비에서 폭넓고 지속적인 수축 | NBER 기준과 정합적인 깊이·확산·지속성 |

NBER 날짜는 침체 사후 검증 앵커로 사용한다. NBER는 네 국면을 공식 제공하지 않으므로 회복·확장·둔화의 직접 정답으로 사용하지 않는다.

## 데이터 구조

```text
Official sources
  -> ingestion job
  -> vintage-aware observations
  -> as-of loader
  -> point-in-time transformations
  -> cycle factors and probabilities
  -> persisted cycle read model
  -> Market Context UI
```

### 빈티지 관측 계약

현재 `macro_series_observation`의 `(series_id, observation_date, source)` 유일 키는 수정치를 덮어쓰므로 실시간 과거 재현에 충분하지 않다. 신규 저장 구조 또는 호환 확장에는 최소한 다음 의미가 필요하다.

- `series_id`
- `observation_date`
- `vintage_date` 또는 실제 공개 시점
- `value`
- `source`
- `ingested_at`
- 값 상태와 누락 사유

`as_of_date` 조회는 해당 날짜까지 공개된 빈티지만 선택해야 한다. 기존 매크로 소비자는 호환 loader 또는 view로 보호한다.

### 초기 지표 묶음

- 실물 활동: 산업생산, 실질소득, 실질소비·판매, CFNAI, ADS, WEI
- 고용·소득: 비농업고용, 실업률, 신규 실업수당, 근로시간
- 물가·정책: 근원 PCE, 기대인플레이션, 정책금리
- 금융·선행: 건축허가, OECD CLI, 장단기 금리차, 신용스프레드, 금융여건

최종 core series는 구현 1차에서 빈티지 가용성, 발표 지연, 중복도, 장기 커버리지를 기준으로 축소 확정한다. 각 관측에는 기준일, 공개일, 기대 주기, 노후도와 사용 여부를 남긴다.

## 특징 생성과 누수 방지

- 월별 forecast origin마다 당시 공개된 최신값만 사용한다.
- 발표되지 않은 참조월과 이후 수정값은 특징에서 제외한다.
- 전년비, 3개월 변화율, 수준 변화, 확산도 등은 지표 의미에 맞춰 변환한다.
- 표준화와 결측치 처리 파라미터는 해당 forecast origin까지의 표본으로만 계산한다.
- 코로나 충격이 전체 스케일을 지배하지 않도록 robust scaling과 민감도 검증을 사용한다.
- OECD CLI는 기능 또는 비교 기준으로 사용할 수 있지만 네 국면의 유일한 정답으로 사용하지 않는다.

## 학습 정답

- 침체 구간은 NBER 공식 날짜를 사후 benchmark로 사용한다.
- 비침체 세 국면은 생산·고용·소득·소비로 구성한 실물 활동 요인의 수준과 모멘텀으로 투명하게 생성한다.
- 예측 입력으로 사용할 금융·선행지표는 비침체 정답 생성에서 제외해 순환 논리를 줄인다.
- 사후 benchmark와 실시간 모델 출력을 명확히 구분한다.
- 네 상태 라벨의 안정성은 OECD 성장 사이클 사분면 및 대안 규칙과 비교한다.

## 모델 구조

### 1. 해석 가능한 요인

실물 활동, 고용·소득, 물가·정책, 금융여건별로 공통 움직임을 압축한다. 각 요인은 방향, 확산도, 데이터 신선도와 기여 지표를 함께 반환한다.

### 2. 전환 제약 국면 엔진

네 국면의 emission 확률과 transition prior를 결합한다. 일반적인 `회복 → 확장 → 둔화 → 침체 → 회복` 흐름에 더 높은 사전확률을 부여하되, 코로나와 같은 상태 건너뛰기를 불가능하게 만들지는 않는다. 상태 이름은 경제적 의미로 고정하고 학습 후 임의 교환되지 않도록 식별 규칙을 둔다.

### 3. 지평별 확률 보정

현재, `+1개월`, `+2개월` 결과를 별도 지평으로 평가한다. 미래 확률은 현재 transition matrix를 반복 적용한 값만 사용하지 않고, 요인 변화와 현재 상태 분포를 입력으로 하는 직접 지평 모델 또는 보정기를 사용한다. 다중분류 확률은 합이 1이 되며 보정 표본과 품질 기준을 통과해야 한다.

## 검증

검증은 실시간 빈티지를 사용한 rolling-origin 방식으로 수행한다.

### 비교 기준

- 현재 국면 유지
- 단순 역사 전환행렬
- 투명한 수준×모멘텀 규칙
- OECD CLI 사분면

### 평가 지표

- Brier score
- multiclass log loss
- 확률 보정 오차와 reliability plot
- 국면 혼동행렬
- turning-point lead/lag
- 거짓 전환 횟수 및 국면 체류 안정성
- recession event 단위 민감도와 오탐률

### 확률 공개 게이트

정확한 문턱값은 구현 계획의 baseline 실험에서 고정한다. 다음 중 하나면 UI는 숫자 확률을 숨기거나 `제한적`으로 표시한다.

- 지표 커버리지 또는 신선도 부족
- 지평별 보정 표본 부족
- naive baseline 대비 확률 품질이 유의미하게 나쁘거나 불안정
- 빈티지 누락 때문에 point-in-time 보장이 불가능
- 모델·데이터 오류 또는 결과 합계/스키마 검증 실패

## 조회 모델 계약

UI는 원천 시계열이나 모델 객체를 직접 읽지 않고 저장된 조회 결과만 사용한다. 최소 결과는 다음 의미를 포함한다.

```text
as_of_date
model_version
data_quality_status
current_probabilities[recovery, expansion, slowdown, recession]
month_1_probabilities[...]
month_2_probabilities[...]
expected_transition
factor_contributions[activity, labor_income, inflation_policy, financial]
top_evidence[]
historical_regimes[]
forecast_path[]
warnings[]
```

전체 원천 시계열과 full model artifact는 DB 또는 모델 저장소에 두며, UI 조회 모델에는 설명에 필요한 compact evidence만 둔다.

## 화면 설계

`Workspace > Overview > 시장 맥락`에서 동일한 계층의 선택기를 제공한다.

```text
경제 사이클 | S&P 500 | 미국 개별주식
```

기존 valuation 화면은 동작을 유지하고, 경제 사이클은 별도 컴포넌트와 service boundary로 분리한다.

### C안 정보 위계

1. 상단 확률 요약
   - 현재, `+1개월`, `+2개월`
   - 각 시점의 네 국면 확률
   - 1위 국면, 상위 두 국면 차이, 예상 이동 방향
2. 사이클 시계
   - 최근 18개월 실제 궤적은 실선
   - 향후 2개월 예상 경로는 점선
   - 불확실성은 영역 또는 분포로 표시
3. 근거 패널
   - 실물 활동, 고용·소득, 물가·정책, 금융여건
   - 기여 방향, 주요 지표, 관측 기준일
   - 사용자 학습 노트를 확장한 시장 시사점
4. 과거 국면 리본
   - 기본 10년 범위
   - 모델 추정 국면과 NBER 공식 침체 음영 분리
   - 과거 월 선택 시 당시 빈티지 기준 스냅샷 재현
5. 방법론·품질
   - 데이터 기준일, 모델 버전, 신뢰도, 경고
   - 상세 방법론은 보조 영역에 배치

모바일은 `확률 → 시계 → 근거 → 리본` 단일 열 순서로 재배치한다.

## 사용자 문구 원칙

- `현재 국면`이 아니라 필요하면 `현재 모델 추정`으로 표시한다.
- `NBER 침체`와 `모델 침체 확률`을 같은 색·라벨로 혼동시키지 않는다.
- 가장 높은 국면만 강조하되 나머지 세 확률을 숨기지 않는다.
- 시장 시사점은 가능성과 조건으로 표현하고 투자 행동을 지시하지 않는다.
- 예측이 제한되면 마지막 유효 숫자를 최신 결과처럼 재사용하지 않는다.

## 오류·제한 상태

- 데이터 미수집: 필요한 지표와 기준일을 설명하고 예측을 보류한다.
- 데이터 노후화: 영향받은 요인과 예상 주기를 표시한다.
- 빈티지 공백: 과거 재현 불가 사유를 표시한다.
- 모델 검증 미통과: 순위 또는 정성 상태만 제공하거나 전체 결과를 보류한다.
- 부분 요인 누락: 남은 요인으로 자동 확신을 높이지 않고 품질 상태를 낮춘다.
- UI 조회 실패: 원천 fetch를 시도하지 않고 재시도 가능한 오류 상태를 제공한다.

## 코드 경계

예상 소유 범위는 다음과 같다. 정확한 파일명은 구현 계획에서 프로젝트 구조와 충돌 여부를 다시 확인한다.

- vintage schema/collector: `finance/data/db/schema.py`, `finance/data/`, `app/jobs/ingestion_jobs.py`
- as-of loader: `finance/loaders/`
- transforms/model/read model: 신규 focused `finance` cycle modules
- Overview routing: `app/web/overview/market_context.py` 및 helper
- UI: 신규 독립 economic-cycle Streamlit/React component
- tests: 데이터 경계, 변환, 모델, 조회 계약, Overview regression, component build

기존 `market_context_valuation` 컴포넌트 안에 전체 경제 사이클 도메인을 넣지 않는다.

## 구현 로드맵

### 1차. 의미·지표 카탈로그·빈티지 계약

- core series와 변환 승인
- forecast-origin 이후 데이터 차단
- 기존 macro consumer 호환성

### 2차. 현재 네 국면 엔진·과거 판정

- historical as-of replay
- 현재 확률과 기여 근거
- baseline 및 공식 지표 비교

### 3차. 1개월·2개월 확률 예측

- 지평별 rolling-origin 검증
- 보정 및 공개 게이트
- 품질 부족 시 명시적 degradation

### 4차. 시장 맥락 경제 사이클 UI

- 동일 계층 선택기
- C안 시계·리본·확률·근거
- 기존 valuation 회귀 방지

### 5차. Browser QA·문서 정렬·운영 인계

- desktop 및 420px Browser QA와 스크린샷
- Python/TypeScript 검증 및 build
- data/architecture/flow/runbook 문서 동기화

## 완료 조건

- 사용자가 과거·현재·향후 두 달을 한 화면에서 구분해 이해할 수 있다.
- 네 국면 확률과 이동 방향이 보이며, 근거와 데이터 기준일을 추적할 수 있다.
- 과거 판정이 당시 공개 데이터만으로 재현된다.
- 숫자 확률은 지평별 검증과 보정 기준을 통과한 경우에만 노출된다.
- 기존 S&P 500·미국 개별주식 valuation 흐름이 유지된다.
- UI가 외부 provider를 직접 fetch하지 않는다.
- NBER 공식 구간, 모델 추정, 시장 시사점이 시각적·문구상 분리된다.
- 모바일과 데스크톱 Browser QA가 통과한다.

## 남은 구현 계획 결정

- 선택한 core series별 ALFRED/FRED 빈티지 취득 방식과 API-key 정책
- 빈티지 테이블을 기존 테이블 확장으로 할지 신규 테이블로 할지
- 비침체 사후 benchmark 생성 방식의 후보 실험
- 상태 엔진과 지평별 보정기의 최소 복잡도
- 확률 공개의 정량 문턱값
- V1 시장 시사점에서 사용할 공식·라이선스 가능한 금·달러·원자재 시계열

이 항목은 승인된 제품 방향을 바꾸지 않으며, 다음 구현 계획에서 조사·실험·검증 작업으로 분해한다.

## 근거

- [NBER Business Cycle Dating](https://www.nber.org/research/business-cycle-dating)
- [NBER Business Cycle Dating FAQ](https://www.nber.org/research/business-cycle-dating/business-cycle-dating-procedure-frequently-asked-questions)
- [Hamilton (1989), Markov Switching](https://doi.org/10.2307/1912559)
- [Stock and Watson, Diffusion Indexes](https://stock.scholars.harvard.edu/publications/macroeconomic-forecasting-using-diffusion-indexes)
- [Chauvet and Hamilton, Dating Business Cycle Turning Points](https://www.nber.org/papers/w11422)
- [Federal Reserve, Nowcasting GDP and Inflation](https://www.federalreserve.gov/econres/feds/nowcasting-gdp-and-inflation-the-real-time-informational-content-of-macroeconomic-data-releases.htm)
- [OECD Composite Leading Indicators](https://www.oecd.org/en/data/datasets/oecd-composite-leading-indicators-clis.html)
- [Chicago Fed CFNAI Methodology](https://www.chicagofed.org/research/data/cfnai/about)
- [Philadelphia Fed ADS Index](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/ads)
- [Dallas Fed Weekly Economic Index](https://www.dallasfed.org/research/wei)
- [ALFRED Download Data Help](https://alfred.stlouisfed.org/help/downloaddata)

세부 현재 제품 감사, 벤치마크, UI 패턴, 기능 후보, 위험과 전체 source note는 `.aiworkspace/note/finance/researches/active/2026-07-us-economic-cycle-regime-forecast/`에 유지한다.
