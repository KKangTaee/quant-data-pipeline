# Phase 4 Strict Annual Public Universe Decision Current DB

## 목적

- strict annual family의 공식 public default universe를 현재 DB 기준으로 다시 고정한다.

## 결정

현재 public default는 그대로 유지한다.

- single-strategy default:
  - `US Statement Coverage 300`
- compare default:
  - `US Statement Coverage 100`

그리고 아래 preset은 노출하되 staged operator preset으로 해석한다.

- `US Statement Coverage 500`
- `US Statement Coverage 1000`

## 이유

- `300`은 이미 strict annual public candidate 검증에 충분한 coverage / history / runtime 균형을 보여줬다.
- current DB audit에서 `500`, `1000`은 아직
  - statement coverage가 충분하지 않고
  - price freshness spread도 더 크다.
- closeout refresh 이후에도 `Coverage 1000`에는
  stale symbol `4`개(`CADE`, `CMA`, `DAY`, `CFLT`)와
  `49d` freshness spread가 남아 있다.
- 따라서 지금 `500` 또는 `1000`을 public default로 올리면,
  전략 자체보다 operator freshness/coverage 상태에 더 크게 흔들리게 된다.

## 다음 조건

아래가 충족되면 `500` 재평가가 가능하다.

- strict annual covered symbol count가 의미 있게 증가할 것
- `common_latest_date`가 public run target end에 충분히 근접할 것
- runtime이 single-strategy public default로 허용 가능한 수준일 것

## 현재 결론

- strict annual public default:
  - `300` 유지
- wider preset:
  - operator / staging only
- NYSE 전체:
  - 아직 시기상조
