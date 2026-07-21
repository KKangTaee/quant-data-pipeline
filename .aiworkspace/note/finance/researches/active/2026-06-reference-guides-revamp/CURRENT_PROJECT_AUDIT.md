# Current Project Audit

Status: Re-audited
Last Updated: 2026-07-20

## 2026-07-20 Re-audit Summary

### Implemented Facts

- 2026-06-08 V1~V5 작업으로 `Reference > Guides`는 이미 task-first `Reference Center`로 한 차례 개편됐다.
- 현재 catalog는 task card 6개, journey 7개, troubleshooting playbook 7개, record row 6개,
  shared operational concept 9개를 제공한다.
- `Reference > Glossary`는 shared concept 9개와
  `.aiworkspace/note/finance/docs/GLOSSARY.md`의 markdown section 168개를 함께 검색한다.
- Guide/Glossary는 모두 Streamlit native render다. Reference 전용 React component는 없다.
- 관련 구현 크기는 `app/web/reference_guides.py` 1,328줄,
  `app/services/reference_guides_catalog.py` 782줄,
  `app/services/reference_glossary_catalog.py` 196줄,
  `.aiworkspace/note/finance/docs/GLOSSARY.md` 3,101줄이다.
- focused catalog/contextual-help test 14개는 통과한다.

### Current Drift

- current user-facing surface인 `Workspace > Institutional Portfolios`가 Guides catalog에 한 번도 등장하지 않는다.
- current Overview 이름인 `Futures Macro`, 신규 `Economic Cycle`도 catalog에 등장하지 않는다.
- 반대로 current primary surface가 아닌 `Futures Monitor`, `Macro Thermometer`,
  제거된 Archive screen 경로는 catalog에 남아 있다.
- Glossary에는 `Candidate Review`, `Portfolio Proposal`, `Pre-Live`, `Selected Portfolio Dashboard`,
  `Main Worktree`, `Sub Worktree`, `Phase`, `Task`, `Fixture` 같은 legacy 또는 개발 운영 용어가
  사용자-facing 용어와 같은 레벨로 노출된다. 보수적인 title filter로도 이런 항목이 최소 19개다.
- V5 drift guard는 shared contextual-help key/link 정합성만 검사한다.
  전체 Guides copy와 `GLOSSARY.md` section의 current product freshness는 검증하지 않는다.

### Current UX Diagnosis

- Guides 첫 화면은 task-first 구조지만 hero, runtime/build chip, read-only 경계 설명,
  6개 장문 card가 먼저 이어져 실제 답에 도달하기 전 읽을 양이 많다.
- desktop card는 `owner screen`, 영어 내부 용어, safe action, boundary를 작은 글씨로 압축해
  사용자가 “무엇을 누르면 되는가”보다 시스템 ownership을 먼저 해석하게 한다.
- mobile은 card가 한 열로 길게 쌓여 검색이나 원하는 항목으로의 빠른 점프보다 스크롤 의존도가 높다.
- Glossary는 첫 viewport의 큰 `Runtime / Build` panel 뒤에 검색이 나온다.
  사용자 도움말보다 개발 프로세스 진단이 먼저 보이는 구조다.
- 검색어가 없으면 168개 section을 모두 expander로 렌더링한다.
  이 구조는 발견성과 우선순위가 낮고, 최신/legacy/internal 구분도 제공하지 않는다.
- Guide와 Glossary 검색이 분리돼 있어 사용자는 문제 해결과 용어 해석을 오가야 한다.

### Product Decision

Reference capability는 유지해야 한다. 현재 제품은 Overview, Institutional Portfolios,
Backtest, Practical Validation, Final Review, Portfolio Monitoring에 걸쳐
상태/근거/경계 해석 비용이 크므로 도움말 자체를 제거하면 화면별 설명 중복이 다시 늘어난다.

다만 `Guides`와 `Glossary`를 현재 두 개의 독립 navigation page로 유지하는 것은 권장하지 않는다.
두 화면을 하나의 React `Reference Center`로 통합하고, Guide와 Glossary는 내부 view/filter로 낮추는 방향이 적절하다.

