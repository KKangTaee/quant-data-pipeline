# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Design

Status: User-approved direction; written-spec review pending
Date: 2026-07-21

## Problem

`evaluate_portfolio_rules()`는 개별 종목과 모든 고상관 종목쌍을 각각 유효한 `DiagnosisFact`로 만든다. `project_diagnoses()`의 current root dedup은 같은 `root_id`만 하나로 줄인다. 따라서 `correlation:AMD:NVDA`, `correlation:AMD:MSFT`, `correlation:MSFT:NVDA`는 서로 다른 root로 유지된다.

각 row의 측정값은 다르지만 React 카드는 subject identity를 표시하지 않고 공통 `meaning`만 headline으로 사용한다. 그 결과 사용자는 서로 다른 근거를 같은 경고의 중복으로 읽는다. `current_drawdown:<item>`도 같은 문제가 있다.

진단 열은 현재 모든 카드를 직접 렌더링한다. CSS에 높이 상한과 overflow가 없어 취약점이 많을수록 Portfolio Monitoring의 다음 업무 영역이 계속 아래로 밀린다.

## Considered Approaches

### A. React에서 같은 문구만 합치기

`meaning` 또는 `rule_id` prefix로 client-side group을 만든다.

- 장점: Python 변경이 작고 빠르다.
- 단점: diagnosis priority와 대표 severity 선택이 React로 이동한다. 문구가 바뀌면 grouping identity가 흔들리고 Python-owned 진단 계약을 약화한다.
- 결정: 채택하지 않는다.

### B. Python projection에 display group을 추가하고 React는 표현만 담당

원본 `DiagnosisFact`와 `all_rows`는 그대로 보존하고, Python이 같은 진단 family를 `DiagnosisDisplayGroup`으로 묶는다. React는 group headline, 대표 측정값, member evidence를 렌더링한다.

- 장점: severity/confidence/priority/group identity가 Python에 남는다. 원본 근거를 잃지 않고 top-three와 상세 목록의 의미 중복을 함께 해소한다.
- 단점: additive workspace contract와 TypeScript type이 필요하다.
- 결정: 채택한다.

### C. 그룹화 없이 스크롤만 추가

- 장점: 가장 작은 UI 변경이다.
- 단점: 반복 문구 문제를 숨길 뿐 원인을 해결하지 않는다. 카드가 많다는 정보 구조도 개선되지 않는다.
- 결정: 채택하지 않는다.

## Selected Design

### 1. Diagnosis display grouping

원본 rule 계산과 threshold는 변경하지 않는다. `project_diagnoses()`가 root dedup 뒤 사용자 표시용 그룹을 추가한다.

그룹 identity:

- `correlation_cluster:*` -> `family:correlation_cluster`
- `current_drawdown:*` -> `family:current_drawdown`
- 그 외 -> 기존 `root_id` 유지

V1은 화면에서 실제 반복이 확인된 상관 집중과 현재 낙폭만 family grouping한다. sector/asset key, 개별 항목 집중, 추세, downside contribution은 의미와 대상이 달라 기존 root 단위를 유지한다.

`DiagnosisDisplayGroup`은 다음 정보를 가진다.

- stable `group_id`
- section (`strength`, `weakness`, `data_gap`)
- classification
- representative severity/confidence/meaning/measured fact
- member count
- member `DiagnosisFact` rows

문자열인 `meaning`이나 `measured_fact`를 다시 파싱하지 않도록 `DiagnosisFact`에는 additive `subject_ids`와 `primary_metric`을 둔다. V1에서 correlation row는 두 item id와 correlation 값을, drawdown row는 한 item id와 drawdown 값을 채운다. 기존 row 생성자와 저장 payload는 default empty/`None`으로 호환된다. display group은 이 구조화 값을 사용해 최대 correlation, 가장 큰 drawdown과 member subject를 만든다.

대표 row는 현재 diagnosis priority와 같은 순서인 severity, affected weight, persistence, confidence로 결정한다. 그룹 순서도 대표 row priority를 사용한다. `top_three`는 raw row 세 개가 아니라 서로 다른 display group의 대표 세 개를 사용한다.

