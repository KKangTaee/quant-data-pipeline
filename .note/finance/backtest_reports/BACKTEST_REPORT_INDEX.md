# Backtest Report Index

## 목적

이 문서는 `.note/finance/backtest_reports/` 아래의 결과 리포트 문서를 빠르게 찾기 위한 인덱스다.

## 먼저 볼 문서

- `strategies/README.md`
  - 전략별 허브 문서 안내
- `strategies/GTAA.md`
  - `GTAA` 결과 허브
- `strategies/QUALITY_STRICT_ANNUAL.md`
  - `Quality > Strict Annual` 결과 허브
- `strategies/VALUE_STRICT_ANNUAL.md`
  - `Value > Strict Annual` 결과 허브
- `strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - strongest `Value > Strict Annual` 후보 하나를 전략 구성 중심으로 바로 읽는 one-pager
- `strategies/QUALITY_VALUE_STRICT_ANNUAL.md`
  - `Quality + Value > Strict Annual` 결과 허브

## Phase 13 Raw Archive

- `phase13/README.md`
  - Phase 13 raw report archive 안내 문서
  - 전략 허브에서 연결된 세부 report를 phase 기준으로 모아둔 위치

## Phase 14 Raw Archive

- `phase14/README.md`
  - Phase 14 current-runtime refresh archive 안내 문서
  - calibration 이후 strict annual family를 다시 돌려본 결과 문서 위치
- `phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md`
  - Phase 14 calibration 이후 `Quality / Value / Quality + Value` strict annual family를 current practical contract로 다시 돌려,
    각 family의 strongest non-hold current candidate를 고정한 refresh 문서

## 운영 메모

앞으로 새 report를 만들 때는:

1. 먼저 `strategies/` 아래 전략 허브에 반영한다
2. 세부 결과 원문은 phase archive에 둔다
3. 여기 index에는 허브와 archive entry를 연결한다
