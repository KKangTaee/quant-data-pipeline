# Overview Market Context Turnaround Stage Semantics Fix V1 Status

Last Updated: 2026-07-16

## Current Stage

- 전체 roadmap: 1차~3차
- 현재: 2차 six-rail semantic display 완료, 3차 actual/Browser QA 시작 전
- 구현 완료 차수: 2/3

## Completed

- AAPL actual DB와 current code를 read-only로 추적했다.
- EPS 누락의 직접 원인을 duration unit allowlist의 `USD per share` 누락으로 확정했다.
- 파일 수정 없이 unit 하나만 허용한 재계산에서 TTM EPS `7.90`, `PER_READY` 복구를 확인했다.
- data-only/minimal, selected semantic display, backend taxonomy rewrite 세 접근을 비교하고 중간안을 승인 방향으로 선택했다.
- 사용자가 written spec을 승인했다.
- loader/evidence, React semantics, actual/Browser QA의 3개 task와 RED/GREEN/commit 단위를 `PLAN.md`에 고정했다.
- linked `codex/sub-dev` worktree와 focused baseline 100/100 pass를 확인했다.
- public loader가 canonical `USD per share` diluted EPS를 읽도록 보정했다.
- 영업 개선 판정 임계값은 유지하면서 current margin, latest YoY delta, recent threshold count를 evidence에 추가했다.
- 신규 RED/GREEN 테스트 2개와 focused regression 102/102 pass를 확인했다.
- 6개 rail 문구를 전환 신호/현재 양수 상태/PER 적용 가능 기준으로 분리했다.
- `ESTABLISHED`를 UI-local 상태로 추가해 `MET` 및 미확인 상태와 시각적으로 구분했다.
- headline/status badge를 한국어로 바꾸고 React source tests 2개, focused regression 104/104, Vite production build를 통과했다.

## Next Action

- 3차 actual AAPL과 negative-EPS 종목을 read-only 검증한 뒤 desktop/mobile Browser QA와 문서 정렬을 수행한다.