원본 `weaknesses`, `all_rows`, history snapshot은 보존한다. workspace에 additive `diagnosis.display_groups`를 제공한다. confidence가 낮은 weakness는 기존 계약처럼 `data_gap` section group으로 분류한다. legacy payload에는 React가 기존 strengths/weaknesses/data_gaps row를 해당 section의 one-member group으로 변환하는 compatibility fallback을 둔다.

### 2. User-facing copy and evidence

상관 집중 그룹:

- headline: `함께 움직이는 조합 N개가 확인되었습니다.`
- summary: 대표 row의 최대 상관과 최대 영향 비중
- detail: 각 종목쌍, 63D correlation, cluster weight, threshold/change condition

현재 낙폭 그룹:

- headline: `낙폭 재확인 종목 N개가 확인되었습니다.`
- summary: 가장 큰 낙폭과 대표 영향 비중
- detail: 종목명, current drawdown, threshold/change condition

one-member group도 대상 종목 또는 종목쌍 label을 headline/summary 근처에 표시한다. `monitoring_item_id -> source_ref` 매핑은 이미 workspace `active_group.item_rows`에 있으므로 React는 계산 없이 표시 label만 치환한다. label을 찾지 못하면 저장 identity를 그대로 노출하지 않고 `추적 항목`으로 표시한다.

각 member의 `판정 근거 전체 보기` 데이터는 삭제하지 않는다. 그룹 card의 disclosure 안에서 member별 측정값과 기준을 확인한다.

### 3. Bounded diagnosis lanes

강점·취약점·데이터 부족 각 column은 header와 scroll list를 분리한다.

- header: `취약점`과 display group count
- desktop `> 760px`: list `max-height: 560px`, `overflow-y: auto`, `scrollbar-gutter: stable`
- scrollbar는 내용이 560px를 넘을 때만 나타난다.
- mobile `<= 760px`: `max-height: none`, `overflow: visible`로 page scroll을 유지한다.

내부 스크롤은 진단 내용에만 적용하며 전체 Portfolio Monitoring panel이나 iframe 높이를 고정하지 않는다. 키보드 사용자는 scroll list에 focus할 수 있도록 `tabIndex=0`과 접근 가능한 label을 제공한다.

### 4. Data and persistence boundary

- price/exposure/behavior 계산 변경 없음
- severity/confidence/threshold 변경 없음
- DB schema, saved JSONL, registry, diagnosis snapshot write 변경 없음
- workspace projection은 additive field만 추가
- historical `all_rows`는 원본 fact 단위를 계속 보존

## Files

- `app/services/portfolio_monitoring/diagnosis.py`
- `app/services/portfolio_monitoring/read_model.py`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- corresponding Python/React tests and canonical `component_static`

## Error and Compatibility Handling

- `display_groups`가 없는 legacy workspace는 기존 strengths/weaknesses/data_gaps를 one-member group으로 표시한다.
- member subject label을 찾지 못해도 진단 자체를 숨기지 않는다.
- empty section은 현재 안내 문구를 유지하고 count `0`을 표시한다.

## Verification

- Python: 세 개 correlation pair가 한 display group이 되고 raw rows는 모두 보존되는지 확인
- Python: 두 개 drawdown row가 한 display group이 되고 top-three에서 같은 family가 반복되지 않는지 확인
- React: group count, subject labels, member evidence disclosure, legacy fallback 확인
- CSS/source contract: desktop max-height/overflow와 mobile reset 확인
- Browser QA: repeated fixture, desktop scroll, keyboard focus, mobile page scroll/no horizontal overflow

## Completion Criteria

- 첨부 화면의 상관 집중 3개 카드가 한 요약 카드와 세 member evidence로 표시된다.
- 낙폭 반복도 한 요약 카드와 종목별 근거로 표시된다.
- 취약점이 많아도 desktop 진단 열 높이는 560px를 넘지 않고 내부에서 스크롤된다.
- mobile은 nested vertical scroll 없이 한 열 page scroll을 유지한다.
- 원본 진단 row와 정책 판정은 변경되지 않는다.
