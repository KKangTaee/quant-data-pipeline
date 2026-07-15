# Overview Market Context Turnaround Derived Quarter Provenance V1 Design

Status: Approved Direction — Written Spec Review Requested
Last Updated: 2026-07-16

## Problem

MRNA 2023년 공시 원장에는 FY와 Q1~Q3 매출, 원가, 영업이익이 모두 있다. 그러나 매출 concept가 연중 바뀌었다.

- Q1 `1.862B`, Q2 `0.344B`: `us-gaap:Revenues`
- Q3 `1.831B`, FY `6.848B`: `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
- FY 원가 `4.693B`: `us-gaap:CostOfGoodsAndServicesSold`
- FY 영업이익 `-4.239B`: `us-gaap:OperatingIncomeLoss`

현재 `resolve_discrete_quarters`는 `(symbol, fiscal_year, exact concept, unit)`별로 operand를 묶는다. 따라서 어느 exact concept 그룹에도 Q1/Q2/Q3/FY가 모두 모이지 않아 2023-Q4 매출이 결측이 된다. 반면 영업이익과 원가는 같은 concept가 유지되어 각각 Q4 `0.006B`, `0.929B`로 정상 산출된다.

TTM은 연속 네 분기를 요구하므로 2023-Q4 매출 하나의 결측이 2023-Q4부터 2024-Q3까지 TTM revenue, GP margin, operating margin을 모두 끊는다. 2024-Q4에는 결측 분기가 rolling window에서 빠져 선이 다시 나타난다.

## Considered Approaches

### A. 그래프만 연결하거나 빈 구간을 보간

시각적 단절은 사라지지만 존재하지 않는 재무값을 만든다. 현재 제품의 결측 보존 원칙과 맞지 않으며 채택하지 않는다.

### B. 명시적 concept family 안에서만 공시 기반 Q4 산출 — selected

caller가 이미 같은 회계 의미로 선언한 `TURNAROUND_CONCEPT_FAMILIES` 안에서만 exact-concept fallback을 수행한다. symbol, fiscal year, unit, primary-period, PIT cutoff를 모두 검증하고 FY-Q1-Q2-Q3를 계산한다. 산출 provenance를 데이터 계약과 UI에 남긴다.

### C. direct Q4만 허용하고 현재 결측 유지

가장 보수적이지만, 10-K가 Q4 단독값 대신 FY를 공시하는 일반적인 SEC 구조와 taxonomy rename을 처리하지 못한다. 실제 이용 가능한 확정 공시 근거를 버리므로 채택하지 않는다.

## Authoritative Data Design

### Resolution precedence

1. 기존 direct discrete quarter가 있으면 항상 우선한다.
2. 기존 exact-concept FY 산출이 가능하면 현재 경로를 유지한다.
3. Q4가 여전히 없을 때만 explicit concept family fallback을 시도한다.
4. fallback 조건이 하나라도 맞지 않으면 Q4를 만들지 않는다.

### Family fallback guards

- 동일 `symbol`, `fiscal_year`, `unit`
- `concepts` 인자로 명시된 동일 metric family
- primary-period fact만 사용
- FY 한 개와 Q1/Q2/Q3 각 한 개가 모두 존재
- direct Q4 부재
- 각 operand가 `as_of_date` 이전에 공개됨
- 기존 concept priority와 latest-as-of 규칙으로 operand를 결정
- 산출 `available_at`은 네 operand 공개일의 최댓값

concept 문자열의 유사도, label 텍스트, issuer별 임의 매칭은 사용하지 않는다. 이 변경은 source DB를 바꾸지 않고 read-time pure calculation에서만 동작한다.

### Derived value contract

MRNA 2023-Q4는 다음처럼 산출된다.

```text
revenue = 6.848B - 1.862B - 0.344B - 1.831B = 2.811B
cost = 4.693B - 0.792B - 0.731B - 2.241B = 0.929B
gross profit = 2.811B - 0.929B = 1.882B
operating income = -4.239B - (-0.366B) - (-1.867B) - (-2.012B) = 0.006B
```

이는 forecast나 통계 추정이 아니라 공개된 FY와 Q1~Q3 actual facts의 산술 차감이다. 다만 direct standalone Q4와 동일한 출처 형태는 아니므로 `FILING_DERIVED`로 구분한다.

### Provenance contract

각 timeline row는 metric별 구조화 근거를 제공한다.

```text
metric_provenance.<metric>.source_kind = REPORTED | FILING_DERIVED
metric_provenance.<metric>.rule = reported_quarter | fy_minus_q1_q2_q3 | revenue_minus_cost
metric_provenance.<metric>.operands = concept, unit, period, value, available_at, accession_no 목록
derived_metrics = 현재 분기에서 FILING_DERIVED인 metric 이름 목록
ttm_derived_metrics = 현재 TTM 4분기 창에 FILING_DERIVED input이 포함된 metric 이름 목록
```

`ttm_derived_metrics`는 새로운 값을 다시 추정한다는 뜻이 아니라 TTM 합계의 네 입력 중 공시 기반 산출 분기가 포함됐음을 나타낸다. TTM 값이 결측이면 포함 여부만으로 숫자를 만들지 않는다.

## Authoritative UI Design

- 산출값이 유효하면 기존 차트 선은 정상적으로 이어진다.
- 해당 source quarter에는 중립색의 작은 `산출` marker를 표시한다.
- active inspector의 분기 값 옆에는 `공시 기반 산출` badge를 표시한다.
- active TTM 값이 산출 분기를 포함하면 `공시 기반 산출값 포함`이라고 표시한다.
- 계산 근거는 `FY − Q1 − Q2 − Q3`와 operand 숫자로 보여준다.
- 직접 공시값에는 별도 badge를 붙이지 않아 화면 소음을 줄인다.
- 산출 표시는 경고색이나 실패색을 쓰지 않고 텍스트와 marker를 함께 사용한다.
- hover에만 의존하지 않는다. 키보드/터치로 선택되는 현재 inspector에도 같은 정보가 남는다.
- 상세 출처 영역에는 rule과 operand 공시일을 제공한다.

사용자 문구는 `추정`이 아니라 `공시 기반 산출`로 통일한다.

## Error And Edge Cases

- family allowlist 밖 concept는 결합하지 않는다.
- unit 또는 fiscal year가 다르면 결합하지 않는다.
- Q1~Q3 중 하나라도 없으면 결합하지 않는다.
- direct Q4가 있으면 산출값으로 덮어쓰지 않는다.
- 미래 filing/restatement는 해당 `as_of_date` 이전 point에 소급하지 않는다.
- 산출 결과가 음수라는 이유만으로 폐기하지 않는다. 음수 매출/GP/영업 값은 실제 공시 산술 결과일 수 있다.
- provenance가 없는 legacy point는 direct reported로 단정하지 않고 UI 표시를 생략한다.
- 안전 조건 실패 시 현재 `MISSING_QUARTER_IN_WINDOW`와 line segmentation을 그대로 유지한다.

## Files

- `finance/data/us_stock_turnaround.py`
- `tests/test_us_stock_turnaround.py`
- `app/services/overview/us_stock_turnaround.py` — 기존 재귀 `_json_safe`가 provenance를 그대로 전달하므로 수정하지 않고 service regression으로 계약만 검증
- `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx`
- `app/web/streamlit_components/market_context_valuation/src/style.css`
- `tests/test_market_context_valuation.py`
- existing task/docs/root handoff files at closeout

## Verification Contract

- MRNA-like mixed-concept fixture가 기존 코드에서 RED이고 수정 후 Q4 `2.811B`로 GREEN
- allowlist 밖 concept/unit/year/missing operand/direct-Q4 precedence/PIT cutoff 회귀
- gross profit `1.882B` 및 2023-Q4~2024-Q3 TTM 복구
- provenance와 `ttm_derived_metrics` pure tests
- React source/behavior contract와 Vite production build
- actual MRNA DB read model의 연속 margin series와 산출 표시
- desktop/420px Browser QA, horizontal overflow 0, 신규 console error 0
- existing AAPL/RIVN/PER/turnaround focused regressions

## Trade-off

이 설계는 exact-concept-only보다 더 많은 실제 공시값을 사용할 수 있지만, family 선언의 정확성에 의존한다. 따라서 자동 taxonomy 유사도 매칭은 도입하지 않고 현재 코드가 명시적으로 관리하는 concept family만 신뢰한다. UI에 산출 근거를 남겨 direct standalone Q4보다 출처 형태가 한 단계 가공됐음을 사용자에게 숨기지 않는다.
