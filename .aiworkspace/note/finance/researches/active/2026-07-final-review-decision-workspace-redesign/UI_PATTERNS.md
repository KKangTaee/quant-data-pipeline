# UI And Workflow Patterns

Status: Approved
Last Updated: 2026-07-16

## Product Goal

저장된 validation evidence를 사용자가 읽을 수 있는 portfolio thesis, observed behavior, trade-off, Monitoring condition으로 압축하고 하나의 최종 판단을 끝낸다.

Confirmed primary question:

> 이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가?

## Internal Reference: Overview > Market Context

이 reference는 information projection과 visual language를 모두 포함한다. Final Review는 Market Context component를 복제하거나 공용화하지 않지만, blue-gray palette, 20px rounded outer surface, soft shadow, 17px chart shell, 14px metric band, compact heading scale을 같은 제품 문법으로 사용한다.

| Layer | Market Context behavior | Final Review implication |
| --- | --- | --- |
| Primary question | 최근 멀티플과 예상 실적을 함께 비교 | Monitoring 후보로 선정할지 판단 |
| Headline answer | 상대적 고평가/저평가와 현재 위치 | 후보 thesis + 가장 큰 trade-off |
| Primary evidence | 목적이 분명한 두 chart | 성과/낙폭/국면/benchmark 행동을 보여주는 소수의 visual |
| Assumptions | EPS source, SEP, 기준일을 화면 가까이에 표시 | portfolio/benchmark/period/cost/rebalance 기준을 가까이에 표시 |
| Disclosure | 산식·출처·한계는 접기 | Level2 closure/provenance는 접기 |
| Action | 해석 surface 자체가 목적 | 최종 route/reason 저장을 같은 React surface에서 완료 |

Canonical presentation tokens:

- text / muted / border: `#152033` / `#647589` / `#dae4ee`
- candidate / benchmark / underwater: `#274764` / `#269789` / `#e2763b`
- outer / chart / metric radius: `20px` / `17px` / `14px`
- section shadow: `0 10px 30px rgba(33, 53, 72, .055)`
- workbench rhythm: one-column `18px` gap with 760px / 460px responsive collapse

## Pattern 1. One Question, One Decision Surface

- 화면 첫 문장은 사용자가 끝낼 결정을 질문형으로 고정한다.
- 후보 선택, 핵심 해석, 판단 입력, 저장을 한 시각 체계 안에서 이어간다.
- registry count, hidden candidate count, schema state는 secondary operations disclosure로 내린다.

## Pattern 2. Portfolio Truth Before Validation Truth

- 첫 화면은 portfolio behavior를 말한다: return source, benchmark-relative behavior, drawdown/stress, concentration, turnover/cost.
- validation truth는 `이 결론을 얼마나 믿을 수 있는가`를 설명한다.
- readiness/Gate pass는 강점이 아니라 eligibility 또는 confidence metadata다.

## Pattern 3. Progressive Disclosure By Decision Relevance

- 본문: thesis, 3축 evidence, strength/weakness, decision conditions, action.
- 한 단계 아래: accepted limits and evidence confidence summary.
- 상세: root issue, provenance, technical path, legacy compatibility note.
- eligible 후보에서 0개인 unresolved item은 빈 카드로 렌더링하지 않는다.

## Pattern 4. React-First Workbench

- Streamlit: top navigation, page heading, component fallback.
- Python: candidate list/read model, Gate, evidence confidence, trait normalization, decision projection, persistence.
- React: candidate selector intent, report presentation, route/reason intent, save response presentation.
- 후보 선택 이후 페이지가 다시 시작되는 느낌을 없앤다.

## Approved Information Architecture

본문 순서는 고정한다.

1. `추적 가치 결론`: 한 문장 verdict와 가장 중요한 trade-off
2. `행동 근거`: 누적 성과/benchmark와 underwater drawdown
3. `진짜 강점과 약점`: measured portfolio behavior에서 생성
4. `변화 조건`: 실제 저장될 Monitoring trigger 2~4개
5. `최종 판단`: route 선택, operator reason, 저장
6. `접힌 상세`: evidence confidence, accepted limits, root provenance, technical path

`선정 전 미해결 0개`, Level2 REVIEW 처리 메모, 점수 정책 반복, 저장 전 질문 묶음은 본문 section으로 렌더링하지 않는다.

## Approved Score Policy

- overall investment score와 tracking value composite score를 만들지 않는다.
- 기존 `투자 매력도 / 근거 신뢰도 / Monitoring 준비도` 3종 headline score를 제거한다.
- `근거 신뢰도`만 결론을 얼마나 믿을 수 있는지 설명하는 secondary metadata로 허용한다.
- strength/weakness, route, trait map은 evidence confidence 숫자에서 파생하지 않는다.

## Approved Visual Evidence

- 주 근거: 동일 기간/빈도의 누적 net performance와 benchmark 비교
- 주 근거: underwater drawdown과 recovery path
- 보조 지표: concentration, turnover, modeled cost, liquidity freshness 등 직접 관측값
- 보조 visual: 포트폴리오 성격 지도

성격 지도 규칙:

- 바깥쪽은 `좋음`이 아니라 해당 위험 또는 부담의 노출이 크다는 뜻이다.
- 관측값과 해석 기준이 모두 있을 때만 axis를 채운다.
- 자료가 없으면 0이 아니라 `미측정`이다.
- overall polygon score, 평균 점수, 순위는 계산하지 않는다.
- chart와 직접 관측값이 strength/weakness의 원천이고 성격 지도는 빠른 탐색만 돕는다.

## Approved Decision Labels

| 사용자 label | Canonical route |
| --- | --- |
| 계속 추적 | `SELECT_FOR_PRACTICAL_PORTFOLIO` |
| 관찰 후 재검토 | `HOLD_FOR_MORE_PAPER_TRACKING` |
| 추적 대상에서 제외 | `REJECT_FOR_PRACTICAL_USE` |
| Level2로 돌려보내기 | `RE_REVIEW_REQUIRED` |

새 label은 product language만 바꾸며 기존 registry route와 status display contract를 변경하지 않는다.

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| 현재 투자 적합성/매수 타이밍 판단 | Final Review는 live approval이 아니며 account/current market context를 소유하지 않는다. | 별도 제품 범위 승인 전에는 Monitoring 후보 선정 판단으로 제한한다. |
| Final Review에서 data fix CTA 제공 | Level2 stage ownership과 충돌한다. | 재검토 route만 제공하고 실제 해결 action은 Level2 deep-link/handoff로 보낸다. |
| React에서 score/Gate 재계산 | Python ownership과 충돌한다. | React는 서버가 만든 decision projection만 표시한다. |
