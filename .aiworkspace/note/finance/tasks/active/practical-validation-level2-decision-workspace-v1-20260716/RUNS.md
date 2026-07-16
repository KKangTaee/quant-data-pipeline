# Runs

## 2026-07-16 Diagnosis Baseline

- `git status --short --branch`, recent commit log 확인.
- finance INDEX / ROADMAP / PROJECT_MAP / SCRIPT_STRUCTURE_MAP / BACKTEST_UI_FLOW / PORTFOLIO_SELECTION_FLOW 확인.
- 2026-07 Practical Validation validation audit와 Final Review evidence closure task 문서 확인.
- current Practical Validation page / workspace / closure / stage role / React component / boundary test source 확인.
- focused baseline:
  - `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_backtest_refactor_boundaries tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationReplayServiceContractTests`
  - result: 66 tests, `OK`.

## 2026-07-16 Design

- B안 Hybrid One-Shell Decision Workspace를 채택했다.
- protected `PRACTICAL_VALIDATION_RESULTS.jsonl`, run history, saved JSONL, generated QA artifact는 수정하거나 stage하지 않았다.

## 2026-07-16 Plan

- `superpowers:writing-plans` 기준으로 1차 truth contract, 2차 read model, 3차 one-shell UI, 4차 QA / docs의 RED -> GREEN -> commit 단위를 작성했다.
- 구현 세션은 새 worktree를 만들지 않고 현재 `codex/backtest-dev`에서 `superpowers:executing-plans`를 사용한다.
- plan self-review에서 exact file, interface, test command, expected failure/pass, Korean commit, protected artifact exclusion을 확인했다.
- self-review에서 provider CTA와 실제 callable handler의 커밋 순서를 맞추고, `validation_result_id`를 read model 최상위 계약으로 고정했다.
- `source_required`, explicit measurement 기반 `measured_caution`, method audit의 actual PASS / remaining REVIEW 분리, 동일 root 중복 방지, React fallback / ResizeObserver / stale intent guard를 계획에 보강했다.
- current saved GRS-shaped row의 Validation Efficacy audit는 walk-forward REVIEW 1개와 OOS / regime PASS 2개를 실제로 보유하므로 generic module 문구만 first-read에 쓰지 않도록 projection 기준을 명시했다.

## 2026-07-16 Implementation / TDD

- 1차 RED: single component applicability, provider callable action, closure class count contract 실패를 확인했다.
- 1차 GREEN: focused 49 tests, py_compile, diff-check 통과.
- commit: `a2352f01 Practical Validation 검증 의미 계약 보정`.
- 2차 RED: 새 Decision Workspace service import failure 6건을 확인했다.
- 2차 GREEN: focused 58 tests, py_compile, diff-check 통과.
- commit: `0e180f93 Practical Validation 판단 워크스페이스 모델 도입`.
- 3차 RED: one-shell component / active render / visual contract 부재로 boundary / visual tests가 실패함을 확인했다.
- 3차 review RED: 동일 replay/profile에서 validation UUID가 rerun마다 바뀌는 stale intent 결함과 제거된 import를 참조하는 legacy command-center `NameError`를 각각 failing test로 고정했다.
- 3차 GREEN: focused 52 tests, React production build 175 modules, target py_compile, diff-check 통과.
- commit: `b661e83a Practical Validation Level2 원셸 UI 전환`.

## 2026-07-16 Completion Verification

- command:
  - `.venv/bin/python -m unittest tests.test_backtest_practical_validation_decision_workspace tests.test_practical_validation_market_context_visual_contract tests.test_backtest_evidence_closure tests.test_backtest_refactor_boundaries tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationReplayServiceContractTests`
