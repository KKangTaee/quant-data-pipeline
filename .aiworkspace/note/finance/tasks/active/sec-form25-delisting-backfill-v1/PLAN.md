# SEC Form 25 Delisting Backfill V1 Plan

Status: Complete
Started: 2026-05-28
Completed: 2026-05-28

## 이걸 하는 이유?

Historical Universe Survivorship V1은 lifecycle evidence를 읽어 survivorship bias 위험을 표시할 수 있게 만들었지만,
실제 historical delisting source를 채우는 collector는 아직 없다.

이번 task는 무료 공식 source인 SEC EDGAR Form 25 filing history를 이용해 delisting evidence를 DB에 적재하고,
Data Coverage / Validation Efficacy가 실제 evidence를 읽을 수 있는 기반을 만든다.

## Scope

- SEC ticker / CIK mapping과 submissions API를 사용한다.
- Form 25 / 25-NSE / amendment filing을 delisting evidence로 normalize한다.
- `finance_meta.nyse_symbol_lifecycle`에 `source_type=delisting_feed`, `coverage_status=actual`, `listing_status=delisted` row를 idempotent UPSERT한다.
- `app/jobs/ingestion_jobs.py`에 job wrapper를 추가한다.
- service contract test와 데이터 문서를 갱신한다.

## Out Of Scope

- 새 workflow JSONL registry
- 사용자 메모, preset, 시간 기록 저장
- Form 25 원문 전문 저장
- live approval, broker order, auto rebalance
- 전체 historical universe membership 완성

## Done Criteria

- collector pure parser / DB write contract test가 통과한다.
- job wrapper가 no-symbol, partial/missing, success 상태를 표준 `JobResult`로 반환한다.
- docs/data와 architecture map이 SEC Form 25 source boundary를 설명한다.
- `.DS_Store`, run history, generated artifact는 stage하지 않는다.
