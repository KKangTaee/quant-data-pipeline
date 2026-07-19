# Economic Cycle Rates, Equities, and Commodities Pathways Design

Status: Draft for written review
Design approved in conversation: 2026-07-17
Implementation scope: roadmap stages 3-5
Depends on: `2026-07-17-economic-cycle-multichannel-asset-interpretation-design.md`

## 이걸 하는 이유

1·2차는 공통 시계열 판정기와 금·달러 다중 경로 파일럿을 구현했다. 이 구조는 미국 경제상태를 자산가격의 정답으로 두지 않고, 측정된 시장 경로와 실제 가격을 나란히 보여준다.

3·4·5차는 같은 원칙을 채권·금리, S&P 500, 원자재로 확장한다. 자산마다 정보 구조가 다르므로 하나의 우호·부담 점수로 합치지 않는다. 사용자는 각 카드에서 다음을 끝낼 수 있어야 한다.

1. 자산 또는 금리 구조가 최근 1주·1개월·3개월 동안 어떻게 움직였는지 확인한다.
2. 같은 기간에 어떤 측정 경로가 함께 움직였는지 확인한다.
3. 경로가 같은 방향인지 엇갈리는지 정량 문장으로 읽는다.
4. 향후 1·2개월에 무엇을 다시 확인해야 해석이 유지되거나 바뀌는지 확인한다.

이 기능은 가격 원인을 증명하거나 가격·수익률을 예측하지 않는다. 미래 영역은 현재 관측값의 연장이 아니라 `다음 확인 조건`이다.

## 승인된 범위

### 3차 — 채권·금리 구조

- 미국 2년물 금리
- 미국 10년물 금리
- 10년-2년 금리차
- 10년 실질금리와 10년 기대인플레이션
- 채권 가격과 국채선물은 이번 차수에서 제외

### 4차 — 주식

- 미국 주식시장의 대표값은 S&P 500 단일 지수
- 개별주식, Nasdaq-100, Russell 2000은 제외
- 실질금리, 신용스프레드, 변동성, 실제 지수 이익을 병렬 경로로 사용

### 5차 — 원자재

- 에너지: WTI 원유
- 산업금속: 구리
- 귀금속: 금
- 금은 2차 결과를 재계산하지 않고 동일 read model을 재사용
- 천연가스와 은은 제외

## 선택한 접근

### 관측 경로 병렬 설명

`현재 움직임 -> 함께 관찰된 경로 -> 현재 해석 -> 향후 확인 조건` 순서로 표시한다.

대안으로 검토한 가중 종합점수는 가중치가 자의적이고 단정적인 결론으로 회귀할 위험이 있어 채택하지 않는다. 원자료만 나열하는 방식은 투명하지만 사용자의 해석 부담이 커 채택하지 않는다.

## 공통 제품 계약

### 현재 움직임

- 가격·지수: 5·21·63거래일 수익률
- 금리·스프레드: 5·21·63거래일 basis-point 변화
- 화면 표기: 1주·1개월·3개월
- 기존 공통 판정기의 reference date, freshness, materiality, history 규칙을 그대로 사용

### 함께 관찰된 경로

- 각 경로를 별도 행 또는 블록으로 표시한다.
- 경로를 더하거나 빼서 종합점수를 만들지 않는다.
- 방향이 작으면 `통상 변동 범위`, 기간끼리 충돌하면 `기간별 방향 혼재`, 데이터가 없으면 reason code와 함께 `자료 부족`으로 둔다.
- 저장 데이터가 없는 지정학, 정책 의도, 투자자 심리, 수급을 문장에 삽입하지 않는다.

### 현재 해석

허용 문장:

- `S&P 500은 최근 1개월 상승했고 같은 기간 실질금리는 상승했습니다.`
- `2년물은 하락했지만 10년물은 상승해 10년-2년 금리차가 확대됐습니다.`
- `WTI 가격 하락과 함께 원유 재고 증가가 관찰됐습니다.`

금지 문장:

- `실질금리 상승 때문에 S&P 500이 하락했습니다.`
- `재고 증가가 원유 하락의 원인입니다.`
- `다음 달 구리가 상승할 확률은 70%입니다.`
- `현재 국면에서는 이 자산을 매수해야 합니다.`

### 향후 1·2개월 확인 조건

- 미래 가격 방향을 생성하지 않는다.
- 현재 해석을 유지하거나 바꾸는 관측 조건만 표시한다.
- 조건은 연결된 시계열과 direction semantics로 결정론적으로 생성한다.
- 예: `2년물 하락이 이어지는지`, `신용스프레드와 VIX가 같은 방향으로 움직이는지`, `원유 재고 증가가 반전되는지`.

