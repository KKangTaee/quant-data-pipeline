# Current Project Audit

## Snapshot

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
