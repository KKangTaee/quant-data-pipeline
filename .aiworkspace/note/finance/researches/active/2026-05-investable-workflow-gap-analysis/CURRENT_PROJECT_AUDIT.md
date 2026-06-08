# Current Project Audit

Status: Draft
Last Updated: 2026-06-08

## Snapshot

현재 제품은 `Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard`로 이어지는 좋은 뼈대를 갖고 있다. 특히 백테스트 결과를 곧바로 투자 판단으로 받아들이지 않고, provider evidence, macro context, stress / sensitivity, Final Review 기록으로 한 번 더 걸러내는 방향은 제품 정체성과 맞다.

다만 실전 투자 판단 도구로 보기에는 아직 "검증을 했는가"보다 "검증할 수 없는 부분을 얼마나 안전하게 다루는가"가 약하다. `NOT_RUN`, proxy, current snapshot, legacy registry, manual monitoring이 많고, out-of-sample / walk-forward / Monte Carlo / attribution / look-through / monitoring history가 아직 하나의 엄격한 investment due diligence packet으로 묶이지 않는다.

## Current Product Promise

로컬 문서 기준 제품 약속은 "좋아 보이는 백테스트 결과"를 데이터 신뢰도, ETF 운용성, holdings / exposure, macro context, stress / sensitivity, Final Review evidence로 확인한 뒤 실전 추적 가능한 후보인지 판단하는 퀀트 리서치 워크스페이스다.

명시 경계:

- live approval, broker order, auto rebalance는 범위 밖이다.
- UI는 provider / FRED를 직접 fetch하지 않고 `Ingestion -> DB -> Loader -> UI`를 따라야 한다.
- registry JSONL에는 compact evidence만 저장하고 full provider row, holdings, macro series는 DB에 둔다.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Evidence-first, DB-backed runtime, no-live-trading 경계가 제품 원칙이다. |
| Main workflow | `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Selection V2의 핵심 흐름은 source -> validation -> final decision -> read-only dashboard다. |
| Backtest UI flow | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Backtest, Practical Validation, Final Review, Selected Dashboard 파일 경계와 legacy compatibility가 함께 존재한다. |
| Runtime flow | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | result bundle, metadata, warning, Data Trust Summary가 runtime 해석의 핵심 계약이다. |
| Data flow | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` | provider / macro 수집은 DB snapshot과 loader를 통해 Practical Validation에 연결된다. |
| Data quality | `.aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md` | current profile / current provider snapshot은 historical PIT truth가 아니며, survivorship / look-ahead risk가 남아 있다. |
| Table semantics | `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md` | ETF provider snapshot, holdings, exposure, macro observation의 source / proxy / current snapshot 성격이 구분되어 있다. |
| Active PV task | `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PLAN.md` | P2의 목표는 proxy / NOT_RUN / 설명 부족 항목을 provider / macro / stress evidence로 정상화하는 것이다. |
| Active PV risks | `.aiworkspace/note/finance/tasks/active/practical-validation-v2/RISKS.md` | provider coverage partial, stress REVIEW, official + db_bridge origin confusion이 알려진 risk다. |
| Registry contract | `.aiworkspace/note/finance/registries/README.md` | V2 registry와 legacy registry가 공존하며, registry는 live approval이나 broker order가 아니다. |

## Implemented Capabilities

| Capability | Current state | Product value |
| --- | --- | --- |
| Candidate source creation | Single strategy, compare, weighted portfolio, saved mix replay를 후보 source로 만들 수 있다. | 전략 탐색과 후보 생성의 중심 흐름이 있다. |
| DB-backed runtime | UI payload가 service / runtime을 거쳐 DB-backed strategy runtime으로 이동한다. | UI 직접 fetch를 피하고 재현성을 높인다. |
| Data Trust metadata | result rows, actual result period, price freshness, excluded ticker, malformed rows를 metadata로 남긴다. | 백테스트 결과의 데이터 품질을 화면에서 설명할 수 있다. |
| Practical Validation V2 | 12개 diagnostic, provider coverage, provider gaps, latest runtime recheck, stress / sensitivity interpretation이 있다. | 실전 검토 전 데이터 / 운용성 / stress evidence를 확인한다. |
| Provider snapshot foundation | ETF operability, holdings, exposure, FRED macro series를 DB에 저장하고 loader로 읽는다. | look-through와 macro context의 기반이 있다. |
| Final Review | validation, robustness, paper observation criteria, operator judgment를 final decision row로 저장한다. | 최종 판단 위치가 분리되어 있다. |
| Selected Portfolio Dashboard | selected row를 read-only로 읽고 performance recheck, monitoring signal, optional actual allocation을 보여준다. | 선정 이후 관찰 화면이 있다. |
| Registry boundary | append-only JSONL과 saved setup이 구분되어 있다. | workflow state를 이어서 읽을 수 있다. |

