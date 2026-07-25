# Finance Document Governance Alignment V1 Notes

## Decisions

- canonical 문서는 완료 이력 저장소가 아니라 현재 제품과 문서 체계의 기준이다.
- ordinary task closeout에서 canonical 문서 변경 없음은 정상 결과다.
- root log는 권위 있는 상태 저장소가 아니라 짧은 handoff pointer다.
- 새로 만들거나 이번에 손대는 task/phase는 `State:` 정규화 필드를 사용한다.
- phase는 번호가 아니라 의미 있는 `<phase-id>` 폴더를 사용한다.

## Current-State Decision

- Active: none
- Paused: `overview-sentiment-cnn-aaii-v1-20260719`
- Verification-Only:
  - `portfolio-monitoring-chart-zoom-pan-v1-20260719`
  - `market-movers-chart-navigation-polish-v1-20260721`

## Compatibility

- 기존 task의 `Status:` 표기는 legacy fallback으로 읽는다.
- 기존 phase/task 폴더와 완료 이력은 보존한다.
- phase bootstrap의 과거 numbered CLI는 새 문서에서 제거하며, 새 생성은 현재 계약만 허용한다.

## Forward Review Result

- Backtest instruction paths가 실제 Project Map과 달랐던 문제를 발견해
  `app/web/backtest_page.py`, `app/services/backtest_*`, `app/runtime/backtest/` 기준으로 교정했다.
- INDEX가 소유하는 읽기 경로와 AGENTS의 역할별 first read를 맞췄다.
- Roadmap의 `Complete`에서 handoff는 task/phase 기록이 기본이며 root log는 고신호일 때만
  필요하다고 명시했다.
- INDEX는 discovery/read-order 사실이, Roadmap은 completion state 의미가 바뀌었기 때문에
  이번 작업에서 역할에 맞게 갱신했다.
