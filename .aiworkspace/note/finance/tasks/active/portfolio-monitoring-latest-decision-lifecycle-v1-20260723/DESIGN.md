# Portfolio Monitoring Latest Decision Lifecycle V1 Design

Status: Approved
Date: 2026-07-23

## 이걸 하는 이유?

Final Review 판단은 append-only로 보존되지만 Portfolio Monitoring은 현재 모든 과거 row를 개별 후보로 읽는다. 같은 후보가 과거에는 `계속 추적`이었고 최신 판단은 보류·제외·Level2 반환이어도 과거 `monitoring_candidate=true` row가 신규 후보와 기존 추적 실행에 계속 사용될 수 있다. 과거 기록을 삭제하지 않으면서 최신 판단을 현재 자격으로 해석해야 한다.

## 검토한 접근

### A. 최신 판단이 바뀌면 기존 추적 자동 종료

- 장점: 현재 판단과 Monitoring 상태가 즉시 일치한다.
- 단점: 사용자 포트폴리오를 자동 변경하고 기존 관측 기록의 연속성을 끊는다.
- 결론: 채택하지 않는다.

### B. 경고만 표시하고 Scenario 실행 유지

- 장점: 기존 계산이 중단되지 않는다.
- 단점: 사용자가 제외한 후보가 새 결과를 계속 만들고, 최신 판단과 운영 상태가 어긋난다.
- 결론: 채택하지 않는다.

### C. 최신 판단을 current truth로 사용하고 기존 항목은 잠금

- 장점: append-only 이력을 보존하고 신규 등록·기존 실행의 의미를 일치시키며 자동 삭제를 피한다.
- 단점: 사용자가 Final Review 재확인 또는 추적 종료 중 하나를 명시적으로 선택해야 한다.
- 결론: 사용자 승인으로 채택한다.

## 승인된 사용자 흐름

1. 신규 `백테스트 전략` 목록은 후보별 최신 Final Review 판단만 읽는다.
2. 최신 판단이 `계속 추적`이고 selection Gate를 통과한 후보만 신규 등록 목록에 표시한다.
3. 이미 Monitoring에 담긴 전략의 최신 판단이 보류·제외·Level2 반환으로 바뀌면 항목은 삭제하지 않는다.
4. 해당 항목은 `추적 자격 변경`으로 표시하고 새 Scenario/replay 실행을 잠근다. 다른 정상 항목은 계속 계산한다.
5. 사용자는 다음 중 하나를 선택한다.
   - `최신 판단 재확인`: Backtest Final Review로 이동해 최신 근거를 확인하고, 계속 추적하려면 새 `계속 추적` 판단을 기록한다.
   - `추적 종료`: 기존 Portfolio Monitoring 종료 명령을 사용해 항목과 종료 시점 기록을 보존한다.
6. 같은 후보의 최신 판단이 다시 유효한 `계속 추적`으로 저장되면 기존 Monitoring 항목은 최신 selected decision contract로 자동 연결되어 실행 잠금이 해제된다.

## 최신 판단 identity

동일 후보 판단을 묶는 key는 다음 순서로 만든다.

1. `selection_source_id`
2. `source_type + source_id`
3. `decision_id`

최신 row는 `updated_at`, `created_at`, registry 입력 순서를 기준으로 결정한다. 같은 subject의 과거 row는 삭제하거나 재작성하지 않는다.

## 소유 경계

- 새 Streamlit-free lifecycle helper가 subject identity, 최신 row projection, 기존 decision의 현재 자격을 계산한다.
- Portfolio Monitoring catalog는 helper가 반환한 최신 row 중 `monitoring_candidate is True`만 노출한다.
- Selected Strategy replay adapter는 기존 `decision_id`를 원본으로 찾은 뒤 같은 subject의 최신 row를 다시 확인한다.
  - 최신 row가 selected이면 최신 replay contract를 사용하고 requested/effective decision ID를 provenance에 남긴다.
  - 최신 row가 non-select이면 `TRACKING_ELIGIBILITY_CHANGED`로 실행을 차단한다.
- Portfolio Monitoring read model은 lifecycle 상태와 최신 route를 item row에 투영한다.
- React는 계산하지 않고 `추적 자격 변경`, 최신 판단, 두 후속 행동을 표시한다.
- Final Review registry, Monitoring item, run history는 자동 재작성하지 않는다.

## 이동 및 명령

- `최신 판단 재확인`은 Portfolio Monitoring React event를 Python이 검증한 뒤 Backtest Final Review로 이동한다.
- 가능한 경우 latest decision의 `source_id`를 Final Review active candidate hint로 전달한다.
- `추적 종료`는 기존 idempotent `end_item` command를 그대로 사용한다.
- Portfolio Monitoring에서 Final Review 판단을 대신 생성하거나 selected 자격을 로컬 override하지 않는다.

## 실패 처리

- 원본 decision row가 없으면 기존 `decision not found` 차단을 유지한다.
- subject identity를 만들 수 없으면 해당 `decision_id` 자체를 독립 subject로 취급한다.
- 최신 selected row에 replay component가 없으면 기존 replay-contract blocker를 유지한다.
- 최신 non-select row는 다른 정상 항목의 가치 계산을 막지 않고 해당 항목만 partial/failure로 투영한다.
- Final Review 이동 대상이 없으면 사용자에게 경로 안내를 표시하고 registry를 변경하지 않는다.

## 완료 조건

- 같은 subject의 과거 selected + 최신 hold/reject/re-review 조합에서 신규 catalog에 과거 selected가 나오지 않는다.
- 기존 item은 삭제되지 않으며 `추적 자격 변경`과 최신 route를 표시한다.
- 자격 변경 item은 replay/Scenario 실행이 잠기고 다른 정상 item은 계산된다.
- 최신 selected 판단이 다시 생기면 기존 item이 최신 decision contract로 정상 실행된다.
- `최신 판단 재확인`과 기존 `추적 종료`가 화면에서 명확히 분리된다.
- registry/saved/run history를 테스트나 구현 과정에서 재작성하지 않는다.
- Python/React 회귀 테스트, typecheck/build, actual Browser QA, durable finance 문서 동기화를 완료한다.

## 범위 밖

- 과거 Final Review row 삭제 또는 수정
- Portfolio Monitoring 항목 자동 종료·자동 삭제
- Monitoring 내부의 Final Review 판단 override 또는 waiver 저장
- broker order, account sync, live approval, auto rebalance