- result: 82 tests, `OK`, 6.907s.
- React: Vite 5.4.21 production build, 175 modules, 458ms.
- py_compile: construction risk, evidence closure, practical validation wrapper, decision workspace, legacy workspace, page, fallback panel, component wrapper 8 targets 통과.
- `git diff --check`: 통과.
- read-only projection:
  - source `selection_rebuilt_grs_macro_top1_ma200_aef1f226`
  - Final Review latest-per-source selector validation `validation_selection_rebuilt_grs_macro_top1_ma200_aef1f226_d289e7e8`
  - `ready_with_handoff / resolve_now 0 / engineering 0 / missing_contract 0 / accepted_limit 6 / final_decision 1`
- Streamlit:
  - 기존 backtest-dev 8505 process만 중지하고 same command로 재시작.
  - new PID `60347`.
  - `GET /backtest` HTTP 200, `/_stcore/health` = `ok`.
- Browser QA:
  - Browser / Computer Use skill이 요구하는 Node JS UI control tool이 현재 세션에 노출되지 않아 desktop / 760px visual, console, overflow, screenshot QA는 실행하지 못했다.
  - provider collection, audit save, Final Review save는 실행하지 않았다.
- protected scope:
  - `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` unstaged.
  - `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl` untracked / unstaged.
  - saved JSONL, generated screenshots, `.superpowers/` unstaged.

## 2026-07-16 Correction Task 5

- RED:
  - computed `pv_practical_caution`이 `accepted_limit`로 잘못 분류됨을 확인.
  - missing Level2 validation도 `accepted_limit`로 우회됨을 확인.
  - module producer에 `evidence_state`, closure/workspace에
    `validated_caution_count`가 없음을 확인.
- GREEN:
  - module audit / diagnostic status에서 `verified / computed / missing /
    not_applicable` evidence state를 명시.
  - evidence가 있는 Level2 caution은 `validated_caution / resolved`,
    missing required validation은 `engineering_required / deferred`로 분리.
  - focused closure / workspace / boundary / service 85 tests `OK`.
  - target py_compile과 `git diff --check` 통과.
- protected registry, run history, saved JSONL, generated artifact는 stage하지 않음.

## 2026-07-16 Correction Task 6

- RED:
  - 후보 source kind가 `selection_source` 같은 내부 값으로 노출됨을 확인.
  - 후보 선택과 검증 정책이 같은 카드 묶음으로 렌더링됨을 확인.
  - 최신 재검증 intent가 전체 앱 rerun만 호출해 Step 1까지 다시 마운트됨을 확인.
- GREEN:
  - 후보 선택을 `1A`, 검증 관점을 `1B` 독립 영역으로 분리하고 현재 선택을
    disabled opacity 대신 active state로 표현.
  - source kind를 `혼합 포트폴리오`, `단일 전략 실행` 사용자 언어로 projection.
  - selection / profile / replay / Level2 resolution은 `@st.fragment` 범위로
    rerun하고 Final Review 이동만 app scope rerun을 유지.
  - React pending state는 Step 2 재검증 영역에만 표시.
  - focused 89 tests `OK`, React production build 175 modules 통과.
  - target py_compile과 `git diff --check` 통과.
- protected registry, run history, saved JSONL, generated artifact는 stage하지 않음.

## 2026-07-16 Correction Task 7

- RED:
  - explanation service import가 없고 audit row가 `Criteria / Current /
    Evidence` 원문으로 바로 노출됨을 확인.
  - 상세 근거가 비정규 category 2개로 projection되고 모든 group을 한꺼번에
    렌더링함을 확인.
- GREEN:
  - pure `explain_practical_validation_row` 계약으로 검증 항목, 확인 결과,
    의미, 다음 조치를 사용자 언어로 분리.
  - raw function path와 status trace는 `technical_trace` disclosure 안으로 이동.
  - 데이터/편향, 검증 방법, 포트폴리오 구성, 실전 현실성, 스트레스/강건성
    5개 고정 category와 상호 배타 count를 projection.
  - React는 category selector와 active panel 하나만 렌더링하고 Streamlit
    fallback도 동일 설명 순서를 유지.
  - focused 98 tests `OK`, React production build 175 modules 통과.
  - explanation / decision workspace / fallback target py_compile과
    `git diff --check` 통과.
