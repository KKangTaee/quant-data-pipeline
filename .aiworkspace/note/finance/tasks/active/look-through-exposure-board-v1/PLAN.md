# Look-through Exposure Board V1 Plan

Status: Complete
Created: 2026-05-28
Owner: finance-db-pipeline + finance-backtest-web-workflow

## 이걸 하는 이유?

`data-provenance-coverage-v1`에서 provider / macro evidence의 출처와 freshness를 볼 수 있게 했다.
하지만 Final Review에서 아직 부족한 부분은 "ETF 이름과 겉보기 비중"이 아니라 실제 underlying holdings / exposure가 어떤 자산군과 종목 집중으로 이어지는지 한눈에 보는 surface다.

이번 task는 새 JSONL이나 DB schema를 추가하지 않고, 이미 DB에 저장된 `etf_holdings_snapshot` / `etf_exposure_snapshot` loader 결과를 compact look-through board로 요약해 Practical Validation과 Final Review에서 같은 근거를 읽게 만든다.

## Scope

- provider context에 compact `look_through_board` 추가
- holdings coverage, exposure coverage, top holding, overlap, asset bucket, fund별 coverage row를 요약
- Practical Validation 화면에 Look-through Exposure Board 표시
- Final Review validation summary에 같은 board의 compact summary 표시
- Final decision snapshot에 기존 validation payload 경유로 board가 보존되도록 유지
- service contract test 추가
- 관련 phase / flow / data docs 동기화

## Out Of Scope

- 새 JSONL registry
- registry rewrite
- 새 DB table / schema migration
- UI에서 provider source 직접 fetch
- full holdings row를 JSONL에 저장
- ETF-of-ETF 2차 look-through expansion
- broker order, live approval, auto rebalance

## Completion Criteria

- provider context가 `look_through_board`를 반환한다.
- board는 compact summary / asset bucket / top holdings / fund coverage rows를 포함한다.
- Practical Validation과 Final Review에서 board를 확인할 수 있다.
- `tests/test_service_contracts.py`에 look-through board contract가 추가된다.
- `git diff --check`, focused py_compile, service contract test, boundary check, Browser smoke가 통과한다.
