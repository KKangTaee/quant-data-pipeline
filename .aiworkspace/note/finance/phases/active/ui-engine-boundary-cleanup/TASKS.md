# UI Engine Boundary Cleanup Tasks

Status: Active
Created: 2026-05-27

## Task Board

| Task | Owner Scope | Status | Notes |
| --- | --- | --- | --- |
| `0. ui-engine-boundary-cleanup-audit` | phase/task design, current code audit | Complete | hard violation 없음, advisory 3건과 Task 6~9 방향 확정 |
| `6. practical-validation-helper-boundary` | Practical Validation curve / provider context helper 이동 | Complete | `app.services/app.runtime -> app.web` advisory 제거 |
| `7. practical-validation-diagnostics-split` | 큰 diagnostics service 책임 분할 | Complete | `7-01`~`7-04` 완료; diagnostics public compatibility contract 명시 |
| `8. runtime-wrapper-cleanup` | 큰 runtime wrapper 구조 분석과 낮은 위험 split | Complete | `8-01`~`8-04` 완료; result bundle helper를 `app/runtime/backtest_result_bundle.py`로 분리 |
| `9. boundary-contract-hardening` | lint / test / docs hardening | Complete | `app.web` import hard fail 승격, boundary contract test / runbook 정렬 |

## Task 0. Cleanup Audit

하위 단계:

| Step | Goal | Status |
| --- | --- | --- |
| `0-01` | docs / code boundary baseline 확인 | Complete |
| `0-02` | lint advisory와 큰 파일 후보 확인 | Complete |
| `0-03` | Task 6~9 범위와 완료 기준 문서화 | Complete |
| `0-04` | root handoff log와 roadmap 갱신 | Complete |

## Task 6. Practical Validation Helper Boundary

목표:

- `app/web`에 남아 있는 Streamlit-free helper를 service 위치로 이동한다.
- `app/services`와 `app/runtime`이 `app/web`을 import하지 않는 상태로 만든다.
- 계산 결과 shape는 바꾸지 않는다.

하위 단계:

| Step | Goal | Expected Files | Done Check |
| --- | --- | --- | --- |
| `6-01` | curve helper 이동 | `app/services/backtest_practical_validation_curve.py`, imports | Complete |
| `6-02` | provider context connector 이동 | `app/services/backtest_practical_validation_provider_context.py`, imports | Complete |
| `6-03` | docs / tests / lint 정렬 | project map, script map, data flow docs, service tests | Complete |

권장 검증:

- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `rg -n "from app\\.web\\.|import app\\.web\\." app/services app/runtime -g '*.py'`

브라우저:

- import 이동만으로 화면이 바뀌지 않으면 browser QA는 생략 가능하다.
- provider coverage / diagnostics board 표시 shape를 건드리면 Streamlit Practical Validation 화면을 열어 확인한다.

## Task 7. Practical Validation Diagnostics Split

목표:

- 2956 line diagnostics service를 역할별 helper로 나눈다.
- `build_practical_validation_result`는 orchestration entry로 유지한다.
- source / profile / curve / stress / sensitivity 계산을 더 찾기 쉽게 만든다.

하위 단계:

| Step | Goal | Notes |
| --- | --- | --- |
| `7-01` | source/profile builder 분리 | Complete |
| `7-02` | curve context helper 분리 | Complete |
| `7-03` | stress/sensitivity evidence helper 분리 | Complete |
| `7-04` | orchestration import 정리 | Complete |

주의:

- 이 task는 코드 흐름을 깊게 다시 읽고 시작한다.
- 계산식 변경은 하지 않는다.
- provider helper 이동 Task 6이 끝난 뒤 진행한다.

## Task 8. Runtime Wrapper Cleanup

목표:

- `app/runtime/backtest.py`의 5191 line 책임을 함수군 단위로 정리한다.
- 바로 대규모 split하지 않고, strategy family / policy surface / result bundle / preflight 영역을 먼저 지도화한다.
- 안전한 낮은 위험 split만 적용한다.

하위 단계:

| Step | Goal | Notes |
| --- | --- | --- |
| `8-01` | runtime function-family map 작성 | Complete |
| `8-02` | import cycle / public API 사용처 확인 | Complete |
| `8-03` | characterization test 후보 추가 | Complete |
| `8-04` | 낮은 위험 split 적용 | Complete: result bundle helper split |

주의:

- strategy 결과 숫자가 바뀌는 refactor는 하지 않는다.
- split 전후 public runtime function 이름을 유지한다.
- 브라우저보다 unit / smoke verification이 우선이다.

## Task 9. Boundary Contract Hardening

목표:

- Task 6~8 cleanup 결과가 다시 흐트러지지 않도록 자동 검증을 강화한다.
- advisory였던 `app.services/app.runtime -> app.web` import를 hard failure로 승격한다.
- docs/runbook을 phase 이후 구조에 맞춘다.

하위 단계:

| Step | Goal | Notes |
| --- | --- | --- |
| `9-01` | boundary lint hardening | Complete |
| `9-02` | service contract test 보강 | Complete |
| `9-03` | docs/runbook 정렬 | Complete |
| `9-04` | phase closeout QA | Complete |