## Surface Role Classification

| Surface | Role | Notes |
| --- | --- | --- |
| Workspace > Ingestion | Internal / ops console | provider, macro, data refresh를 담당한다. 실전 제품 화면이라기보다 데이터 보강 작업대다. |
| Workspace > Overview | Mixed | 후보 funnel과 next action은 user-facing, runtime / registry 상태는 ops 성격이다. |
| Backtest > Backtest Analysis | User-facing product surface | 후보 source 생성의 핵심. 단, 실험 설계 / overfit 방어 protocol은 아직 약하다. |
| Backtest > Practical Validation | User-facing product surface with ops controls | 12개 진단은 user value지만 Provider Data Gaps / collection button은 ops control이다. |
| Backtest > Final Review | User-facing product surface | 최종 판단 기록. 다만 "투자 가능 후보" 표현은 no-live boundary와 함께 계속 조심해야 한다. |
| Operations > Candidate Library | Mixed / legacy inspector | current / pre-live legacy registry 재검토 도구다. Selection V2 source-of-truth는 아니다. |
| Operations > Backtest Run History | Internal / ops console | 과거 실행 inspect / replay 도구다. |
| Operations > Selected Portfolio Dashboard | User-facing monitoring surface | read-only monitoring이지만 자동 snapshot history와 trigger lifecycle은 아직 약하다. |
| Reference > Guides | User-facing guide | 제품 흐름을 설명하지만, 투자 due diligence checklist 자체는 별도 packet으로 더 강하게 만들 수 있다. |

## Strengths

- Stage ownership이 명확하다. Backtest는 후보 생성, Practical Validation은 검증, Final Review는 판단, Selected Dashboard는 사후 확인을 맡는다.
- UI-engine boundary가 많이 정리되어 `app/services`, `app/runtime`, `app/web` 역할이 분리되어 있다.
- Practical Validation이 단순 score가 아니라 provider coverage, benchmark parity, curve provenance, stress / sensitivity evidence를 남긴다.
- `NOT_RUN`은 pass가 아니라는 문서 원칙이 명확하다.
- full holdings / macro series를 JSONL에 넣지 않고 DB에 두는 방향은 장기적으로 맞다.

## Weaknesses

| Weakness | Evidence | Why it matters for real investing |
| --- | --- | --- |
| Backtest robustness protocol is not first-class | Runtime metadata와 stress / sensitivity는 있으나, walk-forward / out-of-sample / parameter sweep / multiple-testing control이 제품 flow의 필수 gate로 보이지 않는다. | 좋은 in-sample backtest를 고르는 과정 자체가 overfitting을 만들 수 있다. |
| `NOT_RUN` and proxy still have positive scoring weight | `app/services/backtest_practical_validation_diagnostics.py`에서 `NOT_RUN` status weight가 0.35이고, blocker가 없으면 Final Review 이동이 가능하다. | 점수화가 "검증하지 못함"을 부분 점수로 읽게 만들 수 있다. |
| Provider coverage is intentionally partial | active task risk가 provider coverage partial을 명시한다. iShares / SSGA / Invesco 중심이며 source map 밖 ticker는 gap으로 남을 수 있다. | ETF 후보가 늘수록 holdings / cost / liquidity 검증 효력이 흔들린다. |
| Current snapshot and PIT truth are mixed risks | data docs가 `nyse_asset_profile`, ETF provider snapshot, macro observation의 current / stale / vintage 한계를 명시한다. | 과거 검증일 기준으로 실제 알 수 있었던 정보와 현재 정보가 섞이면 look-ahead 판단이 생긴다. |
| Data governance is still lightweight | schema sync는 정식 migration system이 아니고, registry JSONL과 legacy compatibility registry가 공존한다. | 데이터 저장 / 보존 / 정리 기준이 약하면 "무분별한 데이터 저장"과 재현성 저하가 생긴다. |
| Final decision packet is not yet investment committee-grade | Final Review row는 많은 evidence를 담지만, 하나의 report artifact, checklist, unresolved-risk attestation, assumption disclosure로 고정되어 있지 않다. | 나중에 왜 선택했는지, 무엇을 검증하지 못했는지, 어떤 조건이면 폐기할지 추적하기 어렵다. |
| Monitoring loop is mostly manual / read-only | Selected Dashboard는 recheck와 optional allocation check를 보여주지만, monitoring snapshot은 사용자가 명시적으로 저장할 때만 남긴다. | 선정 이후 drift, benchmark underperformance, cost/liquidity deterioration을 운영 이력으로 쌓기 어렵다. |
| Legacy and V2 concepts coexist | Candidate Review / Portfolio Proposal / Pre-Live registry가 compatibility로 남아 있고, Selection V2 주 흐름과 병행된다. | 사용자가 어느 기록이 source-of-truth인지 헷갈릴 수 있다. |

