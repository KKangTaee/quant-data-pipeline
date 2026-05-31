# Phase 12 Selected Monitoring / Recheck Operations Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8은 investability data evidence를 강화했고, Phase 9는 cost / liquidity realism을 강화했으며, Phase 10은 walk-forward / OOS / regime validation을 강화했고, Phase 11은 portfolio construction risk를 selected-route gate에 연결했다.
이제 남은 약점은 최종 선정 이후다.

Final Review에서 한 번 선택된 포트폴리오도 시간이 지나면 가격 데이터가 stale해지거나, provider holdings / exposure 근거가 낡거나, 최신 구간 성과가 baseline을 더 이상 지지하지 않거나, 실제 배분 drift가 커질 수 있다.
Phase 12의 목적은 Selected Portfolio Dashboard가 선정 이후에도 "이 포트폴리오를 계속 실전 검토 대상으로 유지해도 되는가, 아니면 재검토해야 하는가"를 read-only evidence로 판단하게 만드는 것이다.

이 phase는 live approval, broker order, auto rebalance를 만들지 않는다.
또한 monitoring log 자동 저장, 사용자 메모, 프리셋 저장을 늘리는 작업이 아니다.
검증 효력을 높이는 데이터가 필요하면 `Ingestion -> DB -> Loader -> UI` 흐름으로만 다룬다.

## Phase Goal

Selected Portfolio Dashboard가 아래 질문에 답할 수 있게 만든다.

- 최종 선정 row가 dashboard monitoring에 필요한 component, evidence packet, review trigger, timeline 경계를 계속 갖고 있는가?
- Performance Recheck 실행 전 DB market data / benchmark / component replay contract가 준비되어 있는가?
- recheck portfolio ticker와 benchmark ticker의 최신 가격 데이터가 stale하거나 missing하지 않은가?
- provider holdings / exposure / operability evidence가 선정 당시 판단을 계속 지지하는가?
- 최신 recheck 결과가 Final Review baseline 대비 약화되었는가?
- monitoring timeline과 review signal이 재검토 필요 상태를 pass처럼 숨기지 않는가?
- optional actual allocation / drift check가 주문이나 자동 리밸런싱으로 오해되지 않는가?

## Scope

포함한다.

- Phase 12 official board 생성
- current Selected Portfolio Dashboard / Final Review / runtime selected portfolio source map 확인
- recheck readiness / symbol freshness / provider evidence 운영 contract 점검
- recheck comparison / review signal / timeline gap contract 점검
- optional allocation / drift evidence의 read-only 경계 점검
- Final Review decision dossier / selected dashboard continuity 정리
- integrated QA / closeout

포함하지 않는다.

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- broker order, live approval, auto rebalance
- account holdings 자동 연결
- live trading signal generation
- UI direct provider / FRED / broker fetch
- paid data source 우선 도입

## Storage Boundary

Phase 12는 기존 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` final decision row와 Selected Portfolio Dashboard runtime read model을 읽는다.
`SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 사용자가 명시적으로 monitoring check record를 남길 때만 쓰는 optional record로 유지하며, phase 작업에서 자동 append path를 추가하지 않는다.

full price history, provider holdings, exposure, macro series, raw broker/account response는 workflow JSONL에 저장하지 않는다.
필요한 full data는 DB 또는 runtime 계산 영역에 두고, UI에는 compact readiness / freshness / comparison / signal evidence만 전달한다.

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 12-0 | Phase 12 board open / scope and task split | Complete |
| 12-1 | Selected monitoring source map / gap audit | Complete |
| 12-2 | Recheck readiness / freshness operations contract | Complete |
| 12-3 | Provider evidence staleness and coverage contract | Complete |
| 12-4 | Recheck comparison / review signal policy | Complete |
| 12-5 | Optional allocation drift evidence boundary | Complete |
| 12-6 | Decision dossier / continuity operations refinement | Complete |
| 12-7 | Phase 12 integrated QA / closeout | Complete |

## Done Criteria

- Selected Portfolio Dashboard의 current readiness / freshness / provider / continuity / timeline / signal / comparison source map이 문서화된다.
- Missing, stale, failed recheck, partial provider evidence, incomplete continuity는 pass로 처리하지 않는다.
- 최신 recheck 결과가 Final Review baseline 대비 약화되면 review signal이나 comparison evidence에서 드러난다.
- optional actual allocation / drift check는 read-only check로 남고 account integration, order draft, auto rebalance를 만들지 않는다.
- monitoring log 자동 저장, user memo, preset, approval, order, auto rebalance path가 추가되지 않는다.
- 관련 service contract test와 compile / diff check가 통과한다.

## Carry Forward To Later Phases

- Phase 13: 1차 hardening cycle 전체 closeout, 문서 / runbook / gate QA 정리.
