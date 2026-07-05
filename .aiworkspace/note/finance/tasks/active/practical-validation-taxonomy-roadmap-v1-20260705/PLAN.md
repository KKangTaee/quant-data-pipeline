# Practical Validation Taxonomy Roadmap V1

Status: Active
Created: 2026-07-05
Owner: backtest-dev

## Goal

`Backtest > Practical Validation` 개편을 바로 구현하지 않고, 현재 검증 taxonomy와 화면 책임을 먼저 정리해 V1-V8을 개발 / QA / 커밋 가능한 단위로 고정한다.

## 이걸 하는 이유?

Practical Validation은 이미 많은 검증 기능을 갖고 있지만, 현재 화면에서는 diagnostics, audits, validation modules, board map, selected-route preflight가 서로 다른 이름으로 비슷한 정보를 반복해서 보여준다.

사용자는 2단계에서 "이 후보를 Final Review로 넘길 만큼 실전 검증 근거가 충분한가?"를 빠르게 판단해야 한다. 지금 구조는 3단계 Final Review의 최종 선정 판단까지 섞여 보이기 때문에, 구현 전에 stage boundary와 evidence taxonomy를 먼저 정리해야 한다.

## Scope

이번 task의 범위:

- 현재 12개 Practical Diagnostics가 각각 무엇을 검증하는지 정리한다.
- diagnostics, audits, validation modules, board map, selected-route preflight의 관계를 정리한다.
- 2단계에 남길 검증과 3단계로 넘길 판단을 분리한다.
- 중복되거나 과한 UI / 검증 / board를 제거 또는 접힘 처리 후보로 정리한다.
- React custom component 전환 우선순위를 잡는다.
- V2-V8 개발 순서를 개발 / QA / 커밋 단위로 구체화한다.

## Out Of Scope

이번 task에서 하지 않는 일:

- `app/web/backtest_practical_validation/page.py` 코드 수정
- React custom component 생성
- registry / saved JSONL rewrite
- provider snapshot 수집 실행
- validation threshold / gate policy 의미 변경
- Final Review selected-route 저장 정책 변경
- Browser QA screenshot 생성

## Stop Condition

아래 문서가 준비되면 이번 task는 설계 단계로 완료한다.

- `PLAN.md`: scope, stop condition, V1-V8 roadmap
- `DESIGN.md`: taxonomy, stage boundary, implementation direction
- `STATUS.md`: 현재 진행 상태와 다음 action
- `NOTES.md`: 코드 구조 분석 결과
- `RUNS.md`: 읽은 문서 / 코드와 실행 명령
- `RISKS.md`: 남은 판단 리스크와 승인 필요 지점

## Current Roadmap Position

전체 Practical Validation 개편 로드맵 중 현재 완료하려는 것은 `V1. 검증 taxonomy 정리`의 설계 / 개발 방향 고정이다.

아직 구현은 시작하지 않았다.

## V1-V8 Development Roadmap

| Version | Purpose | Main Files | Completion Condition | QA / Commit Unit |
|---|---|---|---|---|
| V1 | 검증 taxonomy와 중복 UI 정리 기준 확정 | task docs, later `workspace_model.py` 후보 | 2단계 핵심 / 보조 / 3단계 참고 taxonomy가 문서화되고 개발 범위가 승인됨 | docs diff check; commit as planning unit if requested |
| V2 | Practical Validation / Final Review stage boundary 재정의 | `backtest_practical_validation_modules.py`, `backtest_selected_route_preflight.py`, Practical Validation copy | selected-route preflight가 "Final Review 준비 상태"로 낮춰지고 최종 선택처럼 보이지 않음 | focused unit tests, py_compile, diff check |
| V3 | Practical Validation workspace read model 추가 | new `app/services/backtest_practical_validation_workspace.py`, possibly `workspace_model.py` | page가 summary / queue / gate / evidence groups / action state를 직접 여러 service에서 조합하지 않음 | service tests with representative validation payloads |
| V4 | 7-step 화면을 5-flow로 재배치 | `app/web/backtest_practical_validation/page.py`, new panel modules | 첫 화면이 현재 2차 검증 상태, Fix Queue, 다음 action을 먼저 보여줌 | py_compile, focused render helper tests, Browser QA |
| V5 | React custom component 전환 1차 | `app/web/components/practical_validation_*` | Control Center, Replay action, Gate / Fix Queue, Provider action, Handoff 중 우선순위 영역이 card + action을 한 DOM에 묶음 | component build check, Streamlit integration smoke, Browser QA |
| V6 | `page.py` 물리 분리 | `source_summary.py`, `profile_panel.py`, `replay_panel.py`, `gate_panel.py`, `evidence_boards.py`, `provider_actions.py`, `handoff_panel.py` | `page.py`가 orchestration only로 줄고 re-export 파일이 실제 렌더링 책임을 가짐 | py_compile, import boundary tests, Browser QA |
| V7 | 검증 결과 표현 통일 | workspace read model, panel renderers | user-facing status가 `PASS / REVIEW / NEEDS_INPUT / BLOCKED / NOT_RUN / NOT_APPLICABLE`로 통일되고 raw route는 접힘 처리됨 | focused tests for status mapping and display rows |
| V8 | QA / durable docs alignment | `BACKTEST_UI_FLOW.md`, `PORTFOLIO_SELECTION_FLOW.md`, `SCRIPT_STRUCTURE_MAP.md`, task docs | 흐름 문서와 코드 책임 지도가 최종 구조와 일치함 | focused unittest, py_compile, git diff --check, Browser QA screenshot |

## V1 Development Direction After Approval

승인 후 V1 구현은 가장 작은 코드 변경으로 시작한다.

1. `app/services/backtest_practical_validation_workspace.py` 초안을 만든다.
2. 현재 validation result에서 `core_evidence_groups`, `downstream_reference_groups`, `technical_details`를 분리하는 read model만 추가한다.
3. 기존 `page.py` render는 크게 바꾸지 않고, 먼저 tests로 taxonomy grouping을 고정한다.
4. UI 재배치는 V4로 미룬다.

V1 구현 완료 조건은 "보이는 화면 변경"이 아니라 이후 V2-V4가 안전하게 쓸 taxonomy/read-model contract를 만드는 것이다.
