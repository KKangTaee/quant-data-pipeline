# Phase 4 Quality Factor Expansion Options

## 목적

- `Quality Snapshot` / `Quality Snapshot (Strict Annual)`의 다음 확장 후보 quality factor를 좁힌다.
- strict annual wider-universe 기준에서
  어떤 factor가 실제로 usable한지 coverage 관점으로 먼저 판단한다.

## 점검 기준

점검 대상:
- `US Statement Coverage 300`
- `annual`
- `nyse_factors_statement` latest snapshot 기준

비교한 후보:
- `roe`
- `gross_margin`
- `operating_margin`
- `debt_ratio`
- `roa`
- `net_margin`
- `asset_turnover`
- `current_ratio`
- `cash_ratio`
- `interest_coverage`
- `net_debt_to_equity`
- `debt_to_assets`
- `fcf_margin`
- `ocf_margin`
- `revenue_growth`
- `gross_profit_growth`
- `op_income_growth`
- `net_income_growth`

## latest snapshot coverage 요약

상위 coverage 후보:

| Factor | Coverage |
| --- | ---: |
| `roa` | `99.66%` |
| `net_income_growth` | `98.65%` |
| `asset_turnover` | `95.29%` |
| `net_margin` | `94.95%` |
| `ocf_margin` | `94.28%` |
| `revenue_growth` | `93.94%` |
| `roe` | `90.91%` |
| `current_ratio` | `85.19%` |

현재 기본 factor의 latest snapshot coverage:

| Factor | Coverage |
| --- | ---: |
| `roe` | `90.91%` |
| `operating_margin` | `75.08%` |
| `debt_ratio` | `61.28%` |
| `gross_margin` | `42.42%` |

## 해석

중요한 점:
- 현재 strict annual wide-universe 기준에서는
  `gross_margin`과 `debt_ratio`가 생각보다 결측이 많다.
- 따라서 factor를 “늘리는” 작업은 실제로는
  단순 추가가 아니라
  **기본 factor set 재정비**에 더 가깝다.

## 추천 옵션

### 옵션 A. Coverage-First Quality 5

구성:
- `roe`
- `roa`
- `net_margin`
- `asset_turnover`
- `current_ratio`

장점:
- latest snapshot coverage가 전체적으로 높다
- `NYSE 전체` 방향으로 넓힐 때도 가장 안정적이다
- quality 전략의 핵심 의미
  - 수익성
  - 자본 효율
  - 재무 안정성
  을 무난하게 담는다

단점:
- 현재 default와 의미가 조금 달라진다
- `gross_margin` / `debt_ratio`를 빼게 된다

### 옵션 B. Coverage-First Quality 6

구성:
- `roe`
- `roa`
- `net_margin`
- `asset_turnover`
- `current_ratio`
- `debt_to_assets`

장점:
- 옵션 A보다 leverage 관점을 조금 더 살린다
- `debt_ratio`보다 `debt_to_assets` coverage가 조금 낫다

단점:
- `debt_to_assets` coverage도 아주 높은 편은 아니다
- lower-is-better factor handling이 하나 더 늘어난다

### 옵션 C. Legacy Plus

구성:
- `roe`
- `gross_margin`
- `operating_margin`
- `debt_ratio`
- `roa`
- `net_margin`

장점:
- 현재 전략 의미를 덜 흔든다
- 기존 설명을 유지하기 쉽다

단점:
- `gross_margin`, `debt_ratio`가 여전히 coverage bottleneck이다
- `NYSE 전체` 확장 전에 결측 문제가 그대로 남을 가능성이 크다

## 추천

현재 단계에서는 **옵션 A**가 가장 자연스럽다.

이유:
- 지금 다음 큰 작업이
  `Coverage 300 -> 더 넓은 universe -> eventually NYSE 전체`
  방향이기 때문이다.
- 이 방향에서는 factor 의미도 중요하지만,
  **coverage 안정성**이 먼저다.

즉 추천 순서는:
1. `Coverage-First Quality 5`로 strict annual quality를 먼저 정리
2. `Coverage 100 / 300` 다시 비교
3. 괜찮으면 annual coverage를 더 넓힘
4. 그 다음 `NYSE 전체` 가능성 판단

## 현재 상태

- 선택된 기본안:
  - `옵션 A`
- 구현 상태:
  - `completed`

즉 현재 public `Quality Snapshot (Strict Annual)` 기본 factor set은
- `roe`
- `roa`
- `net_margin`
- `asset_turnover`
- `current_ratio`

로 갱신된 상태다.

## 상장 시점이 다른 종목 처리

현재 snapshot 전략 경로는 이미 아래를 처리한다.

- price input:
  - union calendar 사용
- rebalance 시점:
  - 현재 `Close`가 있는 종목만 selection 후보로 남김
- 결과:
  - 늦게 상장한 종목은 상장 전 구간에서 자동 제외
  - 해당 시점에 usable 종목이 하나도 없으면 현금 대기

즉:
- `A`는 2016 상장
- `B`는 2024 상장
- `2016 ~ 2025` 백테스트

같은 경우,
`2016 ~ 2023` 구간에서 `B`는 자연스럽게 제외되도록 현재 경로가 이미 설계되어 있다.
