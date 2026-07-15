# Current Project Audit

Status: Complete — approved direction recorded in `RECOMMENDATION.md`
Last Updated: 2026-07-16

## Snapshot

현재 Final Review의 Gate와 저장 계약은 이전보다 안전해졌다. Final Review eligible 후보는 Level2의 unresolved actionable / critical engineering / missing contract를 통과해야 하고, 실제 저장은 Python이 소유한다. 문제는 이 안전 계약을 사용자에게 설명하는 층이 계속 추가되면서, 화면이 더 이상 "후보의 최종 판단"을 중심으로 읽히지 않는다는 점이다.

실제 화면은 `Decision Desk -> 후보 선택 -> 투자 검토서 -> 점수 3종 -> 총평 -> 총평 해석 4종 -> 최종 판단 -> 근거 종결 -> 강점/약점 -> 저장 전 질문 -> Monitoring 방향 가이드 -> Final Review 판단 항목 -> 상세 탭`으로 이어진다. 각각은 개별적으로 이유가 있지만, 같은 결론·점수·Level2 한계를 서로 다른 이름으로 반복한다. 사용자는 포트폴리오가 어떤 수익 원천과 손실 구조를 가졌는지보다 workflow contract를 더 많이 읽게 된다.

냉정하게 보면 현재 화면은 **투자 후보 decision workspace가 아니라 validation contract inspector에 가깝다.**

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Final Review는 live approval이나 주문이 아니라 저장된 근거를 읽어 Monitoring 후보 여부를 결정하는 단계다. |
| Roadmap | `.aiworkspace/note/finance/docs/ROADMAP.md` | current eligible 후보의 unresolved actionable / critical engineering / missing contract는 0이어야 한다. |
| Project map | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Python read model과 persistence, Streamlit page shell, React investment report의 소유 경계가 나뉜다. |
| Final Review page | `app/web/backtest_final_review/page.py` | React report보다 먼저 registry/Gate 중심 Decision Desk와 Streamlit 후보 선택 UI가 노출된다. |
| Final Review read model | `app/services/backtest_evidence_read_model.py` | 강점은 80점 이상 score dimension과 ready policy row, 약점은 critical gap / must-fix / must-review row에서 만들어진다. |
| Final Review React report | `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx` | 총평, 해석, 판단, closure, 강점/약점, 저장 전 질문, Monitoring 가이드, Level2 판단 항목, 상세 탭을 한 페이지에 연속 렌더링한다. |
| Overview Market Context | `app/web/overview/market_context.py`, `app/web/overview/market_context_helpers.py` | Streamlit은 짧은 heading만 제공하고, 하나의 DB-backed React surface가 질문·차트·시나리오·disclosure를 일관되게 렌더링한다. |
| Existing investment workflow audit | `.aiworkspace/note/finance/researches/active/2026-05-investable-workflow-gap-analysis/CURRENT_PROJECT_AUDIT.md` | evidence packet과 stricter gate가 필요하다는 이전 방향은 타당했지만, 현재는 그 evidence가 사용자 판단 surface에 과도하게 승격됐다. |

## Runtime Observation

2026-07-16 로컬 앱의 current GRS 후보를 실제로 확인했다.

- Final Review 상단은 `Gate 통과 후보 3`, `선택 가능 1`, `보류/재검토 2`, `숨김 3`, `저장된 판단 6`, `Monitoring 연결 6`을 먼저 보여준다.
- 투자 검토서에는 `총평` 관련 텍스트가 여러 구간에 반복되고, `최종 판단` 역시 action, 질문, closure, disposition에서 반복된다.
- `선정 전 미해결 항목 0개`를 보여준 직후에도 `인수한 한계와 최종 판단 항목` 6개가 같은 크기의 카드로 이어진다.
- 강점은 `선정 준비도 100`, `Monitoring 적합성 90`, policy 통과 항목으로 구성된다. 이는 후보의 수익 동인이나 방어 특성이 아니다.
- 약점은 `투자 성과 매력도 59` 같은 score dimension 또는 Level2 review 상태를 재포장한다. 포트폴리오가 어떤 시장 국면에서 왜 약한지는 핵심 요약에 없다.
- Monitoring 방향 가이드가 집중도, 금리, 낙폭, 비용, benchmark, parameter sensitivity 등을 길게 다루지만, 이것이 최종 선택 전 핵심 thesis인지 선정 후 운영 조건인지 우선순위가 섞여 있다.

같은 앱의 `Workspace > Overview > 시장 맥락`은 다음처럼 작동했다.

