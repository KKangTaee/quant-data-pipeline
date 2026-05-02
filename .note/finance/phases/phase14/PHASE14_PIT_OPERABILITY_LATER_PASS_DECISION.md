# Phase 14 PIT Operability Later-Pass Decision

## 목적

- ETF operability를 current snapshot overlay로 계속 둘지,
  아니면 actual block rule까지 올리려면 무엇이 더 필요한지 정리한다.
- 동시에
  **왜 Phase 14에서는 actual block rule 승격을 하지 않는지**
  를 문서로 고정한다.

## 이번 문서의 한 줄 결론

- 현재 ETF operability는
  **current snapshot diagnostic**으로는 유용하다.
- 하지만 PIT/history가 없기 때문에
  **actual block rule로 승격하기에는 아직 이르다.**

## 1. 현재 구현 상태

현재 ETF operability surface는
`load_asset_profile_status_summary(tickers)`를 통해
current snapshot row를 읽고,
아래 값을 계산한다.

- `aum_b`
- `bid_ask_spread_pct`
- `etf_operability_clean_coverage`
- `etf_operability_data_coverage`
- `etf_operability_status`

즉 현재 operability는
**“지금 시점 snapshot 기준으로 ETF universe가 얼마나 운용 가능해 보이는가”**
를 읽는 diagnostic layer다.

## 2. 왜 PIT/history가 아직 없다고 보는가

현재 경로의 한계는 분명하다.

### 2-1. schema가 current snapshot 중심이다

- `nyse_asset_profile`는 append-only history가 아니라
  current row UPSERT 구조다.
- `last_collected_at`은 있지만,
  `as_of` 기반 historical snapshot key가 없다.

### 2-2. loader가 as-of lookup을 지원하지 않는다

- 현재 loader는 rebalance date 기준 nearest snapshot을 고르지 않는다.
- 즉 `2018-03 rebalance` 시점의 operability를
  그 시점 기준으로 다시 읽을 수 없다.

### 2-3. history에 raw snapshot이 안 남는다

- backtest history에는 최종 `etf_operability_status`와 `gate_snapshot`은 남는다.
- 하지만 raw asset profile snapshot 자체는 남지 않는다.

## 3. 그래서 무엇이 문제인가

현재 snapshot operability를 바로 actual block rule로 올리면,

- 과거 리밸런싱 시점의 운용 가능성
- 현재 snapshot warning
- 진짜 historical block signal

이 서로 섞인다.

즉 지금 구조에서는
“현재 데이터가 비어 있다”와
“과거에도 실제로 운용 불가능했다”
를 분리해서 말할 수 없다.

## 4. actual block rule 승격을 위해 필요한 것

### 4-1. historical asset-profile snapshot 저장

후보:

- `nyse_asset_profile_history` append-only table

최소 필드 후보:

- `symbol`
- `kind`
- `quote_type`
- `status`
- `total_assets`
- `bid`
- `ask`
- `collected_at` 또는 `as_of`

### 4-2. PIT loader

예시 목적:

- `load_etf_operability_snapshot(..., as_of_date=rebalance_date)`

즉 rebalance 시점 기준 nearest available snapshot을 읽을 수 있어야 한다.

### 4-3. runtime source split

나중에는 meta에 아래 구분이 필요하다.

- `operability_source = current_snapshot`
- `operability_source = pit_snapshot`

그리고 current diagnostic과 actual block contract를 분리해야 한다.

### 4-4. history raw evidence 강화

run history에는 적어도 아래가 같이 남는 것이 좋다.

- `operability_source`
- `operability_as_of`
- `data_coverage`
- `clean_coverage`
- missing-data symbol summary

## 5. Phase 14 판단

Phase 14에서는

- current snapshot operability가 왜 repeated hold를 만들었는지
- 그 해석 규칙이 어디서 watch/caution으로 갈리는지

까지는 충분히 설명됐다.

하지만 actual block rule 승격은
PIT/history implementation 전에는 섣부르다.

따라서 이번 phase에서는
**snapshot overlay와 PIT actual block contract의 경계를 문서화하고,
승격은 later pass backlog로 남기는 것이 맞다.**

## 6. 다음 phase handoff

다음 phase에서 실제 구현 질문은 아래 순서가 자연스럽다.

1. historical asset-profile snapshot schema 설계
2. append-only collector path
3. PIT loader
4. runtime source split
5. actual block rule experiment

