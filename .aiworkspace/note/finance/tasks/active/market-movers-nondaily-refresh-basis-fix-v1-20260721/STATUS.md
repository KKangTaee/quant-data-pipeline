# Status

Status: Complete
Last Updated: 2026-07-21

## Roadmap

- [x] 1차 갱신 목표일 계약 수정
- [x] 2차 화면 기준일·액션 방어 및 QA

## Current Step

최신 완료 NYSE session과 coverage-qualified 랭킹 기준일을 분리했다. 가격 이력 수동 갱신은 비-Daily에서 항상 보이며, 실제 보강 대상이 있을 때 primary로 강조한다.

## Completion Evidence

- 실제 DB preflight: target `2026-07-20`, Weekly `502`, Monthly `501` symbols due
- Market Movers/NYSE pytest: `114 passed`
- NYSE calendar pytest: `4 passed`
- Vite production build: success
- Browser QA: localhost URL policy 차단으로 미실행

## Roadmap Position

이번 버그 수정 roadmap은 `2/2차` 완료했다. broader Market Movers roadmap은 계속 `4/5차`이며 남은 5차는 별도 conditional outlook/OOS publication gate다.