- 첫 질문: 현재 S&P 500 멀티플과 예상 실적 시나리오를 어떻게 읽을 것인가.
- 핵심 답: 현재 PER, 최근 5년 중심, 상대적 위치, 시나리오 적정 범위.
- 근거: 두 개의 목적이 분명한 chart와 계산 기준일.
- 한계: 잠정 PER, EPS source, 거시 가정, 공식 매매 신호가 아니라는 disclosure.
- 상세 산식·출처는 접혀 있고, 동일 결론을 별도 guide 카드로 반복하지 않는다.

## Surface Classification

| Surface | User-facing / internal / mixed | Notes |
| --- | --- | --- |
| Final Review Decision Desk | Mixed | 후보 선택은 user-facing이나 registry/Gate count와 hidden row 수가 첫 화면의 주인공이다. |
| Final Review investment report | User-facing, contract-heavy | 결정을 받아야 하지만 validation schema, score policy, closure state, monitoring disposition을 과다 노출한다. |
| Final Review detail tabs | Mixed | provenance와 다음 실험은 유용하지만 primary flow와 동일한 시각 무게를 가진다. |
| Practical Validation Level2 | User-facing validation workbench | 해결 가능한 근거를 보강하고 저장하는 책임을 가진다. Final Review에서 다시 작업 대상으로 보이면 안 된다. |
| Overview Market Context | User-facing reference | 하나의 질문, React-first visualization, secondary disclosure의 계층이 명확하다. |

## Strengths

- Gate와 저장 책임이 Python에 있어 presentation 변경이 안전 계약을 우회하지 않는다.
- Level2와 Final Review 사이의 evidence closure root dedup 계약이 있어 동일 issue 중복 계산을 방지할 기반이 있다.
- current eligible 후보에서 unresolved actionable 0을 보장하는 방향은 맞다.
- 투자 매력도, 근거 신뢰도, Monitoring 준비도를 구분하려는 의도는 건전하다.
- React investment report가 이미 있으므로 React-first 단일 surface로 수렴할 기술 기반이 있다.
- Monitoring condition, final route, reason을 구조화해 저장할 수 있다.

## Weaknesses

### 1. 화면의 primary question이 하나가 아니다

`후보를 고른다`, `투자 검토서를 해석한다`, `Level2 한계를 인수한다`, `저장 전 질문에 답한다`, `Monitoring 조건을 설계한다`가 모두 같은 페이지에서 primary task처럼 보인다. 그래서 최종 판단 버튼이 있어도 사용자는 어디까지 읽어야 판단이 끝나는지 알기 어렵다.

### 2. 총평이 결론이 아니라 목차가 됐다

총평 뒤에 다시 네 가지 해석, 강점/약점, 저장 전 질문, Monitoring 가이드, Final Review 판단 항목이 붙는다. 총평이 이후 내용을 압축하지 못하고 같은 정보를 예고하는 역할만 한다.

### 3. 강점과 약점의 의미가 잘못됐다

`_report_dimension_strengths()`는 80점 이상 score dimension을 강점으로, `_report_strengths()`는 ready policy row를 보충 강점으로 사용한다. `_report_weaknesses()`는 critical gap / must-fix / must-review를 약점으로 사용한다. 이 로직은 "근거가 얼마나 준비됐는가"를 설명하지, 다음을 설명하지 않는다.

- 무엇이 수익을 만들었는가
- 어떤 시장 국면에 강하거나 약한가
- benchmark 대비 어떤 행동 특성이 있는가
- 손실이 어디에서 발생하고 회복은 어땠는가
- 집중도·회전율·민감도가 후보의 실제 trade-off를 어떻게 만드는가

### 4. Level2 종결 상태가 Final Review의 본문을 다시 점유한다

`_level2_review_cards()`와 `_closure_review_cards()`는 Practical Validation card와 closure issue를 Final Review disposition으로 가져온다. `_level2_review_action()`은 "Final Review에서 다시 해결하지 않는다"고 말하지만, 화면은 그 항목을 큰 카드와 질문으로 다시 보여준다. 계약상 종결됐지만 UX상 미종결처럼 보인다.

### 5. 정보의 깊이보다 카드의 개수가 늘었다

React report는 `AssessmentPanel -> InterpretationRows -> FinalDecisionAction -> EvidenceClosureSections -> EvidenceRows -> DecisionQuestionList -> PatternGuidePanel -> ReviewActionBoard -> DetailTabs` 순서다. 서로 다른 disclosure depth를 가진 정보가 거의 같은 크기의 bordered card로 이어져 시각적 우선순위가 무너진다.