## Data And Validation Risks

- Point-in-time risk: `period_end`, `filing_date`, `accepted_at`, `available_at` 기준을 엄격히 분리하지 않으면 factor backtest가 look-ahead bias를 만들 수 있다.
- Survivorship risk: `nyse_stock`, `nyse_etf`, `nyse_asset_profile`은 listing / profile master지만 완전한 historical membership table은 아니다.
- Provider staleness risk: ETF holdings / exposure / operability는 current snapshot 성격이며, 과거 특정 검증일의 truth로 쓰려면 해당 날짜 snapshot이 DB에 있어야 한다.
- Macro vintage risk: FRED observation은 저장하지만 ALFRED vintage point-in-time 계층은 아직 없다.
- Benchmark parity risk: Final Review로 넘기기 전 benchmark 기간 / frequency / coverage parity가 `REVIEW`인 경우가 생길 수 있다.
- Implementation risk: 같은 전략이라도 engine implementation, cost, rebalance convention, close-price execution assumption이 다르면 실전성과가 달라질 수 있다.

## UX / Workflow Friction

- 사용자는 "검증 결과가 충분한가?"보다 "부족한 evidence가 무엇이고, 이 후보를 왜 보류해야 하는가?"를 더 빨리 알아야 한다.
- Provider gap collection이 Practical Validation 안에 있어 편하지만, 사용자-facing validation과 ops ingestion control이 섞인다.
- Final Review가 선택 / 보류 / 거절 / 재검토를 저장하더라도, 선택 전 mandatory checklist와 unresolved-risk acknowledgement가 약하다.
- Selected Dashboard가 read-only라 안전하지만, 사후관리 루프가 기록으로 축적되지 않으면 실제 운용 관리 도구로 성장하기 어렵다.

## Documentation Or Handoff Drift

