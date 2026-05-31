# Concentration / Overlap / Exposure Contract V1 Plan

Status: Complete
Created: 2026-05-29

## Goal

Phase 11의 11-2로 existing provider look-through evidence를 read-only construction risk audit contract로 묶는다.

이걸 하는 이유?

- Practical Validation이 이미 계산하는 concentration / overlap / exposure evidence를 Final Review에서도 같은 의미로 읽게 한다.
- provider holdings / exposure coverage가 없을 때 proxy-only 결과를 `PASS`처럼 보이지 않게 한다.
- full holdings, raw provider response, memo, preset, time log 저장 없이 compact evidence만 사용한다.

## Scope

- `app/services/backtest_construction_risk_audit.py` 추가
- Practical Validation result에 `construction_risk_audit`와 display rows 연결
- Practical Validation / Final Review 화면에서 audit summary 표시
- Final Review decision snapshot / investability packet에 audit payload 보존
- focused service contract tests 추가

## Out Of Scope

- selected-route gate policy 차단 연결
- 신규 provider collector / DB schema
- issuer / sector grouping 확장
- ETF-of-ETF 2차 look-through expansion
- user memo / preset / comment persistence
- broker order / live approval / auto rebalance

## Completion Criteria

- provider look-through board PASS / REVIEW / NOT_RUN 조합을 construction risk audit row로 변환한다.
- provider holdings / exposure가 없으면 overall route가 ready가 되지 않는다.
- top holding / top overlap / unknown exposure review trigger를 service contract로 고정한다.
- no new JSONL registry or memo-like persistence가 추가되지 않는다.