### 6. Streamlit shell과 React report가 하나의 제품처럼 보이지 않는다

상단 Streamlit은 운영 count와 selectbox 중심, 하단 React는 백색 보고서와 자체 spacing/type scale을 쓴다. 사용자는 페이지가 두 번 시작한다고 느낀다. Market Context처럼 Streamlit은 navigation/heading/fallback만 맡고, candidate chooser부터 decision/save까지 하나의 React workbench로 이어지는 편이 일관적이다.

### 7. 점수가 서로를 설명하지 못한다

현재 후보는 투자 매력도 59, 근거 신뢰도 59, Monitoring 준비도 96처럼 보이지만, 실제 투자 매력도와 위험 방어력 모두 같은 59로 수렴하는 구간이 있다. readiness와 evidence quality가 상세 scorecard에서 다시 강점으로 등장해, portfolio quality와 process readiness가 혼합된다.

## Root Cause

근본 원인은 UI polish 부족이 아니다.

1. 이전 단계에서 evidence packet과 gate hardening을 강화했다.
2. 종결 계약을 잃지 않기 위해 거의 모든 intermediate schema를 Final Review read model에 보존했다.
3. React가 그 schema를 각각 독립 section으로 정직하게 렌더링했다.
4. 그 결과 correctness는 좋아졌지만 사용자에게 필요한 결론 압축과 stage-specific projection이 사라졌다.

즉, **Python read model이 Final Review 전용 decision projection을 만들지 않고, 여러 내부 계약을 하나의 보고서에 합친 것**이 핵심이다.

## Product Boundaries

- Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
- Final Review의 기본 결정은 현재 계약상 `Portfolio Monitoring 후보 선정 / 보류 / 제외 / Level2 재검토`다.
- 해결 가능한 데이터·replay·validation 작업은 Level2에서만 실행한다.
- Final Review는 저장된 evidence를 해석할 뿐 provider fetch, replay, DB ingestion을 실행하지 않는다.
- Python이 classification, Gate, score, decision projection, persistence를 소유하고 React는 presentation과 intent만 소유한다.
- 승인된 research design은 implementation plan 입력으로 사용하되 roadmap 변경은 별도 docs sync에서 명시적으로 반영한다.

## Confirmed Product Direction

2026-07-16 사용자 확인으로 Final Review의 primary decision을 다음 질문에 고정한다.

> 이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가?

Final Review를 `최종 검토 보고서`가 아니라 **Decision Workspace**로 재정의한다.

1. 한 문장 질문: "이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가?"
2. 한 문장 결론: 후보의 투자 thesis와 가장 큰 trade-off를 함께 말한다.
3. 핵심 근거 3축: 수익 원천, 손실/국면 행동, 실행·구성 현실성.
4. 진정한 강점/약점: validation status가 아니라 관측된 portfolio behavior에서 생성한다.
5. 선정 조건: 실제로 저장될 Monitoring trigger만 2~4개로 압축한다.
6. 판단 action: 선정/보류/제외/Level2 재검토와 이유 입력을 한 곳에서 끝낸다.
7. 근거·한계: Level2 종결 요약과 provenance는 접힌 disclosure로 내린다. blocker는 eligible 후보가 아니므로 본문에 0개 card를 만들지 않는다.
8. 화면 소유: 후보 선택부터 저장까지 React-first 한 surface로 통합하고 Streamlit은 navigation, page heading, fallback만 맡긴다.

## Audit Conclusion

현재 Final Review의 큰 gate/persistence 계약은 버릴 대상이 아니다. 버려야 할 것은 그 계약의 모든 중간 상태를 사용자 본문에 같은 비중으로 노출하는 방식이다.

Market Context에서 가져와야 할 핵심은 둥근 카드나 색상이 아니라 **질문 중심 projection**이다. Final Review도 저장된 많은 근거를 그대로 보여주는 대신, 후보의 투자 행동과 최종 결정에 필요한 몇 가지 문장·차트·조건으로 먼저 압축해야 한다. validation 상태는 그 결론의 신뢰도를 설명하는 secondary disclosure가 되어야 한다.

primary decision, Decision Brief 접근, score 제거, 행동 chart 중심 근거, 보조 성격 지도, React-first 책임 구조가 승인됐다. canonical 설계와 구현 순서는 `RECOMMENDATION.md`를 따른다.