- `.aiworkspace/note/finance/registries/README.md`는 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`을 V2 source-of-truth로 설명하지만, 현재 로컬 파일 목록에는 legacy `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`만 존재한다. V2 파일은 runtime 생성 전일 수 있으므로 코드 path와 실제 workspace artifact 확인이 필요하다.
- `Backtest UI Flow`에는 legacy 흐름이 길게 남아 있어 Selection V2만 보려는 사용자에게 정보량이 많다.
- Product direction은 "Practical Validation V2 P2/P3" 중심이고, 이번 리서치처럼 상위 investment readiness 기준은 아직 roadmap으로 승격되지 않았다.

## Benchmark Questions

1. 상용 / 실서비스는 backtest result를 어떤 investment decision packet으로 묶는가?
2. holdings look-through, cost, benchmark, attribution, stress, Monte Carlo를 어느 단계에서 보여주는가?
3. 실제 투자 전에는 `NOT_RUN`, missing data, current snapshot, hypothetical performance를 어떻게 표시하고 차단하는가?
4. 선정 이후 monitoring은 단순 dashboard인지, snapshot / review trigger / attribution history를 축적하는지?
5. no-live-trading 경계를 유지하면서도 실전 투자 판단에 필요한 "운영 가능한 후보" 기준을 어떻게 강화할 수 있는가?

## Audit Conclusion

현재 프로젝트의 큰 흐름은 맞다. 하지만 다음 개발 방향은 새 전략을 더 추가하거나 화면을 더 늘리는 것이 아니라, 기존 흐름을 "투자 판단용 검증 프로토콜"로 더 엄격하게 만드는 쪽이어야 한다.

우선순위는 다음 순서가 적절하다.

1. `Investability Evidence Packet`: Backtest부터 Final Review까지의 evidence, unresolved gaps, assumptions, source provenance를 하나의 packet으로 고정한다.
2. `Validation Gate Hardening`: `NOT_RUN`, proxy, benchmark parity, provider staleness, critical stress missing을 점수보다 gate / acknowledgement 중심으로 다룬다.
3. `Data Governance Layer`: DB snapshot, JSONL registry, generated artifact, source provenance, schema version, retention policy를 분리한다.
4. `Robustness Lab`: walk-forward / out-of-sample / parameter sensitivity / Monte Carlo / stress scenario를 Backtest Analysis의 선택 옵션이 아니라 Practical Validation의 검증 근거로 연결한다.
5. `Post-Selection Monitoring Log`: selected portfolio recheck, drift, benchmark underperformance, provider data deterioration, review triggers를 append-only monitoring evidence로 축적한다.

## 2026-06-08 Main-Dev Session Refresh

### Session Role

이 `main-dev` 세션은 전략 자체를 새로 발굴하거나 심층 성과 개선을 담당하지 않는다. 그 작업은 `backtest-dev` / `codex/backtest-dev`에서 진행한다.

이 세션의 목적은 현재 제품의 `Backtest Analysis -> Practical Validation -> Final Review -> Operations > Portfolio Monitoring` 흐름을 제품 관점에서 감사하고, 상용 quant / portfolio analytics 제품 패턴과 비교해 다음 개발 방향을 선정할 수 있는 근거를 만드는 것이다.

이번 refresh는 새 지침이나 확정 roadmap이 아니다. 향후 개발 세션을 열기 전의 제품 방향 baseline이다.

### Current Implemented Flow

2026-06-08 문서와 코드 기준 현재 주 흐름은 아래처럼 읽는다.

```text
Workspace > Ingestion
  -> Workspace > Overview
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

Backtest 주 흐름은 `app/web/backtest_workflow_routes.py`에서 3개 visible stage로 정리돼 있다.

- `Backtest Analysis`: 단일 전략, Portfolio Mix Builder, saved mix replay로 후보 source를 만든다.
- `Practical Validation`: source traits, module gate, provider / macro / robustness / construction / data coverage / realism evidence를 만든다.
- `Final Review`: Gate 통과 후보만 모니터링 후보로 선정하고, selected-route decision row를 저장한다.
- `Operations > Portfolio Monitoring`: Final Review selected row를 사용자 monitoring portfolio에 담고 명시적 scenario update 후 read-only로 관찰한다.

### Current Strengths

| Strength | Why it matters |
| --- | --- |
| Stage ownership is clear | 후보 생성, 검증, 최종 선정, 사후 모니터링의 책임이 분리돼 있다. |
| Evidence-first direction is strong | 수익률만 보고 선택하지 않고 data trust, provider, look-through, robustness, realism, open review items를 함께 본다. |
| No-live boundary is explicit | live approval, broker order, account sync, auto rebalance를 반복적으로 차단한다. |
| DB-backed data boundary is mostly sound | provider / macro / sentiment / futures / lifecycle evidence는 ingestion -> DB -> loader -> UI 흐름을 따른다. |
| Operations IA was corrected | Portfolio Monitoring과 System / Data Health를 primary lane으로, Run History와 Candidate Library를 archive / recovery로 낮췄다. |
| Reference Center now explains the product flow | 주요 workflow 화면에서 contextual help와 Glossary concept drift guard가 붙었다. |

### Current Weaknesses

