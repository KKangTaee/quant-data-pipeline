# Practical Validation Stage Ownership V1 Design

## 문제 이해

현재 Flow4는 검증 모듈 수가 줄어든 것이 아니라 `REVIEW` 상태가 사용자-facing UI에서 두 가지 문제를 만든다.

- `REVIEW`가 모두 `Final Review review`처럼 표시되어 Practical Validation의 실용성 판단 책임이 Final Review로 밀린다.
- REVIEW-only 카테고리가 `visible_criteria_detail_groups`에서 숨겨져 카테고리별 검증 결과가 1~2개만 남은 것처럼 보인다.

## Stage Ownership Matrix

| Stage | 사용자 질문 | 소유 검증 | PV 표시 원칙 | Final Review 표시 원칙 |
|---|---|---|---|---|
| 1단계 데이터 / 기본 검증 | 이 후보가 검증 가능한 입력과 최신 재현성을 갖췄나? | source integrity, latest replay, data coverage, benchmark parity, PIT / survivorship / lifecycle gap | PASS / 보강 필요 / 미실행을 명확히 표시 | 이미 통과한 입력 근거는 부록으로만 읽음 |
| 2단계 Practical Validation | 실제로 써도 되는 후보인가? | realism, tradability, validation method strength, stress / robustness, construction, risk contribution, component role, provider investability, macro / regime | 모든 적용 카테고리를 표시. REVIEW는 숨기지 않고 `2단계 실용성 주의`로 표시 | 선택 판단 근거로 소비하지만 주 검증으로 반복하지 않음 |
| 3단계 Final Review | 후보들 중 무엇을 모니터링 후보로 저장할까? | profitability / benchmark comparison, candidate comparison, profile fit, final decision memo, tax/account caveat | PV에서는 handoff reference로만 표시 | Candidate Board / Decision Cockpit / Final Decision Action 중심 |
| Monitoring | 선정 후 무엇을 계속 추적할까? | monitoring baseline, trigger, cadence, dashboard handoff, future deployment readiness | PV first-read에는 반복 노출하지 않음 | 저장 이후 Dashboard / Monitoring handoff에서 추적 |

## REVIEW Role Taxonomy

| `review_role` | 의미 | 예시 module | UI label |
|---|---|---|---|
| `pv_data_caution` | 데이터/기본 검증은 막지는 않지만 주의가 필요 | latest_replay, data_coverage, benchmark_parity | 데이터 주의 |
| `pv_practical_caution` | 실용성 판단에서 반드시 읽어야 하는 caution | validation_efficacy, backtest_realism, stress_robustness, construction_risk, risk_contribution, component_role_weight, provider_investability, macro_regime, leverage_inverse | 2단계 실용성 주의 |
| `final_decision_input` | 최종 선택 메모에서 판단해야 하는 항목 | tax_account_scope | 최종 판단 참고 |
| `monitoring_followup` | 선정 이후 dashboard / monitoring에서 추적할 항목 | monitoring_baseline | Monitoring 추적 |
| `final_readiness_blocker` | Final Review 저장 전에 막힐 deterministic gap | selected_route_preflight | 저장 전 보강 |

## Non-goals

- 새 provider/FRED/API fetch를 만들지 않는다.
- React가 validation 판단, provider 수집, replay 실행, registry/saved JSONL write를 하지 않는다.
- full holdings, full macro series, raw provider response를 UI/read model에 싣지 않는다.
- Final Review를 PV 검증 재실행 화면으로 키우지 않는다.

## UI Flow

1. 카테고리별 검증 결과: 적용된 PV 카테고리를 모두 보여준다.
2. 데이터 보강 / 수집 실행: 현재 수집 가능한 외부 데이터 근거, source map 탐색, connector mapping 필요, 현재 수집으로 해결 불가를 한 보드에 보여준다.
3. 상세 근거 / 원자료: 검산용 read-only 보조 영역으로 유지한다.

## Tradeoff

REVIEW-only 카테고리를 다시 보이면 화면 정보량은 조금 늘어난다. 대신 "검증이 사라졌다"는 오해를 없애고, Final Review가 모든 REVIEW를 떠안는 구조를 줄인다.
