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
- Product Direction은 task 이름과 구현 이력을 제거하고 product promise, 사용자 여정,
  7개 current surface, 원칙, safety와 known limit만 소유한다.
- Data Operations는 설치 단계가 아니라 전체 workflow evidence layer이며 Research는
  Portfolio Lab의 필수 선행 gate가 아니다.
- Project Map은 surface별 route adapter, primary Python owner와 React presentation을
  한 표에서 찾게 하고, algorithm / payload / UX history는 focused docs로 넘긴다.
- optional generated directory처럼 현재 존재하지 않는 위치는 실제 code path처럼
  표기하지 않고 storage policy로만 설명한다.
- Roadmap은 active product work 없음, Sentiment paused, 두 Browser QA task를
  Verification-Only로 분리하고 future candidate는 approval queue로만 유지한다.
- next order는 verification debt → correctness PIT decision → one product research
  lane → strategy governance → maintenance / platform work다.

## Protected Existing Work

- `.aiworkspace/note/finance/registries/*.jsonl`
- `.aiworkspace/note/finance/saved/*.jsonl`
- `.aiworkspace/note/finance/run_history/*.jsonl`
- root의 기존 generated QA image / snapshot
- 사용자와 다른 task가 만든 unrelated dirty changes
