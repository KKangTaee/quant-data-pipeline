# Finance Canonical Docs Alignment V1 Notes

## Measured Drift

| Document | Lines | Main Drift |
|---|---:|---|
| `INDEX.md` | 189 | task link 124개, rolling status가 index 역할을 압도 |
| `PRODUCT_DIRECTION.md` | 76 | old navigation 표현 13곳, product purpose와 snapshot 혼합 |
| `PROJECT_MAP.md` | 288 | entry map과 세부 domain contract / UX history 혼합 |
| `ROADMAP.md` | 1,291 | 완료 표현 163개, task link 182개, next decisions가 하단에 매몰 |

## Current Navigation Contract

- Research: Today, Market Research, Institutional Holdings
- Portfolio: Portfolio Lab, Portfolio Monitoring
- Data: Data Operations
- Help: Reference Center

## Decisions

- INDEX를 네 번째 개편 대상으로 포함한다.
- 완료 이력은 삭제하지 않고 retained task / phase / root handoff에 보존한다.
- current docs에는 current fact, stable ownership, next decision만 남긴다.
- active, paused, verification-only를 명시적으로 구분한다.
- detailed code/data/flow/runbook content는 owning focused doc으로 연결한다.

## Protected Existing Work

- `.aiworkspace/note/finance/registries/*.jsonl`
- `.aiworkspace/note/finance/saved/*.jsonl`
- `.aiworkspace/note/finance/run_history/*.jsonl`
- root의 기존 generated QA image / snapshot
- 사용자와 다른 task가 만든 unrelated dirty changes
