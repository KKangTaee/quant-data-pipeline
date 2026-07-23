# Final Review Liquidity Evidence Copy V1 Design

## 문제

Final Review(Level3)의 실행 근거 카드가 `liquidity_capacity_contract.proof_status`를 그대로 `display_value`와 비교 기준에 넣는다. 그 결과 `weak_source_or_proxy_liquidity_evidence`, `official_fresh_capacity_evidence` 같은 내부 enum이 사용자 화면에 노출된다.

현재 판정 자체는 `app/services/backtest_realism_audit.py`가 올바르게 소유한다. 문제는 `app/services/backtest_final_review_decision_brief.py`가 내부 판정값과 사용자 표시값을 분리하지 않은 presentation adapter 경계다.

## 검토한 접근

### 1. 권장: Final Review read model에서 상태별 사용자 문구로 변환

- 내부 `proof_status`와 Gate 의미는 그대로 유지한다.
- Decision Brief가 `proof_status -> 사용자 현황 문구`를 명시적으로 매핑한다.
- 카드의 기준 문구도 내부 enum 대신 `공식 제공처의 최신 유동성 근거 확보`로 표시한다.
- 알 수 없는 신규 상태는 안전한 일반 문구로 표시하고 raw 값은 사용자 first-read에 노출하지 않는다.

장점은 저장 계약과 판정 로직을 건드리지 않으면서 Level3 표시만 정확하게 개선한다는 점이다.

### 2. React에서 underscore를 공백으로 치환

영문 내부 용어가 그대로 남고 상태별 의미를 설명하지 못한다. 다른 enum에도 우연히 적용될 수 있어 채택하지 않는다.

### 3. upstream enum 자체를 한글 문구로 변경

테스트, registry, Gate, audit contract의 stable identity를 깨뜨릴 수 있어 채택하지 않는다.

## 선택 설계

### 표시 문구

- 카드 제목: `유동성·운용 가능성 근거`
- 설명: `공식 제공처의 유동성 자료 범위와 최신성을 확인합니다.`
- 비교 기준: `공식 제공처의 최신 유동성 근거 확보`

상태 매핑:

| 내부 상태 | 사용자 표시 |
|---|---|
| `official_fresh_capacity_evidence` | 공식 제공처의 최신 유동성 근거 확보 |
| `weak_source_or_proxy_liquidity_evidence` | 공식 자료가 부족하거나 일부 대체 지표를 사용함 |
| `partial_liquidity_coverage` | 일부 구성요소의 유동성만 확인됨 |
| `stale_or_unknown_provider_snapshot` | 유동성 자료의 최신성 확인 필요 |
| `provider_operability_review` | 유동성 근거 추가 검토 필요 |
| `missing_provider_operability` | 유동성 근거가 아직 없음 |
| `blocked_provider_operability` | 가격 또는 제공처 문제로 유동성 확인 불가 |
| `legacy_provider_pass_without_capacity_contract` | 이전 형식 자료로 세부 유동성 근거 확인 필요 |
| `incomplete_liquidity_capacity_evidence` | 유동성 근거가 불완전함 |
| 그 외 신규 상태 | 유동성 근거 상태 확인 필요 |

### 데이터 경계

- `measured_value`에는 기존 raw `proof_status`를 유지해 내부 진단과 계약 호환성을 보존한다.
- `display_value`와 `threshold_or_comparator`만 사용자 문구로 변환한다.
- React는 현재처럼 전달받은 read model을 표시만 하며 별도 변환 로직을 갖지 않는다.

### 테스트

- weak/proxy 상태가 사용자 문구로 변환되는 계약 테스트
- official/fresh 기준 문구가 내부 enum이 아닌 사용자 문구인지 확인
- raw `measured_value`에는 stable enum이 남는지 확인
- 기존 Decision Brief / Final Review focused regression
- Browser QA에서 underscore enum이 보이지 않고 카드 줄바꿈과 좁은 폭 overflow가 없는지 확인

## 범위 밖

- 유동성 판정 기준, Gate, `proof_status` 생성 규칙 변경
- registry / saved JSONL rewrite
- 다른 Level3 카드의 수치나 문구 전면 개편
- provider 수집 또는 replay 변경

## 완료 조건

- Level3 카드의 제목, 현황, 설명, 기준에서 내부 변수명처럼 보이는 문구가 사라진다.
- internal enum과 Gate 계약은 그대로 유지된다.
- focused test와 actual Browser QA를 통과한다.
