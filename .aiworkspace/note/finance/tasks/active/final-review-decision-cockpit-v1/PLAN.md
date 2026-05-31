# Final Review Decision Cockpit V1 Plan

Status: Active
Created: 2026-05-31

## 이걸 하는 이유?

Final Review는 현재 많은 검증 근거를 보여주지만, 사용자가 먼저 알아야 하는 질문인 "이 후보를 최종 선정해도 되는가, 아니면 보류 / 재검토 / 거절해야 하는가"가 화면 상단에서 충분히 선명하지 않다.

이번 작업의 목적은 새 저장소나 DB 변경 없이 기존 Practical Validation result와 investability packet read model을 재구성해, Final Review를 최종선별용 Decision Cockpit으로 만드는 것이다.

## Scope

포함한다.

- Final Review Gate 통과 후보를 비교하는 Candidate Board
- 선택 후보의 blocker / review-required / ready state를 먼저 보여주는 Decision Cockpit
- 기존 Investability Evidence Packet / Gate Policy / Decision Dossier 재사용
- `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장 gate 유지
- focused service contract / compile / Browser QA
- 관련 flow / phase / root handoff 문서 sync

포함하지 않는다.

- 새 DB schema
- 새 JSONL registry
- registry rewrite
- provider / FRED 직접 fetch
- monitoring log 자동 저장
- waiver UI / persistence
- broker order, live approval, account sync, auto rebalance

## Expected Files

- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_final_review.py`
- `app/web/backtest_final_review_helpers.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- phase / root handoff docs

## Done Criteria

- Final Review 상단에서 eligible 후보 비교와 선택 후보 decision summary를 확인할 수 있다.
- Candidate Board는 기존 validation / packet evidence만 읽고 새 저장 side effect를 만들지 않는다.
- Decision Cockpit은 selected-route blocker, review-required, suggested route, monitoring handoff seed를 명확히 표시한다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO`는 gate policy가 허용할 때만 저장 가능하다.
- UI QA screenshot을 남기고 generated artifact는 commit하지 않는다.