## 3차 상세 설계 — 채권·금리 구조

### 데이터

| Series | 의미 | 단위 | 역할 |
|---|---|---|---|
| `DGS2` | 미국 2년 국채 수익률 | percent | 단기 금리 구조 |
| `DGS10` | 미국 10년 국채 수익률 | percent | 장기 금리 구조 |
| derived `DGS10 - DGS2` | 10년-2년 금리차 | basis points | steepening / flattening |
| `DFII10` | 미국 10년 실질수익률 | percent | 10년물 실질금리 구성 경로 |
| `T10YIE` | 미국 10년 기대인플레이션 | percent | 10년물 기대인플레이션 구성 경로 |

`DGS2`, `DGS10`, `DFII10`은 1·2차 수집 계약을 재사용한다. `T10YIE`는 기존 economic-cycle catalog 정의를 macro observation 수집 범위로 연결한다.

금리차는 별도 provider 시계열을 요구하지 않고 동일 기준일의 저장된 `DGS10 - DGS2`로 계산한다. 한쪽이 stale 또는 unavailable이면 금리차도 unavailable이다.

### 해석 계약

- 2년물: 수준과 기간별 bp 변화만 `단기금리`로 표현한다. 연준의 의도나 확정된 정책경로로 번역하지 않는다.
- 10년물: 수준과 기간별 bp 변화를 표시한다.
- 금리차: 양수·음수 수준과 확대·축소를 구분한다.
- `steepening`: 10년-2년 금리차가 material하게 확대
- `flattening`: 10년-2년 금리차가 material하게 축소
- 역전 해소와 정상화는 level sign이 음수에서 양수로 바뀐 경우에만 사용한다.

### 10년물 구성 경로

같은 horizon의 `DFII10`과 `T10YIE` 변화를 병렬로 보여준다. 이를 완전한 수학적 attribution이나 원인 분해로 부르지 않는다.

- 둘 다 상승: `실질금리와 기대인플레이션이 함께 상승`
- 둘 다 하락: `실질금리와 기대인플레이션이 함께 하락`
- 반대 방향: `10년물 구성 경로가 엇갈림`
- 하나가 neutral/unavailable: 계산 가능한 경로만 표시하고 범위를 제한

## 4차 상세 설계 — S&P 500

### 데이터

| 데이터 | 의미 | 역할 |
|---|---|---|
| `^GSPC` 우선, `SPY` fallback | S&P 500 가격 | 실제 지수 움직임 |
| `DFII10` | 10년 실질금리 | 할인율 관련 관측 경로 |
| `BAA10Y` | Baa 회사채-10년 국채 스프레드 | 신용여건 관측 경로 |
| `VIXCLS` | VIX | 주식시장 변동성 관측 경로 |
| `sp500_index_earnings` actual rows | S&P 500 실제 EPS | 이익 경로 |

가격은 기존 DB price boundary를 사용한다. `^GSPC`와 `SPY`가 모두 있으면 지수 자체인 `^GSPC`를 우선하고, fallback 사용 여부를 provenance에 남긴다.

EPS는 완료된 actual 분기만 사용한다. 추정 EPS, SEP scenario, 미래 컨센서스는 이번 카드에서 사용하지 않는다. 동일한 4개 완료 분기로 TTM EPS를 구성할 수 있을 때만 전년 동기 대비 TTM EPS 성장률을 계산한다.

### 경로 표현

- 실제 가격 흐름: S&P 500 1주·1개월·3개월 수익률
- 실질금리: 같은 기간 bp 변화
- 신용여건: BAA10Y 같은 기간 bp 변화
- 변동성: VIX 같은 기간 percent 변화 또는 기존 evaluator가 정한 일관된 변화 단위
- 이익: 완료 분기 기준 TTM EPS와 전년 대비 변화

실질금리·신용스프레드·VIX·EPS를 `상승 요인/하락 요인`으로 고정 합산하지 않는다. 각 경로의 실제 변화와 가격 흐름의 동시 관찰만 설명한다.

EPS는 일별 가격 horizon과 억지로 맞추지 않는다. 카드에 `최근 완료 분기 기준`과 basis date를 명시하고, 1·2개월 확인 조건에서도 새 actual 분기가 발표되기 전에는 EPS 방향을 반복 추정하지 않는다.

## 5차 상세 설계 — WTI·구리·금

### 공통 가격 데이터

