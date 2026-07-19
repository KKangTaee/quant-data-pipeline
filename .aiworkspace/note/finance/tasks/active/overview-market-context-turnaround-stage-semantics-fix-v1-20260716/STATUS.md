# Overview Market Context Turnaround Stage Semantics Fix V1 Status

Last Updated: 2026-07-16

## Current Stage

- 전체 roadmap: 1차~3차
- 현재: 1차~3차 구현·actual QA·Browser QA·문서 정렬 완료
- 구현 완료 차수: 3/3

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
- actual AAPL에서 PER/전환 TTM EPS `7.90`, headline `PER_READY`, rail `PER_READY=MET`의 일치를 확인했다.
- actual RIVN에서 TTM EPS `-3.07`, `PER_READY=NOT_MET`, recommended analysis `turnaround`를 확인했다.
- desktop/420px Browser QA에서 AAPL established rail, RIVN negative-EPS rail, horizontal overflow 0, 서버 재시작 후 신규 console error 0을 확인했다.
- focused 118/118 pass와 repository-wide baseline-equivalent 4 failures/154 Streamlit isolation errors를 확인했다.

## Next Action

- 완료 기록으로 유지한다. 후속 변경은 새 user-approved task로 연다.
