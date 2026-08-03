# Inflation Policy Core Engines Status

State: active

## Current

- 2026-08-03 actual DB 재감사에서 Q4/Q4·policy·joint path가 production validation과
  materialization을 갖추지 못한 사실이 확인되어 functional recovery로 재개했다.

- 전체 phase 2/5차 완료
- Task 0/7: 설계 분해·소유 경계·baseline 확인 완료
- Task 1/7: Core PCE index/Q4·목표 역산·5상태·path simulation 구현 완료
- Task 2/7: SEP net move·경제 반응행렬·실제 표결·policy ensemble 구현 완료
- Task 3/7: pivot known-at·동적 저항 zone·상태·driver 분해 구현 완료
- Task 4/7: 두 rate lens·순방향 target·조건부 역산·next-PCE 재가중 구현 완료
- Task 5/7: chronological metric·baseline·calibration·publication gate 구현 완료
- Task 6/7: PIT 전체 vintage 기반 bridge·ridge·momentum 혼합모형과 snapshot pipeline 완료
- Task 7/7: 2026-07-29 replay·실제 artifact/snapshot UPSERT·durable docs 정렬 완료
- 기존 data foundation actual gate: 필수 source gap 0
- 1개월 Core PCE artifact: `LIMITED` (97 release origins/99 targets, CRPS 0.06052 <
  best comparable baseline 0.10757; SEP/공식 benchmark 묶음 대기)
- 통합 snapshot: `LIMITED`
- 연말 Q4/Q4·정책·저항 event probability: `LIMITED`
- joint rate 역산·침체: `NOT_AVAILABLE`

## Next

전체 phase 3/5차에서 저장 snapshot을 읽는 순방향·10년물 목표 역산 workbench를
구현한다. UI는 `LIMITED/NOT_AVAILABLE`을 숨기거나 `READY`처럼 표시하지 않는다.