| Symbol | 의미 | 역할 |
|---|---|---|
| `CL=F` | WTI 연속선물 | 원유 가격 움직임 |
| `HG=F` | 구리 연속선물 | 구리 가격 움직임 |
| `GC=F` | 금 연속선물 | 2차 금 가격 움직임 재사용 |
| `DX-Y.NYB` | 달러인덱스 | 원자재 공통 달러 경로 |

연속선물의 계약 교체 효과가 포함될 수 있다는 제한을 provenance에 유지한다.

### WTI

WTI는 가격만으로 수급을 설명하지 않는다. 공식 주간 EIA 계열 가운데 기존 FRED/ALFRED ingestion boundary로 저장 가능한 원유 재고, 미국 원유 생산, 석유제품 공급 또는 정제 투입량을 사용한다.

- 가격: 1주·1개월·3개월 수익률
- 재고: 최근 4주 변화와 전년 동기 대비 변화
- 생산: 최근 4주 변화
- 수요 proxy: 석유제품 공급 또는 정제 투입량의 최근 4주 변화
- 달러: 1개월·3개월 변화

주간 수급 지표는 일별 가격과 같은 거래일 horizon으로 가장하지 않는다. UI에 `최근 4주`와 observation date를 표시한다.

### 구리

구리는 글로벌 자산이므로 미국 경제지표 하나로 글로벌 수요를 단정하지 않는다.

- 가격: `HG=F` 1주·1개월·3개월 수익률
- 달러: 1개월·3개월 변화
- 미국 산업활동: canonical 생산·소비 factor 또는 underlying series의 최근 공개 변화
- 글로벌 활동: 신뢰 가능한 공식·무료·저장 가능한 시계열이 구현 시점에 검증된 경우만 추가

글로벌 활동 경로가 없으면 coverage는 `PARTIAL`이며 narrative에 `연결된 산업활동 자료는 미국 중심`이라고 표시한다. 빈 경로를 임의의 설명으로 채우지 않는다.

### 금

2차 `gold` pathway read model을 그대로 원자재 섹션에서 참조한다. 실질금리, 달러, 단기금리, 위험회피, 가격을 다시 계산하지 않는다. 같은 기준일에 금 카드와 원자재 금 요약이 서로 다른 상태를 만들 수 없게 한다.

## 화면 구조

### 자산별 카드

각 카드는 다음 구조를 공유한다.

1. 제목과 기준일
2. `현재 움직임` — 1주·1개월·3개월
3. `함께 관찰된 경로` — 측정값별 흰색 행 또는 중립적인 연한 배경 블록
4. `현재 해석` — 숫자에서 결정론적으로 생성한 2~4문장
5. `향후 1·2개월 확인 조건` — 최대 3개
6. 작은 provenance / 판단 범위 문구

좌측 장식선은 사용하지 않는다. 상승·하락을 강한 결론색으로 칠하지 않고, 블록 배경의 낮은 채도로 구분한다. 기존 금·달러 카드도 같은 정보명으로 정렬하되 데이터와 판정 결과는 유지한다.

### 섹션 배치

- `채권·금리 구조`: 하나의 넓은 카드 안에 2년물, 10년물, 금리차, 10년물 구성 경로
- `S&P 500`: 가격 흐름과 네 관측 경로를 하나의 카드에 표시
- `원자재`: WTI, 구리, 금을 각각 독립 카드로 표시
- 모바일에서는 모든 카드와 경로 행을 단일 열로 쌓는다.

## Read Model 계약

기존 `market_implications`의 asset group 순서와 호환성을 유지한다.

각 연결 자산은 최소 다음 필드를 가진다.

```text
asset_group
analysis_status
coverage_status
as_of_date
current_movement
observed_pathways[]
current_interpretation[]
next_check_conditions[]
provenance[]
limitations[]
```

세부 자산이 필요한 원자재는 `assets[]` 아래 `wti`, `copper`, `gold`를 둔다. 금 subasset은 기존 gold context의 reference를 normalize해 넣는다.

예상 상태:

- `READY`: 필수 가격과 핵심 경로가 모두 fresh
- `PARTIAL`: 가격은 있으나 일부 핵심 경로가 없거나 범위가 제한됨
- `UNAVAILABLE`: 필수 가격 또는 금리 구조를 만들 데이터가 없음

`PATHWAYS_NOT_CONNECTED`는 3·4·5차 구현이 완료되면 해당 그룹에서 더 이상 반환하지 않는다.

## 아키텍처와 파일 경계

