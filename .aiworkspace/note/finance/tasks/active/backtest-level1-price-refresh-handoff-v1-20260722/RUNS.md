# Runs

- 문서와 코드 소유 경계를 확인해 current Result Workspace와 legacy refresh UI의 연결 단절을 확인했다.
- `2026-07-22 13:00 KST`의 마지막 완료 NYSE session이 `2026-07-21`임을 확인했다.
- GTAA 기본 Universe + BIL actual DB freshness:
  - common latest `2026-06-26`
  - newest latest `2026-07-21`
  - stale 11, missing 0
  - refresh plan `refresh_available`
  - collection window `2026-06-27` ~ `2026-07-21`
- written spec self-review: placeholder scan, six-file task contract, pure service boundary, partial-success transition, diff whitespace check 통과.
- detailed implementation plan self-review:
  - Single `BacktestAnalysisResultWorkspace`와 별도 `PortfolioMixWorkspace`의 active route 소유 경계 재확인
  - 공통 public 함수 2개, 네 상태, 세 Single intent, Mix `run_mix` projection 정합성 확인
  - 6개 TDD task, focused pytest/compile/Vite build/Browser QA/문서 closeout 명령 구체화
  - placeholder scan과 `git diff --check` 통과
- 제품 코드, DB, registry, saved setup은 변경하지 않았다.
