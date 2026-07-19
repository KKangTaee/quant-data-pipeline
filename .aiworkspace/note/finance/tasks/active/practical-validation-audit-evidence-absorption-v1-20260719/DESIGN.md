# Practical Validation Audit Evidence Absorption V1 Design

## 이걸 하는 이유?

Level 2 하단 `원본 데이터·감사 정보`는 후보 약 493KB, 판정 약 833KB의 내부 JSON과 중복 snapshot을 그대로 노출한다. 데이터는 재현과 Final Review 인계에 필요하지만 사용자가 현재 단계에서 판단하기에는 너무 크고, 후보 원본 / 재검증 원본 / 판정 원본의 차이를 내부 schema 지식 없이 이해하기 어렵다.

필요한 provenance를 실제로 사용하는 Step 1, Step 2, Step 4에 흡수하고 raw 탭을 제거한다. registry와 validation contract는 그대로 보존한다.

## 승인된 정보 구조

### Step 1: 검증 대상 요약

현재 후보 title / type / as-of에 다음 compact facts를 추가한다.

- 실제 백테스트 기간
- CAGR / MDD
- 구성 전략 수
- Data Trust 상태와 warning 수

후보 전체 curve, selection history, source snapshot JSON은 표시하지 않는다.

### Step 2: 재검증 기록

replay 실행 전에는 범위 선택과 실행 action만 보여준다. 실행 뒤에는 다음 provenance를 표시한다.

- 선택한 재검증 범위
- 요청 기간 / 실제 계산 기간
- 최신 공통 가격일
- 기간 coverage 상태 / 종료일 gap
- 제한 종목이 있으면 compact warning

`replay_id`와 실행 시각은 Step 4 기술 기록으로 낮춘다.

### Step 3: 사용자 판정 근거

현재 `상세 검증 근거`를 유지한다. raw validation JSON을 추가하지 않는다. 기준별 기술 원문은 이미 각 explanation 내부 disclosure가 소유한다.

### Step 4: 검증 기록

현재 세션 validation이 있을 때만 작은 `검증 기록` disclosure를 표시한다.

- 판정 프로필
- 재검증 방식
- 실행 시각
- Replay ID
- Validation ID

저장 성공 여부는 기존 notice가 소유한다. 별도 JSON download는 명시된 export/auditor 요구가 없으므로 이번 범위에 넣지 않는다.

## 데이터와 UI 경계

- `PORTFOLIO_SELECTION_SOURCES.jsonl`과 `PRACTICAL_VALIDATION_RESULTS.jsonl` 저장 계약을 변경하지 않는다.
- replay/validation builder 입력과 Final Review handoff payload를 변경하지 않는다.
- Python service가 raw dict에서 compact provenance를 투영한다.
- React와 Streamlit fallback은 투영된 text/list만 표시한다.
- 하단 `_render_decision_workspace_audit_evidence`와 `원본 데이터·감사 정보` expander는 current path에서 제거한다.

## 상태별 동작

- replay 전: Step 2 provenance는 표시하지 않고 `NOT_RUN`과 실행 action만 유지한다.
- replay 성공/주의: 실제 기간과 coverage를 표시한다.
- replay 실패: 존재하는 요청 기간과 상태를 표시하고 없는 실제 기간은 `-`로 표현한다.
- validation 전: Step 4 `검증 기록`은 표시하지 않는다.
- validation 생성 후: compact record만 표시하고 raw JSON은 렌더링하지 않는다.

## 완료 조건

1. current Level 2 path에 `원본 데이터·감사 정보`, `후보 원본`, `재검증 원본`, `판정 원본` 탭이 없다.
2. Step 1이 후보 기간 / 핵심 성과 / 구성 수 / Data Trust를 표시한다.
3. replay 후 Step 2가 요청·실제 기간 / 데이터 기준일 / coverage를 표시한다.
4. Step 4가 profile / replay / validation 식별자를 compact disclosure로 표시한다.
5. registry와 Final Review handoff behavior가 바뀌지 않는다.
6. desktop / 760px에서 가로 overflow와 browser console error가 없다.

## Scope Review

- Threshold 계산, replay engine, provider 수집, DB schema, registry row shape는 변경하지 않는다.
- Final Review / Monitoring UI와 live approval / broker order / auto rebalance는 범위 밖이다.
- raw data 삭제가 아니라 current Level 2 화면의 raw JSON 렌더링 제거다.