| Weakness | Current signal | Product implication |
| --- | --- | --- |
| Evidence is rich but still heavy | Final Review / Practical Validation에 근거가 많고 상세 표가 많다. | 사용자는 "그래서 오늘 무엇을 해야 하는가"를 빠르게 파악하기 어렵다. |
| Monitoring history is not durable enough | Portfolio Monitoring scenario result는 session state 중심이고 monitoring log는 explicit optional 기록이다. | 선정 이후 drift / underperformance / stale evidence / review trigger가 운영 이력으로 충분히 쌓이지 않는다. |
| Robustness is present but not yet an experiment lifecycle | walk-forward / OOS / regime / stress evidence가 audit row로 연결됐지만, 실험 registry / run set / parameter family 관리는 약하다. | backtest-dev 전략 개선 결과를 제품 workflow로 승격할 때 검증 이력과 selection-bias control이 부족할 수 있다. |
| Data provenance is still uneven | PIT / current snapshot / provider staleness 경계는 문서화됐지만 모든 evidence row가 같은 provenance contract를 갖지는 않는다. | 나중에 "그때 알 수 있었던 정보인가"를 재현하기 어렵다. |
| Large product surfaces remain | `app/web/backtest_compare.py`, `app/web/final_selected_portfolio_dashboard.py`, `app/runtime/final_selected_portfolios.py`는 여전히 큰 파일이다. | 기능 추가 전후로 회귀 위험과 UX 판단 비용이 커진다. |
| Legacy compatibility is still visible | Candidate Review / Portfolio Proposal / Candidate Library / legacy panel routes가 compatibility로 남아 있다. | 삭제 대상은 아니지만, 주 흐름과 archive / recovery 경계가 계속 흐려질 수 있다. |
| Risk-On Momentum 5D governance is deferred | Backtest Analysis 연구 lane으로 구현됐지만 Practical Validation / Final Review / Portfolio Monitoring daily signal policy에 연결되지 않았다. | `backtest-dev` 연구 결과를 main product workflow로 받아들이는 기준이 필요하다. |

### Legacy / Removal Read

지금 삭제보다 먼저 할 일은 "primary workflow에서 더 낮추고, archive / recovery 의미를 고정"하는 것이다.

| Surface / concept | Current read | Direction |
| --- | --- | --- |
| Candidate Review | legacy compatibility / old candidate packaging | 신규 주 흐름에서는 숨김 또는 archive로 유지. 즉시 삭제는 보류. |
| Portfolio Proposal | legacy proposal draft and paper path | Backtest Analysis Portfolio Mix / Final Review selected-route로 대체되는 부분은 demote. |
| Backtest Run History | archive / recovery | 보존. 후보 생성 주 단계로 올리지 않는다. |
| Candidate Library | archive / recovery | 보존. Selection V2 source-of-truth는 아니다. |
| `Selected Portfolio Dashboard` file name | legacy implementation name | 사용자-facing 명칭은 `Operations > Portfolio Monitoring`으로 유지. 파일명 rename은 별도 refactor scope. |
| Generated run history / artifacts | local runtime artifact | 명시 승인 없이는 커밋 / roadmap evidence로 승격하지 않는다. |

### Product Direction Implication

다음 개발 방향은 새 화면을 늘리는 것보다, 이미 만들어진 evidence 흐름을 "운영 가능한 판단 체계"로 만드는 쪽이 맞다.

1. `Portfolio Monitoring Snapshot / Review Loop`: 선정 후 monthly / rebalance / manual review snapshot을 append-only로 남긴다.
2. `Research-to-Product Strategy Governance`: backtest-dev에서 개선한 전략을 Practical Validation / Final Review / Monitoring policy로 승격하는 계약을 만든다.
3. `Robustness Experiment Registry`: parameter sweep, walk-forward, OOS, regime, cost/slippage, Monte Carlo/bootstrap run set을 재현 가능한 단위로 묶는다.
4. `Data Provenance / PIT Upgrade`: evidence row마다 snapshot id, source date, available-at assumption, current-vs-historical label을 통일한다.
5. `Legacy Demotion / Archive Cleanup`: 삭제가 아니라 source-of-truth breadcrumb와 navigation demotion으로 혼란을 줄인다.
6. `Large Surface Refactor Round`: 개발 방향이 정해진 뒤 `backtest_compare`, Portfolio Monitoring runtime/UI를 기능별로 더 나눈다.
