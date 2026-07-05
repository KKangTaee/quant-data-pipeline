# Practical Validation Taxonomy Roadmap V1

Status: Complete
Created: 2026-07-05
Owner: backtest-dev

## Goal

`Backtest > Practical Validation` 개편을 taxonomy 설계에서 시작해 V1-V8 개발 / QA / 커밋 단위로 완료한다.

## 이걸 하는 이유?

Practical Validation은 이미 많은 검증 기능을 갖고 있지만, 현재 화면에서는 diagnostics, audits, validation modules, board map, selected-route preflight가 서로 다른 이름으로 비슷한 정보를 반복해서 보여준다.

사용자는 2단계에서 "이 후보를 Final Review로 넘길 만큼 실전 검증 근거가 충분한가?"를 빠르게 판단해야 한다. 지금 구조는 3단계 Final Review의 최종 선정 판단까지 섞여 보이기 때문에, 구현 전에 stage boundary와 evidence taxonomy를 먼저 정리해야 한다.

## Scope

이번 task의 완료 범위:

- 현재 12개 Practical Diagnostics가 각각 무엇을 검증하는지 정리한다.
- diagnostics, audits, validation modules, board map, selected-route preflight의 관계를 정리한다.
- 2단계에 남길 검증과 3단계로 넘길 판단을 분리한다.
- 중복되거나 과한 UI / 검증 / board를 제거 또는 접힘 처리 후보로 정리한다.
- workspace read model, selected-route readiness wording, 5-flow 화면, read-only React Fix Queue, Flow 3 workspace panel split, user-facing status normalization을 구현한다.
- 각 차수마다 focused QA와 commit을 만든다.
- durable docs와 root handoff logs를 최종 구조에 맞춘다.

## Out Of Scope

이번 task에서 하지 않는 일:

- `app/web/backtest_practical_validation/page.py` 코드 수정
- React custom component 생성
- registry / saved JSONL rewrite
- provider snapshot 수집 실행
- validation threshold / gate policy 의미 변경
- Final Review selected-route 저장 정책 변경
- live approval / broker order / auto rebalance semantics

## Stop Condition

아래 조건이 충족되면 이번 task는 V8 closeout으로 완료한다.

- `PLAN.md`: scope, stop condition, V1-V8 roadmap
- `DESIGN.md`: taxonomy, stage boundary, implementation direction
- `STATUS.md`: 현재 진행 상태와 다음 action
- `NOTES.md`: 코드 구조 분석 결과
- `RUNS.md`: 읽은 문서 / 코드와 실행 명령
- `RISKS.md`: 남은 판단 리스크와 승인 필요 지점
- focused unittest / py_compile / diff check / Browser QA
- V1-V8 각 차수 commit

## Current Roadmap Position

전체 Practical Validation 개편 로드맵 중 V1-V8을 완료했다. 이번 task의 마지막 위치는 V8 durable docs alignment와 integrated QA closeout이다.

## V1-V8 Development Roadmap

| Version | Purpose | Main Files | Completion Condition | QA / Commit Unit |
|---|---|---|---|---|
| V1 | workspace read model 추가 | `app/services/backtest_practical_validation_workspace.py` | 핵심 / 조건부 / downstream / technical evidence grouping contract가 테스트로 고정됨 | focused service tests, py_compile, diff check, commit |
| V2 | Practical Validation / Final Review stage boundary 문구 재정의 | `backtest_practical_validation_modules.py`, `backtest_practical_validation_board_registry.py`, selected-route policy wording | selected-route preflight가 "Final Review 준비 상태"로 낮춰지고 최종 선택처럼 보이지 않음 | focused unit tests, py_compile, diff check, commit |
| V3 | Practical Validation result와 workspace model 연결 | `app/services/backtest_practical_validation_diagnostics.py` | built result가 `practical_validation_workspace`를 함께 제공함 | diagnostics contract tests, py_compile, diff check, commit |
| V4 | 7-step 화면을 5-flow로 재배치 | `app/web/backtest_practical_validation/page.py` | 첫 화면이 후보/profile, validation 실행, 2차 결론/Fix Queue, 근거 Workbench, 저장/이동 흐름으로 읽힘 | py_compile, focused tests, Browser QA, commit |
| V5 | React custom component 전환 1차 | `app/web/components/practical_validation_fix_queue/` | Flow 3 Fix Queue / review count / core evidence가 read-only React card로 렌더됨 | component build, Streamlit integration smoke, Browser QA, commit |
| V6 | Flow 3 workspace panel 물리 분리 | `app/web/backtest_practical_validation/workspace_panel.py` | `page.py`는 5-flow orchestration을 유지하고 Flow 3 first-read surface는 별도 module이 소유함 | py_compile, boundary tests, Browser QA, commit |
| V7 | 검증 결과 표현 통일 | workspace read model, panel renderers | user-facing status가 `PASS / REVIEW / NEEDS_INPUT / BLOCKED / NOT_RUN / NOT_APPLICABLE`로 통일되고 raw route는 접힘 처리됨 | focused tests for status mapping and display rows |
| V8 | QA / durable docs alignment | `BACKTEST_UI_FLOW.md`, `PORTFOLIO_SELECTION_FLOW.md`, `SCRIPT_STRUCTURE_MAP.md`, task docs | 흐름 문서와 코드 책임 지도가 최종 구조와 일치함 | focused unittest, py_compile, git diff --check, Browser QA screenshot |

## V1 Development Direction After Approval

승인 후 V1 구현은 아래처럼 가장 작은 코드 변경으로 시작했고, 이후 V2-V8로 이어졌다.

1. `app/services/backtest_practical_validation_workspace.py` 초안을 만든다.
2. 현재 validation result에서 `core_evidence_groups`, `downstream_reference_groups`, `technical_details`를 분리하는 read model만 추가한다.
3. 기존 `page.py` render는 크게 바꾸지 않고, 먼저 tests로 taxonomy grouping을 고정한다.
4. UI 재배치는 V4로 미룬다.

V1 구현 완료 조건은 "보이는 화면 변경"이 아니라 이후 V2-V4가 안전하게 쓸 taxonomy/read-model contract를 만드는 것이다.
