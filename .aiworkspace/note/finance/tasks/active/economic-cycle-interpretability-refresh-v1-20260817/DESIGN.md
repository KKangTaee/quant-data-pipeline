# Economic Cycle Interpretability & Refresh v1 Design

## 문제 진단

### Data Freshness

- 공식 국면은 RTDSM 월말 스냅샷인데 freshness는 legacy intramonth snapshot을 최신 평일과 비교한다.
- 최신 공식 월말 결과가 있어도 월중 row가 없으면 매일 `MISSING`이 된다.
- 수동 버튼은 legacy FRED 17지표 수집과 intramonth materialization을 실행해 현재 공식 국면 소유 경계와 다르다.
- React `collecting`은 클릭 시 true가 된 뒤 새 `refresh_result`를 받아도 false로 돌아가지 않는다.

### 현재 국면과 판단 근거

- 2026-07-31 공식 confirmed state는 회복이고, 2026-01 전환 확정 후 7개월 유지다.
- 최근 변화는 현재 3개월 평활 수준을 1·3·6개월 전과 비교한 값이지만 UI가 비교 월을 밝히지 않는다.
- 생산에 사용되는 RTDSM 핵심지표는 `IPT`, `H`, `EMPLOY`, `RUC` 네 개지만 UI 분모가 8로 고정되어 있다.
- `top_evidence_json`은 자산 경로 호환을 위해 이전 8지표 근거를 보존하므로 RTDSM 현재 상태와 값이 일치하지 않는다.
- `confidence`, `revision_sensitivity`, `available_series`가 production observed state에 없어서 `제한`, `비교 불가`, `-`가 기본값으로 노출된다.
- RUC는 분기 자료인데 120일 기준을 하루 넘긴 것만으로 stale 처리되어 status가 지나치게 보수적으로 제한된다.

## 승인된 사용자 흐름

1. **Data Freshness**: 공식 경기 국면 월말, RTDSM 가용성, 자산 데이터 최신일을 별도 칸으로 읽는다.
2. **현재 관측 국면**: 회복/확장/둔화/위축과 지속기간을 먼저 보고, 1·3·6개월의 정확한 비교 월과 변화를 본다.
3. **Cycle route**: 표준 순환 `회복 → 확장 → 둔화 → 위축 → 회복`과 현재 데이터에서 가장 유력한 조건부 경로를 동시에 본다.
4. **현재 진단과 향후 방향**: 전환압력과 `전환 발생 시` 목적지 분포를 분리하고 상승·하락 driver를 각각 본다.
5. **판단 근거**: 종합 판단을 먼저 읽고 RTDSM 현재 위치의 직접 근거를 확인한다.
6. **최근 12개월**: 색 범례와 전환 확인 월을 확인하고 월별 세부사항은 hover/focus로 본다.
7. **자산별 확인 포인트**: 공통 경제 배경은 한 번만 보고, 기존 자산 카드 전체 구조를 그대로 사용한다.

## 데이터 계약

### 공식 freshness

- 기준일 `reference_date`에서 가장 최근에 완전히 닫힌 calendar month-end를 `target_as_of_date`로 사용한다.
- `current` snapshot의 `as_of_date >= target_as_of_date`이면 공식 국면은 `READY`다.
- 자산 freshness는 기존 daily/weekly cadence-aware 계약을 독립적으로 유지한다.
- 액션은 `cycle_snapshot` 또는 `asset_pathways` 중 실제 stale scope가 있을 때만 노출한다.

### 수동 공식 갱신

- 경기 scope: Philadelphia Fed RTDSM 4개 원천 수집 → latest closed month confirmed production publication → DB postcondition 확인.
- 자산 scope: 기존 asset pathway refresh를 그대로 사용한다.
- 각 scope는 독립 성공/실패로 집계하고 성공한 scope만 cache invalidation 대상으로 반환한다.

### RTDSM 품질

- observed state에 `available_series`, `total_series=4`, `series_quality[]`를 저장한다.
- `series_quality[]`는 series id, cadence, latest observation date, freshness/lag 상태를 포함한다.
- 분기 RUC의 정상 발표 간격을 고려해 stale 허용기간을 150일로 사용한다. 값은 존재하지만 분기 시차가 있는 상태는 UI에서 `발표 시차`로 설명한다.
- 수정 민감도 값이 없으면 오류가 아니라 `향후 빈티지 비교 대기`로 설명한다.

### 현재 판단 근거 분리

- 화면의 `evidence`는 current observed state의 `activity_score`, `labor_income_score`, RTDSM source series에서 생성한다.
- 자산 pathway는 호환성 유지를 위해 기존 economic state 계산을 계속 사용한다.
- 즉, 현재 국면 설명과 자산 pathway 배경을 별도 read contract로 취급하며 서로의 계산을 덮어쓰지 않는다.

## UI 설계

### 색과 시각 계층

- 기본 강조색은 기존 recovery 계열의 하늘색을 사용한다.
- 확장·둔화·위축 고유 색은 legend와 phase node에만 제한적으로 유지한다.
- 양수/음수 색상은 좋음/나쁨이 아니라 방향이다. 양수는 녹색 `▲`, 음수는 빨간색 `▼`, 0은 회색 `—`로 표시하고 범례를 둔다.

### Cycle route

- route visual과 우측 설명을 `minmax(0, 1.35fr) / minmax(280px, .65fr)`로 배치한다.
- SVG는 정사각형 viewBox와 동일 반경 node를 사용해 찌그러짐을 방지한다.
- 우측 `현재 공식 관측`, `전환이 발생한다면` 카드는 같은 grid row 높이를 사용한다.
- 기본 순환 track은 옅은 하늘색, 조건부 최우선 경로는 amber dashed arrow로 표시한다.

### 자산 카드

- `MarketImplicationCard` 안의 `EconomicStateBlock`만 제거한다.
- 자산 섹션 상단에 첫 market implication의 동일 economic state를 한 번만 표시한다.
- `CurrentMovementBlock`과 `ObservedPathwaysBlock`은 기존 수치와 설명을 모두 유지한다.
- `SeriesMetrics`의 21d/63d를 독립 metric cell로 렌더링하고 방향색/arrow를 적용한다.
- commodities assets는 WTI와 copper만 포함하며 standalone gold group은 유지한다.

## 오류와 경계 처리

- 공식 snapshot read error와 자산 freshness error는 scope별 상태로 표시한다.
- 갱신 중 React가 새로운 결과나 freshness snapshot을 받으면 collecting을 반드시 종료한다.
- 반올림 결과가 `-0.0`이면 0으로 정규화하고 회색으로 표시한다.
- 전환 목적지 분포는 `전환 발생 조건부` 문구 없이 단독 확률로 노출하지 않는다.
- 좁은 화면에서 route, 판단 카드, 1·3·6개월, 자산 metric cell은 한 열로 내려간다.