```text
provider collection
  -> finance_meta / finance_price DB
  -> finance/loaders/*
  -> finance/economic_cycle_asset_pathways.py
  -> finance/economic_cycle_interpretation.py
  -> app/services/overview/economic_cycle.py
  -> Economic Cycle React workbench
```

예상 변경 범위:

- `finance/data/macro.py`: 승인된 추가 공식 시계열 catalog
- `finance/loaders/economic_cycle_assets.py`: 가격·금리·수급·EPS DB read
- `finance/economic_cycle_asset_pathways.py`: 금리 구조, S&P 500, WTI, 구리 builder
- `finance/economic_cycle_interpretation.py`: placeholder를 연결 결과로 교체
- `app/services/overview/economic_cycle.py`: read model 전달과 failure isolation
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- focused Python tests와 React build artifact

UI는 provider, FRED, EIA, yfinance를 직접 호출하지 않는다. provider refresh failure는 기존 저장값을 삭제하지 않으며 stale 자료는 경로 판정에서 제외한다.

## 오류와 제한 처리

- 한 자산 실패가 경제사이클 확률, 다른 자산 카드, 기존 금·달러 카드를 막지 않는다.
- 가격 누락과 경로 누락을 구분한다.
- 일별·주별·분기별 series를 같은 기준일처럼 표시하지 않는다.
- 휴장일 차이는 각 series의 최신 유효 관측일로 보존한다.
- actual EPS가 4개 완료 분기 미만이면 이익 경로만 unavailable이다.
- WTI 수급 series가 stale이면 가격 흐름은 표시하고 수급 설명만 제외한다.
- 구리는 글로벌 활동 자료가 없으면 partial을 정상적인 상태로 취급한다.
- 금은 기존 gold context가 unavailable이면 재계산 fallback을 만들지 않는다.

## 검증 전략

### 단위 테스트

- 2년·10년·금리차 horizon 변화와 steepening/flattening
- 금리차 한쪽 stale 시 unavailable
- 실질금리·기대인플레이션 병렬 경로 조합
- S&P 500 `^GSPC` 우선, `SPY` fallback 및 provenance
- actual TTM EPS 4분기/전년 비교와 불충분 분기 제한
- WTI 일별 가격과 주간 수급 horizon 분리
- 구리 partial coverage
- 금 read model 재사용 동일성
- 인과·예측 금지 문구 회귀 테스트

### 서비스 테스트

- `rates`, `equities`, `commodities`가 더 이상 `PATHWAYS_NOT_CONNECTED`가 아님
- 한 그룹 loader failure가 나머지 그룹을 막지 않음
- historical `as_of_date` 이후 관측값을 사용하지 않음
- mixed frequency 기준일과 provenance 보존

### UI 테스트

- 데스크톱과 모바일 정보 순서
- 1주·1개월·3개월 및 주간·분기 basis label 구분
- hover/focus는 상세 날짜·값만 추가하고 핵심 내용을 숨기지 않음
- 좌측 장식선 없음
- 금·달러·3~5차 카드의 공통 용어 정렬

### Actual data QA

- macro와 futures/price collection 후 DB row와 최신 observation date 확인
- 각 카드의 실제 값과 source table sample 대조
- React production build
- Streamlit 실제 화면 desktop/mobile browser QA
- QA 스크린샷은 generated artifact로 남기고 commit하지 않음

## 완료 조건

1. 3차 채권·금리 구조가 2년물·10년물·10년-2년 금리차를 실제 저장 데이터로 표시한다.
2. 10년물의 실질금리·기대인플레이션 경로를 인과 분해 없이 병렬 설명한다.
3. 4차 S&P 500이 실제 가격, 실질금리, 신용스프레드, VIX, actual EPS를 가능한 범위에서 표시한다.
4. 5차가 WTI·구리·금을 독립적으로 표시하고 금 결과를 재사용한다.
5. 모든 설명은 숫자로 재현 가능하며 인과·확률·매매 결론을 만들지 않는다.
6. 누락·stale·빈 history를 추정으로 채우지 않는다.
7. 기존 경제사이클 확률·publication gate·금·달러 결과가 회귀하지 않는다.
8. focused tests, React build, actual data browser QA가 통과한다.

## 명시적으로 하지 않는 일

- 자산군 종합점수 또는 추천 순위
- 가격 상승·하락 확률
- 매수·매도·비중조절 신호
- 뉴스·지정학·정책 발언의 비정형 분석
- 채권 가격·국채선물 분석
- Nasdaq-100·Russell 2000·개별주식 분석
- 천연가스·은 추가
- 구리의 글로벌 수요를 미국 지표만으로 단정
- provider를 UI에서 직접 호출
