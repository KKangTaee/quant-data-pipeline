# Phase 6 Test Checklist

## 목적

- Phase 6 first pass에서 추가된
  - `Market Regime Overlay`
  - `Quality Snapshot (Strict Quarterly Prototype)`
  를 수동으로 검증하기 위한 체크리스트다.

## 1. Single Strategy - Annual Strict Quality

- `Backtest > Single Strategy`
- 전략:
  - `Quality Snapshot (Strict Annual)`
- 확인:
  - `Enable Market Regime Overlay` 입력이 보이는지
  - `Market Regime Window`
  - `Market Regime Benchmark`
  가 함께 보이는지
  - overlay가 꺼져 있어도
    - `Window`
    - `Benchmark`
    값을 미리 수정할 수 있는지
  - 도움말에서
    - `Window 200 = 200거래일 이동평균`
    의미가 읽히는지

### 1-1. Overlay Off

- overlay off로 1회 실행
- 확인:
  - 실행 성공
  - `Selection History` 정상
  - `Interpretation Summary` 정상
  - `Market Regime Events`가 비활성 또는 비어 있는지

### 1-2. Overlay On

- overlay on
- benchmark:
  - `SPY`
- window:
  - `200`
- 확인:
  - 실행 성공
  - `Meta > Execution Context`에 market regime 정보가 보이는지
  - `Selection History -> Interpretation`에
    - `Regime Blocked Events`
    - `Regime Cash Rebalances`
    - `Market Regime Events`
    가 보이는지

## 2. Single Strategy - Annual Strict Value

- 전략:
  - `Value Snapshot (Strict Annual)`
- preset:
  - `US Statement Coverage 100` 또는 `300`
- 확인:
  - market regime 입력이 보이는지
  - overlay on/off 둘 다 정상 실행되는지
  - interpretation에서 regime 관련 지표가 자연스럽게 보이는지

## 3. Single Strategy - Annual Strict Quality + Value

- 전략:
  - `Quality + Value Snapshot (Strict Annual)`
- 확인:
  - quality/value factor set과 market regime overlay가 함께 노출되는지
  - overlay on/off 실행이 둘 다 되는지
  - `Selection History`에 regime blocked 정보가 보이는지

## 4. Single Strategy - Quarterly Prototype

- 전략:
  - `Quality Snapshot (Strict Quarterly Prototype)`
- 확인:
  - single strategy 목록에 노출되는지
  - research/prototype 안내 문구가 보이는지
  - quarterly coverage가 늦게 시작될 수 있다는 안내 문구가 보이는지
  - trend filter / market regime overlay 입력이 같이 보이는지
  - 실행 성공
  - `Selection History`와 `Interpretation`이 정상 동작하는지

## 5. Compare - Annual Strict Family

- `Backtest > Compare & Portfolio Builder`
- 전략 선택:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- 확인:
  - 각 전략별 advanced input이 시각적으로 구분되어 읽기 쉬운지
  - 각 전략별 advanced input에서 market regime overlay 입력이 보이는지
  - 전략마다 benchmark/window를 따로 줄 수 있는지
  - overlay가 꺼져 있어도 window / benchmark를 먼저 수정할 수 있는지
  - compare 실행 후 focused strategy drilldown에서 regime interpretation이 보이는지
  - 새 compare history record를 drilldown으로 열었을 때
    per-strategy summary row가 보이는지

## 6. History / Prefill

- annual strict strategy 하나를 market regime overlay on으로 실행
- `Backtest > History`
- 확인:
  - history row가 저장되는지
  - drilldown meta에
    - `market_regime_enabled`
    - `market_regime_window`
    - `market_regime_benchmark`
    가 남는지
  - compare record drilldown에서는
    strategy별 override / regime 값이 context 표로 보이는지
  - `Load Into Form` 시 single strategy form에 값이 되돌아오는지
  - `Load Into Form` 설명 문구가 보이는지

## 7. Tooltip / Help Copy

- `Market Regime Overlay` 옆 도움말 확인
- `Interpretation Summary` 도움말 확인
- `Market Regime Events` 도움말 확인
- 기대:
  - “시장 전체 상태를 보는 상위 오버레이”라는 설명이 읽히는지
  - rebalance-date only 동작이 명확한지

## 8. Preflight / Historical Semantics Regression

- strict annual strategy에서 preset을 wider preset으로 바꿔 실행
- 확인:
  - preset은 historical fixed-universe 설명을 유지하는지
  - `Price Freshness Preflight`는 경고/진단만 수행하는지
  - market regime overlay 추가 이후에도 preflight나 selection history가 깨지지 않는지

## 완료 기준

- annual strict family 3종에서 market regime overlay on/off가 모두 실행된다
- quarterly prototype single strategy가 실행된다
- compare에서 strict annual family별 regime 입력이 각각 동작한다
- history / prefill / interpretation / tooltip이 모두 자연스럽게 읽힌다
