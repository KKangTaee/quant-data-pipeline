# Finance Registries

Status: Active
Last Verified: 2026-05-13

이 폴더는 앱과 운영 helper가 다시 읽어야 하는 append-only JSONL 저장소를 둔다.

Registry 파일은 단순 실행 로그가 아니라 다음 UI 단계가 읽는 운영 데이터다.
새 row를 추가할 때는 기존 row를 덮어쓰지 않고 append-only로 남긴다.

## Current Selection V2 Flow

현재 주 사용자 흐름은 아래 registry를 우선 읽는다.

| File | Producer | Consumer | Meaning |
|---|---|---|---|
| `PORTFOLIO_SELECTION_SOURCES.jsonl` | Backtest Analysis | Practical Validation | 단일 전략, compare, saved mix replay를 검증 후보 source로 저장 |
| `PRACTICAL_VALIDATION_RESULTS.jsonl` | Practical Validation | Final Review | 12개 practical diagnostics, provider coverage, blocker / review 근거 저장 |
| `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | Final Review | Selected Portfolio Dashboard | select / hold / reject / re-review 최종 판단 저장 |
| `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | Selected Portfolio Dashboard | Selected Portfolio Dashboard | 사용자가 명시적으로 남기는 monitoring 보조 기록 |

## Legacy / Compatibility Registries

아래 registry는 기존 workflow와 호환성을 위해 유지한다.
현재 Selection V2 주 흐름의 필수 저장 단계는 아니다.

| File | Meaning | Current Boundary |
|---|---|---|
| `CURRENT_CANDIDATE_REGISTRY.jsonl` | Candidate Review를 통과해 현재 후보로 남긴 row | legacy candidate library / replay compatibility |
| `CANDIDATE_REVIEW_NOTES.jsonl` | 후보 초안에 대한 operator review note | 후보 source-of-truth가 아님 |
| `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | pre-live / paper tracking / watchlist 운영 상태 기록 | Final Review V2 이전 운영 기록 |
| `PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | 여러 후보를 묶은 portfolio proposal draft | saved proposal compatibility |
| `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | 별도 paper tracking 조건과 trigger 기록 | 현재 main flow에서는 final review record 안의 paper observation을 우선 사용 |
| `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | 기존 Final Review V1 판단 기록 | V2 dashboard source-of-truth가 아님 |

## What Registry Is Not

- live approval이 아니다.
- broker order가 아니다.
- 자동매매 지시가 아니다.
- runtime history나 임시 artifact를 대체하지 않는다.
- 사람이 읽는 backtest report를 대체하지 않는다.

## Commit Policy

- registry JSONL은 제품 workflow 데이터이므로 삭제하거나 재작성하지 않는다.
- 사용자가 명시적으로 요청하지 않으면 새 runtime row를 커밋 대상으로 만들지 않는다.
- schema나 의미가 바뀌면 관련 runtime helper와 `docs/flows/PORTFOLIO_SELECTION_FLOW.md`를 같이 확인한다.
