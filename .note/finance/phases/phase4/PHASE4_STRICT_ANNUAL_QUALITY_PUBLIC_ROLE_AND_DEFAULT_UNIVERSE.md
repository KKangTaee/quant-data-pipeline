# Phase 4 Strict Annual Quality Public Role And Default Universe

## 목적

- `Quality Snapshot (Strict Annual)`의 public 역할을
  sample-universe trial이 아니라,
  annual statement coverage가 검증된 stock-universe candidate로 재정의한다.
- broad quality path와 strict annual quality path가
  UI에서 서로 다른 의미를 갖도록 기본 preset과 설명을 분리한다.

## 왜 이 작업이 필요했는가

- 기존 strict annual form은 여전히 `Big Tech Quality Trial`과 비슷한 sample-universe 감각을 유지하고 있었다.
- 그런데 annual coverage stage 2 결과로,
  `United States` issuer + `market_cap DESC` top `300` 기준
  strict annual coverage가 `297 / 300`까지 확인되었다.
- 즉 strict annual path는 더 이상
  `AAPL / MSFT / GOOG` smoke trial로만 설명할 필요가 없는 상태가 되었다.

## 반영한 원칙

### broad quality

- 역할:
  - research-oriented public factor path
- 기본 preset:
  - `Big Tech Quality Trial`

### strict annual quality

- 역할:
  - statement-ledger-backed public candidate path
- single-strategy 기본 preset:
  - `US Statement Coverage 300`
- compare 기본 preset:
  - `US Statement Coverage 100`
  - compare는 multi-strategy run이므로 응답성을 위해 single default보다 가볍게 둔다.
- 추가 smoke preset:
  - `Big Tech Strict Trial`

## 구현한 것

- `app/web/pages/backtest.py`
  - `QUALITY_BROAD_PRESETS`
  - `QUALITY_STRICT_PRESETS`
  로 분리
- strict annual form은 이제
  `QUALITY_STRICT_PRESETS`를 사용한다.
- strict annual single form의 기본 preset은
  `US Statement Coverage 300`
  이다.
- strict annual compare default는
  `US Statement Coverage 100`
  으로 고정했다.
- prefill / history load도
  strict annual preset 집합을 기준으로 해석하도록 정리했다.

## 현재 의미

- `Quality Snapshot`
  - broad / research path
- `Quality Snapshot (Strict Annual)`
  - verified wider stock universe를 가진 strict public candidate path

즉 이제 두 전략은 이름만 다른 것이 아니라,
source, strictness, default universe까지 분리된 상태다.
