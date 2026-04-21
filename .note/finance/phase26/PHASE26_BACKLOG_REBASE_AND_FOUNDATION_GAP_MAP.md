# Phase 26 Backlog Rebase And Foundation Gap Map

## 이 문서는 무엇인가

이 문서는 Phase 26의 실제 산출물이다.

목표는 과거 phase의 `manual_qa_pending`, `practical_closeout`, remaining backlog를
현재 제품 상태 기준으로 다시 분류하고,
Phase 27~30으로 넘길 foundation gap을 정리하는 것이다.

## 쉽게 말하면

예전 phase에 남아 있던 "아직 확인 필요" 표시를
지금 다시 읽었다.

그 결과,
일부는 이미 이후 phase에서 기능과 QA가 흡수되었고,
일부는 다음 phase의 입력으로 넘기는 것이 더 맞고,
일부는 future option으로만 남기는 것이 맞다고 정리했다.

## 왜 전체 phase가 아니라 일부 phase만 보았나

전체 phase를 다시 검토하지 않은 이유는 간단하다.
Phase 26은 전체 역사 감사가 아니라,
현재 roadmap에서 실제 혼선을 만들 수 있는 phase만 재분류하는 작업이기 때문이다.

우선 대상은 아래 조건 중 하나에 해당하는 phase였다.

- 현재 roadmap / index에 `manual_qa_pending`으로 남아 있다.
- `practical_closeout`으로 남아 있어 현재 blocker인지 future backlog인지 헷갈릴 수 있다.
- Phase 27~30의 방향과 의미가 겹칠 수 있다.
- Real-Money, Pre-Live, candidate, quarterly, structural redesign 같은 현재 제품 영역과 직접 연결된다.

그래서 우선 대상은 Phase 8, 9, 12~15, 18이었다.
Phase 19~25는 최근 QA / closeout이 명확하고,
Phase 1~7, 10~11, 16~17은 현재 immediate blocker를 만들지 않는 historical foundation으로 읽는다.

## 재분류 결과 요약

주의:

- 아래 재분류는 현재 기준의 roadmap / index 해석이다.
- 과거 phase 폴더 안의 checklist나 completion 문서는 historical record로 유지한다.
- 따라서 오래된 phase 문서 안에 `manual_validation_pending` 같은 표현이 남아 있어도,
  현재 gate는 이 문서와 `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`의 재분류 결과를 따른다.

| Phase | 이전 상태 | Phase 26 재분류 | 현재 판단 | 다음 처리 |
|---|---|---|---|---|
| Phase 8 | `implementation_complete / manual_qa_pending` | `complete / superseded_by_later_phase` | quarterly prototype family와 diagnostics는 Phase 23 quarterly productionization에서 제품 흐름으로 흡수됨 | Phase 27 data diagnostics, Phase 28 quarterly parity 입력으로만 유지 |
| Phase 9 | `implementation_complete / manual_qa_pending` | `complete / superseded_by_later_phase` | strict coverage / promotion policy는 Phase 10, 12, 23, 25 흐름에 흡수됨 | Phase 27 coverage trust, Phase 28 promotion parity 입력으로 유지 |
| Phase 12 | `practical_closeout / manual_qa_pending` | `complete / superseded_by_later_phase` | Real-Money first-pass hardening은 Phase 13~15와 Phase 25 Pre-Live로 이어졌음 | ETF PIT operability, richer benchmark, execution readiness는 Phase 27/28/30 입력 |
| Phase 13 | `implementation_complete / manual_qa_pending` | `complete / superseded_by_later_phase` | deployment readiness / probation 언어는 Phase 25 Pre-Live 운영 기록으로 재정의됨 | monthly review note, paper tracking은 Phase 30 입력 |
| Phase 14 | `practical_closeout / manual_qa_pending` | `complete / superseded_by_later_phase` | gate blocker / calibration 설계는 current candidate 및 Pre-Live 흐름의 배경 지식으로 남음 | threshold experiment, PIT operability, candidate review는 Phase 27~29 입력 |
| Phase 15 | `practical_closeout / manual_qa_pending` | `complete / superseded_by_later_phase` | candidate quality improvement와 strategy log 체계는 current candidate registry / backtest reports로 이어짐 | 후보 검토 표준화는 Phase 29, portfolio grouping은 Phase 30 입력 |
| Phase 18 | `practical_closeout / manual_qa_pending` | `complete / superseded_by_later_phase` | next-ranked fill 첫 번째 구조 작업은 구현/검증 완료. 남은 구조 작업은 current blocker가 아님 | Phase 28 future structural option으로만 유지 |

## Immediate blocker 판단

Phase 27로 넘어가기 전에 반드시 해결해야 하는 immediate blocker는 없다.

