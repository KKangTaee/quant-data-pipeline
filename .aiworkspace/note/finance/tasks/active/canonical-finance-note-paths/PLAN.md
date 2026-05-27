# Canonical Finance Note Paths

Status: Active
Started: 2026-05-28

## 이걸 하는 이유?

Streamlit Finance Console이 예전 `.note/finance` 기준 경로를 직접 참조하면, 현재 보존 데이터가 있는 `.aiworkspace/note/finance`의 `registries`, `saved`, `run_history`를 읽지 못한다.
Overview, Candidate Library, saved portfolio replay, Practical Validation, Final Review가 같은 canonical workspace 데이터를 읽도록 경로 기준을 통일한다.

## Scope

- `app/runtime`의 JSONL registry / saved / run history 경로를 canonical helper로 통일한다.
- `app/jobs` run history / run artifact 경로를 canonical helper로 통일한다.
- Streamlit app glossary와 Compare V2 registry status check의 직접 `.note` 참조를 제거한다.
- 기존 registry / saved JSONL 데이터는 재작성하지 않는다.

## Verification

- Python compile for changed app modules
- `tests.test_service_contracts`
- UI-engine boundary lint
- Browser smoke check for Finance Console overview