- protected registry, run history, saved JSONL, generated artifact는 stage하지 않음.

## 2026-07-16 Correction Task 8

- RED:
  - 계산되지 않은 walk-forward / OOS / regime 방법론 row가 `REVIEW`로
    생성되어 computed caution처럼 종결됨을 확인.
  - 모든 historical stress window가 후보 기간 밖이어도 `NOT_RUN`으로
    집계되어 validator 누락과 구별되지 않음을 확인.
  - producer가 받은 `NOT_APPLICABLE`을 NEEDS_INPUT / REVIEW로 coercion하는
    경계를 확인.
- GREEN:
  - 실제 미실행 필수 방법론은 `NEEDS_INPUT`, module evidence state
    `missing`, closure `engineering_required / deferred`로 연결.
  - 기간 밖 stress는 `NOT_APPLICABLE`, covered-but-uncomputed만
    `missing_validator_count`로 분리.
  - PASS와 NOT_APPLICABLE row는 audit ready count에 포함하고 REVIEW를
    만들지 않도록 validation efficacy / realism aggregation 보정.
  - 수집 가능한 provider gap은 기존
    `run_practical_validation_provider_gap_collection` handler를 가진
    `resolve_now`로 유지하는 회귀 계약 추가.
  - focused producer / module / closure 75 tests `OK`.
  - 6 target py_compile과 `git diff --check` 통과.
- protected registry, run history, saved JSONL, generated artifact는 stage하지 않음.

## 2026-07-16 Correction Task 9

- current GRS read-only projection:
  - validation:
    `validation_selection_rebuilt_grs_macro_top1_ma200_aef1f226_d289e7e8`
  - state: `ready_with_handoff`
  - verified 22 / measured caution 0 / validated caution 5
  - resolve-now 0 / engineering blocker 0 / missing contract 0
  - enrichment required false / item count 0
  - Final Review handoff:
    `historical_universe_coverage / accepted_limit`,
    `tax_account_scope / final_decision`
- runtime projection RED:
  - summary는 accepted limit 1 / final decision 1이었지만 measurement가 있는
    handoff issue가 measured-caution으로 덮여 lane이 비는 회귀를 확인.
  - failing test:
    `test_measured_accepted_limit_remains_final_review_handoff`.
- runtime projection GREEN:
  - measured caution을 `validated_caution`에만 한정.
  - accepted limit / final decision / monitoring transfer는 measurement가
    있어도 Final Review handoff class를 유지.
  - focused decision-workspace / hardening 22 tests `OK`.
  - commit:
    `d968b6a4 Practical Validation Final Review 인계 분류 보정`.
- completion verification:
  - focused closure / service / boundary / visual contract 124 tests `OK`.
  - Vite 5.4.21 production build, 175 modules, CSS
    `index-DAxIKqih.css`, JS `index-Bywe31X0.js`.
  - target py_compile 통과.
  - `git diff --check` 통과.
  - restarted worktree Streamlit on 8505; `/_stcore/health=ok`,
    `/backtest=HTTP 200`.
- Browser QA:
  - installed Browser skill이 요구하는 `mcp__node_repl__js` control tool이
    현재 세션 tool surface에 노출되지 않아 desktop / 760px interaction,
    console, overflow, screenshot QA를 실행하지 못했다.
  - 외부 Playwright / Computer Use 대체는 Browser skill contract에 따라
    사용하지 않았다.
- protected scope:
  - `PRACTICAL_VALIDATION_RESULTS.jsonl` modified / unstaged.
  - `BACKTEST_RUN_HISTORY.jsonl`, generated screenshot, `.superpowers/`
    untracked / unstaged.
  - saved JSONL과 run artifact는 stage하지 않음.
