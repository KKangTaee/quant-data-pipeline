# Benchmarks

Status: Complete for approved scope
Last Updated: 2026-07-16

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Product / Service | Category | Evidence | Relevant pattern |
| --- | --- | --- | --- |
| Current Final Review | Internal product | Observed | Gate와 저장 계약은 안전하지만 총평·해석·점수·closure·질문·Monitoring guide가 같은 무게로 반복된다. |
| Workspace > Overview > 시장 맥락 | Internal product reference | Observed | 하나의 질문, 두 개의 목적이 분명한 chart, 가까운 가정 표시, 접힌 산식·출처·한계로 정보 계층을 만든다. |
| Practical Validation Level2 | Internal workflow | Documented | 해결 가능한 근거는 Level2에서 실행·저장하고 current Final Review eligible 후보에는 unresolved actionable / critical engineering / missing contract가 없어야 한다. |
| Existing evidence closure contract | Internal service contract | Documented | root issue dedup, terminal state, Gate, append-only persistence를 Python이 소유한다. |

## Key Findings

### 1. 내부 기준 화면만으로 핵심 방향을 결정할 수 있다

- 이번 문제는 외부 상용 서비스 기능 부족보다 같은 앱 안에서 이미 검증된 정보 계층을 Final Review에 적용하지 못한 문제다.
- 시장 맥락의 성공 요인은 카드 모양이 아니라 `질문 -> 관측 -> 해석 -> disclosure` projection이다.
- 따라서 승인된 1차 구현 방향을 정하기 위한 외부 benchmark는 필수 dependency가 아니다.

### 2. Final Review는 evidence packet 전체를 렌더링할 필요가 없다

- evidence closure contract는 보존하되 Final Review 전용 decision projection으로 압축해야 한다.
- Level2에서 이미 종결된 한계는 본문 판단 항목이 아니라 evidence confidence와 접힌 disclosure가 되어야 한다.

### 3. 투자 특성과 검증 준비도는 다른 개념이다

- 최대 비중, drawdown, benchmark-relative path, turnover, 비용은 portfolio behavior다.
- Gate pass, selection readiness, Monitoring handoff readiness는 process state다.
- 강점과 약점은 portfolio behavior에서만 생성하고 process state는 eligibility와 confidence로 제한한다.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| Primary question 부재 | Market Context의 single-question projection | Final Review의 질문을 `실제 투자 검토 대상으로 계속 추적할 가치가 있는가`로 고정한다. |
| Portfolio behavior 대신 validation status를 강약점으로 표시 | Market Context의 direct observation-first 해석 | 행동 chart와 직접 관측값에서만 강점·약점을 생성한다. |
| Level2 종결 근거가 본문을 점유 | Market Context의 progressive disclosure | accepted limit와 provenance를 접힌 disclosure로 내린다. |
| Streamlit/React 이중 시작 | Market Context의 React-first surface | Streamlit은 navigation/heading/fallback, React는 후보 선택부터 판단 intent까지 담당한다. |
| 3종 점수와 종합점수의 의미 중복 | Direct observation-first pattern | 종합 투자점수를 제거하고 근거 신뢰도만 보조 정보로 남긴다. |