권장 정보 구조:

1. `Reference` 단일 navigation entry
2. unified search: 작업, 화면, 상태, 용어를 한 검색창에서 찾음
3. task journeys: 시장 이해, 기관 포트폴리오 탐색, 데이터 준비, 후보 생성, 검증/판단, 모니터링
4. term/status detail: 사용자-facing current term만 기본 노출
5. contextual help: 각 화면의 정확한 상태에서 관련 Reference detail로 이동
6. legacy/internal glossary: UI 기본 노출에서 제외하고 durable docs에만 보존

제외 범위:

- 별도 log 관리 tab
- Reference 안에서의 ingestion/job 실행
- runtime/build panel의 first-read 노출
- raw registry/run history/failure artifact browser
- broker order, live approval, auto rebalance

## Initial Snapshot (2026-06-07)

`Reference > Guides`는 현재 `Portfolio Selection Guide` 성격이 강하다.
사용자가 단일 후보, 여러 후보 묶음, 저장된 Mix, 보류 / 재검토 중 현재 상황을 고르고
`Backtest Analysis -> Practical Validation -> Final Review -> Operations > Portfolio Monitoring`
흐름의 단계 / gate / 저장 경계를 확인하는 화면이다.

이 방향 자체는 현재 제품의 핵심 workflow와 맞지만, `Reference`라는 상위 탭의 역할에는 아직 좁다.
최근 제품은 `Workspace > Overview`, `Workspace > Ingestion`, `Operations > System / Data Health`,
`Operations > Portfolio Monitoring`까지 확장됐고, 사용자가 실제로 막히는 지점은
후보 선정뿐 아니라 데이터 갱신, stale context, `NOT_RUN` 해석, provider evidence, run history recovery,
live trading 아님 경계 같은 운영 지식까지 포함한다.

Browser audit 기준 현재 화면 첫 진입은 아래 성격으로 보인다.

- 화면 title: `Guides`
- hero: `모니터링 후보 포트폴리오를 찾는 운영 가이드`
- primary selector: `단일 후보`, `여러 후보 묶음`, `저장된 Mix`, `보류 / 재검토`
- main timeline: `전체 1~4 단계에서 현재 위치`
- lower sections: route summary, Portfolio Flow, route checkpoints, Decision Gates, Reference Drawer

