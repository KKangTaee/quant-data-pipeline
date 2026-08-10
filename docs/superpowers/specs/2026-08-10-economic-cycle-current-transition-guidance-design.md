# Economic Cycle Current Transition Guidance Design

## 목적

경제사이클 화면에서 `현재 관측 위축`과 `회복 앵커 → 확장 조건`이 동시에 보이면서 사용자가 확장을 가까운 전망으로 오해하는 문제를 해결한다. 현재 정식 월말 국면에서 실제로 다음에 확인해야 할 인접 국면과 그 근거를 첫 판단 흐름으로 만들고, 과거 앵커는 추적용 보조 정보로 내린다.

## 확인된 원인

- 저장된 transition state machine은 단기 좌표 변동에 즉시 앵커를 바꾸지 않도록 `observed_phase`, `anchor_phase`, `target_phase`를 분리한다.
- 현재 payload는 `observed_phase=contraction`, `anchor_phase=recovery`, `target_phase=expansion`, `non_adjacent_observation=true`다.
- 순환 경로 지도는 non-adjacent 상태에서 `위축 → 회복`을 표시하지만 전환 패널은 원래 앵커를 그대로 사용해 `회복 → 확장` 조건을 표시한다.
- `UNMET` 조건을 모두 `관찰 중`으로 번역하고 threshold만 노출해 실제 값이 기준에서 얼마나 떨어져 있는지 알 수 없다.

## 승인된 화면 계약

### 1. 현재 판단 요약

전환 패널 첫 줄은 아래 네 항목을 보여준다.

- 정식 월말 국면과 지속 개월
- 최근 1·3개월 방향
- 다음 확인 국면
- 전환 조건 충족 수

현재 데이터의 기본 문구는 `현재 위축 3개월 · 1·3개월 혼조 · 다음 확인 회복 · 0/3 충족`이다.

### 2. 사용자용 전환 경로

- `non_adjacent_observation=true`이면 `현재 관측 국면 → 현재 국면의 구조적 다음 인접 국면`을 표시한다.
- 그 밖에는 state machine의 `anchor_phase → target_phase`를 유지한다.
- 이 경로는 발생 확률이나 특정 시점 예측이 아니다.
- 저장된 transition monitor와 observed-state 계산은 변경하지 않는다. Overview service가 DB row를 사용자용 `current_transition` read model로 파생한다.

### 3. 조건 표시

`current_transition.conditions`는 각 조건에 아래 필드를 제공한다.

- `status`: `MET | UNMET | UNAVAILABLE`
- `label`
- `value_label`: 실제 값
- `threshold_label`: 비교 기준

현재 `위축 → 회복`은 모멘텀 기준으로 계산한다.

- 지속성: 현재/이전 종합 모멘텀이 2회 연속 0 이상
- 확산도: 모멘텀 방향을 지지하는 실물지표가 60% 이상
- 활동·고용 동반: 활동 모멘텀과 고용·소득 모멘텀이 모두 0 이상

UI 상태 문구는 `충족`, `미충족`, `자료 부족`으로 구분한다. 영문 threshold는 노출하지 않는다.

### 4. 잠정 변화와 과거 앵커

- 월중 잠정 변화가 있으면 `잠정 좌표`, `raw level 변화`, `정식 월말 판정 유지`를 한 줄로 보여준다.
- 사용자용 경로와 과거 앵커가 다를 때 앵커는 `이전 모델 기준 · 보조 정보`로 축소한다.
- `LEGACY_OBSERVED`는 확정 앵커로 표현하지 않고 `미확정 이력`을 명시한다.

## 계층과 파일 경계

- `app/services/overview/economic_cycle.py`: 기존 snapshot/history에서 사용자용 `current_transition`과 한국어 값/기준을 파생한다. provider fetch, DB write, materialization은 하지 않는다.
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`: current transition을 primary로 렌더하고 anchor를 secondary로 표시한다.
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`: 승인된 요약·조건 row·보조 anchor 반응형 layout을 구현한다.
- 기존 `finance/economic_cycle_observed_state.py` state machine, 자산별 확인 포인트, Data Freshness는 변경하지 않는다.

## 완료 조건

- 실제 2026-07-31 payload에서 전환 패널의 primary path가 `위축 → 회복`이다.
- 조건은 0/3이며 실제 값과 한국어 기준, `미충족` 상태를 표시한다.
- `회복 앵커 · 미확정 이력`은 secondary reference에서만 보인다.
- 순환 경로 지도와 전환 패널이 같은 current path를 사용한다.
- 기존 인접 transition과 confirmed transition 동작은 유지한다.
- React/Python regression, TypeScript, production build, desktop/420px Browser QA를 통과한다.

## Non-goals

- 미래 국면 확률 또는 전환 시점 예측
- 경제사이클 phase 계산식이나 확인 threshold 변경
- 앵커 state machine 재설계 또는 DB snapshot 재작성
- 자산별 확인 포인트와 Data Freshness 디자인 변경
