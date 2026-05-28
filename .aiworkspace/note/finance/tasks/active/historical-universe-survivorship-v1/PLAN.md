# Historical Universe Survivorship V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

Data Coverage Audit은 현재 listing / asset profile evidence만으로 survivorship control을 PASS 처리하지 않는다.

이번 작업은 historical universe / delisting evidence를 DB에 둘 수 있는 lifecycle 계약과 read path를 추가해서, 실제 검증 데이터가 있는 경우에만 survivorship control을 통과시킬 수 있게 한다.

## Scope

- `nyse_symbol_lifecycle` DB schema 추가
- NYSE current listing 적재 시 lifecycle bridge row도 함께 갱신할 수 있는 idempotent UPSERT 경로 추가
- `finance/loaders/universe.py`에 compact lifecycle coverage loader 추가
- Practical Validation Data Coverage context / audit이 lifecycle evidence를 읽도록 연결
- Validation Efficacy survivorship row가 Data Coverage의 lifecycle 근거를 참고하도록 보강
- 새 workflow JSONL, memo, preset, approval, order, auto rebalance는 추가하지 않음

## Non-Goals

- 과거 전체 delisting 데이터 backfill
- 유료 데이터 소스 연결
- UI에서 원격 provider 직접 fetch
- live trading 승인 / 주문 / 자동 리밸런싱

## Exit Criteria

- historical / delisting lifecycle row가 요청 기간을 덮을 때 Data Coverage survivorship row가 PASS가 된다.
- current listing snapshot / asset profile만 있을 때는 survivorship PASS가 되지 않는다.
- service contract와 관련 py_compile이 통과한다.

## Implemented Slice

- `finance/data/db/schema.py`
  - `nyse_symbol_lifecycle` schema 추가
- `finance/data/nyse_db.py`
  - NYSE current listing CSV 적재 시 current listing lifecycle bridge row를 idempotent하게 UPSERT할 수 있게 추가
- `finance/loaders/universe.py`
  - `load_symbol_lifecycle_coverage_summary` 추가
- `app/services/backtest_data_coverage_audit.py`
  - Data Coverage context / audit이 symbol lifecycle evidence를 읽도록 연결
- `app/services/backtest_validation_efficacy.py`
  - Data Coverage survivorship PASS를 Validation Efficacy survivorship guard에 반영
- `app/services/backtest_evidence_read_model.py`
  - on-demand Data Coverage Audit 결과를 Validation Efficacy Audit 생성 전에 연결
