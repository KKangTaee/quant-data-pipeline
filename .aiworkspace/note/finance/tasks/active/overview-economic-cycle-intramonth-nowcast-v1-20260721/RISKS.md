# Overview Economic Cycle Intramonth Nowcast V1 Risks

Last Updated: 2026-07-21

| Risk | Mitigation |
|---|---|
| 월중 값을 확정 국면으로 오해 | 항상 `현재 입수정보 기반 잠정 계산`과 source dates 표시 |
| 증분 window가 interval closure를 놓침 | 마지막 known vintage date를 overlap해 기존 open interval도 재수집 |
| 일부 series 실패 뒤 불완전 row 저장 | 17-series combined collection 성공 전 snapshot write 금지 |
| 월중 row가 ribbon history에 섞임 | run_kind 전용 loader와 service contract로 격리 |
| UI가 느린 full PIT 계산을 수행 | backend daily materialization, UI DB-only 유지 |
| 자동화 credential 부재 | job failure 기록 후 last-good 유지; browser-safe에서는 실행하지 않음 |
| 새 달에도 오래된 월말 baseline을 계속 사용 | 첫 평일 closed-month rollover로 누락된 직전 월말만 append |

## Remaining Validation

- `FRED_API_KEY`가 있는 운영 환경에서 실제 incremental overlap 수집 1회를 실행하고 provider 결과를 확인해야 한다.
- desktop / 420px Browser QA와 console / overflow 검증이 남아 있다.
- historical pseudo-intramonth stability validation은 V1의 표시 승격 조건이 아니라 후속 research다.
