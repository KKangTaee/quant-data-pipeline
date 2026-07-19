# Overview Market Context Nasdaq-100 Valuation V1 Status

Status: 1차~5차 Implementation Complete — Valuation Output Blocked by 95% Coverage Gate
Last Updated: 2026-07-13

## Current Progress

- 1차: SEC QQQ N-PORT/N-30B-2, identity, filing-aware TTM EPS, weight drift, calibration pure contract와 coverage spike를 완료했다.
- 2차: holdings identity/timing schema와 `nasdaq100_monthly_valuation`, idempotent UPSERT, DB loader를 구현했다.
- 3차: Nasdaq read model과 S&P/Nasdaq isolated composition service를 구현했다.
- 4차: React instrument selector와 Nasdaq coverage-block surface, responsive style, static build를 구현했다.
- 5차: daily-safe automation job, 실제 DB run, focused regression, Browser QA, canonical docs sync를 완료했다.

## Actual Result

- 공식 SEC holdings job: normalized `3,060` rows attempted; unique business keys persisted `3,049` across 30 snapshots.
- QQQ EOD refresh: `20` rows.
- 월별 materialization: 2016-09~2026-07 `119` rows.
- quality: `reconstructed_actual 5`, `blocked 114`.
- latest coverage: `94.46678%`; required: `95%`.
- diagnostic P/E calibration: reconstructed `31.91997`, public fixture `31.89`, APE `0.09398%`.
- S&P read model은 `READY`; Nasdaq read model은 `INSUFFICIENT_EARNINGS_COVERAGE` evidence를 가진 `BLOCKED`다.

## User Flow

Market Context 기본값은 S&P 500이다. 사용자가 `Nasdaq-100 / QQQ`를 선택하면 값이 없는 그래프나 합성값 대신 94.47% coverage, 95% 기준, 미확인 비중, holdings 기준일과 blocker를 본다. UI는 원격 source를 호출하지 않는다.

## Remaining Gap

- 승인된 95% gate를 최근 60개월 모두 통과하지 못했으므로 Nasdaq 두 graph는 production-ready 값으로 노출되지 않는다.
- acquired/delisted constituent historical EOD의 별도 무료 source contract가 승인·구현되어야 114 blocked month를 재평가할 수 있다.
- implementation과 QA는 5차까지 완료했지만 active task는 data-quality blocker 추적을 위해 active 위치에 둔다.

## Commits

- `50fe4059` — 1차 coverage spike
- `10a973f4` — 2차 DB pipeline
- `287d359f` — 3차 combined service
- `6ed08d0e` — 4차 React selector / blocked UI
- 5차 automation/docs closeout은 이 상태 문서를 포함한 최종 task commit으로 묶는다.
