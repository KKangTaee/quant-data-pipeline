# Overview Market Context Brief Flow Redesign V1 Design

## Product Intent

Market Context는 운영 진단표가 아니라 시장 브리프 화면이다.

사용자는 이 화면에서 다음 순서로 이해해야 한다.

1. 지금 저장 자료 기준으로 시장이 어떻게 움직였는가.
2. 해석할 때 어떤 자료가 약하거나 오래됐는가.
3. 과거 유사 맥락은 어떤 기준으로 계산됐는가.
4. macro 조건을 추가하면 broad analog와 무엇이 달라지는가.
5. 필요한 자료 보강을 어디서 시작할 수 있는가.

## UI Structure

### Current Market Brief

- `오늘의 시장 맥락`을 상단 대표 브리프의 역할로 유지한다.
- 기존 `시장 브리프` 단계형 rows는 중복 섹션이 아니라 `오늘의 시장 맥락` 아래의 read sequence로 흡수한다.
- 자료 상태 배지는 대상 source를 함께 보여준다.

### Historical Analog Controls

- `기준 시점 / 기준일 / 패턴 기간` 컨트롤은 `참고: 과거 유사 맥락` 섹션 안으로 들어간다.
- 컨트롤 설명은 historical analog 전용임을 명시한다.
- 상단 시장 브리프는 latest stored snapshot 기준임을 짧게 표시한다.

### Historical Analog Basis

기존 한 줄 meta string은 다음 그룹으로 나눈다.

- 기준: sector, ETF proxy, requested as-of, calculation as-of.
- 패턴: selected pattern window, calculation formula.
- 표본: sample, data window.
- 한계: current universe metadata replay, selected as-of 이후 가격 미사용, context-only note.

### Macro Pilot Comparison

- nested card 구조를 피한다.
- `Macro 조건 포함 시 어떻게 달라지나`라는 비교 섹션으로 보인다.
- sample funnel: broad sample -> GLD condition -> futures condition.
- condition chips: used / insufficient / excluded 상태를 compact하게 표시한다.
- broad vs macro comparison: sample, median, positive rate, worst path, sample quality를 비교한다.

### Source Ledger And Refresh

- `다음 맥락 체크`는 guide card grid가 아니라 compact priority rows로 표시한다.
- `근거: 자료 기준 / 출처 상태`는 source ledger 형태로 정리한다.
- refresh assist는 하단 독립 expander가 아니라 자료 상태 영역의 "필요 자료 보강" action으로 의미를 바꾼다.
- raw job result table은 접힌 상세에만 둔다.

## Data Boundary

- 모든 render는 DB-backed read model을 사용한다.
- 수집은 기존 `app/jobs/overview_actions.py` facade를 통해서만 실행한다.
- selected as-of는 historical analog 계산 전용이며 상단 market brief replay가 아니다.
- FRED / events / sentiment는 참고 / 보류 상태이며 hard condition으로 표시하지 않는다.
