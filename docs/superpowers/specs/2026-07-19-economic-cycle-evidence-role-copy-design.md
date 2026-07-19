# Economic Cycle Evidence Role-Aware Copy Design

## 목적

Economic Cycle의 `현재와 전망의 판단 근거` 패널에서 모든 factor를 `강화 / 약화 / 중립`으로 표시해 사용자가 `강화=좋음`으로 오해하는 문제를 해결한다.

현재 위치를 설명하는 실물 factor와 1·2개월 전망을 조정하는 factor의 역할을 분리하고, 각 행에 역할별 상태와 한 줄 해석을 표시한다.

## 현재 의미 계약

- Evidence의 `value`는 해당 factor를 구성하는 시계열을 방향 정규화하고 expanding robust scale로 표준화한 종합 점수다.
- `value > 0.15`는 종합 점수가 자기 과거 분포 기준보다 높은 편, `value < -0.15`는 낮은 편, 그 사이는 중립권이다.
- 이 값은 직전 달 대비 변화량이 아니다. 따라서 모든 factor를 `강화 / 약화`라고 부르는 것은 정확하지 않다.
- 현재 국면은 생산·소비와 고용·소득 factor를 사용한다.
- 1·2개월 전망은 현재 factor에 금융·선행 여건과 물가·정책 압력을 추가한다.

## 승인 범위

- 기존 Evidence 패널과 두 그룹 구조를 유지한다.
- 각 행의 상태 배지를 factor 역할에 맞는 문구로 바꾼다.
- 각 행에 동적으로 생성되는 한 줄 해석을 추가한다.
- 상단의 `강화 · 약화 · 중립` 안내를 `현재 수준과 전망 영향을 구분해 표시`로 바꾼다.
- factor 계산, 임계값, 모델 확률, 국면 좌표, 데이터 source와 payload 값은 변경하지 않는다.
- 세부 원시 지표 목록, 새 hover panel, 외부 데이터 수집은 이번 범위에 포함하지 않는다.

## 역할별 상태 매핑

### 현재 위치 factor

| Factor | 점수 방향 | 표시 상태 | Tone |
|---|---|---|---|
| 생산·소비 활동 | 양수 | `기준 이상` | positive-level |
| 생산·소비 활동 | 음수 | `기준 이하` | weak-level |
| 생산·소비 활동 | 중립 | `기준 부근` | neutral |
| 고용·소득 | 양수 | `기준 이상` | positive-level |
| 고용·소득 | 음수 | `기준 이하` | weak-level |
| 고용·소득 | 중립 | `기준 부근` | neutral |

한 줄 해석은 해당 종합점수가 자기 과거 기준보다 높거나 낮아 현재 경기 위치를 지지하거나 낮추는 근거임을 설명한다.

예시:

> 생산·소비 관련 지표의 종합점수가 자기 과거 기준보다 낮아 현재 경기 위치를 낮추는 근거입니다.

### 금융·선행 여건

| 점수 방향 | 표시 상태 | Tone |
|---|---|---|
| 양수 | `전망 지원` | support |
| 음수 | `전망 부담` | burden |
| 중립 | `영향 중립` | neutral |

예시:

> 금리차·신용스프레드·금융여건·선행지표 조합이 향후 1·2개월 경기 전망을 지지하는 방향입니다.

`금리·신용·금융여건`이라는 기존 label은 긴축 강화로 오해될 수 있으므로 factor 역할을 드러내는 `금융·선행 여건`으로 표시한다.

### 물가·정책 압력

| 점수 방향 | 표시 상태 | Tone |
|---|---|---|
| 양수 | `전망 부담` | burden |
| 음수 | `부담 완화` | support |
| 중립 | `영향 중립` | neutral |

예시:

> 근원물가·기대인플레이션·정책금리 조합의 압력이 높아 향후 1·2개월 경기 전망에 부담을 주는 방향입니다.

물가·정책 factor는 압력 factor이므로 양수일 때 초록색 `강화`가 아니라 주황색 `전망 부담`으로 표시한다.

## UI 구조

각 Evidence 행은 다음 세 층으로 구성한다.

1. factor 이름과 역할별 상태 배지
2. 기준월과 `FRED/ALFRED point-in-time` source
3. 역할과 방향을 설명하는 한 줄 해석

행 자체의 흰색 카드와 기존 간격은 유지하고, 별도 좌측 강조선은 추가하지 않는다.

색상은 다음처럼 사용한다.

- `기준 이상`, `전망 지원`, `부담 완화`: 연한 청록
- `기준 이하`: 연한 빨강
- `전망 부담`: 연한 주황
- `기준 부근`, `영향 중립`: 회색

색상만으로 의미를 전달하지 않고 항상 문구를 함께 표시한다.

모바일에서는 factor 이름과 배지를 첫 줄에 유지하고, source와 설명은 아래로 자연스럽게 줄바꿈한다. 수평 스크롤을 만들지 않는다.

## 구현 경계

- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
  - factor와 기존 direction을 역할별 상태, tone, 설명으로 변환하는 단일 helper를 둔다.
  - Evidence 행의 상태와 한 줄 해석을 렌더링한다.
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
  - 역할별 tone, 설명 문장, desktop/mobile 배치를 담당한다.
- `tests/test_market_context_economic_cycle.py`
  - 새 상단 안내, 역할별 상태 문구, 한 줄 해석 source contract를 검증한다.
- 필요할 경우 기존 service test는 payload의 factor/value/direction 계약이 바뀌지 않았음을 확인하는 회귀 검증만 추가한다.

## 완료 조건

- 생산·소비와 고용·소득은 `기준 이상 / 기준 이하 / 기준 부근`으로 읽힌다.
- 금융·선행 여건은 `전망 지원 / 전망 부담 / 영향 중립`으로 읽힌다.
- 물가·정책 압력 양수는 `전망 부담`, 음수는 `부담 완화`로 읽힌다.
- 각 행만 읽어도 현재 수준인지 전망 영향인지 이해할 수 있다.
- 모델 계산, payload 값, 확률과 국면 결과에는 변화가 없다.
- React production build, focused contract tests, desktop/mobile Browser QA와 수평 overflow 검증을 통과한다.

## 단계

1. 역할별 표시 helper와 상태 계약을 구현한다.
2. Evidence 행 문구·색상·반응형 UI를 적용한다.
3. focused tests, React build, desktop/mobile Browser QA와 Finance 문서 정렬을 완료한다.