다만 Phase 27의 입력으로 넘겨야 할 데이터 / 백테스트 신뢰성 문제가 있다.
즉 "멈추고 과거 phase로 돌아가야 한다"가 아니라,
"다음 phase에서 제품 기능으로 정리해야 한다"가 더 정확하다.

## Phase 27 입력: Data Integrity And Backtest Trust Layer

Phase 27에서 우선 다룰 입력은 다음과 같다.

| 입력 | 출처 | 왜 중요한가 |
|---|---|---|
| common-date truncation | Phase 24 QA, GRS 실행 | 종목 하나의 결측 때문에 전체 결과 기간이 줄어드는 상황을 사용자가 놓치면 안 된다 |
| stale / missing ticker diagnosis | Phase 8 operator diagnostics, Phase 24 QA | EEM/IWM 같은 이슈를 전략 성과 문제와 데이터 문제로 구분해야 한다 |
| malformed price row | Phase 24 QA | 특정 날짜 행이 깨졌을 때 결과 범위와 warning이 일관되어야 한다 |
| statement coverage gap semantics | Phase 8~9 | strict quarterly / annual factor run에서 coverage 부족 원인을 일관되게 보여줘야 한다 |
| ETF operability data coverage | Phase 12~14 | AUM / spread / partial coverage warning이 실제 block rule인지 diagnostic인지 구분해야 한다 |

## Phase 28 입력: Strategy Family Parity And Cadence Completion

Phase 28로 넘길 입력은 다음과 같다.

| 입력 | 출처 | 왜 중요한가 |
|---|---|---|
| quarterly Real-Money / Guardrail parity | Phase 8~9, Phase 23 | quarterly가 제품 기능으로 올라왔지만 annual strict와 검증 surface가 아직 완전히 같지는 않다 |
| annual / quarterly / 신규 전략 option parity | Phase 23~24 | 전략 family가 늘어나면 UI / payload / history / saved replay 의미가 흔들릴 수 있다 |
| Phase 18 remaining structural ideas | Phase 18 | 지금 blocker는 아니지만, strategy family parity를 다룰 때 다시 선택할 수 있는 future option이다 |
| ETF PIT operability history | Phase 12~14 | current snapshot overlay를 historical live contract로 오해하지 않게 해야 한다 |

## Phase 29 입력: Candidate Review And Recommendation Workflow

Phase 29로 넘길 입력은 다음과 같다.

| 입력 | 출처 | 왜 중요한가 |
|---|---|---|
| current candidate registry workflow | Phase 15, Phase 20, Phase 25 | 좋은 run을 후보로 등록하고 다시 꺼내는 흐름이 표준화되어야 한다 |
| near-miss / watchlist distinction | Phase 14~15 | 성과는 좋지만 gate가 약한 후보를 어떻게 보관할지 필요하다 |
| Real-Money -> Pre-Live handoff | Phase 25 | 진단표와 다음 행동 기록이 이어져야 한다 |
| strategy hub / one-pager / log linkage | Phase 15 | 후보 설명, 실행 기록, registry가 흩어지지 않아야 한다 |

## Phase 30 입력: Portfolio Proposal And Pre-Live Monitoring Surface

Phase 30으로 넘길 입력은 다음과 같다.

| 입력 | 출처 | 왜 중요한가 |
|---|---|---|
| weighted / saved portfolio workflow | Phase 20~22 | 단일 후보를 넘어 포트폴리오 후보를 만들려면 재현 가능한 저장 / 재실행 흐름이 필요하다 |
| paper tracking / monthly review note | Phase 13, Phase 25 | Pre-Live record가 저장된 뒤 실제로 어떻게 관찰되는지 보여줘야 한다 |
| portfolio proposal boundary | Phase 22, Phase 30 계획 | 포트폴리오 제안과 live approval을 분리해야 한다 |
| Pre-Live monitoring surface | Phase 25 | 저장된 Pre-Live record를 운영 화면에서 다시 읽고 갱신할 수 있어야 한다 |

## Live Readiness / Final Approval 경계

Live Readiness / Final Approval은 Phase 26~30에서 직접 열지 않는다.

현재 흐름은 다음과 같이 둔다.

1. Phase 26: 과거 backlog와 foundation gap 정렬
2. Phase 27: 데이터 / 백테스트 신뢰성 강화
3. Phase 28: 전략 family parity 강화
4. Phase 29: 후보 검토 workflow 표준화
5. Phase 30: 포트폴리오 제안 / Pre-Live monitoring surface
6. Phase 30 이후: Live Readiness / Final Approval

## 한 줄 결론

Phase 26 재분류 결과,
과거 pending 상태는 현재 Phase 27 진입을 막는 blocker가 아니며,
각각 Phase 27~30의 입력 또는 future option으로 정리하는 것이 맞다.