결론적으로 현재 Guides는 "좋은 portfolio-selection guide"에 가까우며,
"제품 전체를 사용하는 Reference Center"로는 정보 구조와 진입점이 부족하다.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | 현재 제품은 DB-backed quant research workspace이며 live trading / broker order / auto rebalance가 아니다. |
| Roadmap | `.aiworkspace/note/finance/docs/ROADMAP.md` | UI / engine boundary, Overview / Operations / Backtest workflow가 현재 active surface다. |
| Project map | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | `app/web/reference_guides.py`는 `Reference > Guides` render owner이며, `app/web/streamlit_app.py`가 Reference navigation을 소유한다. |
| Backtest UI flow | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Reference 문서가 일부 legacy route와 현재 route를 같이 설명해 drift가 있다. |
| Portfolio flow | `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | 현재 canonical user flow는 4단계이며 Portfolio Monitoring은 Operations에 속한다. |
| System boundaries | `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md` | Reference는 read-only guide여야 하며 DB write, provider fetch, validation decision, broker/order action을 소유하지 않는다. |
| Current implementation | `app/web/reference_guides.py` | 단일 파일에 static guide data, CSS, GraphViz, Streamlit render가 함께 있다. |
| Navigation | `app/web/streamlit_app.py` | Reference group은 `Guides`, `Glossary` 두 화면으로 구성된다. |

## Surface Classification

| Surface | User-facing / internal / mixed | Notes |
| --- | --- | --- |
| `Reference > Guides` | User-facing | 현재는 portfolio-selection workflow guide. 전체 product help center로 확장 여지가 크다. |
| `Reference > Glossary` | User-facing | 용어 사전 역할. Guides와 검색 / concept linking이 분리돼 있다. |
| `Workspace > Overview` | User-facing | Market context와 data freshness 문제의 주요 출처. Reference가 해석 가이드를 제공해야 한다. |
| `Workspace > Ingestion` | User-facing | 데이터 수집 / 복구 action surface. Reference가 "언제 어떤 refresh를 실행할지"를 안내해야 한다. |
| `Backtest > Backtest Analysis` | User-facing | 후보 생성 source owner. Reference가 signal / benchmark / data trust 용어를 설명해야 한다. |
| `Backtest > Practical Validation` | User-facing | `NOT_RUN`, `REVIEW`, blocker, provider coverage 해석이 필요한 핵심 surface. |
| `Backtest > Final Review` | User-facing | 최종 판단과 monitoring 후보 저장 경계를 안내해야 한다. |
| `Operations > Portfolio Monitoring` | User-facing | monitoring은 live approval이 아니라 read-only / explicit scenario update임을 Reference에서 반복해야 한다. |
| `.aiworkspace/note/finance/docs/*` | Internal / durable knowledge | Reference content의 source가 될 수 있지만, 사용자가 그대로 읽기에는 세분화돼 있다. |

## Strengths

- Current Guides has a strong decision-flow skeleton: route selector, timeline, flowchart, checkpoint cards, Go / Review / Stop gates.
- It already uses user-facing Korean copy and explains live approval / order boundary in several places.
- It exposes runtime / git snapshot in a compact way, useful for debugging stale UI complaints.
- The `Reference Drawer` idea is useful: deeper concepts and storage boundaries are lower priority than the user's current task.
- Glossary exists as a separate Reference page, so concept-level content already has a landing place.

## Weaknesses

- Reference scope is too narrow. It mostly answers "이 후보를 Final Review까지 어떻게 보낼까?" and not "이 프로그램 전체를 어떻게 운영할까?"
- Current first screen does not offer task-based entry points such as "데이터가 stale일 때", "Overview refresh가 이상할 때", "`NOT_RUN`이 보일 때", "선정 후 monitoring을 어떻게 읽을 때".
- Static data, CSS, GraphViz, and render logic live in one large `app/web/reference_guides.py`, making iteration and content review awkward.
- Canonical docs and Guides copy have drift: docs still mention older 1~10 stages / Candidate Packaging / Portfolio Proposal details while current UI has 1~4 stages.
- The page is not a searchable help center. Tables have Streamlit table search, but there is no top-level product reference search / filter.
- There is no explicit cross-surface map connecting `Overview`, `Ingestion`, `System / Data Health`, `Archive`, `Portfolio Monitoring`, and `Reference`.
- Troubleshooting knowledge is scattered across docs / runbooks / user conversations rather than surfaced as user-facing playbooks.

## Product Boundaries

- Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
- Do not turn research output into roadmap commitment without user approval.
- Reference must stay read-only. It may link to other screens or explain actions, but should not write registries, execute jobs, fetch providers, approve trades, or update portfolios.
- UI should keep the existing `Ingestion -> DB -> Loader -> Runtime -> UI` boundary. Reference should explain the boundary, not bypass it.
- `NOT_RUN` remains "not executed / missing evidence", never pass.
- Raw holdings, raw provider responses, and full macro series stay in DB / artifacts, not in Reference content.

## Audit Conclusion

Reference should be reframed from a single `Portfolio Selection Guide` into a compact `Reference Center`.

Recommended target:

1. Keep the current portfolio-selection guide as one journey.
2. Add a top-level Reference landing that starts from user intent:
   `시장 / 데이터 보기`, `데이터 갱신 / 복구`, `후보 만들기`, `검증 / 최종 판단`, `선정 후 모니터링`, `문제 해결`.
3. Merge Guides and Glossary conceptually through search and cross-links, while keeping two navigation pages if that is cheaper.
4. Move static guide content into structured, testable read-model data so future docs drift is easier to catch.
5. Add explicit troubleshooting playbooks for stale Overview/Futures, provider gaps, `NOT_RUN`, blocked Practical Validation, and monitoring replay mismatch.
