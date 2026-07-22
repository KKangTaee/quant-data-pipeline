# Practical Validation Enrichment Recheck UX V1 Design

## Context

Level2는 외부 데이터 보강을 실행하면 stale validation evidence를 재사용하지 않도록 current replay와 decision result를 지운다. 이 동작은 정확하다. 문제는 `practical_validation_enrichment_progress_<source>`와 provider collection results가 session에 남아 있어도 현재 React Decision Workspace가 이를 입력으로 받지 않는다는 점이다.

기존 `build_practical_validation_recovery_progress()`와 Python recovery renderer는 4단계 진행 계약을 보유하지만, 2026-07-16 one-shell 전환 뒤 main render path에서 호출되지 않는다. 현재 boundary test는 이 Python renderer가 없어야 한다고 고정해 진행 계약이 UI에서 단절된 상태다.

## Approved Product Direction

권장안은 한 화면 안에서 두 개의 명시적 작업을 연결하는 방식이다.

1. 사용자가 `필수 데이터 보강`을 명시적으로 실행한다.
2. 수집 완료 후 같은 decision surface가 `자료 보강 완료 · 재검증 필요` 상태로 바뀐다.
3. primary CTA는 `보강된 데이터로 재검증`이 된다.
4. replay 완료 후 Gate 결과에 따라 `새 결과 저장 / Final Review 이동` 또는 구체적인 남은 해결 항목으로 전환된다.

수집과 replay를 한 번의 자동 실행으로 합치지 않는다. 이 구분은 장시간 실행, 부분 실패, 수집과 검증의 감사 경계를 명확히 유지한다.

## Alternatives Considered

### A. 상태 기반 one-shell 진행 카드 — 채택

- 장점: 사용자의 다음 행동이 즉시 보이고 기존 실행/저장 경계를 유지한다.
- 단점: 사용자는 수집 후 재검증 버튼을 한 번 더 눌러야 한다.

### B. 수집 완료 직후 replay 자동 실행

- 장점: 클릭 수가 줄어든다.
- 단점: 일부 collector 실패 시 어떤 데이터로 replay했는지 불명확하고, 장시간 두 작업이 하나의 pending 상태로 합쳐진다.

### C. 기존 Python recovery panel을 React 위에 다시 표시

- 장점: 구현 범위가 작다.
- 단점: Streamlit panel과 React one-shell이 다시 분리돼 시각적·상태적 중복이 생긴다.

## Architecture

### 1. Python Session State Boundary

`_complete_provider_gap_collection()`은 기존처럼 다음을 수행한다.

- provider collection result 저장
- current replay / decision result 초기화
- source별 enrichment progress를 `recheck_required`로 저장

추가로 notice는 문자열이 아니라 `tone`, `title`, `detail`을 가진 UI feedback contract로 저장한다. collector result는 성공/부분 성공/실패 개수와 실행된 영역만 compact summary로 정규화한다.

### 2. Decision Workspace Read Model

`build_practical_validation_decision_workspace()`는 선택 인자로 enrichment progress와 collection summary를 받는다. read model은 다음 상태를 명시적으로 투영한다.

- `none`: 일반 Level2 진입
- `recheck_required`: 자료 보강은 실행됐고 새 replay가 필요함
- `blocked`: replay 후에도 blocker가 남음
- `save_ready`: replay와 Gate가 새 결과 저장 조건을 충족함

기존 `build_practical_validation_recovery_progress()`의 단계 의미를 재사용하되 React가 소비할 JSON-safe 모델로 전달한다.

### 3. React Decision Surface

Step 2 상단에 enrichment lifecycle이 있을 때만 compact progress surface를 표시한다.

- 현재 단계 headline과 다음 행동
- `자료 보강 / 재검증 / 새 결과 저장 / Final Review` 단계 상태
- 수집 결과 `성공 N / 일부 확인 N / 실패 N` compact summary
- `보강된 데이터로 재검증` primary CTA

raw job name, rows written, internal status table은 first-read에 두지 않는다. 필요한 기술 근거는 기존 상세 disclosure 또는 session evidence에 남긴다.

### 4. Feedback Semantics

- 수집 완료 후 재검증 필요: `warning`
- replay/저장 완료: `success`
- 잘못된 intent, 실행 불가, Gate 차단: `warning` 또는 `error`
- 단순 정보: `info`

현재처럼 모든 notice를 `st.success()`로 렌더링하지 않는다.

### 5. Fallback

React component가 unavailable일 때도 같은 read model을 사용해 현재 단계, compact collection summary, primary replay action을 Streamlit fallback에 표시한다. 별도의 legacy Flow panel은 복원하지 않는다.

## Data And Persistence Boundaries

- provider raw data와 holdings/exposure/macro series는 DB에 저장한다.
- collection execution history는 기존 run history 경계를 유지한다.
- enrichment progress, notice, latest collection result는 session state다.
- Practical Validation registry는 명시적 저장 action에서만 append한다.
- 기존 validation row와 saved setup을 재작성하거나 삭제하지 않는다.

## Error Handling

- collector 일부가 실패해도 stale replay는 초기화한다.
- 전체 성공처럼 표시하지 않고 `부분 완료 · 재검증 후 남은 항목 확인`으로 안내한다.
- replay 실패/REVIEW도 시도한 current replay로 판정하되, Gate 결과에 따라 저장/이동을 제한한다.
- 후보가 바뀌면 다른 source의 progress와 collection result를 노출하지 않는다.
- notice는 일회성일 수 있지만 enrichment lifecycle은 replay 또는 save 완료 전까지 source별 session state로 유지한다.

## Test Contract

- collection completion이 replay를 지우고 structured warning feedback과 `recheck_required` progress를 만든다.
- collection result summary가 SUCCESS/partial/failure를 전체 성공으로 합치지 않는다.
- Decision Workspace가 progress를 받아 `보강된 데이터로 재검증` action을 제공한다.
- React source가 lifecycle surface와 단계 label을 렌더링한다.
- boundary test는 Python recovery panel 부재가 아니라 one-shell lifecycle projection 존재를 검증한다.
- current replay 없는 save-and-move 차단, Gate, explicit storage/handoff tests는 유지한다.
- actual Browser QA에서 보강 직후 상태, replay CTA, replay 후 결과/저장 전환, console/overflow를 확인한다.

## Files Likely To Change

- `app/web/backtest_practical_validation/page.py`
- `app/services/backtest_practical_validation_decision_workspace.py`
- `app/services/backtest_practical_validation_workspace.py` 또는 작은 전용 helper
- `app/web/backtest_practical_validation/workspace_panel.py`
- `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- 관련 Python/React contract tests

## Non-Goals

- provider collector, parser, source map 정책 변경
- 자동 replay 또는 자동 validation 저장
- Final Review 판단 기준 변경
- raw 운영 진단 panel 신설
- registry 정리, 과거 row 삭제, saved setup 변경
