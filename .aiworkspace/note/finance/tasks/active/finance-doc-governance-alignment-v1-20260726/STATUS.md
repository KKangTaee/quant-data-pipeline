# Finance Document Governance Alignment V1 Status

State: active

## Current

- 안전 진단과 깊은 진단 결과를 승인된 설계와 실행 계획으로 고정했다.
- 현재 `codex/backtest-dev` linked worktree에서 작업 중이다.
- 다음 작업은 phase bootstrap과 hygiene checker의 새 계약을 실패 테스트로 먼저 고정하는 것이다.

## Next

1. `tests/test_finance_document_workflow.py` 작성
2. RED 확인
3. phase 자동화와 runbook 교정
4. 지침·skill·상태 pointer 동기화
5. mirror 및 최종 검증

## Scope Guard

- registry, saved portfolio, run history, QA 이미지에는 손대지 않는다.
- 과거 task 491개의 상태 형식은 일괄 변환하지 않는다.
- `main-dev` 통합은 별도 작업으로 남긴다.

