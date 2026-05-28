# Data Coverage Hardening V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

Validation Efficacy와 Backtest Realism은 gate에 연결됐지만, PIT / survivorship / universe / DB price coverage 근거는 아직 한 화면에서 독립적으로 확인하기 어렵다.

이번 첫 slice는 새 저장소를 만들지 않고, 기존 DB loader와 Practical Validation compact evidence를 읽어 데이터 커버리지 공백을 read-only audit으로 드러낸다.

## Scope

- DB-backed price window coverage loader 추가
- Practical Validation source ticker 기준 data coverage context 생성
- Data Coverage Audit read model 추가
- Practical Validation / Final Review / investability packet / saved evidence row에 audit 표시
- PIT replay / period coverage, provider freshness, universe listing, survivorship evidence를 분리 표시
- 새 JSONL registry, memo, preset, approval, order, rebalance 없음

## Non-Goals

- 새 remote provider 수집
- DB schema 변경
- historical constituent master 구축
- survivorship 완전 해결
- Data Coverage Audit gate policy 연결

## Exit Criteria

- service contract test에서 ready / missing coverage audit 확인
- Practical Validation과 Final Review가 같은 audit을 읽음
- 저장 경계와 남은 survivorship 한계를 문서화

## Implemented Slice

- `finance/loaders/price.py`
  - `load_price_window_summary(...)` 추가. Full OHLCV row 대신 requested validation window의 first / latest / row count summary만 읽는다.
- `app/services/backtest_data_coverage_audit.py`
  - `data_coverage_audit_v1` read model 추가.
  - DB price window, provider freshness, PIT replay / period coverage, universe listing, survivorship / delisting control, storage boundary를 분리한다.
- `app/services/backtest_practical_validation_diagnostics.py`
  - Practical Validation result에 `data_coverage_context`, `data_coverage_audit`, display rows를 붙인다.
- `app/services/backtest_evidence_read_model.py`
  - Investability packet과 saved final decision evidence rows가 Data Coverage Audit을 읽는다.
- `app/web/backtest_practical_validation.py`, `app/web/backtest_final_review.py`
  - Practical Validation과 Final Review에서 audit board를 표시한다.
