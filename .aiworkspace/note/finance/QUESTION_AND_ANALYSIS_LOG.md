# Finance Question And Analysis Log

## Purpose
This file stores the current, concise set of durable `finance` design decisions and analysis outcomes.

Use it for:
- active architecture interpretations
- current strategy-refinement direction
- decisions that should influence the next turns

Detailed historical analysis was archived on `2026-04-13`.

## Active Pointers

- current phase board:
  - none. Open a new phase only after the user approves a concrete scope.
- latest completed phase:
  - [Phase 13 First-Cycle Hardening Closeout](./phases/done/phase13-hardening-cycle-closeout.md)
- current candidate summary:
  - Latest completed structure work is Refactor Round Closeout 10차 in [refactor-round-closeout-20260607](./tasks/active/refactor-round-closeout-20260607/AUDIT.md).
  - Recent merged work should be read as five product areas: Overview / Market Context, Backtest Analysis, Practical Validation / Final Review, Operations / Portfolio Monitoring, and UI / Engine Boundary.
  - Market context surfaces are not approval or signal owners; Portfolio Monitoring remains read-only and explicit-action based.
- historical full archive:
  - [QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.aiworkspace/note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md)

## Entries

### 2026-06-10 - Market Context should read as a cockpit, not a refresh console
- User request:
  - `Overview > Market Context` 탭의 1차~4차 UX/UI 개선 진행을 승인함.
- Interpreted goal:
  - 첫 화면에서 일괄 갱신 / 진단값보다 시장 맥락 요약, 자료 상태, 다음 확인 순서가 먼저 보이게 한다.
- Analysis result:
  - Market Context의 headline은 자료 경고가 아니라 현재 시장 맥락 한 줄이어야 한다. stale/partial/missing 같은 데이터 상태는 `자료 상태`와 `Data Health` handoff로 분리하고, core 3개 카드와 supporting 3개 카드를 나눠 읽는 순서를 만든다.
- Follow-up:
  - Direct `/overview` first-load Page not found modal은 normal root navigation과 분리된 Streamlit routing risk로 남긴다.

### 2026-06-08 - Reference should appear inside the workflow screens
- User request:
  - Reference 탭 개편의 4차 작업 진행을 요청함.
- Interpreted goal:
  - 1차~3차에서 만든 Reference Center / Glossary를 실제 업무 화면에서 발견 가능하게 만든다.
- Analysis result:
  - 첫 연결 범위는 Backtest Analysis, Practical Validation, Final Review, Operations Console, Portfolio Monitoring이 적절하다. 각 화면은 현재 workflow의 owner screen이고, 사용자가 `NOT_RUN`, selected-route gate, monitoring scenario stale 같은 용어에서 막힐 가능성이 높다. 공용 service catalog와 얇은 Streamlit renderer를 분리하면 UI 화면은 한 줄 호출만 갖고, 도움말 문구 drift는 줄일 수 있다.
- Follow-up:
  - 5차는 Reference drift guard / QA polish다. `GLOSSARY.md` deep-link query, Ingestion / Overview까지의 확대, visual polish는 별도 후속으로 둔다.

### 2026-06-08 - Operations V2 closeout should separate normal navigation from direct-route noise
- User request:
  - Operations Overview V2 5차 작업 진행을 요청함.
- Interpreted goal:
  - 1차~4차 Operations V2 개편을 최종 QA / 문서 / runbook 기준으로 닫는다.
- Analysis result:
  - 정상 사용자 흐름은 root `/`에서 top navigation의 `Operations Overview`를 누르는 경로이며, 이 경로는 같은 `/operations` URL에 도달해도 Page not found dialog가 없다. 직접 `/operations` first-load에서는 Streamlit local routing dialog가 보일 수 있으므로 QA runbook에 별도 diagnostic으로 남긴다.
- Follow-up:
  - Operations V2 자체는 closeout하고, archive helper code / historical data deletion은 별도 audit / migration task로 승인받고 다룬다.

### 2026-06-08 - Operations queue should be priority and evidence ordered
- User request:
  - Operations Overview V2 4차 작업 진행을 요청함.
- Interpreted goal:
  - Evidence Health 다음에 나오는 daily queue를 단순 안내 목록이 아니라 운영 우선순위가 있는 review queue로 재정렬한다.
- Analysis result:
  - Queue는 이미 로드된 portfolio summary / evidence health / run history 상태만 사용한다. P0 setup blocker와 system/data failure, P1 scenario freshness, P2 open review, P3 routine/no-selected-row 안내로 정렬하고 각 row에 evidence key와 summary metric을 붙인다.
- Follow-up:
  - 5차는 Operations V2 최종 QA / 문서 closeout으로, archive helper code 삭제 여부는 별도 audit로 분리하는 것이 안전하다.

### 2026-06-07 - Operations evidence health should stay lightweight
- User request:
  - Operations Overview V2 3차 작업 진행을 요청함.
- Interpreted goal:
  - Portfolio-first summary 다음에 운영 근거의 건강 상태를 빠르게 확인하는 mini strip을 붙인다.
- Analysis result:
  - Provider / holdings / exposure 세부 evidence는 DB-backed provider context read가 필요하므로 Operations Overview 입구에서 매번 조회하지 않는다. 3차는 이미 로드된 selected dashboard / monitoring portfolio setup / run history payload로 scenario freshness, selected evidence readiness, open review, system run health만 요약한다.
- Follow-up:
  - 4차는 이 strip과 action queue를 연결해 review queue를 더 운영자 행동 중심으로 재정렬하는 작업이 자연스럽다.

### 2026-06-07 - Operations Overview should start from portfolio status
- User request:
  - Operations Overview V2 2차 작업 진행을 요청함.
- Interpreted goal:
  - 운영 화면 첫 판단을 archive/history나 queue가 아니라 현재 monitoring portfolio 상태로 바꾼다.
- Analysis result:
  - Operations Overview는 Portfolio Monitoring의 session-only scenario 결과를 직접 소유하지 않는다. 따라서 2차 summary는 selected dashboard / monitoring portfolio setup에서 안정적으로 읽히는 active portfolio, assigned strategy, stale 또는 pending scenario metadata, blocked / missing / incomplete slot, open review, target snapshot, next review를 read-only로 요약한다.
- Follow-up:
  - 3차는 provider / scenario / data freshness evidence health mini strip으로 이어가는 것이 자연스럽다.

### 2026-06-07 - Operations Overview should read as cockpit, not cleanup history
- User request:
  - Operations Overview V2 중 1차 작업 진행을 요청함.
- Interpreted goal:
  - 새 지표 확장 전에 archive / development-history 노출을 제거해 Operations의 첫 화면을 portfolio monitoring + system/data health cockpit으로 정리한다.
- Analysis result:
  - `surface_audit`, `stage_roadmap`, archive decision table은 운영자가 매일 보는 화면의 정보가 아니므로 user-facing read model / renderer에서 제거했다. Archive data/helper 삭제, portfolio-first counters, evidence strip은 후속 차수로 남겼다.
- Follow-up:
  - 2차는 active portfolio / assigned strategy / stale / blocked / open review / next review date summary를 Overview 상단에 추가하는 작업이 자연스럽다.

### 2026-06-07 - Reference Glossary should share operational concepts with Guides
- User request:
  - Reference 탭 개편의 3차 작업 진행을 요청함.
- Interpreted goal:
  - 1차 Reference Center와 2차 journey / playbook 확장 이후, `Guides` 상태 lookup과 `Glossary` page가 서로 다른 용어 소스를 갖지 않게 통합한다.
- Analysis result:
  - Durable `GLOSSARY.md`는 긴 문서 용어 사전으로 유지하고, UI-critical operational status / concept rows는 `app/services/reference_glossary_catalog.py`의 Streamlit-free shared dictionary가 소유하는 구조가 맞다. `Guides`와 `Glossary`는 같은 concept row를 표시하고, Glossary는 추가로 markdown section parser를 통해 기존 문서 용어를 함께 보여준다.
- Follow-up:
  - 4차는 Backtest / Operations 주요 화면에서 Reference contextual link 또는 help drawer를 연결한다. 5차는 Reference drift guard와 QA polish를 다룬다.

### 2026-06-07 - Refactor round should close before opening another broad split
- User request:
  - 9차 이후 다음 단계 진행을 요청함.
- Interpreted goal:
  - 새 기능 개발이 아니라 5차~9차 구조정리 흐름을 닫고, 남은 작업을 active work와 follow-up으로 분리한다.
- Analysis result:
  - `app/web/backtest_compare.py`는 여전히 크지만, 추가 분리는 saved replay / weighted result / strategy-specific form body처럼 별도 ownership을 가진 후속 task로 여는 것이 맞다. 이번 10차는 boundary baseline, generated artifact hygiene, manifest / roadmap 상태를 닫는 closeout으로 처리한다.
- Follow-up:
  - 다음 code work는 Backtest Compare follow-up split 중 하나 또는 별도 large-surface refactor round로 승인받고 시작한다.

### 2026-06-07 - Backtest Compare split should start with visual components
- User request:
  - 9차 작업으로 Backtest Compare Streamlit split 진행을 승인함.
- Interpreted goal:
  - `app/web/backtest_compare.py`의 대형 Streamlit 책임을 줄이되 strategy math, runtime, service, registry behavior는 바꾸지 않는다.
- Analysis result:
  - 가장 안전한 first pass는 Portfolio Mix Builder visual shell 분리다. CSS / stepper / section heading / component result card는 실행 / 저장 / handoff와 독립적이므로 `app/web/backtest_compare_components.py`가 소유하고, `app/web/backtest_compare.py`는 orchestration owner로 유지한다.
- Follow-up:
  - saved replay, weighted result, strategy-specific form body는 별도 후속 split 후보로 남긴다.

### 2026-06-07 - Ingestion diagnostics should be a service facade
- User request:
  - 7단계를 다 마무리하고 진행하자며 7B 진행을 요청함.
- Interpreted goal:
  - 7A 이후 `app/web/ingestion_console.py`에 남아 있던 read-only diagnostics orchestration을 UI 밖으로 옮겨 7차를 닫는다.
- Analysis result:
  - Price Stale / Statement Coverage / Statement PIT inspection은 모두 수집 write가 아니라 진단 read path다. 따라서 `app/services/ingestion_diagnostics.py`가 loader / job helper / source inspection 호출을 소유하고, Streamlit module은 입력과 렌더만 소유하는 구조가 가장 안전하다.
- Follow-up:
  - Ingestion diagnostic facade는 완료됐으므로 roadmap next decision에서 제거한다. 다음 구조 후보는 Backtest Compare Streamlit split이다.

### 2026-06-07 - Strict runtime family can move without finishing Ingestion 7B
- User request:
  - 다음 단계를 진행하되 7단계를 다 마무리 못한 것 같은데 괜찮은지 확인함.
- Interpreted goal:
  - 7차 잔여 범위를 명확히 한 뒤, 독립적인 8차 runtime split을 계속 진행한다.
- Analysis result:
  - 당시 7A Ingestion Console physical split은 완료됐고, 7B Ingestion diagnostic facade extraction은 후속 후보로 남아 있었다. 8C strict runtime family split은 `app/runtime/backtest*.py` 경계 작업이므로 Ingestion diagnostic facade와 충돌하지 않았다.
- Follow-up:
  - `app/runtime/backtest_strict.py`를 strict family implementation owner로 둔다. 7B는 이후 `ingestion-diagnostic-facade-20260607`에서 완료됐고, 다음 구조정리 선택지는 Backtest Compare Streamlit split로 남는다.

### 2026-06-07 - Runtime real-money helpers should be a helper-family module
- User request:
  - 8A 다음 단계로 runtime 대형 파일 분해를 계속 진행해 달라고 요청함.
- Interpreted goal:
  - strategy runner 동작을 바꾸지 않고 `app/runtime/backtest.py`에 남은 real-money / guardrail / benchmark / deployment readiness helper family를 분리한다.
- Analysis result:
  - `_apply_real_money_hardening`은 거래비용 / turnover, benchmark overlay, validation / promotion / shortlist / probation / monitoring / deployment readiness, ETF operability policy helper를 한 덩어리로 사용한다. 따라서 순환 import를 만들지 않으려면 이 helper family 전체를 `app/runtime/backtest_real_money.py`로 이동하고 `app.runtime.backtest`는 compatibility facade로 re-export하는 구조가 맞다.
- Follow-up:
  - 다음 runtime split은 strict quality / value / quality-value annual and quarterly wrappers를 family module로 옮기는 8C가 자연스럽다.

### 2026-06-07 - Runtime split should keep `app.runtime.backtest` as compatibility facade
- User request:
  - 8차로 runtime 대형 파일 분해 작업을 진행해 달라고 요청함.
- Interpreted goal:
  - `app/runtime/backtest.py`를 한 번에 재작성하지 않고, strategy family별 구현을 전용 module로 옮기되 기존 UI / service public import path는 유지한다.
- Analysis result:
  - 첫 slice는 Risk-On Momentum 5D가 가장 안전하다. core logic이 `finance/swing.py`, `finance/swing_analysis.py`로 이미 분리되어 있고, runtime orchestration도 universe / macro / artifact wiring으로 응집되어 있다.
- Follow-up:
  - 다음 runtime split은 real-money / guardrail / deployment readiness contract helpers 또는 strict quality / value family wrappers가 자연스럽다.

### 2026-06-07 - Ingestion Console split should be physical first, service extraction second
- User request:
  - 7차로 대형 Streamlit 파일 분해 작업을 진행해 달라고 요청함.
- Interpreted goal:
  - `streamlit_app.py`의 대형 Ingestion render/state/job UI 책임을 분리하되, collector / DB / job behavior는 바꾸지 않는다.
- Analysis result:
  - 첫 단계는 `Workspace > Ingestion` 전체 UI boundary를 `app/web/ingestion_console.py`로 이동하는 것이 안전하다. 이 작업으로 top-level shell이 얇아지고, 후속 diagnostic facade extraction을 더 작은 범위에서 진행할 수 있다.
- Follow-up:
  - 7B는 Ingestion read-only diagnostics / live source inspection을 Streamlit-free service/job facade로 옮길지 결정하는 작업이 자연스럽다.

### 2026-06-07 - Overview refresh is allowed only through an action facade
- User request:
  - 6차로 수집 / 조회 경계 정리 작업을 진행해 달라고 요청함.
- Interpreted goal:
  - Overview와 Ingestion의 수집 / 조회 경계를 코드와 durable docs에서 일치시킨다.
- Analysis result:
  - Overview는 market context 조회 표면이지만, 제품상 bounded refresh가 이미 필요하다. 따라서 금지 대신 `app/jobs/overview_actions.py`를 공식 action facade로 두고, UI는 세부 ingestion job / automation / run-history helper를 직접 import하지 않는 구조가 맞다.
- Follow-up:
  - 다음 구조정리는 Ingestion diagnostic facade와 Ingestion Console render split로 이어가는 것이 안전하다.

### 2026-06-07 - Refactor should start with action boundary, not file splitting
- User request:
  - 5차로 코드 구조 감사 / 리팩토링 기준선 작업을 진행해 달라고 요청함.
- Interpreted goal:
  - 기능 개발 없이 현재 코드 경계와 대형 파일을 점검하고, 다음 구조정리 순서를 정한다.
- Analysis result:
  - hard UI / engine boundary는 통과한다. 그러나 Overview는 context-only surface 문서와 달리 bounded refresh job trigger를 가진 mixed surface다. 큰 파일 분해는 가능하지만, 먼저 Overview / Ingestion action boundary 정책을 정해야 안전하다.
- Follow-up:
  - 6차는 Overview refresh를 공식 예외로 둘지, action facade로 모을지, Ingestion / automation으로 되돌릴지 결정하는 작업으로 시작한다.

### 2026-06-07 - Post-merge cleanup handoff should be docs-only and explicit
- User request:
  - 4차로 검증 및 handoff를 진행해 달라고 요청함.
- Interpreted goal:
  - 1차~3차 정리 결과가 다음 작업자에게 안전하게 전달되도록 검증 evidence와 read order를 남긴다.
- Analysis result:
  - 현재 작업은 코드 검증보다 문서 포인터 / manifest / stale pointer / generated artifact exclusion 검증이 핵심이다. UI / DB / runtime은 변경하지 않았으므로 Browser QA나 backtest 실행은 범위 밖이다.
- Follow-up:
  - `post-merge-verification-handoff-20260607/HANDOFF.md`를 handoff entry point로 둔다. Push / PR, `.note/` cleanup, physical archive migration은 별도 승인 scope로 남긴다.

### 2026-06-07 - Active folder cleanup should be manifest-first, not mass-move-first
- User request:
  - 3차로 active task / phase 상태 정리를 진행해 달라고 요청함.
- Interpreted goal:
  - 병합 후 남은 `tasks/active`와 `phases/active` 폴더가 실제 open work처럼 보이지 않게 current state를 정리한다.
- Analysis result:
  - `tasks/active`에는 170개 task folder, `phases/active`에는 11개 phase board가 남아 있었다. `tasks/done`은 README만 있고 `phases/done`은 closeout summary 중심이므로 대량 이동은 링크 churn이 크다. 이번 3차는 manifest / README / roadmap 기준 정리가 가장 안전하다.
- Follow-up:
  - Physical archive migration은 별도 승인 scope로 남긴다. 현재 active task / phase는 none이며, retained folder 해석은 각 `STATUS_MANIFEST.md`를 기준으로 한다.

### 2026-06-07 - Boundary docs need a central source-of-truth
- User request:
  - 2차로 구조 / 경계 문서 정리를 진행해 달라고 요청함.
- Interpreted goal:
  - 병합 후 흩어진 UI / service / runtime / loader / DB / storage 책임 경계를 durable docs에서 한 기준으로 읽게 만든다.
- Analysis result:
  - code flow 문서는 이미 존재하지만 layer ownership, context-only surface, registry / saved / report storage class 판정이 여러 문서에 흩어져 있었다. `SYSTEM_BOUNDARIES.md`를 새 checkpoint로 두고 architecture / data / flow index에서 그 문서를 가리키는 구조가 맞다.
- Follow-up:
  - 2차는 문서 alignment만 수행한다. `.note/` cleanup, active folder migration, Risk-On Momentum 5D governance, Why It Moved V2 storage policy는 별도 승인 scope로 남긴다.

### 2026-06-07 - Post-merge docs need state-model cleanup, not code changes
- User request:
  - master에서 여러 worktree task를 모아 병합했으니, 현재 개발 흐름 / 추가 개발 내용 / 구조와 문서를 크게 파악하고 정리해 달라고 요청함.
- Interpreted goal:
  - 코드 동작을 바꾸기보다 durable docs가 현재 merged product state를 빠르게 설명하게 만든다.
- Analysis result:
  - drift의 핵심은 active 폴더와 roadmap이 완료 이력 / 현재 작업 / 다음 결정을 함께 담아 current state를 흐리게 만든 것이다. 현재 제품은 Ingestion / Overview context -> Backtest Analysis -> Practical Validation -> Final Review -> Operations Console -> Portfolio Monitoring 흐름으로 읽는 것이 맞다.
- Follow-up:
  - 1차 문서 alignment는 진행하고, `.note/` 삭제나 active task / phase 대량 archive 이동은 별도 승인 scope로 남긴다.

### 2026-06-07 - Sentiment context can follow the selection flow without becoming a gate
- User request:
  - 사용자가 Overview Market Sentiment V1의 3단계를 진행해 달라고 요청함.
- Interpreted goal:
  - 2차 Practical Validation overlay를 넘어 Final Review와 Portfolio Monitoring에서도 CNN Fear & Greed / AAII sentiment를 현재 시장 배경으로 보여주되, 판단 / 저장 / 운영 경계는 바꾸지 않는다.
- Analysis result:
  - Final Review의 Decision Desk 아래와 Portfolio Monitoring 진입부가 가장 자연스럽다. 두 위치 모두 이미 gate / monitoring owner가 분리되어 있어 sentiment를 별도 read-only overlay로 넣으면 selected-route gate, Monitoring Scenario, saved setup, registry write와 분리할 수 있다.
- Follow-up:
  - `build_market_sentiment_context_overlay(surface=...)` contract에 `saved_setup_write=false`, `monitoring_signal=false`를 추가하고 두 화면에 context-only UI를 연결한다. 이 context는 PASS/BLOCKER, live approval, order, broker/account sync, auto rebalance가 아니다.

### 2026-06-07 - Korean news can start keyless through Google News KR RSS
- User request:
  - Naver API key 발급 전에는 네이버를 제쳐두고 keyless Google News KR만으로 `Why It Moved` 한국어 뉴스 단서를 진행할 수 있는지 물었고, 진행을 승인함.
- Interpreted goal:
  - Korean article body scraping이나 AI 원인 판정이 아니라, 사용자가 직접 확인할 수 있는 한국어 headline/snippet metadata를 API key 없이 추가한다.
- Analysis result:
  - Google News KR RSS는 dedicated developer API는 아니지만 keyless RSS metadata route로 쓸 수 있다. 앱은 RSS item의 title / source / pubDate / description / link만 session-only로 표시하고, article body / DB persistence는 금지한다.
- Follow-up:
  - `overview-market-movers-second-pass`에 Google News KR RSS provider를 적용했다. RSS 안정성, redirect URL, duplicate/stale result risk는 task `RISKS.md`에 남겼다.

### 2026-06-06 - Korean news should be metadata/snippet, not article scraping
- User request:
  - SEC 공시는 table-only로 유지하고, `Why It Moved`의 영어 뉴스 metadata만으로는 부족하므로 관련 한글 기사도 앱 안에서 단서로 볼 방법을 개선해 달라고 요청함.
- Interpreted goal:
  - 원인 자동판정이 아니라 사용자가 직접 왜 움직였는지 조사할 수 있게 Korean-language source metadata를 추가하되, article body / AI summary / sentiment / durable storage는 금지한다.
- Analysis result:
  - Naver News Search API는 `title`, `originallink`, `link`, `description`, `pubDate` 같은 bounded search-result fields를 주므로 기사 scraping 없이 `제목 / 출처 / 게시 시각 / 단서 / 열기` lane을 만들 수 있다.
- Follow-up:
  - `overview-market-movers-second-pass`에 Korean news lane을 구현했다. Naver credentials가 없으면 setup guidance만 표시하고, DB-backed retention / freshness / replay는 별도 V2 decision으로 남긴다.

### 2026-06-04 - Why It Moved should be an investigation board, not an explanation engine
- User request:
  - benchmark research를 반영해 `Overview > Market Movers > Why It Moved V1.6 UX Pass`를 구현하되 automatic catalyst classifier, AI summary, article / filing body 수집, DB / JSONL 저장 없이 manual investigation board로 개선해 달라고 요청함.
- Interpreted goal:
  - V1.5의 session-only / button-only metadata lookup 경계를 유지하면서, prototype-like fact grid와 raw metadata layout을 movement summary, source status, News / SEC / External source lanes로 재구성해야 함.
- Analysis result:
  - benchmark pattern은 stock detail UX가 identity + movement context를 먼저 보여주고 source categories를 분리한다는 점이다. 이 프로젝트에서는 원인 판정 대신 `Lookup status`, provider row/failure state, `Session-only` boundary를 먼저 보여주는 것이 안전하다.
- Follow-up:
  - V1.6 implementation completed in `overview-market-movers-second-pass`. 후속은 metadata display quality, Korean source provider policy, DB-backed compact metadata retention / freshness / replay policy를 승인 후 별도 scope로 다룬다.

### 2026-06-04 - Why It Moved needs a UX pass before it stops feeling like a prototype
- User request:
  - 사용자가 research link 버튼은 필요 없을 것 같다고 확인했고, 현재 Why It Moved 기능을 리뷰한 뒤 개선점과 prototype 수준 여부를 설명해 달라고 요청함.
- Interpreted goal:
  - V1.5의 no-classifier / session-only boundary는 유지하면서, 잘못된 성공 표시와 버튼 noise를 줄이고 다음 UX/UI 방향을 정리해야 함.
- Analysis result:
  - provider 한쪽만 실패했는데 다른 metadata가 있으면 `OK`로 보이는 점은 investigation state를 과신하게 만든다. 6개 outbound 버튼은 primary action처럼 보여 compact metadata workflow를 방해한다. 현재 UI는 기능 prototype이며, source status / evidence grouping / freshness cue / next-check hierarchy가 아직 부족하다.
- Follow-up:
  - `PARTIAL` 상태를 추가하고 external searches를 collapsed clickable table로 낮췄다. 후속 UX pass는 movement header, provider status strip, News / SEC / External Searches grouping, Korean-source lane policy를 먼저 설계한 뒤 진행한다.

### 2026-06-03 - Why It Moved should remain an investigation panel, not a catalyst classifier
- User request:
  - 사용자가 Market Movers Catalyst Links를 Why It Moved V1.5로 확장하되, 자동 catalyst 판정 / AI 요약 / article 또는 filing 본문 수집 / DB·JSONL 저장 없이 button-triggered session-only metadata lookup으로 구현해 달라고 요청함.
- Interpreted goal:
  - 선택 ticker의 기업 정보, movement context, outbound research links, 최신 news / SEC metadata 상태를 한 패널에서 확인하게 하되 원인 판단은 사용자가 직접 하게 한다.
- Analysis result:
  - `overview_market_intelligence` service가 Streamlit-free read model과 compact metadata helper를 갖고, `overview_dashboard`는 selectbox 변경만으로 fetch하지 않으며 버튼 클릭 시 현재 ticker 1개 결과를 `st.session_state`에만 저장하는 구조가 맞다.
- Follow-up:
  - DB-backed compact metadata는 source retention, freshness, replay, provider throttling, schema / registry policy를 정한 후속 V2 조건으로만 검토한다.

### 2026-06-03 - Market Movers catalyst review should start from links, not app-side crawling
- User request:
  - 사용자가 Market Movers의 Return Rank / Volume Rank 선택 ticker 기준으로 1차 Catalyst Links 기능을 추가하되, AI 요약 / 기사 본문 수집 / 웹 크롤링은 하지 말라고 요청함.
- Interpreted goal:
  - 앱이 원인을 판단하지 않고, period / coverage / rank / symbol / name 맥락을 담은 외부 확인 링크만 제공해 사용자가 직접 catalyst를 조사하게 한다.
- Analysis result:
  - DB schema나 ingestion 추가 없이 `overview_market_intelligence` service read model에서 Yahoo Finance, Google News, SEC company search, IR / earnings 검색 URL을 만들고, `overview_dashboard`는 선택된 Return / Volume rank row의 링크만 렌더링하는 것이 맞다.
- Follow-up:
  - V1은 generic search URL 기반이라 stale / irrelevant result와 회사명 disambiguation은 수동 검토로 남는다. 자동 catalyst 분류, article fetch, summary, registry persistence는 별도 승인 없이는 추가하지 않는다.

### 2026-06-03 - Futures 1d intraday blanks need a bounded 2d fallback
- User request:
  - 사용자가 8501의 `Futures Monitor > Live Futures Charts`가 missing으로 보이는 문제를 해결해 달라고 요청함.
- Interpreted goal:
  - UI render 문제가 아니라 DB-backed futures 1m collection / read model의 coverage gap을 찾아 현재 화면에서 chart row가 회복되게 한다.
- Analysis result:
  - yfinance는 `NQ=F`, `6E=F`, `6J=F`에 대해 `period=1d`, `interval=1m`에서 빈 응답을 냈지만, 같은 symbol의 `period=2d`, `interval=1m`은 최신 candles를 반환했다. 따라서 source fetch 단계에서 empty-symbol만 보강 수집하는 것이 root fix다.
- Follow-up:
  - collector가 empty 1d / 1m symbol만 2d / 1m으로 한 번 retry하고 `fallback_retries` diagnostics를 남긴다. stale provider age는 여전히 REVIEW warning으로 표시하며 exchange-grade realtime으로 해석하지 않는다.

### 2026-06-05 - Sentiment tab should explain context before showing raw evidence
- User request:
  - 사용자가 CNN Fear & Greed / AAII 비관론 노출이 prototype card처럼 보이므로, 지금이 공포인지 탐욕인지, 비관론 수준이 어떤지, 그래서 시장 상황을 어떻게 읽어야 하는지 단계별 context로 설명해 달라고 요청함.
- Interpreted goal:
  - 기존 수집 / 저장 / freshness 노출은 유지하되, Overview Sentiment의 첫 화면을 raw metric card가 아니라 해석 workflow로 바꾼다.
- Analysis result:
  - CNN headline score만으로 결론 내리면 과신 위험이 있으므로 `데이터 상태 -> 공포·탐욕 판정 -> CNN 내부 드라이버 -> AAII 비관론 -> 종합 문맥 -> 다음 확인` 순서가 적절하다. AAII bearish는 historical average 대비 상태와 bull-bear spread를 함께 읽는다.
- Follow-up:
  - Sentiment read model에 `analysis`를 추가하고, UI는 혼합 중립 headline, data confidence, 6단계 학습형 읽기 경로, CNN component learning notes, driver split, next checks를 먼저 보여준다. 이 해석은 market context이며 Practical Validation PASS, live approval, order, broker/account sync, auto rebalance가 아니다.

### 2026-06-05 - CNN / AAII sentiment belongs in Overview as context, not validation approval
- User request:
  - CNN Fear & Greed와 AAII 비관론지수를 수집해 브라우저 화면에 노출하고, 프로젝트에서 가장 합리적인 위치를 분석한 뒤 구현해 달라고 요청함.
- Interpreted goal:
  - 공포탐욕지수와 AAII Bearish Sentiment를 market context로 저장하고 Overview에서 freshness / missing state와 함께 읽게 한다.
- Analysis result:
  - 별도 table보다 기존 `finance_meta.macro_series_observation`의 long-form observation 구조가 적합하다. 화면 위치는 `Workspace > Overview`의 `Futures Monitor` 다음 `Sentiment` 탭이 가장 자연스럽다.
- Follow-up:
  - `finance.data.sentiment`, `finance.loaders.sentiment`, `collect_market_sentiment`, Overview Sentiment tab, Ingestion manual refresh, Data Health target을 추가했다. 이 context는 trade signal, Practical Validation PASS, live approval, order, broker/account sync, auto rebalance가 아니다.

### 2026-06-02 - Selected Dashboard should be daily-monitoring-first
- User request:
  - 사용자가 이미 모니터링 시나리오를 설정한 포트폴리오를 매일 확인할 때 아래로 스크롤해야 하는 문제를 지적하고, 화면 상단에 active portfolio monitoring scenario를 먼저 보여 달라고 요청함.
- Interpreted goal:
  - Selected Portfolio Dashboard는 포트폴리오를 만드는 화면이 아니라, 선택된 포트폴리오의 현재 모니터링 상태를 먼저 보여주고 필요할 때 아래에서 구성을 수정하는 화면이어야 한다.
- Analysis result:
  - 기존 구현은 portfolio-wide scenario cockpit과 session-state contract가 이미 분리되어 있어 runtime / 저장 계약 변경 없이 렌더 순서와 update action 위치를 바꿀 수 있었다. Scenario result는 session-only이고 saved setup은 `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`에 남는다.
- Follow-up:
  - 구현 결과 Active Portfolio Monitoring Scenario가 상단 hero가 되었고, portfolio card shelf / portfolio edit / strategy board / `포트폴리오 시나리오 업데이트`는 아래 관리 영역으로 내려갔다. Detailed readiness / provider / freshness / open issue evidence는 하단에서 선택한 1개 strategy만 lazy-render된다. No portfolio / no strategy / configured-not-run / executed 상태를 구분한다.

### 2026-06-02 - Macro Thermometer confidence must be historical-consistency evidence, not a signal guarantee
- User request:
  - Macro Thermometer가 단순 heuristic에 머무르지 않도록 historical validation과 reliability 표시를 추가해 달라고 요청함.
- Interpreted goal:
  - 저장된 futures daily row를 point-in-time으로 재계산하고, 현재 scenario 옆에 sample / hit rate / confidence / caveat를 표시한다.
- Analysis result:
  - 새 DB table이나 registry가 아니라 `futures_ohlcv` daily row와 필요 시 `nyse_price_history` ETF proxy target을 읽는 read-only service가 적절하다. Mixed scenario는 directional hit rule로 강제하지 않는다.
- Follow-up:
  - `futures_macro_validation.py`를 추가하고 UI에 Interpretation Confidence, Historical Validation Summary, evidence groups, threshold sensitivity, relationship summary를 표시했다. 5y futures smoke는 target source `futures`만 사용했고, yfinance continuous futures / ETF proxy caveat를 docs와 UI에 남겼다.

### 2026-06-01 - Ingestion 탭 리뷰 후속 UX와 결과 해석을 개선한다
- User request:
  - 사용자가 Ingestion 리뷰 결과를 바탕으로 개선을 진행하되, 버튼 / 단어 / 기술 용어를 억지로 모두 한글화하지 말고 설명 내용을 이해하기 쉽게 정리해 달라고 요청함.
- Interpreted goal:
  - 기존 심볼 / 기간 / source 선택 형식은 유지하고, 사용자가 실행 전 수집 범위와 실행 후 데이터 의미를 더 정확히 읽게 해야 함.
- Analysis result:
  - 가장 큰 gap은 화면 구조 전체 교체보다 실행 전 계약, bounded coverage 확인, result domain별 해석 부재였다. 특히 price row, provider snapshot, lifecycle partial evidence를 같은 방식으로 표시하면 coverage를 과신할 수 있음.
- Follow-up:
  - Ingestion workflow overview, 실행 전 contract card, bounded DB coverage quick check, domain-aware result label / interpretation callout, visible lifecycle partial-evidence warning을 추가했다.

### 2026-06-02 - Selected Dashboard scenario execution must remain explicit
- User request:
  - 사용자가 전략 추가 직후 `3. 포트폴리오 모니터 시나리오` 또는 하단 개별 성과가 자동 실행되는 것처럼 보이고 오래 걸린다고 지적하며, 버튼을 눌렀을 때만 업데이트되도록 수정과 성능 검토를 요청함.
- Interpreted goal:
  - Strategy add / slot edit는 saved setup만 바꾸고, scenario result는 명시적인 portfolio-wide 또는 strategy별 실행 action이 있을 때만 새로 계산한다.
- Analysis result:
  - Portfolio-wide recheck 자체는 버튼 뒤에 있었지만, Streamlit `tabs`가 숨겨진 strategy detail 탭까지 eager render해 recheck defaults / preflight / provider evidence 조회가 전략 수만큼 자동 실행됐다. 또한 session result key가 decision-only라 다른 portfolio / slot 설정과 결과가 섞일 수 있었다.
- Follow-up:
  - 구현 결과 scenario result를 portfolio / slot / selected decision / start / end / balance signature로 판정하고, stale 결과는 합산하지 않는다. Portfolio update는 pending / stale 전략만 기본 실행하고 `전체 재실행`으로 full refresh한다. 개별 evidence detail은 사용자가 선택한 1개 strategy만 연다. Full replay는 여전히 selected component contract를 순차 실행하므로 장기적으로 cache / background job / per-strategy incremental queue가 개선 후보로 남는다.

### 2026-06-01 - Selected Dashboard UX polish should go beyond legacy cards/tabs
- User request:
  - 사용자가 방향은 맞지만 UX/UI가 상용 제품처럼 정돈되지 않았고, Streamlit 한계인지 보수적 구현 때문인지 물은 뒤 1~3번 개선 진행을 승인함.
- Interpreted goal:
  - Section 4 evidence는 유지하고, 1~3번만 fixed shelf / command band / strategy board / portfolio-wide scenario cockpit으로 시각 계층을 개선한다.
- Analysis result:
  - 문제는 Streamlit 한계만이 아니라 기존 화면 패턴을 보수적으로 따른 영향이 컸다. Streamlit 안에서도 custom HTML/CSS와 정보 계층 정리로 카드 높이, 삭제 위치, strategy setup 혼잡도, portfolio scenario 의미를 개선할 수 있다.
- Follow-up:
  - 구현 결과 `포트폴리오 시나리오 실행`은 기존 per-strategy recheck logic을 같은 session state에 저장하고, 실행 전 / 부분 집계 / 전체 집계 완료를 명시한다. Live approval / order / broker sync / auto rebalance는 계속 disabled다.

### 2026-06-01 - Selected Dashboard should be portfolio-first and scenario-first
- User request:
  - 사용자가 `Operations > Selected Portfolio Dashboard`를 사용자가 만든 나의 포트폴리오, 전략 구성, 모니터링 시나리오 중심으로 다시 설계해 달라고 요청함.
- Interpreted goal:
  - Final Review handoff / readiness / provider evidence를 첫 화면 주인공에서 내리고, 포트폴리오 생성 / 선택, selected 전략 slot 설정, portfolio-level scenario / 리밸런싱 정보가 먼저 읽히게 만든다.
- Analysis result:
  - 기존 화면은 handoff / evidence 확인이 먼저 보이고 portfolio manager와 strategy recheck가 뒤따라 UX가 운영 대시보드처럼 느껴지지 않았다. 저장 모델은 `strategy_slots`를 추가하되 legacy `selected_decision_ids`를 계속 읽어야 한다.
- Follow-up:
  - 구현 결과 `전략 적용`과 `모니터 시나리오 실행`을 분리하고 evidence detail을 하단으로 낮췄다. Scenario 결과는 session-only이며 live approval / order / broker-account sync / auto rebalance는 계속 disabled다.

### 2026-06-01 - Phase 14 active state was stale and is removed
- User request:
  - Phase 14는 이전에 제거된 것으로 알고 있는데 active 문서가 남아 있는 것 같으니, 개발 재개 전에 문서 정리를 먼저 하자고 요청함.
- Interpreted goal:
  - 현재 worktree의 active phase pointer에서 Phase 14를 제거하고, Phase 13 carry-forward material은 승인 전 source material로만 남긴다.
- Analysis result:
  - `phase14-second-cycle-prioritization`과 `phase14-board-open`은 현재 실행 단위가 아니라 stale active docs였다. 현재 active phase는 없음으로 정리한다.
- Follow-up:
  - prototype/proxy 검증 개선 개발은 Phase 14가 아니라 현재 validation evidence audit / feature recommendation 기준으로 새 scope를 정한 뒤 재개한다.

### 2026-06-01 - Final Decision registry no longer uses the V2 filename
- User request:
  - `V2`가 붙은 current 문서 / JSONL 이름이 헷갈리므로 현재 파일명에서는 `V2`를 떼고, 중복되는 이전 데이터는 `V1`로 이름을 바꿔 달라고 요청함.
- Interpreted goal:
  - current selected-dashboard source는 단순히 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`로 부르고, legacy V1 final decision history는 `_V1` 이름으로 분리한다.
- Analysis result:
  - current runtime source-of-truth는 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이며 schema_version은 그대로 `2`다. legacy helper path는 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl`로 분리했다.
  - Dashboard read model은 selected rows `4`, dashboard rows `4`, assigned references `4`, missing references `0`으로 유지된다.
- Follow-up:
  - 내부 모듈명 `portfolio_selection_v2.py`와 과거 task id의 `v2`는 호환성 / 이력 이름이라 남겨뒀다. 사용자-facing current file path와 source contract에는 old Final Decision V2 이름을 쓰지 않는다.

### 2026-06-01 - Fresh Final Review selected-route pass candidates found
- User request:
  - ETF dynamic source contract 보강 이후 Final Review를 통과하는 포트폴리오 후보를 다시 탐색해 달라고 요청함.
- Interpreted goal:
  - registry / saved append 없이 fresh runtime source를 만들어 Practical Validation replay와 Final Review selected-route gate까지 통과하는 후보를 확인한다.
- Analysis result:
  - 2016-01-29 to 2026-05-29 dry-run sweep에서 `GRS Liquid Macro Top2`와 `GTAA Default Top3`가 selected-route preflight `select_ready`와 Final Review selected gate Ready를 반환했다. `GRS Liquid Macro Top2`는 CAGR `13.31%`, MDD `-17.75%`, Sharpe `1.12`, net spread `7.18%p`, replay PASS로 가장 강한 후보다.
  - Risk Parity와 Dual Momentum은 replay는 PASS지만 Practical Validation `BLOCKED` / selected gate blocked였고, Equal Weight regression 후보는 raw 성과가 높아도 turnover / net cost proof와 net performance policy gap 때문에 selected-route가 막혔다.
- Follow-up:
  - 이 탐색은 dry-run evidence이며 Final Decision V2 row를 저장하지 않았다. 사용자가 원하면 다음 단계는 GRS 후보를 UI 또는 명시적 persistence flow로 Final Review selected row에 저장하는 것이다.

### 2026-06-01 - Lower-MDD GRS candidate is available
- User request:
  - 기존 Final Review 통과 후보의 MDD가 높아 보이므로 CAGR은 높게 유지하면서 MDD가 낮은 후보군을 하나 더 찾아 달라고 요청함.
- Interpreted goal:
  - 기존 selected-route gate 기준을 유지하고, GRS 변형 후보 중 MDD가 낮아진 fresh source를 dry-run으로 찾는다.
- Analysis result:
  - `GRS Macro Top1 MA200`가 같은 liquid macro universe에서 top `1`, MA `200`으로 CAGR `18.03%`, MDD `-12.43%`, Sharpe `1.18`, replay PASS, selected-route preflight ready, Final Review selected gate Ready를 반환했다. top=1 concentration은 tradeoff다.
  - 더 보수적인 top=2 대안은 `GRS QQQ Gold Bonds Top2 MA150`으로 CAGR `12.94%`, MDD `-8.81%`, Sharpe `1.31`, selected-route gate Ready다.
- Follow-up:
  - 둘 다 dry-run evidence이며 Final Decision V2 row를 저장하지 않았다. 최종 선정 전에 top=1 concentration을 받을지, CAGR을 조금 낮추고 MDD를 크게 낮춘 top=2 구조를 택할지 결정해야 한다.

### 2026-06-01 - ETF dynamic strategy sources should carry promotion policy thresholds
- User request:
  - GRS Liquid Macro Top2처럼 실제 성과와 net cost / turnover proof가 충분한 ETF 동적 전략 후보가 `promotion_min_net_cagr_spread` 등 source contract 누락 때문에 Practical Validation selected-route preflight와 Final Review selected gate에서 막히는 문제를 해결해 달라고 요청함.
- Interpreted goal:
  - Final Review gate를 완화하지 않고, Backtest Analysis fresh source contract에서 GTAA / Global Relative Strength / Risk Parity / Dual Momentum이 strict-compatible promotion policy metadata를 자연스럽게 갖게 만든다.
- Analysis result:
  - `_apply_real_money_hardening`은 이미 policy sink 역할을 하고 있었고, 누락 지점은 ETF dynamic runtime / execution dispatch / replay / compare override의 upstream propagation이었다. 해당 경로에 `promotion_min_benchmark_coverage`, `promotion_min_net_cagr_spread`, `promotion_min_liquidity_clean_coverage`, rolling / drawdown policy defaults를 보강했다.
  - Fresh GRS Liquid Macro Top2 검증에서 `promotion_min_net_cagr_spread=-0.02`, `net_cagr_spread=0.0718244521`, Practical Validation replay PASS, selected-route preflight `select_ready`, Final Review selected gate Ready를 확인했다.
- Follow-up:
  - 기존 registry / saved row migration은 하지 않았다. 오래된 row는 rerun/replay 전까지 policy field가 비어 있을 수 있으며, net-cost / turnover proof가 부족한 Equal Weight-style 후보는 계속 selected-route gate에서 막힌다.

### 2026-06-01 - Selected Dashboard should become a monitoring portfolio workspace
- User request:
  - Final Review를 통과한 후보를 실제 투자 후보로 보고, Selected Dashboard에서 사용자가 나의 포트폴리오를 만들고 Final Review selected 후보를 하나씩 담아 가상 시작일 / 종료일 / 초기자산 기준으로 선정 이후 성과와 리밸런싱 필요성을 모니터링하고 싶다고 요청함.
- Interpreted goal:
  - Dashboard의 "portfolio"를 backtest 전략이 아니라 사용자 monitoring container로 재정의하고, selected 후보는 strategy pool로 추가 / 제거하게 만든다. Live / Deployment Readiness는 필수 다음 단계가 아니라 optional preflight로 낮춘다.
- Analysis result:
  - 구현 기준은 `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`에 dashboard setup만 저장하고, Final Decision V2 row는 read-only source-of-truth로 유지하는 것이다. Monitoring scenario / drift / alert / comparison은 기존 selected dashboard read model과 session state를 재사용하며 approval, order, broker/account sync, auto rebalance를 만들지 않는다.
- Follow-up:
  - 현재 worktree에는 fresh selected V2 row가 없어 Browser QA는 empty selected-pool과 portfolio creation surface를 확인했다. 실제 selected row가 생기면 strategy add / scenario execution / transition comparison을 한 번 더 수동 확인한다.

### 2026-06-01 - Selected Dashboard should carry open issues into deployment preflight
- User request:
  - Final Review selected gate 분리 이후 5~7차 작업으로 Selected Dashboard open issue / follow-up 확인, Live / Deployment Readiness read-only preflight, 후보 재탐색 후 fresh selected row 생성 여부 확인을 진행해 달라고 승인함.
- Interpreted goal:
  - Final Review가 `REVIEW` 항목을 저장 차단하지 않는 대신, Selected Dashboard에서 해당 항목을 사라지지 않게 보여주고 future deployment 판단으로 이어지는 read-only preflight를 만든다.
- Analysis result:
  - Open Issues / Follow-up는 Final Decision V2의 `open_review_items`와 review trigger를 읽고, Deployment Readiness preflight는 `deployment_readiness_policy_snapshot`과 recheck / provider / continuity / review signal / allocation evidence를 묶는다.
  - 2026-06-01 registry recheck 기준 Practical Validation row는 2개, Final Review eligible은 GTAA 1개뿐이며, 해당 후보도 selection outcome `hold_or_re_review`라 selected-route pass가 아니다. non-GTAA는 legacy current/proposal registry에만 있어 Clean V2 Practical Validation-passed source가 아니다.
- Follow-up:
  - no selected V2 row 상태에서는 Selected Dashboard가 empty state로 남는다. 다음 후보 탐색은 Backtest Analysis에서 non-GTAA Clean V2 source를 만들고 Practical Validation 필수 gate를 fresh로 통과시키는 쪽으로 진행해야 한다.

### 2026-06-01 - Final Review selection should not equal live deployment readiness
- User request:
  - Final Review가 "진짜 실제 돈을 넣어도 되는가"를 묻고 싶었던 단계라면, 별도 Live / Deployment Readiness를 만들어도 결국 모든 후보가 거기서 막히지 않겠느냐고 질문하고 개선 작업을 승인함.
- Interpreted goal:
  - Practical Validation, Final Review, Selected Dashboard, future Live / Deployment Readiness의 질문을 분리하되, Final Review가 Portfolio Validation과 같은 목적이 되지 않도록 저장 기준과 증거 handoff를 명확히 한다.
- Analysis result:
  - Final Review의 현재 selected-route gate는 live/deployment audit처럼 작동해 기본 `REVIEW`까지 대부분 저장 차단으로 처리했다. 이 때문에 Practical Validation이 허용한 후보가 Final Review에서 거의 저장되지 않는 구조적 병목이 생겼다.
  - 개선 기준은 Final Review를 Selected Dashboard에서 관찰할 모니터링 후보 선정 단계로 좁히고, 실제 자금 투입 판단은 future Live / Deployment Readiness로 분리하는 것이다. Final Review는 hard blocker / critical missing evidence를 막고, 기본 `REVIEW`는 `open_review_items`로 이어서 추적한다.
- Follow-up:
  - Live / Deployment Readiness 화면은 아직 구현하지 않았다. 향후 구현 시 `deployment_readiness_policy_snapshot`을 입력으로 쓰되, broker order / account sync / auto rebalance / live approval은 별도 승인 경계로 다룬다.

### 2026-05-31 - Non-GTAA search did not produce a fresh selected-route pass
- User request:
  - GTAA가 아닌 전략으로도 최종 포트폴리오 후보를 찾아 달라고 요청했고, 다음 개편에는 3단계까지 통과한 최종 포트폴리오가 필요하다고 설명함.
- Interpreted goal:
  - 현재 selection-only save 정책을 유지하면서 비-GTAA 후보가 Practical Validation과 Final Review selected-route gate를 통과해 V2 selected row와 Selected Dashboard 노출까지 가능한지 확인한다.
- Analysis result:
  - Equal Weight, Risk Parity Trend, Dual Momentum, Global Relative Strength, 성장 / 섹터 / 금, SPY / SOXX / IEF / TLT lifecycle mix를 dry-run했지만 fresh current-gate 통과 후보는 없었다.
  - 가장 가까운 후보들은 Practical Validation `READY_FOR_FINAL_REVIEW`와 Final Review evidence `READY_FOR_FINAL_DECISION`까지 갔으나 Backtest Realism, Component Role / Weight, Risk Contribution, Provider / Data / Validation review-required group에서 selected-route가 막혔다.
  - legacy V1 registry에는 비-GTAA Quality selected row가 있으며, read-only Dashboard handoff dry-run은 `HANDOFF_READY` / dashboard row 1개를 반환한다.
- Follow-up:
  - 사용자가 seed가 필요하다고 승인하면 legacy Quality row를 V2 migration seed로 append할 수 있다. 이는 fresh current-gate 재통과가 아니라 명시적 legacy migration으로 라벨링해야 한다.

### 2026-05-31 - Final Review official save should be selection-only
- User request:
  - Final Review에서 비선정 저장 판단이 필요한지 질문했고, 정식 저장은 최종 통과 후보에만 활성화되도록 요청함.
- Interpreted goal:
  - Final Review의 주 action을 모니터링 후보 선정 저장으로 좁히고, 보류 / 거절 / 재검토는 저장 row가 아니라 상태 안내와 보강 방향으로 낮춘다.
- Analysis result:
  - 구현 기준은 `SELECT_FOR_PRACTICAL_PORTFOLIO` + selected-route gate pass + operator reason + unique decision id다.
  - 기존 hold / reject / re-review row는 Saved Decision Review / read model 호환을 위해 읽을 수 있지만, 새 UI의 정식 저장 action은 만들지 않는다.
- Follow-up:
  - Selected Dashboard는 계속 selected row만 읽는다. 보류 후보 queue를 별도 운영 대상으로 관리하고 싶다면 나중에 별도 lightweight queue 기능으로 분리한다.

### 2026-05-31 - Final Review should feel like a user-facing decision desk
- User request:
  - Final Review가 개발자용 UX/UI처럼 보이므로 전체 흐름과 로직을 파악해 사용자가 쉽게 이해할 수 있게 시각적으로 개편해 달라고 승인함.
- Interpreted goal:
  - 검증 / gate / 저장 로직은 유지하면서, 최종 후보 선별 화면의 정보 위계를 사용자-facing Decision Desk로 바꾼다.
- Analysis result:
  - 구현 결과 Final Review는 command center, flow rail, Candidate Board lane cards, visual Decision Cockpit, Final Decision Action, Evidence Appendix, Decision History / Dashboard Handoff 순서로 읽힌다.
  - 새 `app/web/backtest_final_review_components.py`는 CSS / HTML shell만 담당하며, 기존 read model, selected-route gate, JSONL persistence를 바꾸지 않는다.
- Follow-up:
  - 모바일 전용 polish와 깊은 Evidence Appendix redesign은 별도 scope로 남긴다.

### 2026-05-31 - Selected Dashboard handoff should be a read-only connection layer
- User request:
  - Final Review 개편 5번 작업을 진행해 달라고 승인함.
- Interpreted goal:
  - Final Review에서 저장된 선정 판단이 Selected Portfolio Dashboard로 어떻게 이어지는지 명확히 보여주되, 이전 단계 검증을 다시 실행하거나 새 운영 저장을 만들지 않아야 함.
- Analysis result:
  - 구현 결과 Final Decision V2 row를 읽는 `selected_dashboard_handoff_v1` read model이 selected rows, dashboard rows, monitorable / blocked counts, handoff table, checklist, no approval / order / auto-rebalance boundary를 반환한다.
  - Final Review Saved Decision Review와 `Operations > Selected Portfolio Dashboard`가 같은 handoff model을 표시한다.
- Follow-up:
  - 이 handoff는 selected-route gate 또는 continuity check를 대체하지 않는다. 선정 이후 실제 점검은 Selected Dashboard의 recheck / readiness / provider / timeline / allocation evidence에서 이어진다.

### 2026-05-31 - Saved Final Review decisions should read as a ledger
- User request:
  - Final Review 개편 4번 작업을 진행해 달라고 승인함.
- Interpreted goal:
  - 저장된 최종 판단을 단순 table / JSON inspector가 아니라, 과거 판단을 다시 읽고 비교하는 Saved Decision Review UX로 만든다.
- Analysis result:
  - 구현 결과 saved final decision row는 summary counts, route filter, latest decision, review ledger, Summary / Dossier / Evidence Packet / Raw JSON detail tabs로 표시된다.
  - Decision Dossier export는 유지하되 자동 report write가 아니라 read-only download / preview로 남긴다.
- Follow-up:
  - 새 validation, 새 registry, approval, order, account sync, auto rebalance는 추가하지 않았다. 다음 slice는 Selected Dashboard handoff polish다.

### 2026-05-31 - Final decision record should guide the last user action
- User request:
  - Candidate Board V1 다음 단계를 진행해 달라고 승인함.
- Interpreted goal:
  - Final Review의 마지막 action인 `최종 검토 결과 기록`이 어떤 route로 저장되는지, 왜 선정 저장이 막히는지, 비선정 route는 무엇을 의미하는지 더 명확하게 만든다.
- Analysis result:
  - 구현 결과 Final Review는 Decision Record Checklist, selected-route gate badge, route별 판단 사유 / 운영 전 조건 / 다음 행동 문안을 보여준다.
  - 초기 구현에서는 blocked selected-route 후보에 gate-suggested non-select route를 보여줬지만, 이후 selection-only save 정책으로 새 비선정 row 생성은 제거하고 상태 / legacy compatibility 안내로 낮췄다.
- Follow-up:
  - 새 validation, waiver persistence, approval, order, account sync, auto rebalance는 추가하지 않았다. 정식 저장은 `SELECT_FOR_PRACTICAL_PORTFOLIO` selected-route pass에만 열리며, 다음 slice는 saved decision review UX, Selected Dashboard handoff polish, dossier/report polish, or structured waiver UI / persistence 중에서 고른다.

### 2026-05-31 - Candidate Board should guide what to review first
- User request:
  - 앞서 나눈 Final Review 5단계 개발 방향 중 2번 Candidate Board V1을 진행해 달라고 승인함.
- Interpreted goal:
  - Candidate Board를 단순 Gate 통과 후보 표가 아니라, 최종 선별 관점에서 어떤 후보를 먼저 봐야 하는지 알려주는 비교 / 우선순위 보드로 만든다.
- Analysis result:
  - 기존 Practical Validation result, investability packet, Decision Cockpit read model만 사용해 read-only review priority를 계산한다.
  - 구현 결과 Candidate Board는 select-ready / hold / blocked counts, first-review candidate, review queue, primary reason, next action을 표시하고, 후보를 select-ready -> hold / re-review -> blocked 순서로 정렬한다.
- Follow-up:
  - 이 priority는 새 투자 점수나 새 검증 기준이 아니다. 다음 slice에서는 structured waiver, dossier/report polish, saved decision review UX, or Selected Dashboard handoff polish 중 하나를 고른다.

### 2026-05-31 - Final Review should not feel like duplicate validation
- User request:
  - Decision Cockpit의 선정 / 차단 / 보류가 이전 단계 검증을 재검증하는 중복 흐름이 아닌지 우려함.
- Interpreted goal:
  - Final Review를 새 검증 실행 화면이 아니라, Practical Validation 결과를 최종 판단으로 번역하고 기록하는 화면으로 더 명확히 만든다.
- Analysis result:
  - 판정 로직은 기존 Practical Validation / investability packet / selected-route gate evidence를 읽는 해석 layer이며 새 검증을 실행하지 않는다.
  - 중복처럼 보인 원인은 상세 validation evidence table이 최종 판단 전에 길게 노출된 화면 위계였다.
  - 구현 결과 최종 판단 기록을 Decision Cockpit 바로 아래로 올리고, 상세 evidence는 read-only `Evidence Appendix`로 낮췄다.
- Follow-up:
  - Structured waiver, candidate prioritization, dossier/report polish는 별도 task로 다룬다.

### 2026-05-31 - Final Review should act as a decision cockpit
- User request:
  - Final Review 탭이 프로토타입이라 목적과 활용도가 불명확하므로, 외부 조사와 현재 흐름 분석을 바탕으로 개편 방향을 정하고 진행해 달라고 요청함.
- Interpreted goal:
  - Final Review를 검증 결과 모음이 아니라 Practical Validation Gate 통과 후보를 최종 선정 / 보류 / 거절 / 재검토로 판단하는 Decision Desk로 재구성한다.
- Analysis result:
  - Backtest는 후보 생성, Practical Validation은 검증 실행과 Gate, Final Review는 증거 기반 최종 판단, Selected Dashboard는 선정 이후 재확인으로 경계를 유지한다.
  - 첫 구현 slice는 새 저장소 / DB 변경 없이 Candidate Board와 Decision Cockpit을 추가하는 것이 가장 안전하다.
  - 구현 결과 Candidate Board는 Gate 통과 후보의 상태를 비교하고, Decision Cockpit은 selected-route state, suggested decision, Must Fix / Must Review, monitoring seed를 상세 evidence보다 먼저 보여준다.
- Follow-up:
  - 다음 Final Review slice가 필요하면 structured waiver UI, candidate prioritization rules, or dossier/report polish를 별도 task로 연다.

### 2026-05-31 - Practical Validation Save & Move fails during JSONL persistence
- User request:
  - `저장하고 Final Review로 이동` 버튼 클릭 시 `json.dumps` TypeError가 발생한다고 stack trace와 함께 원인 파악 및 수정을 요청함.
- Interpreted goal:
  - Final Review 이동 전 Practical Validation result를 append-only registry에 안정적으로 저장하게 한다.
- Analysis result:
  - latest source로 재현한 결과 raw `json.dumps`가 `Decimal` 값에서 실패했다. 최초 확인 위치는 `input_evidence.data_coverage_context.price_window_rows[].window_row_count`다.
  - DB / pandas scalar가 compact evidence에 포함될 수 있으므로 Clean V2 registry append 경계에서 JSON-safe primitive로 정규화하는 방식이 맞다.
- Follow-up:
  - validation scoring, module gate, Final Review routing은 변경하지 않는다.

### 2026-05-30 - Practical Validation source review should include the original backtest snapshot
- User request:
  - Practical Validation의 `1. 선택 후보 확인`이 CAGR / MDD / 비중만 보여줘 부족하므로 기존 백테스트 결과의 summary, equity curve, result table을 간략히 보여 달라고 요청함.
- Interpreted goal:
  - 검증 profile이나 Final Review gate 전에, Backtest Analysis에서 왜 이 후보가 넘어왔는지 원래 결과 snapshot을 먼저 확인하게 한다.
- Analysis result:
  - `selection_source`에 이미 저장된 `summary`, `result_curve`, `benchmark_curve`, `components` snapshot을 read-only로 표시하면 충분하다.
  - 새 실행이나 registry 재작성 없이 Summary / Equity Curve / Result Table / Components 탭을 추가하는 UI-only 변경으로 처리한다.
- Follow-up:
  - source snapshot이 없는 legacy row는 현재 component fallback과 안내 메시지로 처리한다.

### 2026-05-30 - Practical Validation needs a dedicated workbench shell
- User request:
  - Practical Validation 화면이 여전히 기존 Streamlit 틀을 벗어나지 못하고 상용 프로그램보다 운영툴처럼 보인다고 지적하고, 진짜 시각 개편 진행을 승인함.
- Interpreted goal:
  - 검증 로직과 gate 정책은 유지하되, 화면 레이어를 전용 product shell로 분리해 module gate, evidence board, action board의 위계를 더 분명히 보여준다.
- Analysis result:
  - `app/web/backtest_practical_validation_components.py`를 추가해 Command Center, section header, card grid, step rail, alert panel을 Practical Validation 전용으로 분리했다.
  - Practical Validation render는 `st.container(border=True)` 중심 구획을 제거하고 전용 workbench shell로 후보, profile, replay, gate, evidence, action, save flow를 배치한다.
- Follow-up:
  - 현재 변경은 UI shell only다. light theme 대비나 더 큰 design system화가 필요하면 별도 UX polish task로 연다.

### 2026-05-30 - Backtest Analysis Stage 1 is closed as candidate-source creation
- User request:
  - 1단계 Backtest는 여기까지 진행하면 될 것 같으니, 이번 세션에서 작업한 내용과 최종 수정 상태를 문서로 업데이트하고 정리해 달라고 요청함.
- Interpreted goal:
  - Backtest Analysis를 최종 투자 판단이나 운영 판단이 아니라, 단일 전략 / Portfolio Mix 후보 source를 만들고 1차 readiness 통과 시 Practical Validation으로 보내는 단계로 닫는다.
- Analysis result:
  - Session closeout doc added at `docs/flows/BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md`.
  - Backtest Analysis now has explicit boundaries: Real-Money is first-pass readiness, Practical Validation handoff is gated, Portfolio Mix Builder creates one weighted mix candidate, and no memo / preset / live approval / order / auto rebalance behavior is added.
  - Remaining items are parked as follow-up candidates: separate read-only candidate comparison, saved mix inspector polish, weighted mix cost / turnover aggregation, and profile-specific thresholds.
- Follow-up:
  - Next product work should move to Practical Validation / Final Review review or a newly approved research / phase / task, not keep expanding Backtest Analysis 1단계 without a new explicit scope.

### 2026-05-30 - Portfolio Mix Builder post-run UX is summary-first
- User request:
  - Portfolio Mix Builder에서 mix 실행 후 상단 result UI가 혼잡하고, 기존 보수적 UI 패턴이 반복되어 완성도가 떨어진다고 지적함.
- Interpreted goal:
  - 계산 로직은 유지하되, Portfolio Mix Builder를 "여러 component를 하나의 mix 후보로 만드는 작업 공간"처럼 읽히게 정보 위계와 next action을 정리한다.
- Analysis result:
  - Component 실행 결과는 card overview와 `요약 / 차트 / 진단 / 상세` 4개 tab으로 재구성하고, 원본 summary table / meta / criteria는 접힘 상세로 낮춘다.
  - 화면 flow strip은 `Component 실행 -> Weight 구성 -> Mix 후보 판단 -> Practical Validation`을 보여주며, mix 후보 판단은 handoff 가능 여부와 blocker를 먼저 표시한다.
  - 이 변경은 UI/UX 위계 정리이며, backtest 계산, DB schema, JSONL registry, saved setup policy, live approval, order, auto rebalance는 바꾸지 않는다.
- Follow-up:
  - User review should confirm whether the post-run result now feels like "비중을 정하기 위한 재료 확인" and whether the weight builder / mix 후보 판단까지 자연스럽게 이어지는지 확인한다.

### 2026-05-30 - Portfolio Mix Builder replaces mixed compare/build flow
- User request:
  - Backtest Analysis의 `Compare & Portfolio Builder`가 비교와 조합을 섞고 있어, 여러 전략을 하나의 mix 후보로 만드는 화면으로 재정의하고 후보 비교는 별도 위치를 검토해 달라고 요청함.
- Interpreted goal:
  - Backtest Analysis는 단일 후보 또는 Portfolio Mix 후보를 만들어 2차 Practical Validation으로 보내는 1차 후보 생성 단계로 고정한다.
- Analysis result:
  - Visible mode is now `Portfolio Mix Builder`; legacy `Compare & Portfolio Builder` route remains compatible.
  - Component runs remain as evidence for weight selection, but the handoff button evaluates and sends the weighted mix as one Clean V2 source.
  - Mix handoff requires mix result, 100% / multi-component weight discipline, component data trust, and component first-stage readiness with no hard blocker.
  - Candidate-to-candidate read-only comparison is intentionally left as a future separate tool rather than kept inside the mix builder.
- Follow-up:
  - User review should run a GTAA + Equal Weight mix and confirm that the screen reads as "여러 전략을 하나의 후보로 만들기" rather than "개별 전략 비교 후 하나 고르기".

### 2026-05-30 - Practical Validation handoff requires first-stage readiness
- User request:
  - `검증 후보로 보내기`는 다음 단계로 넘기는 버튼이므로 1차 후보 판단을 통과했다는 의미로 읽히게 하고, 통과하지 못하면 비활성화와 근거 표시가 필요하다고 요청함.
- Interpreted goal:
  - Backtest Analysis의 handoff 버튼을 단순 저장 버튼이 아니라 `Candidate Readiness` gate를 통과한 결과만 2차 `Practical Validation`으로 넘기는 진입 버튼으로 정리한다.
- Analysis result:
  - Handoff enablement now follows `can_move_to_compare`: Promotion not hold, no execution source blocker, no validation source blocker.
  - Disabled state shows concise blocker reasons and the handoff area displays a status card with Promotion / 실행 원천 / 검증 원천 상태.
  - The handoff remains a Clean V2 source registration path only; it does not add live approval, order, account sync, auto rebalance, or a new storage model.
- Follow-up:
  - User review should confirm that the button now feels like "1차 후보 판단 통과 후 2차 실전성 검증 진입" rather than a generic save action.

### 2026-05-30 - Backtest Real-Money readiness now uses source checks only
- User request:
  - Backtest 1차 Real-Money 지표가 실제로 유효한 검증인지 재검토하고, 필요하면 추가 / 수정 / 삭제하되 억지로 바꾸지는 말아 달라고 요청함.
- Interpreted goal:
  - 기존 지표군은 유지하되, 후속 단계인 probation / monitoring 의미가 1차 점수에 섞이지 않도록 scoring / wording / cost display 경계를 정리한다.
- Analysis result:
  - `Execution Preview`는 benchmark, liquidity, validation, guardrail, ETF operability, price freshness, rolling, split-period 같은 source checks만 평가한다.
  - `Candidate Readiness`는 `Promotion`, execution source blockers, validation source blockers 기준으로 계산하고, turnover / cost는 holdings 기반 추정 여부를 같이 표시한다.
  - Backtest의 전후반 구간 점검은 `Split-Period Check`로 낮춰 표시하며, formal OOS / walk-forward / regime validation은 Practical Validation 이후 evidence가 담당한다.
- Follow-up:
  - User review should focus on whether Real-Money의 현재 판단이 "다음 검증으로 넘겨도 되는가"라는 1차 질문에만 답하는지 확인한다.

### 2026-05-30 - Backtest Real-Money is first-pass readiness only
- User request:
  - Backtest 단계에서 `Probation / Monitoring / Deployment`까지 검증하는 것은 Practical Validation / Final Review / Selected Dashboard 역할과 겹치므로 과한 부분을 빼거나 분리하자는 방향을 승인함.
- Interpreted goal:
  - Backtest Analysis의 Real-Money 탭은 후보를 다음 검증으로 넘겨도 되는지 보는 1차 readiness 화면으로 고정하고, 후속 관찰 / 운영 / 최종 선택처럼 보이는 문구를 낮춘다.
- Analysis result:
  - User-facing Backtest / Compare / History surfaces now show `Suggested Route`, `Next Validation Focus`, and `Execution Preview`.
  - Internal legacy metadata remains compatible, but Backtest Analysis does not start paper observation, monitoring, deployment, broker approval, order, account sync, or auto rebalance.
- Follow-up:
  - User review should verify that Backtest Analysis reads as candidate screening, while Practical Validation / Final Review own the actual investability evidence and final decision.

### 2026-05-30 - Real-Money shortlist meaning is absorbed into Promotion
- User request:
  - Real-Money의 후보 shortlist가 사실상 Promotion의 추천 경로 역할이라면 독립 기능처럼 보이지 않게 낮추자는 방향을 승인함.
- Interpreted goal:
  - Backtest Analysis의 Real-Money 탭에서 핵심 질문을 "Promotion 결과상 다음 단계로 넘길 수 있는가?"로 고정하고, shortlist 값을 `Promotion Suggested Route`로 표시한다.
- Analysis result:
  - `shortlist_status` / `shortlist_next_step` metadata is still useful for compatibility, but user-facing UX should not present it as a separate validation stage.
  - The change is UI / wording only; runtime calculation, JSONL registry, user memo / preset storage, broker approval, order, and auto rebalance remain unchanged.
- Follow-up:
  - User review should focus on whether Promotion, Probation, Deployment, and Validation now read as one coherent Real-Money decision flow.

### 2026-05-30 - Phase 13 closes the first hardening cycle
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 13의 13-6으로 13-1~13-5 산출물을 묶고 final QA를 수행한 뒤 1차 hardening cycle을 안전한 범위에서 closeout한다.
- Analysis result:
  - 1차 cycle은 lifecycle / survivorship, cost / liquidity realism, temporal validation, construction risk, selected monitoring evidence를 하나의 investability evidence workflow로 강화했다.
  - 이 완료 선언은 broker-grade trading readiness, live approval, order, account sync, auto rebalance, production alerting, full optimizer 구현을 뜻하지 않는다.
  - Storage boundary remains compact: DB-backed full evidence, workflow JSONL compact evidence, saved reusable setup, generated artifacts, and reports keep separate roles.
- Follow-up:
  - 다음 작업은 자동으로 열지 않는다. 사용자가 `phase13-residual-risk-carry-forward-v1/CARRY_FORWARD_MATRIX.md`에서 2차 cycle 방향을 선택하면 새 phase로 시작한다.

### 2026-05-30 - Phase 13 residual risks separated for final closeout
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 13의 13-5로 Phase 8~12와 Phase 13 13-1~13-4에서 남은 한계를 current limitation, second-cycle candidate, explicit out-of-scope로 분리한다.
- Analysis result:
  - 1차 cycle은 investability evidence workflow 개선으로 closeout할 수 있지만 broker-grade trading / account reconciliation / optimizer / production monitoring system으로 표현하면 안 된다.
  - Key carry-forward candidates are historical membership coverage expansion, broker-grade execution realism design, weighted mix cost / turnover aggregation, profile-specific thresholds, formal validation statistics, construction taxonomy / covariance, provider operations hardening, and selected replay contract hardening.
  - Live approval, broker orders, account sync, tax-lot handling, auto rebalance, paid source adoption, user memo / preset expansion, and automatic monitoring log append remain explicit first-cycle out-of-scope items.
- Follow-up:
  - 다음 task는 `phase13-integrated-qa-final-closeout`로 final QA와 1차 hardening cycle closeout summary를 작성한다.

### 2026-05-30 - Phase 13 docs and runbooks align with current boundaries
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 13의 13-4로 13-1 inventory, 13-2 gate QA, 13-3 storage audit 결과를 durable docs와 runbook에 맞춘다.
- Analysis result:
  - Current user flow docs now identify `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` as the selected dashboard source, while legacy V1 remains history / compatibility.
  - Storage docs clarify runtime-defined JSONL paths, DB-backed full evidence, workflow compact evidence, saved setup, generated artifacts, and selected monitoring read-only boundaries.
  - Added a reusable Phase Closeout QA runbook for future phase/task verification and artifact hygiene.
- Follow-up:
  - 다음 task는 `phase13-residual-risk-carry-forward-v1`로 남은 limitations, second-cycle candidates, and out-of-scope broker-grade items를 분리한다.

### 2026-05-30 - Phase 13 storage boundary audit finds no drift
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 13의 13-3으로 DB-backed data, workflow JSONL compact evidence, saved setup, run artifact, and selected monitoring read-only boundaries를 감사한다.
- Analysis result:
  - Lifecycle / survivorship collectors write DB-backed `finance_meta.nyse_symbol_lifecycle` evidence with `registry_write: False`.
  - Practical Validation / Final Review persistence remains compact workflow handoff / validation / decision evidence, while saved portfolio rows remain reusable setup rather than approval or monitoring evidence.
  - Selected Dashboard read models expose no DB write, registry write, monitoring log auto-write, live approval, order instruction, or auto rebalance behavior. No task-created registry / saved / run history / run artifact / Playwright output drift was found.
- Follow-up:
  - 다음 task는 `phase13-docs-runbook-alignment-v1`로 13-1 inventory, 13-2 QA matrix, and 13-3 storage audit를 durable docs / runbooks / roadmap에 맞춘다.

### 2026-05-30 - Phase 13 gate validation QA finds no immediate code defect
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 13의 13-2로 Practical Validation / Final Review / Selected Dashboard gate와 severity consistency를 확인한다.
- Analysis result:
  - `build_investability_gate_policy()` and `build_selected_route_gate()` consistently block selected route for critical `NOT_RUN`, `NEEDS_INPUT`, `BLOCKED`, and critical `REVIEW` evidence.
  - Selected Dashboard post-selection routes surface continuity, recheck, provider, review signal, and allocation drift gaps as read-only operations evidence without live approval, order, monitoring log auto-write, or auto rebalance.
  - Full `tests.test_service_contracts` passed, 126 tests. No immediate code defect was identified.
- Follow-up:
  - 다음 task는 `phase13-storage-data-boundary-audit-v1`로 DB-backed data, workflow JSONL compact evidence, saved setup, monitoring log, report, and generated artifact boundary를 확인한다.

### 2026-05-29 - Phase 13 inventory sets the QA source map
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 13의 13-1로 Phase 8~12 1차 hardening cycle이 어떤 약점을 줄였고 무엇을 남겼는지 하나의 inventory로 정리한다.
- Analysis result:
  - Phase 8~12는 lifecycle / survivorship, cost / liquidity realism, temporal validation, construction risk, selected monitoring evidence를 순차적으로 보강했다.
  - 현재 제품은 단순 backtest exploration보다 investability evidence workflow에 가까워졌지만, broker-grade execution, account reconciliation, optimizer, production alerting, auto rebalance는 아직 구현된 기능이 아니다.
  - No new JSONL registry, user memo / preset storage, monitoring log auto-write, account sync, approval, order, or auto rebalance behavior was added.
- Follow-up:
  - 다음 task는 `phase13-gate-validation-qa-matrix-v1`로 Practical Validation / Final Review / Selected Dashboard gate와 severity consistency를 확인한다.

### 2026-05-29 - Actual allocation drift remains session-only evidence
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 12의 12-5로 optional Actual Allocation / drift check가 저장, 주문, 자동 리밸런싱 기능처럼 보이지 않도록 경계를 명확히 한다.
- Analysis result:
  - Existing Dashboard behavior was already session-only, but runtime boundary fields were not explicit enough.
  - Added `selected_allocation_drift_evidence_boundary_v1` with DB / registry / monitoring log / raw input / alert persistence and account / broker / order / auto rebalance all disabled.
  - Breached drift now means manual review signal only; Dashboard action is labeled `Reflect Session Signal`.
- Follow-up:
  - 다음 task는 `decision-dossier-continuity-operations-v1`로 Decision Dossier, Continuity, Timeline, Review Signals source consistency를 정리한다.

### 2026-05-29 - Selected monitoring source map chooses recheck readiness / freshness first
- User request:
  - Phase 12 작업 진행을 요청함.
- Interpreted goal:
  - Phase 12의 첫 task로 current Selected Portfolio Dashboard / Final Review / runtime monitoring evidence source map과 gap을 확인한다.
- Analysis result:
  - Selected Dashboard는 Final Review V2 decision row를 canonical source로 읽고, readiness / freshness / provider / timeline / comparison / drift / dossier evidence를 read-only로 제공한다.
  - 주요 gap은 Performance Recheck / symbol freshness가 Current Candidate Registry replay contract에 의존한다는 점, readiness와 symbol freshness가 policy상 분리되어 있다는 점, Review Signals와 Recheck Comparison이 CAGR / MDD / benchmark spread threshold를 중복 계산한다는 점이다.
  - 새 JSONL registry, automatic monitoring log append, user memo, preset, account integration, approval, order, auto rebalance는 추가하지 않는다.
- Follow-up:
  - 다음 task는 `recheck-readiness-freshness-contract-v1`로 Final Review V2 selected row, replay contract, DB latest market date, symbol freshness를 하나의 operations preflight contract로 정리한다.

### 2026-05-29 - Phase 12 opens for selected monitoring / recheck operations
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 11 closeout 이후 다음 hardening target인 selected monitoring / recheck operations를 공식 phase로 연다.
- Analysis result:
  - Phase 12 board를 `.aiworkspace/note/finance/phases/active/phase12-selected-monitoring-recheck-operations/`에 생성했다.
  - 이번 phase는 Final Review 선정 이후에도 recheck readiness, symbol freshness, provider evidence, timeline, review signals, recheck comparison, optional allocation drift, continuity evidence가 재검토 필요 상태를 숨기지 않도록 정리하는 방향이다.
  - 새 JSONL registry, automatic monitoring log append, user memo, preset, account integration, approval, order, auto rebalance는 추가하지 않는다.
- Follow-up:
  - 다음 task는 `selected-monitoring-source-map-v1`로 current Selected Portfolio Dashboard / Final Review / runtime source map과 gap을 확인한다.

### 2026-05-29 - Phase 11 construction risk controls close out
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 11의 마지막 task로 construction risk controls 전체를 통합 검증하고 완료 상태로 정리한다.
- Analysis result:
  - Phase 11 integrated QA passed: service / web compile, full service contracts 112 tests, UI / engine boundary checker, finance refinement hygiene, and diff check.
  - Phase 11 closeout summary was added under `phases/done/`.
  - This phase strengthened portfolio construction risk evidence and selected-route gate policy without adding new JSONL registry, memo, preset, approval, order, or auto rebalance behavior.
- Follow-up:
  - Next hardening target is Phase 12 selected monitoring / recheck operations. Start with `phase12-board-open`.

### 2026-05-29 - Construction risk gate policy feeds selected-route evidence
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 11의 11-5로 세 construction risk audit route와 row-level non-PASS evidence를 Final Review selected-route gate policy에 연결한다.
- Analysis result:
  - `construction_risk`, `risk_contribution`, `component_role_weight` are now first-class critical gate groups.
  - `NEEDS_INPUT` / `BLOCKED` blocks selected-route, and `REVIEW` requires hold / re-review before selection.
  - Failing row criteria are merged into gate policy evidence without adding JSONL registry, user memo, preset, approval, order, or auto rebalance behavior.
- Follow-up:
  - 다음 task는 `phase11-integrated-qa-closeout`로 Phase 11 전체 compile / service contract / boundary / hygiene / docs closeout을 수행한다.

### 2026-05-29 - Component role / weight audit V1 covers role discipline
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 11의 11-4로 component role / target weight / validation profile evidence를 read-only construction risk contract로 묶는다.
- Analysis result:
  - `component_role_weight_audit_v1` now reads explicit proposal role source coverage, target weights, profile-aware max weight, role concentration, profile intent fit, weight reason, and storage boundary.
  - Missing or partial role metadata does not become `PASS`; inferred or single-component role evidence remains `REVIEW` or `NEEDS_INPUT`.
  - Practical Validation and Final Review display the audit, and final decision snapshots / evidence rows preserve it without adding role preset, user memo, saved setup, approval, order, or auto rebalance behavior.
- Follow-up:
  - 다음 task는 `construction-risk-gate-policy-v1`로 세 construction risk audit route와 row-level non-PASS evidence를 selected-route gate policy에 연결한다.

### 2026-05-29 - Risk contribution audit V1 covers correlation / risk contribution
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 11의 11-3으로 component return correlation / risk contribution evidence를 read-only construction risk contract로 묶는다.
- Analysis result:
  - `risk_contribution_audit_v1` now reads component return matrix coverage, average / max correlation, max risk contribution proxy, Robustness Lab drop-one dependency, and storage boundary.
  - Missing component matrix or missing drop-one evidence does not become `PASS`; DB price proxy / mixed source evidence remains `REVIEW`.
  - Practical Validation and Final Review display the audit, and final decision snapshots / evidence rows preserve it without adding JSONL registry, user memo, approval, order, or auto rebalance behavior.
- Follow-up:
  - 다음 task는 `component-role-weight-discipline-v1`로 role source와 profile-aware weight discipline을 분리한다.

### 2026-05-29 - Construction risk audit V1 covers concentration / overlap / exposure
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 11의 11-2로 provider look-through evidence를 read-only Construction Risk Audit contract로 묶는다.
- Analysis result:
  - `construction_risk_audit_v1` now reads component max weight, provider holdings / exposure coverage, top holding, top overlap, dominant asset, and unknown exposure.
  - Missing or partial provider holdings / exposure does not become `PASS`; it remains `NEEDS_INPUT` or `REVIEW`.
  - Practical Validation and Final Review display the audit, and final decision snapshots preserve it without adding JSONL registry, user memo, approval, order, or auto rebalance behavior.
- Follow-up:
  - 다음 task는 `correlation-risk-contribution-contract-v1`로 component return correlation / risk contribution evidence를 construction risk 관점으로 분리한다.

### 2026-05-29 - Phase 11 source map chooses concentration / overlap first
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 11의 첫 task로 current construction risk evidence source map과 gap을 확인한다.
- Analysis result:
  - Practical Validation already emits concentration / overlap / exposure and correlation / risk contribution diagnostics.
  - Provider look-through board already emits holdings coverage, exposure coverage, top holding, top overlap, dominant asset, and unknown exposure as compact evidence.
  - Robustness Lab already has drop-one and weight tilt dependency evidence, but Final Review has no explicit construction risk gate group yet.
  - 새 JSONL registry, user memo, preset, raw holdings artifact, approval, order, auto rebalance는 추가하지 않는다.
- Follow-up:
  - 다음 task는 `concentration-overlap-exposure-contract-v1`로 기존 provider look-through evidence를 read-only Construction Risk Audit contract로 묶는다.

### 2026-05-29 - Phase 11 opens for portfolio construction risk controls
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 10 closeout 이후 다음 hardening target인 portfolio construction risk controls를 공식 phase로 연다.
- Analysis result:
  - Phase 11 board를 `.aiworkspace/note/finance/phases/active/phase11-portfolio-construction-risk-controls/`에 생성했다.
  - 이번 phase는 concentration, overlap, correlation, risk contribution, component role / weight discipline이 selected-route 판단에서 숨지 않도록 만드는 방향이다.
  - 새 JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않는다.
- Follow-up:
  - 다음 task는 `construction-risk-source-map-v1`로 current Practical Validation / Look-through / Robustness Lab / Final Review gate source map과 gap을 확인한다.

### 2026-05-29 - Phase 10 validation efficacy hardening closes
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 10의 walk-forward / OOS / regime validation work를 통합 검증하고 closeout한다.
- Analysis result:
  - Phase 10 integrated QA passed: targeted service / loader compile, full service contracts 98 tests, UI / engine boundary checker, finance refinement hygiene, and diff check.
  - Phase 10 closeout summary was added under `phases/done/`.
  - This phase strengthened Validation Efficacy and selected-route gate evidence without adding new JSONL registry, memo, preset, approval, order, or auto rebalance behavior.
- Follow-up:
  - Next hardening target is Phase 11 portfolio construction risk controls. Start with `phase11-board-open`.

### 2026-05-29 - Validation efficacy temporal gaps become selected-route gate evidence
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 10의 10-5로 walk-forward / OOS / regime gap이 Final Review selected-route gate에서 blocker 또는 review-required 근거로 드러나게 한다.
- Analysis result:
  - `build_investability_gate_policy()`가 Validation Efficacy Audit non-PASS row를 `validation_efficacy` gate policy group에 병합한다.
  - `REVIEW` temporal row는 hold / re-review 요구이며, `NEEDS_INPUT` / `BLOCKED` temporal row는 selected-route blocker다.
  - 이 변경은 기존 investability packet / selected-route gate를 재사용하는 read-only evidence 정렬이며 새 JSONL registry, user memo, preset, approval, order, auto rebalance를 추가하지 않는다.
- Follow-up:
  - 다음 task는 `phase10-integrated-qa-closeout`으로 Phase 10 전체 compile / service contracts / boundary / hygiene 검증과 closeout을 수행한다.

### 2026-05-29 - Regime split validation becomes compact audit evidence
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 10의 10-4로 DB-backed macro history를 사용한 historical regime split evidence를 Practical Validation과 Final Review 판단 경로에 연결한다.
- Analysis result:
  - `app/services/backtest_temporal_validation.py`에 `build_regime_split_validation()`을 추가해 VIX / yield curve / credit spread 기반 monthly regime bucket별 portfolio / benchmark excess와 drawdown gap을 compact evidence로 계산한다.
  - Practical Validation result가 `regime_split_validation` evidence를 가지며, Validation Efficacy Audit이 `Regime split validation` row를 읽는다.
  - missing / short / proxy-only macro evidence는 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- Follow-up:
  - 다음 task는 `validation-efficacy-gate-policy-refinement-v2`로 temporal / OOS / regime gap이 selected-route gate policy에 미치는 영향을 정리한다.

### 2026-05-29 - OOS holdout validation becomes compact audit evidence
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 10의 10-3으로 in-sample / out-sample holdout evidence를 Practical Validation과 Final Review 판단 경로에 연결한다.
- Analysis result:
  - `app/services/backtest_temporal_validation.py`에 `build_oos_holdout_validation()`을 추가해 benchmark-aligned OOS excess, split deterioration, out-sample drawdown gap을 compact evidence로 계산한다.
  - Practical Validation result가 `oos_holdout_validation` evidence를 가지며, Validation Efficacy Audit이 `OOS holdout validation` row를 읽는다.
  - missing / short / proxy-only evidence는 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- Follow-up:
  - 다음 task는 `regime-split-validation-v1`로 DB / macro loader source를 기준으로 historical regime split evidence를 추가한다.

### 2026-05-29 - Walk-forward temporal validation becomes compact audit evidence
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 10의 10-2로 benchmark-aligned walk-forward / rolling split evidence를 Practical Validation과 Final Review 판단 경로에 연결한다.
- Analysis result:
  - `app/services/backtest_temporal_validation.py`를 추가해 rolling portfolio return, benchmark return, excess return, strategy MDD, benchmark MDD, drawdown gap을 compact evidence로 계산한다.
  - Practical Validation result가 `temporal_validation` evidence를 가지며, Validation Efficacy Audit이 `Walk-forward temporal validation` row를 읽는다.
  - missing / short / proxy-only evidence는 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- Follow-up:
  - 다음 task는 `oos-holdout-validation-contract-v1`로 in-sample / out-sample holdout evidence를 분리한다.

### 2026-05-29 - Phase 10 source map chooses walk-forward contract first
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 10의 첫 task로 current Practical Validation / Robustness Lab / runtime replay / Final Review gate source map과 gap을 확인한다.
- Analysis result:
  - Practical Validation에는 runtime replay, embedded source curve, component curve, DB price proxy를 읽는 curve source hierarchy가 이미 있다.
  - Runtime backtest에는 benchmark-aligned rolling / OOS metadata가 있지만, Validation Efficacy Audit과 Final Review gate에 explicit temporal validation row로 연결되지는 않았다.
  - Robustness Lab rolling evidence는 존재하지만 benchmark-relative rolling excess row가 부족하다.
- Follow-up:
  - 다음 task는 `walkforward-split-contract-v1`로 compact benchmark-aligned walk-forward / rolling validation contract를 먼저 구현한다.

### 2026-05-29 - Phase 10 opens for walk-forward / OOS / regime validation
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 9 closeout 이후 다음 hardening target인 walk-forward / out-of-sample / regime split validation을 공식 phase로 연다.
- Analysis result:
  - Phase 10 board를 `.aiworkspace/note/finance/phases/active/phase10-walkforward-oos-regime-validation/`에 생성했다.
  - 이번 phase는 전체기간 백테스트 성과를 과대 신뢰하지 않도록 OOS / walk-forward / regime evidence를 Practical Validation과 Final Review gate에 연결하는 방향이다.
  - 새 JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않는다.
- Follow-up:
  - 다음 task는 `walkforward-oos-source-map-v1`로 current Practical Validation / Robustness Lab / replay / result metadata source map과 gap을 확인한다.

### 2026-05-29 - Phase 9 cost / slippage / liquidity realism closes
- User request:
  - Phase 9 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 9의 cost / turnover / net curve / liquidity / sensitivity / gate policy 변경을 통합 검증하고 closeout한다.
- Analysis result:
  - Phase 9 integrated QA passed: touched service compile, UI / engine boundary checker, full service contracts 90 tests, refinement hygiene, and diff check.
  - Phase 9 closeout summary was added under `phases/done/`.
  - This phase strengthened Backtest Realism and selected-route evidence gates without adding new JSONL registry, memo, preset, approval, order, or auto rebalance behavior.
- Follow-up:
  - Next hardening target is Phase 10 walk-forward / out-of-sample / regime split validation.

### 2026-05-29 - Backtest realism gate policy surfaces row-level gaps
- User request:
  - Phase 9 다음 작업 진행을 요청함.
- Interpreted goal:
  - Phase 9에서 추가한 Backtest Realism row-level gap이 Final Review selected-route gate에서 의도한 severity와 evidence로 보이게 한다.
- Analysis result:
  - `build_investability_gate_policy()`가 failing Backtest Realism Audit row criteria를 `backtest_realism` policy evidence에 병합한다.
  - cost / slippage sensitivity와 liquidity row-level REVIEW는 review-required, NEEDS_INPUT은 blocker severity로 고정했다.
  - 이 작업은 read-only gate evidence refinement이며 새 JSONL, memo, preset, waiver persistence, approval, order, auto rebalance를 추가하지 않는다.
- Follow-up:
  - 다음 task는 `phase9-integrated-qa-closeout`으로 Phase 9 전체 통합 검증과 Phase 10 handoff를 정리한다.

### 2026-05-29 - Cost / slippage sensitivity requires explicit evidence
- User request:
  - Phase 9 다음 작업 진행을 요청함.
- Interpreted goal:
  - Backtest Realism Audit이 단일 transaction cost bps나 일반 robustness sensitivity만으로 cost / slippage robustness를 PASS 처리하지 않게 한다.
- Analysis result:
  - `cost_slippage_sensitivity_contract_v1`과 `Cost / slippage sensitivity evidence` row를 추가했다.
  - explicit cost / slippage sensitivity evidence만 PASS 후보이고, generic robustness-only sensitivity는 REVIEW, cost / net curve baseline missing은 NEEDS_INPUT으로 남긴다.
  - 이 작업은 기존 validation payload를 읽는 read-only audit이며 새 JSONL, memo, preset, raw artifact, DB schema, provider fetch를 추가하지 않는다.
- Follow-up:
  - 다음 task는 `backtest-realism-gate-policy-refinement-v1`로 selected-route gate severity를 Phase 9 보강 후 기준에 맞게 고정한다.

### 2026-05-29 - Liquidity capacity evidence requires fresh official provider proof
- User request:
  - Phase 9 다음 단계 진행을 요청함.
- Interpreted goal:
  - Backtest Realism Audit이 liquidity / capacity evidence를 legacy `PASS` 문자열이 아니라 provider coverage, freshness, source strength, capacity metric으로 판단하게 한다.
- Analysis result:
  - Provider operability context에 compact capacity metrics를 추가했다.
  - Backtest Realism Audit에 `liquidity_capacity_contract_v1`을 추가해 fresh official actual evidence는 PASS 후보로 보고, stale / partial / bridge-proxy / legacy pass-only evidence는 REVIEW 또는 NEEDS_INPUT으로 남긴다.
  - 이 작업은 기존 Ingestion -> DB -> Loader -> UI 흐름만 읽으며 새 JSONL, memo, preset, DB schema, UI direct fetch를 추가하지 않는다.
- Follow-up:
  - 다음 task는 `cost-slippage-sensitivity-audit-v1`로 cost / slippage sensitivity evidence 공백을 read-only audit으로 분리한다.

### 2026-05-29 - Net cost curve proof separates applied cost from measurable impact
- User request:
  - Phase 9 다음 단계 진행을 요청함.
- Interpreted goal:
  - cost application proof와 turnover evidence가 실제 net result curve에 연결됐는지 더 직접적으로 확인한다.
- Analysis result:
  - `cost_application_status=applied_to_result_curve`만으로는 measurable cost impact를 증명하기 부족했다.
  - Runtime metadata, candidate/history snapshot, Practical Validation source, Backtest Realism Audit에 compact `net_cost_curve_contract_v1`을 연결했다.
  - measurable gross-net delta와 positive estimated-cost rows는 PASS 후보, zero-cost / turnover 미추정 / legacy flag only / missing proof는 REVIEW 또는 NEEDS_INPUT으로 해석한다.
- Follow-up:
  - 다음 task는 `liquidity-capacity-evidence-v1`로 DB provider / price 기반 liquidity와 capacity evidence를 강화한다.

### 2026-05-29 - Turnover evidence separates holdings-derived estimates from cadence-only
- User request:
  - Phase 9 다음 단계 진행을 요청함.
- Interpreted goal:
  - 거래비용 realism이 turnover 근거에 의존하므로, actual estimate와 cadence-only evidence를 분리한다.
- Analysis result:
  - Runtime turnover estimate는 holdings delta 기반이지만, holdings column이 없을 때도 audit이 강한 근거처럼 읽을 수 있는 공백이 있었다.
  - `turnover_evidence_contract_v1`을 runtime metadata, source snapshot, Backtest Realism Audit에 연결했다.
  - holdings-derived estimate는 PASS 후보, legacy estimate / cadence-only는 REVIEW, missing은 NEEDS_INPUT으로 해석한다.
- Follow-up:
  - 다음 task는 `net-cost-curve-application-v1`로 gross / net cost result curve proof를 더 명확히 연결한다.

### 2026-05-29 - Cost model source contract distinguishes assumption from applied cost
- User request:
  - Phase 9 다음 단계 진행을 요청함.
- Interpreted goal:
  - Backtest Realism Audit이 transaction cost bps를 단순 가정과 실제 result curve 적용 증거로 구분하게 한다.
- Analysis result:
  - `_apply_transaction_cost_postprocess`는 이미 net `Total Balance` / `Total Return`을 만들고 있었지만, Practical Validation source snapshot이 그 적용 증거를 명시적으로 보존하지 못했다.
  - Runtime metadata, source snapshot, Backtest Realism Audit에 compact `cost_model_source_contract_v1` 경계를 추가했다.
  - 비용 bps만 있고 application proof가 없으면 `Transaction cost model` row는 `REVIEW`다.
- Follow-up:
  - 다음 task는 `turnover-rebalance-evidence-v1`로 turnover estimate와 cadence-only evidence를 더 분리한다.

### 2026-05-29 - Phase 9 opens for cost / liquidity realism
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 8 closeout 이후 1차 hardening cycle의 다음 단계인 cost / slippage / turnover / liquidity realism을 공식 phase로 연다.
- Analysis result:
  - Phase 9 board를 `.aiworkspace/note/finance/phases/active/phase9-cost-slippage-liquidity-realism/`에 생성했다.
  - 현재 Backtest Realism Audit은 cost / turnover / liquidity row를 갖고 있으나, cost assumption과 net-curve-applied proof를 더 분리해야 한다.
  - Phase 9는 새 JSONL / memo / preset 저장이 아니라 existing metadata, DB provider / price snapshot, compact audit evidence를 우선 사용한다.
- Follow-up:
  - 다음 task는 `cost-model-source-contract-review-v1`로 current runtime / validation / audit cost source contract를 먼저 정리한다.

### 2026-05-29 - Phase 8 lifecycle evidence hardening closes
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Phase 8 전체 lifecycle evidence path를 통합 검증하고 closeout / Phase 9 handoff를 정리한다.
- Analysis result:
  - Phase 8 closeout summary를 `.aiworkspace/note/finance/phases/done/phase8-investability-data-evidence-expansion.md`에 추가했다.
  - lifecycle schema / collectors / loader / ingestion wrapper / Data Coverage Audit compile check와 full service contracts가 통과했다.
  - Phase 8은 complete이며, complete free historical membership feed는 residual risk로 남긴다.
- Follow-up:
  - 다음 hardening target은 Phase 9 cost / slippage / turnover / liquidity realism이다.

### 2026-05-28 - Lifecycle audit scoring separates evidence strength
- User request:
  - Phase 8 다음 작업 진행을 요청함.
- Interpreted goal:
  - Data Coverage Audit에서 lifecycle evidence가 어떤 종류의 근거인지 source semantics 기준으로 분리해 보여준다.
- Analysis result:
  - `app/services/backtest_data_coverage_audit.py`가 current snapshot, SEC identity cross-check, computed partial, actual coverage, actual non-covering, delisting actual symbol metrics를 분리한다.
  - Universe / listing evidence와 Survivorship / delisting control row는 partial evidence class를 evidence string에 표시한다.
  - `coverage_status=actual` requested-period coverage가 없으면 partial evidence는 계속 REVIEW다.
- Follow-up:
  - 다음 task는 `phase8-integrated-qa-closeout`으로 Phase 8 전체 lifecycle evidence path를 통합 검증하고 Phase 9 handoff를 정리한다.

### 2026-05-28 - Computed snapshot lifecycle remains partial evidence
- User request:
  - Phase 8 다음 작업 진행을 요청함.
- Interpreted goal:
  - existing current snapshot lifecycle rows를 반복 관찰 근거로 요약하되, absence / disappearance를 delisting proof로 과대 해석하지 않는다.
- Analysis result:
  - `finance/data/computed_lifecycle.py` collector와 `run_collect_computed_snapshot_lifecycle()` job wrapper를 추가했다.
  - computed row는 `source_type=computed_from_snapshots`, `coverage_status=partial`, `event_type=historical_membership`로 저장된다.
  - Data Coverage Audit은 lifecycle row가 requested period를 덮더라도 `coverage_status=actual`이 아니면 survivorship PASS로 보지 않는다.
- Follow-up:
  - 다음 task는 `lifecycle-audit-scoring-v1`로 partial snapshot / identity cross-check / computed partial / actual evidence를 audit scoring에서 더 분명히 분리한다.

### 2026-05-28 - SEC CIK exchange crosscheck becomes DB lifecycle identity evidence
- User request:
  - Phase 8 다음 작업 진행을 요청함.
- Interpreted goal:
  - SEC current CIK / ticker / exchange association을 lifecycle identity 보조 evidence로 DB에 연결한다.
- Analysis result:
  - `finance/data/sec_company_tickers.py` collector와 `run_collect_sec_company_ticker_crosscheck()` job wrapper를 추가했다.
  - SEC `company_tickers_exchange.json` row는 `source_type=current_listing_snapshot`, `coverage_status=partial`, `event_type=listing_observed`로 저장되고 CIK는 `related_cik`에 저장된다.
  - 이 row는 identity cross-check evidence이며 historical membership PASS, delisting proof, ticker action proof로 해석하지 않는다.
- Follow-up:
  - 다음 task는 `computed-snapshot-lifecycle-v1`로 repeated current snapshot 기반 computed lifecycle evidence 조건을 보수적으로 설계한다.

### 2026-05-28 - Symbol Directory snapshots become DB lifecycle evidence
- User request:
  - Phase 8 다음 작업 진행을 요청함.
- Interpreted goal:
  - Source review에서 정한 public Nasdaq Symbol Directory current files를 DB-backed lifecycle evidence로 적재한다.
- Analysis result:
  - `finance/data/symbol_directory.py` collector와 `run_collect_symbol_directory_snapshots()` job wrapper를 추가했다.
  - `nasdaqlisted.txt` / `otherlisted.txt` row는 `source_type=current_listing_snapshot`, `coverage_status=partial`, `event_type=listing_observed`로 저장된다.
  - 이 row는 current snapshot evidence이며 historical membership PASS, delisting proof, ticker action proof로 해석하지 않는다.
- Follow-up:
  - 다음 task는 `sec-cik-exchange-crosscheck-v1`로 SEC current CIK / ticker / exchange association을 lifecycle identity 보조 evidence로 연결한다.

### 2026-05-28 - Phase 8 source review chooses public current snapshot path first
- User request:
  - Phase 8 다음 작업 진행을 요청함.
- Interpreted goal:
  - historical membership / ticker action source 후보를 확인하고, 무료 / 공식 source 우선 원칙에 맞는 다음 구현 대상을 정한다.
- Analysis result:
  - Nasdaq Daily List는 new listings, delistings, symbol/name changes 같은 corporate action source로 가장 강하지만 subscription / approval product이므로 parking lot으로 분리했다.
  - Nasdaq public Symbol Directory `nasdaqlisted.txt` / `otherlisted.txt`는 current snapshot source로 바로 접근 가능하고, `listing_observed` partial lifecycle evidence를 DB에 적재하는 다음 구현 대상으로 적합하다.
  - SEC company ticker / exchange file과 Submissions API는 CIK / exchange / former-name 보조 source로 유용하지만 complete historical membership proof는 아니다.
- Follow-up:
  - 다음 task는 `symbol-directory-snapshot-ingestion-v1`로 public current symbol directory rows를 `nyse_symbol_lifecycle`에 DB-backed partial evidence로 적재한다.

### 2026-05-28 - Phase 8 starts with lifecycle event semantics
- User request:
  - 1차 hardening cycle을 목표로 Phase 8 작업 진행을 요청함.
- Interpreted goal:
  - Phase 0~7 완료 이후 남은 데이터 evidence 약점을 Phase 8로 공식화하고, lifecycle / survivorship 근거 강화의 첫 구현 slice를 진행한다.
- Analysis result:
  - Phase 8 board를 열고 `symbol-lifecycle-event-fields-v1`을 구현했다.
  - `nyse_symbol_lifecycle`은 `event_type`, `event_date`, `related_symbol`, `related_cik`를 받을 수 있고, current listing row는 `listing_observed`, SEC Form 25 row는 `delisting` event로 저장된다.
  - 이 변경은 lifecycle source semantics를 명확히 하는 DB-backed evidence 작업이며, 새 JSONL / memo / preset / approval / order / rebalance 동작을 추가하지 않았다.
- Follow-up:
  - 다음 Phase 8 task는 `historical-membership-source-review-v1`로 free / official historical membership 또는 ticker action source 후보를 확인한다.

### 2026-05-28 - SEC Form 25 collector should be reachable from Ingestion
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - 이미 구현된 SEC Form 25 delisting collector를 실제 운영 화면에서 수동 실행할 수 있게 한다.
- Analysis result:
  - `Workspace > Ingestion > Practical Validation Provider Snapshots`에 `Delisting Evidence` tab을 추가했다.
  - 이 tab은 symbol list와 SEC user-agent override를 받아 기존 `collect_sec_form25_delistings` job wrapper를 실행한다.
  - Form 25 부재는 active proof가 아니며 complete historical membership은 별도 source가 필요하다는 경고를 화면에 남겼다.
- Follow-up:
  - 다음 개선 후보는 더 완전한 historical listing membership source 또는 cost / turnover 실측 근거 수집이다.

### 2026-05-28 - SEC Form 25 can seed actual delisting evidence
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Historical lifecycle table을 만들었으므로, 이제 무료 공식 source로 실제 delisting evidence를 채운다.
- Analysis result:
  - SEC `company_tickers.json`와 submissions API를 사용해 Form 25 / 25-NSE filing metadata를 수집하는 collector를 추가했다.
  - 수집 row는 `nyse_symbol_lifecycle`에 `source_type=delisting_feed`, `coverage_status=actual`, `listing_status=delisted`로 UPSERT된다.
  - Form 25는 delisting evidence이며, Form 25 부재는 active proof가 아니고 first listing date도 제공하지 않는다.
- Follow-up:
  - 다음 개선 후보는 Ingestion UI 연결, 더 완전한 historical listing membership source, 또는 cost / turnover 실측 근거 수집이다.

### 2026-05-28 - Survivorship control needs DB-backed lifecycle evidence
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Data Coverage gate가 약한 evidence를 막게 됐으므로, 이제 survivorship / historical universe 근거 자체를 DB-backed로 받을 수 있게 만든다.
- Analysis result:
  - `nyse_symbol_lifecycle` schema, NYSE listing lifecycle UPSERT path, `load_symbol_lifecycle_coverage_summary`, Data Coverage Audit 연결을 추가했다.
  - requested period를 덮는 `historical_listing`, `delisting_feed`, `computed_from_snapshots` lifecycle evidence가 있을 때만 survivorship control PASS가 된다.
  - current listing snapshot과 asset profile만 있는 경우는 여전히 REVIEW다.
- Follow-up:
  - 다음 작업은 실제 historical delisting source backfill 또는 cost / turnover 실측 근거 보강이 적절하다.

### 2026-05-28 - Integrated investability gate needs combination QA
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - 개별 audit gate 연결 이후, 세 audit과 기존 provider / robustness / paper observation / final evidence gate가 함께 작동할 때 selected-route가 잘못 열리거나 보류 판단까지 막히지 않는지 확인한다.
- Analysis result:
  - Integrated gate QA contract를 추가했다.
  - all-ready 조합은 selected-route를 허용하고, multi-review 조합은 `INVESTABILITY_PACKET_NEEDS_REVIEW`로 selected-route만 차단하며, multi-blocker 조합은 `INVESTABILITY_PACKET_BLOCKED`로 selected-route를 차단한다.
  - 이 작업은 새 저장소, memo, preset, approval, order, auto rebalance를 추가하지 않았다.
- Follow-up:
  - 다음 큰 개선은 historical universe / delisting source, survivorship control, 또는 cost / turnover 실측 근거처럼 실제 데이터 소스 자체를 보강하는 작업이다.

### 2026-05-28 - Data coverage audit should affect selected-route gate
- User request:
  - 추천 순서대로 작업 진행을 요청함.
- Interpreted goal:
  - Data Coverage Audit을 단순 표시가 아니라 최종 선정 조건에 반영한다.
- Analysis result:
  - `data_coverage` gate group을 추가했다.
  - `DATA_COVERAGE_NEEDS_INPUT` / `DATA_COVERAGE_BLOCKED`는 selected-route blocker로 처리하고, `DATA_COVERAGE_REVIEW`는 review-required로 처리한다.
  - 보류 / 거절 / 재검토 판단은 계속 기록 가능하며, 새 저장 기능이나 실거래 동작은 추가하지 않았다.
- Follow-up:
  - 다음 작업은 Integrated Investability Gate QA로 validation efficacy, data coverage, backtest realism, 기존 provider / robustness / paper observation gate가 함께 작동하는지 점검하는 것이다.

### 2026-05-28 - Data coverage needs explicit DB-backed audit evidence
- User request:
  - 추천 순서대로 작업 진행을 요청함.
- Interpreted goal:
  - Backtest Realism gate 연결 이후 PIT / survivorship / universe evidence를 DB-backed 근거로 더 명확히 확인한다.
- Analysis result:
  - `data_coverage_audit_v1`을 추가했다.
  - Audit은 DB price window coverage, provider freshness, PIT replay / period coverage, universe listing, survivorship / delisting control, storage boundary를 분리한다.
  - Current listing / asset profile row는 historical universe evidence가 아니므로 survivorship PASS로 보지 않는다.
  - 새 JSONL registry, memo, preset, approval, order, auto rebalance는 추가하지 않았다.
- Follow-up:
  - 다음 선택지는 Data Coverage Audit을 selected-route gate policy에 연결하거나, historical universe / survivorship source 자체를 더 강하게 수집하는 것이다.

### 2026-05-28 - Backtest realism audit should affect selected-route gate
- User request:
  - 추천 순서대로 다음 작업 진행을 요청함.
- Interpreted goal:
  - 둘 다 해야 하는 작업 중 먼저 작은 안전장치인 Backtest Realism Gate 연결을 완료한다.
- Analysis result:
  - `backtest_realism` gate group을 추가했다.
  - `BACKTEST_REALISM_NEEDS_INPUT` / `BACKTEST_REALISM_BLOCKED`는 selected-route blocker로 처리하고, `BACKTEST_REALISM_REVIEW`는 review-required로 처리한다.
  - 보류 / 거절 / 재검토 판단은 계속 기록 가능하며, 새 저장 기능이나 실거래 동작은 추가하지 않았다.
- Follow-up:
  - 다음 작업은 Data Coverage Hardening으로 PIT / survivorship / universe evidence를 DB-backed로 보강하는 것이다.

### 2026-05-28 - Backtest realism gap should be visible before selection
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - 검증 효력 gate 다음으로, 백테스트 성과가 실제 투자 환경의 비용 / turnover / liquidity / execution 가정을 충분히 반영했는지 확인할 수 있어야 함.
- Analysis result:
  - `backtest_realism_audit_v1`은 기존 result metadata와 compact validation evidence만 읽어 transaction cost, turnover, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED`로 분리한다.
  - Practical Validation, Final Review, investability packet, saved final decision evidence row가 같은 audit을 읽는다.
  - 새 DB write, JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않았다.
- Follow-up:
  - Backtest Realism gate 연결은 완료됐다. 다음은 Data Coverage Hardening으로 PIT / survivorship evidence를 DB-backed로 보강한다.

### 2026-05-28 - Validation efficacy audit should affect selected-route gate
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - 직전 audit board를 단순 표시에서 끝내지 않고 실전 후보 선정 조건에 반영한다.
- Analysis result:
  - `validation_efficacy` gate group을 추가했다.
  - `VALIDATION_EFFICACY_NEEDS_INPUT` / `VALIDATION_EFFICACY_BLOCKED`는 selected-route blocker로 처리하고, `VALIDATION_EFFICACY_REVIEW`는 review-required로 처리한다.
  - 보류 / 거절 / 재검토 판단은 계속 기록 가능하며, 새 저장 기능이나 실거래 동작은 추가하지 않았다.
- Follow-up:
  - 다음 개선은 Backtest Realism Hardening 또는 Data Coverage Hardening 중 하나가 적절하다.

### 2026-05-28 - Validation efficacy must be visible before final selection
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Practical Validation / Final Review의 검증 효력을 높이되, 새 memo / preset / monitoring storage를 늘리지 않는다.
- Analysis result:
  - `validation_efficacy_audit_v1`은 기존 compact validation evidence만 읽어 runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, execution/storage boundary를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED`로 분리한다.
  - missing runtime replay, stale / missing provider evidence, 명시되지 않은 survivorship evidence는 pass로 추론하지 않는다.
  - 새 DB write, JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않았다.
- Follow-up:
  - 다음 결정은 Validation Efficacy audit을 selected-route gate policy에 연결할지, 또는 Backtest Realism / Data Coverage hardening으로 넘어갈지다.

### 2026-05-28 - Practical Validation V2 P3 selected monitoring can close out
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - 새 기능 추가보다 P3 전체가 read-only selected monitoring 흐름으로 연결됐는지 확인하고 다음 큰 개선으로 넘어갈 준비를 한다.
- Analysis result:
  - P3 closeout QA에서 continuity, recheck comparison, recheck readiness, symbol freshness, selected provider evidence가 하나의 Selected Dashboard 흐름으로 연결된 것을 확인했다.
  - service contract 46개, UI / engine boundary helper, selected dashboard append-path scan이 통과했다.
  - provider 수집, JSONL 자동 저장, monitoring log 자동 저장, memo/preset 저장, approval/order/rebalance는 추가되지 않았다.
- Follow-up:
  - 다음 개선은 P3 연장이 아니라 Validation Efficacy Hardening, Backtest Realism Hardening, Data Coverage Hardening 중 하나를 새 task / phase로 여는 것이 맞다.

### 2026-05-28 - Selected Dashboard should show provider evidence after selection
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - 선정 이후 성과 재검증 전후로 ETF provider / holdings / exposure 근거도 현재 selected portfolio 기준으로 확인한다.
- Analysis result:
  - `selected_provider_evidence_v1`은 selected component ticker weight를 만들고 기존 DB provider context를 read-only로 읽는다.
  - Provider `NOT_RUN`, partial coverage, stale evidence, replay contract fallback은 pass로 숨기지 않고 `NEEDS_DATA` 또는 `REVIEW`로 표시한다.
  - provider 수집, JSONL 저장, monitoring log 저장, memo/preset 저장, approval/order/rebalance는 추가하지 않았다.
- Follow-up:
  - 다음 후보는 Practical Validation V2 P3 closeout QA 또는 remaining selected monitoring gap 점검이다.

### 2026-05-28 - Selected Dashboard should show symbol-level price freshness before recheck
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Recheck Readiness 다음으로 ticker별 DB 가격 최신성을 확인해 최신 recheck의 검증 효력을 높인다.
- Analysis result:
  - `selected_recheck_symbol_freshness_v1`은 selected component replay payload의 portfolio ticker와 benchmark ticker를 모아 DB latest date / row count / lag를 read-only로 표시한다.
  - Missing symbol은 `SYMBOL_FRESHNESS_MISSING`, stale symbol은 `SYMBOL_FRESHNESS_STALE`로 보이며 pass로 숨기지 않는다.
  - OHLCV 수집, DB write, monitoring log 저장, memo/preset 저장, approval/order/rebalance는 추가하지 않았다.
- Follow-up:
  - 다음 후보는 provider-level selected monitoring evidence 또는 Practical Validation V2 P3 closeout QA다.

### 2026-05-28 - Selected Dashboard should show recheck readiness before execution
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - P3 selected monitoring의 검증 효력을 높이되, 새 저장 기능을 늘리지 않아야 함.
- Analysis result:
  - `selected_recheck_readiness_v1`은 DB latest market date, selected component replay contract, default period, execution/storage boundary를 read-only로 확인한다.
  - Candidate replay contract 누락은 `BLOCKED`, DB latest market date 미확인은 `NEEDS_DATA`로 표시한다.
  - 데이터 수집, monitoring log 저장, memo/preset 저장, approval/order/rebalance는 추가하지 않았다.
- Follow-up:
  - 더 깊은 다음 후보는 symbol-level DB freshness 또는 provider-level selected monitoring evidence다.

### 2026-05-28 - Selected Dashboard recheck result must be compared to the original baseline
- User request:
  - Continue the next phase after clarifying that memo-like / preset-like / automatic monitoring storage should be avoided.
- Interpreted goal:
  - Improve post-selection verification without adding another JSONL or user memo storage feature.
- Analysis result:
  - Implemented `selected_recheck_comparison_v1` as a read-only model that compares latest Performance Recheck result with Final Review baseline.
  - Missing or failed Performance Recheck is `NEEDS_INPUT`, not pass; breached CAGR / MDD / benchmark spread routes to re-review.
- Follow-up:
  - Next useful work should focus on DB-backed verification evidence gaps, not user-facing recordkeeping.

### 2026-05-28 - Selected Dashboard needs a continuity check before monitoring
- User request:
  - 다음 작업 진행을 요청함.
- Interpreted goal:
  - Practical Validation V2 P3의 첫 slice로 Final Review selected row가 Selected Dashboard monitoring에 필요한 근거를 갖췄는지 확인해야 함.
- Analysis result:
  - `practical-validation-v2-p3-continuity-check` task를 열고 구현했다.
  - Selected Dashboard는 selected route, investability packet, component target, review trigger, monitoring timeline, Performance Recheck input, execution / storage boundary를 read-only continuity check로 표시한다.
  - Performance Recheck 미실행은 `NEEDS_INPUT`으로 보이며 pass처럼 숨기지 않는다.
  - monitoring log 자동 저장, live approval, broker order, auto rebalance는 계속 비활성이다.
- Follow-up:
  - Recheck evidence 비교는 다음 P3 slice에서 read-only로 구현한다.

### 2026-05-28 - Practical Validation V2 P2 is closed out
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - Investability foundation 이후 남은 carry-forward 중 Practical Validation V2 P2 closeout 가능 여부를 실제 검증 결과로 확정해야 함.
- Analysis result:
  - `practical-validation-v2` task의 P2-7 QA를 완료 처리했다.
  - Service contract, py_compile, UI-engine boundary check가 통과했다.
  - P2 기준은 모든 provider 완전 지원이 아니라 actual / bridge / proxy / `NOT_RUN` origin을 명확히 표시하고 Final Review가 그 gap을 판단 근거로 읽는 것이다.
  - full holdings / full macro / raw provider payload는 JSONL에 저장하지 않는 경계를 유지한다.
- Follow-up:
  - 다음 후보는 P3 범위를 열어 Final Review handoff QA와 Selected Portfolio Dashboard monitoring 연결을 정리하는 것이다.

### 2026-05-28 - Structured waiver is not a pass
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - critical gap을 예외 처리할 수 있는지 여부를 구현 전에 정책으로 정해야 함.
- Analysis result:
  - `structured-waiver-policy-v1` task를 열고 documentation-only 정책을 확정했다.
  - 현재 구현은 `waiver_supported=False`를 유지한다.
  - `BLOCK` severity는 waiver 불가이고, future waiver는 일부 `REVIEW_REQUIRED` gap에만 expiry / review trigger / scope를 가진 구조화 snapshot으로 검토할 수 있다.
  - 새 waiver JSONL registry나 free-form memo 저장은 허용하지 않는다.
- Follow-up:
  - Practical Validation V2 P2 closeout은 이후 완료됐다. Waiver UI / persistence는 아직 별도 구현 task로 열지 않았다.

### 2026-05-28 - Investability foundation implementation track is complete
- User request:
  - 다음 단계 진행을 요청함.
- Interpreted goal:
  - 계획된 구현 task가 끝난 phase를 계속 확장하지 말고 완료 상태와 다음 의사결정을 분리해야 함.
- Analysis result:
  - `investability-decision-foundation-closeout` task를 열고 closeout을 문서화했다.
  - Phase status는 implementation complete로 정리했고, concise done summary를 `phases/done/investability-decision-foundation.md`에 추가했다.
  - Main storage chain은 `PORTFOLIO_SELECTION_SOURCES -> PRACTICAL_VALIDATION_RESULTS -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`로 유지된다.
- Follow-up:
  - `structured-waiver-policy-v1`과 Practical Validation V2 P2 closeout은 이후 완료됐다.

### 2026-05-28 - Final decision evidence는 read-only dossier로 묶는다
- User request:
  - Investability Decision Foundation의 다음 작업 진행을 요청함.
- Interpreted goal:
  - 최종 판단 근거를 여러 화면에서 흩어 읽지 않고, 사람이 읽는 handoff 문서로 확인할 수 있어야 함.
- Analysis result:
  - `decision-dossier-report-v1` task를 열고 구현했다.
  - `build_decision_dossier`는 saved Final Review row와 optional Selected Dashboard monitoring timeline을 `decision_dossier_v1` read model과 markdown string으로 묶는다.
  - Final Review saved record와 Selected Dashboard는 dossier markdown을 표시 / 다운로드할 수 있다.
  - Dossier는 자동 report file write, monitoring log append, live approval, broker order, auto rebalance를 하지 않는다.
- Follow-up:
  - phase의 계획된 구현 task는 완료됐다. 다음은 phase closeout 또는 structured waiver policy 허용 여부 결정이다.

### 2026-05-28 - Selected monitoring은 read-only timeline으로 읽는다
- User request:
  - Investability Decision Foundation의 다음 작업 진행을 요청함.
- Interpreted goal:
  - selected 이후 상태 변화를 새 자동 저장 없이 시간순으로 확인할 수 있어야 함.
- Analysis result:
  - `selected-monitoring-timeline-v1` task를 열고 구현했다.
  - Selected Dashboard Timeline은 Final Review selection, evidence gate snapshot, Performance Recheck, Actual Allocation drift, Review trigger preview를 compact row로 묶는다.
  - Missing Performance Recheck는 `NEEDS_INPUT`이며, Actual Allocation과 alert preview는 입력이 있을 때만 반영되는 optional session-state evidence다.
  - Timeline은 `read_only_timeline`이고 `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`를 자동 append하지 않는다.
- Follow-up:
  - 다음 후보는 final decision evidence를 사람이 읽는 dossier / export contract로 묶는 `decision-dossier-report-v1`이다.

### 2026-05-28 - Robustness evidence는 compact lab board로 읽는다
- User request:
  - Investability Decision Foundation의 다음 작업 진행을 요청함.
- Interpreted goal:
  - stress / rolling / sensitivity / overfit 근거를 새 저장소 없이 Final Review에서 더 직접적으로 읽을 수 있어야 함.
- Analysis result:
  - `robustness-lab-v1` task를 열고 구현했다.
  - Practical Validation result의 `robustness_validation.robustness_lab_board`에 compact summary / detail / follow-up row를 추가했다.
  - Practical Validation, Final Review, final decision evidence read model이 같은 board를 읽는다.
  - Raw run history와 strategy-specific perturbation artifact는 workflow JSONL에 저장하지 않는다.
- Follow-up:
  - 다음 후보는 `selected-monitoring-timeline-v1`로 selected 이후 review signal을 자동 저장 없이 더 잘 읽게 만드는 것이다.

### 2026-05-28 - Look-through evidence는 compact board로 읽는다
- User request:
  - Investability Decision Foundation의 다음 작업 진행을 요청함.
- Interpreted goal:
  - holdings / exposure raw row를 저장하지 않고도 Final Review에서 실제 underlying 노출을 확인할 수 있어야 함.
- Analysis result:
  - `look-through-exposure-board-v1` task를 열고 구현했다.
  - Provider context에 compact `look_through_board`를 추가해 asset bucket, top holding, top overlap, ETF별 coverage를 표시한다.
  - Practical Validation과 Final Review는 같은 board를 읽고, board는 `provider_coverage` 안에만 보존해 top-level 중복 저장을 피한다.
- Follow-up:
  - 다음 후보는 `robustness-lab-v1`로 stress / sensitivity / overfit 근거를 더 실행 가능한 surface로 만드는 것이다.

### 2026-05-28 - Provider evidence는 출처와 freshness를 함께 봐야 한다
- User request:
  - Investability Decision Foundation의 다음 단계 진행을 요청함.
- Interpreted goal:
  - 새 저장소를 만들지 않고 DB-backed provider / macro evidence가 실제 판단에 충분한지 source / freshness / coverage로 더 엄격히 읽어야 함.
- Analysis result:
  - `data-provenance-coverage-v1` task를 열고 provider context schema v2를 구현했다.
  - ETF operability / holdings / exposure context는 source mix, coverage status weight, as-of range, collected range, stale symbols, stale weight를 compact provenance로 제공한다.
  - Macro context는 source mode, observation range, collected range, stale series를 compact provenance로 제공한다.
  - stale ETF provider snapshot은 pass가 아니라 `REVIEW`로 낮춘다.
- Follow-up:
  - 다음 구현은 `look-through-exposure-board-v1`로 holdings / exposure coverage를 사용자가 더 직접적으로 확인하게 만든다.

### 2026-05-28 - 새 저장은 stage handoff 또는 명시적 재사용일 때만 추가한다
- User request:
  - Investability Decision Foundation의 다음 단계 진행을 요청함.
- Interpreted goal:
  - 의미 없는 JSONL 저장과 사용자 memo 저장이 다시 늘어나지 않도록, 기존 저장 지점을 먼저 분류해야 함.
- Analysis result:
  - `storage-governance-audit-v1` task를 열고 JSONL / artifact write surface를 감사했다.
  - main source chain은 `PORTFOLIO_SELECTION_SOURCES -> PRACTICAL_VALIDATION_RESULTS -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`로 유지한다.
  - legacy candidate / proposal / paper registry는 보존하지만 main flow 의존성을 늘리지 않는다.
  - raw provider / holdings / macro data는 DB에 두고 workflow JSONL에는 compact evidence만 남긴다.
- Follow-up:
  - 다음 구현은 `data-provenance-coverage-v1`로 provider / macro / holdings evidence의 source / freshness / coverage를 강화한다.

### 2026-05-28 - Final Review selected route는 profile-aware gate policy를 통과해야 한다
- User request:
  - Phase 0 다음 단계 진행을 요청함.
- Interpreted goal:
  - V1 evidence packet을 더 명시적인 gate policy matrix로 강화하고, selected route가 어떤 이유로 차단되는지 Final Review에서 설명해야 함.
- Analysis result:
  - `validation-gate-hardening-v1` task를 열고 구현했다.
  - `app/services/backtest_evidence_read_model.py`에 profile-aware `gate_policy_snapshot`을 추가했다.
  - Final Review는 `Validation Gate Policy` 표를 표시하고, final decision row에는 compact policy snapshot만 저장한다.
  - 새 JSONL registry, waiver UI, DB schema, crawler는 추가하지 않았다.
- Follow-up:
  - 다음 후보는 기존 JSONL 저장 흐름을 점검하는 `storage-governance-audit-v1` 또는 provider / macro / holdings provenance를 강화하는 `data-provenance-coverage-v1`이다.

### 2026-05-28 - Investability workflow hardening starts with Phase 0 policy
- User request:
  - Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 실전 투자 검토에 더 가깝게 만들기 위한 큰 개발 흐름 진행을 승인함.
- Interpreted goal:
  - 바로 기능을 늘리기보다, 의미 없는 JSONL 저장을 막고, critical `NOT_RUN` / proxy evidence / provider coverage / 데이터 수집 경계를 먼저 고정해야 함.
- Analysis result:
  - 새 active phase `.aiworkspace/note/finance/phases/active/investability-decision-foundation/`를 열었다.
  - Phase 0 기본 정책은 새 JSONL registry와 사용자 memo 저장을 피하고, raw provider / holdings / macro data는 DB에 두며, UI는 remote source를 직접 fetch하지 않는 것이다.
  - `investability-evidence-packet-v1`은 이 phase의 첫 landed slice로 편입했고, 후속 task는 `validation-gate-hardening-v1`이다.
- Follow-up:
  - structured waiver 허용 여부, profile별 critical diagnostic matrix, paper observation 필수 여부를 다음 gate hardening task에서 확정한다.

### 2026-05-30 - Market Movers 2차 개선은 coverage별 자동갱신과 momentum context로 좁힌다
- User request:
  - 새 세션에서 Workspace / Overview 2차 개선으로 Top1000 / Top2000 자동갱신, 거래량 랭킹, 섹터 컬러, 직전 기간 대비 momentum 표시 가능성을 검토하고 개발해 달라고 요청함.
- Interpreted goal:
  - Market Movers를 선택 coverage 기준으로 갱신하고, 수익률 ranking 외에 거래량과 직전 동일 기간 대비 강도 변화를 함께 읽는 화면으로 만든다.
- Analysis result:
  - 자동화 job spec에는 Top1000 / Top2000 intraday가 이미 있으므로 UI heartbeat에서 선택 coverage job_id만 넘기는 방식이 가장 안전하다. `browser_safe` 단독 profile은 S&P 500 용도로 유지한다.
  - Momentum은 유효한 참고 지표지만 단기 noise와 crash risk가 있어 buy/sell 신호가 아니라 `Previous Return %` / `Momentum Delta pp` 보조 context로 표시한다.
- Follow-up:
  - Relative Volume은 평균 거래량 window가 필요한 후속 지표로 남기고, 이번 구현은 raw volume + dollar volume부터 제공한다.

### 2026-05-30 - Overview는 DB-first production baseline으로 병합 준비한다
- User request:
  - Overview Market Intelligence 개발 세션의 흐름을 정리하고 master 병합 전에 문서 / 개발 추적 상태를 업데이트해 달라고 요청함.
- Interpreted goal:
  - 추가 기능 개발이 아니라, Market Movers / Sector-Industry / Events / Data Health / 자동 갱신 / 시장 세션 배너가 어떤 기준으로 동작하는지 다음 작업자가 잃어버리지 않도록 정리해야 함.
- Analysis result:
  - Overview의 핵심 원칙은 `Ingestion or job wrapper -> DB -> service read model -> UI`다. UI render 중 직접 외부 provider를 fetch하지 않는다.
  - Daily Market Movers와 Sector / Industry daily leadership은 저장된 `market_intraday_snapshot`을 공유하고, Weekly / Monthly leadership은 EOD DB의 최신 usable date를 사용한다. 최신 raw EOD row가 sparse하면 UI는 `Effective EOD Date`와 fallback reason을 표시한다.
  - 브라우저 자동 갱신은 OS scheduler가 아니라 Overview 페이지가 열려 있을 때만 작동하는 1차 운영 모드다. 현재 범위는 `S&P 500 + Daily` snapshot이며, 5분 cadence / US market-hours / lock guard를 통과할 때만 실제 provider 수집을 실행한다.
  - Events는 FOMC / macro / earnings row를 `market_event_calendar`에서 읽고, source / validation / quality action을 UI에서 분리해 보여준다. Earnings는 아직 yfinance provider estimate + Nasdaq cross-check 기반이며 official company IR parsing은 후속 후보다.
- Follow-up:
  - master 병합 후 우선순위 후보는 실제 사용 중 발견되는 Overview polish, official earnings IR source 확대, OS scheduler 연결 여부 결정, Practical Validation V2 P2/P3 재개다.

### 2026-05-28 - Market Movers ops는 DB status check와 provider refresh를 분리한다
- User request:
  - 남은 3번 작업, Market Movers 운영 고도화를 진행해 달라고 요청함.
- Interpreted goal:
  - 장중 daily movers에서 refresh 필요 여부와 stale / partial 상태를 빠르게 판단하되, 페이지 렌더나 status check가 자동 수집을 유발하면 안 됨.
- Analysis result:
  - Market Movers read model에 `returnable_ratio`, `returnable_pct`, `next_due_in_minutes`, `check_interval_minutes`, `stale_after_minutes` 같은 운영 필드를 추가했다.
  - SP500뿐 아니라 TOP1000 / TOP2000 daily view도 `Status Check`로 stored DB snapshot 상태를 주기적으로 다시 읽는다.
  - `Update Daily Snapshot`만 provider quote collection을 수행하고, status check는 DB reload만 수행한다.
- Follow-up:
  - 고도화 3개 축은 완료됐다. 다음 후보는 official earnings IR source, scheduled refresh automation, broader macro source expansion이다.

### 2026-05-28 - Events UX는 Focus 중심으로 먼저 읽게 한다
- User request:
  - 남은 고도화 축 중 다음 작업을 진행해 달라고 요청함.
- Interpreted goal:
  - Events 탭에서 전체 DB table을 먼저 읽기보다, 이번 주 일정, high impact 일정, source / validation 조치가 필요한 row를 빠르게 파악해야 함.
- Analysis result:
  - Events read model에 `Days Until`, `Importance`, `Focus`를 추가했다.
  - FOMC / Macro는 `High`, Earnings는 `Medium`으로 표시하고, `Quality Action != No action`인 row는 `Focus=Needs Review`로 우선 노출한다.
  - Overview Events는 `Focus`, `Calendar`, `Table` 탭으로 나뉘며, Calendar chart는 event type별 stacked count로 바뀌었다.
- Follow-up:
  - 남은 주요 후보는 official earnings IR source, scheduled refresh automation, broader macro source expansion, Market Movers ops hardening이다.

### 2026-05-28 - Earnings 고도화 1차는 missing reason과 quality action을 먼저 보강한다
- User request:
  - 남은 고도화 축 중 1번, Events / Earnings 데이터 품질 고도화를 먼저 진행해 달라고 요청함.
- Interpreted goal:
  - 새 공식 IR parser를 바로 붙이기보다, 기존 yfinance / Nasdaq 기반 수집 결과의 품질과 누락 이유를 사용자가 이해할 수 있어야 함.
- Analysis result:
  - Earnings collector가 `symbol_diagnostics`를 남기도록 보강했다. 주요 reason은 `no_provider_earnings_date`, `outside_window`, `provider_error`다.
  - Ingestion / Overview refresh 결과에서 `Earnings Diagnostics` expander로 issue count, reason count, symbol-level detail을 확인할 수 있다.
  - Overview Events row에는 `Quality Action`을 추가해 estimate-only, not-confirmed, stale row의 다음 조치를 표시한다.
- Follow-up:
  - 다음 고도화 후보는 Events 캘린더 UX 정리 또는 company IR official parser prototype이다.

### 2026-05-28 - BLS macro calendar는 공식 `.ics` import fallback으로 보강한다
- User request:
  - BLS 자동 수집이 막힌 이유와 다른 경로를 확인한 뒤, 공식 `.ics` import 방향으로 진행해 달라고 요청함.
- Interpreted goal:
  - 비공식 우회나 유료 API 없이 CPI / PPI / Employment Situation 일정을 공식 출처 기반으로 `market_event_calendar`에 넣을 수 있어야 함.
- Analysis result:
  - BLS backend 자동 요청은 HTTP 403으로 차단될 수 있으므로 direct collector만으로는 Macro Calendar coverage가 `1/4`에 머문다.
  - 사용자가 브라우저로 내려받은 BLS 공식 `.ics` 파일을 Ingestion에서 업로드하면 같은 DB table에 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT` row로 저장하는 fallback을 추가했다.
  - `raw_payload_json.import_method=official_ics_file`로 import 경로를 남기되, source/validation은 official schedule row로 유지한다.
- Follow-up:
  - 실제 BLS `.ics` 파일을 받은 뒤 end-to-end DB write를 한 번 확인하면 Macro Data Health coverage가 GDP 포함 `4/4`로 올라가는지 검증할 수 있다.

### 2026-05-28 - Overview market intelligence 4차는 운영 UX 정식화로 닫는다
- User request:
  - 2차와 3차 이후 다음 단계 진행을 요청함.
- Interpreted goal:
  - 새 데이터 source를 추가하기보다 기존 Market Movers / Sector Leadership / Events를 실제로 매일 읽기 쉬운 화면으로 정식화해야 함.
- Analysis result:
  - Market Movers는 Rank와 Sector Pulse로 나눠 symbol-level과 sector-level 강도를 동시에 보게 했다.
  - Sector / Industry는 equal-weight, cap-weighted, top-symbol return heatmap을 추가하고 table fallback을 유지했다.
  - Events는 Window, Source Type, Validation filter와 Calendar / Table view로 단순 DB table에서 운영 calendar에 가까운 형태로 정리했다.
- Follow-up:
  - 후속 개발 후보는 macro calendar source, company IR official earnings parser, scheduled refresh automation이다.

### 2026-05-28 - Overview prototype 정식화는 4차 흐름이 적절하다
- User request:
  - 1차 기능 구현 완료 이후 prototype을 정식화하려면 몇 차까지 진행해야 하는지 검토하고 phase / task를 다시 작성해 달라고 요청함.
- Interpreted goal:
  - 당장 구현보다 production-ready 상태로 가기 위한 단계, dependency, acceptance gate를 새 phase로 정리해야 함.
- Analysis result:
  - 최소 정식화는 3차까지 가능하지만, 매일 쓰는 product surface로 부르려면 4차까지 권장한다.
  - 2차는 refresh state / diagnostics baseline, 3차는 earnings/events production, 4차는 visual UX / automation polish로 분리했다.
- Follow-up:
  - 새 phase는 `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`이며 첫 구현 task는 `Task 2-01 Refresh State And Diagnostics Baseline`이다.

### 2026-05-28 - Overview market intelligence는 closeout/runbook 단계로 전환한다
- User request:
  - Task 6 이후 다음 단계를 진행해 달라고 요청함.
- Interpreted goal:
  - 기존 task list가 모두 완료됐으므로 새 기능 추가가 아니라 phase 운영 절차와 문서 상태를 정리해야 함.
- Analysis result:
  - Phase 문서에는 Events를 placeholder로 설명하는 stale wording이 남아 있었다.
  - `OVERVIEW_MARKET_INTELLIGENCE.md` runbook을 추가해 Market Snapshot, FOMC, Earnings prototype refresh 순서와 실패 대응을 정리했다.
- Follow-up:
  - 다음 실제 기능 후보는 heatmap/treemap visual, earnings official-source validation, event estimate cleanup 중 하나로 별도 task를 열어야 한다.

### 2026-05-28 - Earnings calendar prototype는 bounded yfinance source로 시작한다
- User request:
  - overview-market-intelligence의 FOMC 이후 다음 단계를 진행해 달라고 요청함.
- Interpreted goal:
  - 무료 API / scraping 원칙을 유지하면서 실적 발표 일정을 `market_event_calendar`에 저장하고 Overview Events에서 확인할 수 있어야 함.
- Analysis result:
  - `Ticker.get_earnings_dates()`는 rich하지만 심볼당 수 초가 걸려 Overview 버튼에 부적합하다.
  - 첫 prototype은 yfinance `Ticker.calendar`의 upcoming `Earnings Date`를 사용하고, 수집 대상을 manual symbols 또는 latest S&P 500 movers 일부로 제한한다.
  - rows는 `event_type=EARNINGS`, `source=yfinance_calendar`, `confidence=0.65`로 저장하며 provider calendar payload를 raw evidence로 남긴다.
- Follow-up:
  - production 단계에서는 stale estimate cleanup, official company IR cross-check, 더 넓은 universe cadence를 별도 task로 설계한다.

### 2026-05-28 - FOMC calendar는 Fed 공식 HTML을 DB-first로 저장한다
- User request:
  - overview-market-intelligence 다음 단계를 진행해 달라고 요청함.
- Interpreted goal:
  - Task 4에서 만든 `market_event_calendar`를 실제 공식 FOMC collector와 Overview Events 표시로 연결해야 함.
- Analysis result:
  - Fed 공식 FOMC calendar page를 파싱해 `event_type=FOMC_MEETING`, `source=federal_reserve_fomc_calendar`로 저장한다.
  - meeting range는 정책 결정일 기준으로 마지막 날을 `event_date`로 저장하고, 원본 range / SEP 표시 / 공식 link는 `raw_payload_json`에 남긴다.
  - Overview와 Ingestion 버튼은 직접 scraping하지 않고 `collect_fomc_calendar` job wrapper를 통해 DB를 갱신한다.
- Follow-up:
  - 다음 calendar slice는 earnings free-source prototype이며, FOMC와 같은 `market_event_calendar` contract를 재사용한다.

### 2026-05-27 - Diagnostics split의 public compatibility contract를 명시한다
- User request:
  - Task 7-04 작업 진행을 요청함.
- Interpreted goal:
  - helper 분리 이후 diagnostics가 어떤 public entry를 유지하는지 명확히 하고, Practical Validation service가 source read model을 올바른 helper에서 읽게 해야 함.
- Analysis result:
  - `source_components_dataframe`를 `app/services/backtest_practical_validation_source.py`로 이동했다.
  - `app/services/backtest_practical_validation_diagnostics.py`에 `__all__`을 추가해 legacy compatibility export를 명시했다.
  - service contract test가 diagnostics re-export identity를 검증하도록 보강됐다.
- Follow-up:
  - Task 7은 완료됐고, 다음은 Task 8 `runtime-wrapper-cleanup`이다.

### 2026-05-27 - Diagnostics stress / sensitivity helper는 별도 service helper로 분리한다
- User request:
  - UI-engine cleanup의 다음 단계 진행을 요청함.
- Interpreted goal:
  - Practical Validation diagnostics service 안에 남은 stress / sensitivity / baseline / market context 계산 보조 로직을 분리해 diagnostics 파일의 책임을 더 줄여야 함.
- Analysis result:
  - `app/services/backtest_practical_validation_stress_sensitivity.py`를 추가해 rolling validation, static stress window, baseline challenge, sensitivity row / interpretation, correlation risk, market context, overfit audit helper를 분리했다.
  - `_operability_rows`는 component ticker inference와 price loader lookup에 붙어 있어 이번 단계에서는 diagnostics에 남겼다.
  - 계산식과 Practical Validation result schema는 바꾸지 않았다.
- Follow-up:
  - 해당 follow-up은 Task 7-04에서 public compatibility contract 정리로 처리했다.

### 2026-05-27 - Diagnostics curve context helper는 service helper로 분리한다
- User request:
  - UI-engine cleanup의 다음 단계 진행을 요청함.
- Interpreted goal:
  - Practical Validation diagnostics service 안에 남은 curve / 수익률 보조 계산을 별도 service helper로 분리해, diagnostics 파일이 orchestration에 더 가까워지게 해야 함.
- Analysis result:
  - `app/services/backtest_practical_validation_curve_context.py`를 추가해 compact curve snapshot, curve normalize, DB price proxy, component curve combination, window perturbation, aligned monthly returns helper를 분리했다.
  - `_build_curve_context`는 component title / weight / ticker interpretation과 붙어 있어 이번 단계에서는 diagnostics에 남겼다.
  - Compare / Candidate Review는 compact snapshot 함수를 새 curve context helper에서 직접 import한다.
- Follow-up:
  - 해당 follow-up은 Task 7-03에서 stress / sensitivity helper 분리로 처리했다.

### 2026-05-27 - Diagnostics split은 source/profile helper부터 시작한다
- User request:
  - UI-engine cleanup의 다음 단계 진행을 요청함.
- Interpreted goal:
  - 큰 Practical Validation diagnostics service를 한 번에 쪼개지 않고, 안전한 helper family부터 분리해야 함.
- Analysis result:
  - `app/services/backtest_practical_validation_source.py`를 추가해 validation profile과 Clean V2 selection source builder를 분리했다.
  - diagnostics module은 기존 public builder import 호환성을 유지하고, Compare / Candidate Review / Practical Validation service는 새 source helper를 직접 import한다.
  - stress / sensitivity / provider / scoring 계산식은 바꾸지 않았다.
- Follow-up:
  - 해당 follow-up은 Task 7-02에서 curve context helper 분리로 처리했다.

### 2026-05-27 - Practical Validation helper는 service boundary로 이동한다
- User request:
  - UI-engine boundary cleanup의 다음 작업 진행을 요청함.
- Interpreted goal:
  - 남은 `app.services/app.runtime -> app.web` advisory를 제거해 service/runtime이 web helper를 거꾸로 참조하지 않게 해야 함.
- Analysis result:
  - curve normalize / provenance / benchmark parity helper를 `app/services/backtest_practical_validation_curve.py`로 이동했다.
  - provider / macro loader output adapter를 `app/services/backtest_practical_validation_provider_context.py`로 이동했다.
  - diagnostics / replay service import를 새 service helper로 바꾸고 boundary lint advisory를 0건으로 줄였다.
- Follow-up:
  - 다음은 Task 7 `practical-validation-diagnostics-split`이며, 큰 diagnostics service를 계산 helper family 단위로 깊게 분석한 뒤 분리한다.

### 2026-05-27 - Cleanup phase는 전체 얕은 audit 후 task별 깊은 분석으로 진행한다
- User request:
  - UI-engine 분리 cleanup 작업을 실제로 진행하되, 수정하면서 브라우저로 테스트 가능한 부분이 있으면 브라우저를 열어 확인을 유도해 달라고 요청함.
- Interpreted goal:
  - 바로 큰 refactor를 하기보다 현재 코드 흐름을 다시 확인하고, Task 6~9를 명확한 하위 단계와 검증 기준으로 진행해야 함.
- Analysis result:
  - `ui-engine-boundary-cleanup` phase와 `ui-engine-boundary-cleanup-audit` task를 열었다.
  - 현재 boundary lint는 hard violation 없이 PASS이며, 남은 구조 부채는 Practical Validation의 `app.services -> app.web` helper advisory 3건이다.
  - Task 6은 Practical Validation curve / provider context helper 이동, Task 7은 diagnostics service split, Task 8은 runtime wrapper map/low-risk cleanup, Task 9는 lint/test/docs hardening으로 정리했다.
- Follow-up:
  - Task 0은 문서 / audit 작업이라 브라우저 QA 대상이 없다. Task 6 이후 visible Streamlit 화면이나 표시 shape가 바뀌면 브라우저로 확인한다.

### 2026-05-20 - Runtime은 app/web 밖의 app/runtime이 맡는다
- User request:
  - 남은 개선 후보인 `app/web/runtime` 위치 / 이름 정리를 다음 task로 진행해 달라고 요청함.
- Interpreted goal:
  - runtime / repository helper가 UI package 아래에 있어 service와 UI 경계가 흐려지는 문제를 정리해야 함.
- Analysis result:
  - Task 5를 `runtime-package-boundary`로 열고 `5-01`, `5-02`로 나눠 진행했다.
  - `5-01`에서 `app/web/runtime/*.py`를 `app/runtime/*.py`로 이동하고 repo imports를 `app.runtime`으로 바꿨다.
  - `5-02`에서 Streamlit-free Candidate Library replay helper를 `app/runtime/candidate_library.py`로 이동했다.
  - boundary lint는 이제 `app/services`와 `app/runtime`을 함께 검사한다.
- Follow-up:
  - 남은 advisory는 Practical Validation curve / connector helper가 아직 `app/web`에 있는 부분이다.

### 2026-05-20 - Practical Validation diagnostics는 service boundary에 둔다
- User request:
  - UI / engine 분리 후속 작업의 다음 단계를 진행해 달라고 요청함.
- Interpreted goal:
  - `app/services`가 `app/web` helper를 호출하는 역방향 구조를 줄이고, 진단 계산 책임을 UI 렌더링에서 더 분리해야 함.
- Analysis result:
  - `app/web/backtest_practical_validation_helpers.py`를 `app/services/backtest_practical_validation_diagnostics.py`로 이동했다.
  - Practical Validation service, Compare, Candidate Review는 source/profile/compact curve helper를 service module에서 import한다.
  - 계산식과 registry schema는 바꾸지 않고 ownership boundary만 이동했다.
- Follow-up:
  - 남은 전이 부채는 diagnostics service가 일부 `app.web` connector / curve helper를 참조한다는 점이며, 다음 cleanup 후보로 분리 가능하다.

### 2026-05-20 - UI-engine boundary는 lint helper로 보호한다
- User request:
  - UI / engine 분리 관점의 개선 후보 중 boundary lint 자동화를 진행해 달라고 요청함.
- Interpreted goal:
  - `app/services`가 다시 Streamlit UI 책임을 들고 오지 않도록 반복 가능한 자동 점검을 만들고 싶음.
- Analysis result:
  - 새 phase가 아니라 단일 task `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-lint/`로 진행했다.
  - `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`를 추가했다.
  - hard fail은 `app/services` / `app/runtime`의 Streamlit 사용과 staged generated / registry / saved artifact이며, 현재 남아 있는 `app.services/app.runtime -> app.web` import는 advisory로 처리한다.
- Follow-up:
  - 후속 구조 정리에서는 남은 Practical Validation Streamlit-free helper advisory를 service/runtime 위치로 옮길지 판단한다.

### 2026-05-20 - Final decision evidence는 공통 read model로 읽는다
- User request:
  - `ui-engine-boundary-foundation`의 다음 단계 진행을 요청함.
- Interpreted goal:
  - Final Review와 Selected Portfolio Dashboard가 같은 최종 판단 evidence를 각자 해석하지 않도록, UI-independent read model 경계를 만들고 싶음.
- Analysis result:
  - `app/services/backtest_evidence_read_model.py`를 추가해 saved final decision status / table rows / evidence check rows를 공통 service로 분리했다.
  - Final Review helper와 Selected Dashboard helper는 이 service 결과를 DataFrame으로 변환하고 렌더링만 담당한다.
  - Selected Dashboard는 read-only 정책을 유지하며 registry schema나 저장 동작은 바꾸지 않았다.
- Follow-up:
  - `ui-engine-boundary-foundation`의 구현 task는 모두 완료됐다. 다음은 phase closeout QA 또는 더 큰 후속 boundary phase 결정이다.

### 2026-05-20 - Practical Validation은 service handoff contract부터 분리한다
- User request:
  - `ui-engine-boundary-foundation`의 다음 task 진행을 요청함.
- Interpreted goal:
  - Practical Validation 전체 재작성보다, UI와 engine / workflow 책임이 섞인 지점을 먼저 안정적으로 분리해야 함.
- Analysis result:
  - `app/services/backtest_practical_validation.py`를 추가해 source/result append와 Practical Validation / Final Review handoff contract를 Streamlit-free service로 분리했다.
  - `app/web/backtest_practical_validation_helpers.py`는 source/profile/diagnostic 생성 helper로 축소하고 Streamlit import를 제거했다.
  - UI modules는 여전히 버튼, 렌더링, `st.session_state`, provider gap collection UI를 담당한다.
- Follow-up:
  - 다음 phase task는 Final Review / Selected Dashboard evidence read model 경계를 확인하는 `evidence-read-model-boundary`다.

### 2026-05-19 - UI와 engine 분리는 하나의 foundation phase로 시작한다
- User request:
  - Next.js / React 전환이 아니라, 현재 Python / Streamlit 프로그램 안에서 UI와 engine 결합도를 먼저 낮추는 phase를 열고 작업을 진행해 달라고 요청함.
- Interpreted goal:
  - 이후 UI agent와 engine agent가 서로 다른 파일 경계를 기준으로 병렬 작업할 수 있도록, Streamlit 화면과 backtest / validation runtime 책임을 분리하고 싶음.
- Analysis result:
  - 새 phase는 `.aiworkspace/note/finance/phases/active/ui-engine-boundary-foundation/`로 열었다.
  - 첫 task는 `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-audit/`이며, 현재 결론은 `app/services`를 UI-engine boundary로 두고 `app/web/backtest_single_runner.py`의 Single Backtest execution dispatch를 먼저 분리하는 것이다.
  - 첫 구현 task `.aiworkspace/note/finance/tasks/active/backtest-execution-service-boundary/`에서 `app/services/backtest_execution.py`를 만들고 Single Backtest dispatch / error normalization을 Streamlit-free service로 이동했다.
  - 이 phase에서는 React / Next.js / FastAPI, DB schema 변경, strategy engine 재설계, registry JSONL rewrite를 하지 않는다.
- Follow-up:
  - 다음 구현 task는 `compare-service-boundary`로 열고, `app/web/backtest_compare.py`에서 가장 작은 service extraction 후보를 먼저 확정한다.

### 2026-05-13 - 제품 방향 리서치 폴더명은 researches로 맞춘다
- User request:
  - 프로젝트 폴더명이 `docs`, `tasks`, `phases`처럼 복수형이므로 `research`보다 `researches`가 일관적이지 않느냐고 질문하고 진행을 요청함.
- Interpreted goal:
  - 새 제품 방향 리서치 작업장을 repo naming convention에 맞추고, legacy `research/` 경로와도 구분하고 싶음.
- Analysis result:
  - `.aiworkspace/note/finance/research/`를 `.aiworkspace/note/finance/researches/`로 rename했다.
  - AGENTS, docs, active task 기록, product research skills, global skill mirror의 경로를 `researches/active/<research-id>/` 기준으로 맞췄다.
- Follow-up:
  - 2단계 실제 리서치 run은 `researches/active/<research-id>/`에 생성한다.

### 2026-05-13 - 실제 제품 방향 리서치 산출물은 researches/active에 둔다
- User request:
  - 2단계에서 수행할 명확한 리서치 결과는 `tasks/active`보다 `research` 폴더에 두는 것이 맞다고 판단하고 진행을 요청함.
- Interpreted goal:
  - 스킬 개발 기록과 실제 제품 방향 리서치 산출물을 분리해, 이후 research worktree에서 조사 결과를 관리하기 쉽게 만들고 싶음.
- Analysis result:
  - `.aiworkspace/note/finance/researches/active/<research-id>/`를 제품 방향 리서치의 canonical output 위치로 확정했다.
  - `tasks/active/`는 리서치 workflow나 스킬 자체를 만들고 수정한 실행 기록에 사용한다.
  - 채택된 장기 방향만 `docs/PRODUCT_DIRECTION.md` 또는 `docs/ROADMAP.md`로 승격하고, 승인된 개발 단위만 phase/task로 전환한다.
- Follow-up:
  - 2단계 실제 리서치 run은 `researches/active/<research-id>/`에 `RESEARCH_PLAN.md`, `CURRENT_PROJECT_AUDIT.md`, `BENCHMARKS.md`, `FEATURE_CANDIDATES.md`, `RECOMMENDATION.md`, `SOURCES.md`, `RISKS.md`를 두고 시작한다.

### 2026-05-13 - 제품 방향 리서치는 스킬 3개로 시작한다
- User request:
  - Notion의 단계적 스킬/플러그인 개발 흐름에 맞춰 1단계를 진행해 달라고 요청함.
- Interpreted goal:
  - 현재 프로젝트 분석, 외부 벤치마킹, 기능 후보 도출을 분리해 future roadmap research를 반복 가능한 workflow로 만들고 싶음.
- Analysis result:
  - 1단계는 plugin 패키징이 아니라 `finance-product-audit`, `finance-benchmark-research`, `finance-feature-opportunity` 스킬 초안 작성으로 진행한다.
  - 실제 외부 조사와 ROADMAP 반영은 후속 research worktree / 승인 흐름에서 수행한다.
- Follow-up:
  - 1~2회 실제 리서치 run 후 scoring, source quality, roadmap proposal, research-to-phase 스킬을 보강한다.

### 2026-05-13 - code_analysis는 폴더 유지가 아니라 docs / active task로 분해한다
- Request topic:
  - `code_analysis` 폴더 안의 문서를 새 문서 구조에서 어디로 옮길지, 그대로 유지할지, 정리해야 할지 분석하고 마이그레이션 진행을 요청함.
- Interpreted goal:
  - 코드 수정자가 계속 봐야 하는 current-state 문서와 Practical Validation V2처럼 진행 중인 task 계획 문서를 분리해, 다음 세션이 문서 위치를 헷갈리지 않게 만드는 것.
- Main result:
  - current-state code / runtime / strategy / data pipeline 문서는 `docs/architecture/`로 이동한다.
  - Backtest UI와 Portfolio Selection 사용자 흐름은 `docs/flows/`로 이동한다.
  - repo-local helper script 사용법은 `docs/runbooks/`로 이동한다.
  - Practical Validation V2 상세 설계와 P2 connector 계획은 장기 docs가 아니라 `tasks/active/practical-validation-v2/`의 active task 문서로 관리한다.
  - legacy refinement guide와 workflow redesign guide는 그대로 보관하지 않고 현재 문서에 흡수한다.

### 2026-05-11 - 문서 작성 지침은 `이걸 하는 이유?` 중심으로 바꾼다
- Request topic:
  - 사용자가 새 문서 작성 시 기존의 분리형 요약 / 완료 효과 섹션을 제거하고, `이걸 하는 이유?`를 쉽게 정리하는 방식으로 지침 수정을 요청함
- Interpreted goal:
  - 계획 문서가 반복 섹션으로 길어지는 대신, 작업을 왜 하는지와 끝났을 때의 구체적 가치를 한 곳에서 바로 이해하게 만들고 싶음
- Result:
  - `AGENTS.md`, phase plan template, automation guide, bootstrap helper, local finance phase/doc-sync skill guidance를 수정했다
  - 앞으로 새 phase / planning 문서에는 `이걸 하는 이유?` 섹션을 두고 문제 / 지금 필요한 이유 / 완료 후 가치를 쉽게 설명한다
  - 기존 historical documents는 보존하고, 새로 생성되거나 크게 다시 쓰는 문서부터 적용한다

### 2026-05-11 - P2 provider connector는 데이터 수집 / DB 저장부터 개발한다
- Request topic:
  - 사용자가 P2 provider connector 개발에서 ETF holdings, macro series, sentiment series를 어디서 어떻게 수집할지 확인하고, DB ingestion 중심으로 개발 순서를 수정해 달라고 요청함
- Interpreted goal:
  - Practical Validation이 실제 provider evidence를 쓰려면 먼저 공식 source에서 데이터를 수집해 DB에 저장해야 하며, UI가 직접 외부 사이트를 호출하는 구조는 피해야 함
- Result:
  - P2 provider source는 공식 issuer / FRED 우선으로 정리했다
  - ETF source는 iShares / BlackRock, SSGA / SPDR, Invesco를 우선 확인하고, `yfinance`와 기존 `nyse_asset_profile` / `nyse_price_history` 값은 bridge / fallback으로 둔다
  - Macro / sentiment 1차 source는 FRED `VIXCLS`, `T10Y3M`, `BAA10Y`와 DB 가격 기반 risk proxy로 잡는다
  - P2 개발 순서는 source map / schema / collector / UPSERT 저장을 먼저 만들고, 그 다음 loader, Practical Validation connector, UI / diagnostics를 연결하는 방향으로 수정했다

### 2026-05-11 - P2는 provider 플랫폼이 아니라 12개 검증 패턴 정상화 작업이다
- Request topic:
  - 사용자가 P2의 목적이 12개 Practical Validation 검증 패턴 중 아직 정상 검증되지 않는 항목을 후속 작업으로 정상화하는 것인지 확인함
- Interpreted goal:
  - P2를 데이터 수집 자체가 아니라 미완성 검증 항목을 actual / proxy / `NOT_RUN` 근거로 명확히 판정하게 만드는 작업으로 재정의해야 함
- Result:
  - P2 작업 순서를 `P2-0. 대상 항목 확정`부터 `P2-7. QA`까지 재정리했다
  - P2 대상 진단은 2 Asset Allocation Fit, 3 Concentration / Overlap / Exposure, 5 Regime / Macro Suitability, 6 Sentiment / Risk-On-Off Overlay, 7 Stress / Scenario Diagnostics, 9 Leveraged / Inverse ETF Suitability, 10 Operability / Cost / Liquidity, 11 Robustness / Sensitivity / Overfit로 정리했다
  - Provider / holdings / macro ingestion은 위 진단을 정상화하기 위한 구현 수단으로 문서화했다
  - 정상화는 모든 항목이 PASS가 된다는 뜻이 아니라, 실제 데이터가 있으면 actual evidence로 검증하고 없으면 명확한 `NOT_RUN` 또는 `REVIEW` reason을 남기는 것으로 정의했다

### 2026-05-11 - P2-0은 대상 진단 계약을 확정하는 작업이다
- Request topic:
  - 사용자가 Practical Validation V2 P2-0 작업 진행을 요청함
- Interpreted goal:
  - 코드 구현 전에 P2에서 정상화할 검증 항목, 필요한 actual data, bridge / proxy fallback, `NOT_RUN` / `REVIEW` 조건을 확정해야 함
- Result:
  - P2-0 산출물을 `CONNECTOR_AND_STRESS_PLAN.md`에 추가했다
  - 대상 진단은 2 Asset Allocation Fit, 3 Concentration / Overlap / Exposure, 5 Regime / Macro Suitability, 6 Sentiment / Risk-On-Off Overlay, 7 Stress / Scenario Diagnostics, 9 Leveraged / Inverse ETF Suitability, 10 Operability / Cost / Liquidity, 11 Robustness / Sensitivity / Overfit로 고정했다
  - 각 진단별 actual data 요구사항, fallback, `NOT_RUN` / `REVIEW` 조건, compact evidence 경계를 정리했다
  - Provider 상세 문서에는 P2-0 provider data 요구사항 표를 추가했고, 다음 작업은 P2-1 schema / ingestion field contract로 정리했다

### 2026-05-03 - Phase 34는 Final Portfolio Selection Decision Pack으로 시작한다
- Request topic:
  - 사용자가 Phase 34 작업 시작을 요청함
- Interpreted goal:
  - Phase 33 paper tracking ledger closeout 이후, 최종 실전 후보 선정 / 보류 / 거절 / 재검토를 다루는 Phase 34를 열어야 함
- Result:
  - Phase 34 문서 bundle을 `.aiworkspace/note/finance/phases/phase34/` 아래에 생성했다
  - Phase 34 상태를 `active / not_ready_for_qa`로 잡았다
  - 첫 작업으로 final decision row 계약과 저장소 경계를 정의했다
  - 다음 작업은 저장된 paper ledger record를 final decision evidence pack으로 읽는 기준을 구현하는 것이다
  - Phase 34도 live approval, broker order, 자동매매가 아니라 final selection decision pack이다

### 2026-05-03 - Phase 33 checklist 완료로 Paper Portfolio Tracking Ledger phase를 닫는다
- Request topic:
  - 사용자가 Phase 33 checklist 완료와 Phase 33 마무리를 요청함
- Interpreted goal:
  - Phase 33을 `complete / manual_qa_completed`로 전환하고, Phase 34를 열기 전 handoff 상태를 문서에 맞춰야 함
- Result:
  - Phase 33 checklist 완료 상태를 보존했다
  - Phase 33 TODO, completion summary, next-phase preparation, roadmap, doc index, comprehensive analysis를 closeout 상태로 동기화했다
  - Phase 34는 저장된 Paper Portfolio Tracking Ledger를 읽어 최종 선정 / 보류 / 거절 decision pack을 만드는 다음 phase로 남겼다

### 2026-05-03 - Phase 33은 paper ledger 저장 / 재확인 / Phase34 handoff까지 구현하고 QA로 넘긴다
- Request topic:
  - 사용자가 Phase 33의 첫 번째 작업부터 네 번째 작업까지 모두 마무리하고 checklist를 할 상황이 되면 공유해달라고 요청함
- Interpreted goal:
  - Phase 33은 최종 선정이나 live approval을 만들지 않고, Phase 32 handoff를 받은 후보 / proposal을 paper tracking ledger로 저장하고 다시 읽을 수 있게 해야 함
- Result:
  - `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` append-only 저장소와 runtime helper를 추가했다
  - Portfolio Proposal Validation Pack에서 Paper Tracking Ledger Draft를 확인하고 명시 저장할 수 있게 했다
  - 작성 중 proposal은 proposal draft 저장 전 paper ledger save가 차단되도록 했다
  - 저장된 ledger review surface와 Phase34 handoff route를 추가했다
  - Phase 33은 `implementation_complete` / `manual_qa_pending`으로 전환했고, 사용자 QA는 `PHASE33_TEST_CHECKLIST.md` 기준으로 진행한다

### 2026-05-03 - Phase 32를 닫고 Phase 33은 Paper Portfolio Tracking Ledger로 시작한다
- Request topic:
  - 사용자가 Phase 32 checklist 완료 후 Phase 32 마무리와 Phase 33 시작을 요청함
- Interpreted goal:
  - Phase 32 Robustness / Stress Validation Pack을 사용자 QA 완료 상태로 닫고,
    Phase 33은 최종 선정이나 live approval이 아니라 실제 돈 없이 관찰할 paper tracking ledger를 만드는 단계로 열어야 함
- Result:
  - Phase 32를 `complete` / `manual_qa_completed`로 닫았다
  - Phase 33 문서 bundle을 `.aiworkspace/note/finance/phases/phase33/` 아래에 생성했다
  - Phase 33의 첫 작업은 `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` row 계약과 저장소 경계를 정의하는 것으로 잡았다
  - paper ledger는 current candidate / Pre-Live / Portfolio Proposal registry를 덮어쓰지 않는 append-only 저장소로 설계한다
  - Phase 33은 paper PnL 계산, 최종 선정 decision, live approval, 주문 지시를 만들지 않는다

### 2026-04-20 - FINANCE_COMPREHENSIVE_ANALYSIS는 현재 구조와 phase 히스토리를 분리해서 읽어야 한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`에서 현재 구조 설명 중에 Phase 14, Phase 24, Phase 25 이야기가 섞여 나와 읽기 어렵다고 지적함
- Interpreted goal:
  - 문서의 상세 구현 히스토리는 유지하되, 현재 시스템 구조와 phase별 구현 히스토리를 분리해서 사용자도 큰 흐름을 읽을 수 있게 만들고 싶음
- Result:
  - section 3을 `현재 시스템 구조와 phase별 구현 히스토리`로 재구성했다
  - `3-1`에는 현재 시스템 구조만 먼저 설명하고, `3-2`에는 Phase 1~25 구현 히스토리를 구간별 표로 정리했다
  - 기존에 phase별 상세 메모가 섞여 있던 긴 서술은 `3-3. 상세 구현 메모`로 남겨, agent deep reference 역할은 유지했다

### 2026-04-20 - FINANCE_COMPREHENSIVE_ANALYSIS는 깊이를 유지하고 입구를 정리하는 방식이 맞다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`를 시각적으로 억지로 줄이기보다,
    구현 히스토리 / 구조 정보 / DB-strategy-runtime-UI 연결 / agent deep reference 가치를 유지하면서
    사람도 읽을 수 있게 정리할 수 있는지 질문함
- Interpreted goal:
  - 상세 기술 문서의 정보 손실 없이 사용자 진입성을 높이고 싶음
- Result:
  - 기존 본문은 유지했다
  - 상단에 문서 역할, 빠른 읽기, 현재 시스템 한 장 요약, 읽기 기준을 추가했다
  - 현재 문서는 deep reference 성격을 유지하되,
    사용자가 어디부터 읽어야 하는지 알 수 있는 entry layer를 갖게 되었다

### 2026-04-20 - Finance overview / index 문서는 정보는 충분하지만 읽기 구조 개선이 필요하다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`와 `FINANCE_DOC_INDEX.md`가 너무 난잡해 보이는데,
    현재 상태로 충분한지 아니면 읽기 쉽게 업데이트해야 하는지 질문함
- Interpreted goal:
  - 두 문서가 agent용 내부 참조로는 충분한지, 사용자/운영자도 읽기 쉬운 문서로 재정리해야 하는지 판단하고 싶음
- Result:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`는 구현 세부 정보를 많이 담고 있어 agent context로는 유용하지만,
    2,700줄 이상으로 커져 사용자용 entry document로는 너무 무겁다
  - `FINANCE_DOC_INDEX.md`는 phase별 문서 위치를 찾는 목적은 맞지만,
    상위 기준 문서 섹션이 과도하게 길고 phase별 구조가 뒤로 밀려 실제 탐색성이 떨어진다
  - 권장 방향은 문서를 없애는 것이 아니라,
    overview / phase index / backtest report index / archive index 역할을 더 분리하고,
    `FINANCE_DOC_INDEX.md`는 phase별 목차 중심으로 재구성하는 것이다

### 2026-04-20 - Phase 24를 닫고 Phase 25를 Pre-Live 운영 체계로 시작했다
- Request topic:
  - 사용자가 Phase 24를 마무리하고 Phase 25 진행을 요청함
- Interpreted goal:
  - Phase 24의 신규 전략 구현 / QA 완료 상태를 공식 closeout하고,
    Phase 25는 Real-Money 탭의 중복 기능이 아니라 paper / watchlist / hold / re-review를 기록하는 운영 체계로 시작해야 함
- Result:
  - Phase 24를 `phase complete / manual_validation_completed`로 닫았다
  - Phase 25 plan / TODO / checklist / completion draft / next-phase draft / first work-unit 문서를 생성하고 정리했다
  - Phase 25 첫 작업은 후보를 고르는 것이 아니라,
    Real-Money 검증 신호와 Pre-Live 운영 점검의 경계 및 운영 상태를 고정하는 것으로 잡았다
  - 다음 작업은 pre-live 후보 기록 포맷과 저장 위치를 정하는 것이다

### 2026-04-20 - Real-Money 검증 신호와 Pre-Live 운영 점검을 분리하기로 했다
- Request topic:
  - 사용자가 Real-Money 검증과 Phase 25에서 할 점검/운영 흐름이 비슷하게 보이므로, 사용자가 혼동하지 않게 명확히 분리해 달라고 요청함
- Interpreted goal:
  - Real-Money는 개별 백테스트 실행의 검증 신호로 두고, Phase 25는 그 신호를 받아 paper / watchlist / 보류 / 재검토를 기록하는 별도 운영 절차로 설계해야 함
- Result:
  - 용어를 `Real-Money 검증 신호`와 `Pre-Live 운영 점검`으로 분리했다
  - `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`에서 두 단계를 별도로 설명하도록 업데이트했다
  - `PHASE24_NEXT_PHASE_PREPARATION.md` handoff에도 Phase 25에서 이 경계를 유지해야 한다고 명시했다

### 2026-04-20 - 결측 가격 행은 임의 보정하지 않고 공통 날짜를 보수적으로 제한하기로 했다
- Request topic:
  - 사용자가 `IWM` 결측 행이 있는 상황에서 4월까지 계산하는 것이 아니라, 결측 문제를 명시하면서 2월에서 끊는 것이 맞지 않느냐고 질문함
- Interpreted goal:
  - 데이터 품질 문제가 있는 티커를 사용자가 놓치지 않도록, 백테스트 결과 구간을 보수적으로 유지하고 warning/meta로 문제를 노출하고 싶음
- Result:
  - 사용자의 판단이 맞다고 정리했다
  - `add_ma`에서 결측 가격 행을 조용히 제거하던 변경을 되돌리고, 원본 결측이 이동평균/공통 리밸런싱 날짜에 영향을 주게 둔다
  - 대신 `malformed_price_rows` metadata와 한국어 주의사항으로 `IWM 1건(2026-03-17)` 같은 원본 가격 품질 문제를 명시한다
  - 따라서 원본 DB 가격 행이 재수집/수정되기 전까지 같은 실행은 `2026-02-27`에서 보수적으로 멈추는 것이 올바른 동작이다

### 2026-04-19 - quarterly first implementation은 real-money promotion이 아니라 portfolio handling contract parity부터 붙이는 것이 맞다
- Request topic:
  - Phase 23 실제 작업 진행 요청
- Interpreted goal:
  - annual strict와 quarterly strict 사이에서 제품 기능으로 먼저 맞춰야 할 gap을 줄이기
- Result:
  - quarterly runner와 sample layer는 이미 strict statement shadow 실행에서 weighting / rejected-slot / risk-off 계열 contract를 처리할 수 있었다
  - 반면 quarterly single / compare UI와 payload에는 해당 contract surface가 충분히 노출되지 않았다
  - 따라서 첫 구현 단위는 real-money promotion이나 guardrail을 붙이는 것이 아니라
    `Portfolio Handling & Defensive Rules`를 quarterly 3개 family에 연결하는 것으로 잡았다
  - 결과적으로 quarterly는 아직 research-only / productionization 중인 path로 유지하되,
    `Weighting`, `Rejected Slot Handling`, `Risk-Off`, `Defensive Tickers` 값은 UI / payload / compare / history 재진입에서 유지되게 했다
  - 다음 판단 지점은 representative quarterly smoke run과 saved replay UI 확인이다

### 2026-04-19 - Phase 23은 quarterly 성과 분석이 아니라 cadence 실행 경로를 제품 기능으로 올리는 phase다
- Request topic:
  - Phase 22 checklist 완료 후 다음 단계를 진행해 달라는 요청
- Interpreted goal:
  - Phase 22에서 portfolio workflow 개발 검증을 닫았으므로,
    roadmap 기준 다음 main phase인 quarterly / alternate cadence productionization을 열어야 함
- Result:
  - Phase 23은 투자 후보를 새로 고르는 phase가 아니라
    quarterly strict family와 alternate cadence 실행 경로를 제품 기능으로 만드는 phase로 잡았다
  - 현재 quarterly strict family는 이미 single strategy / compare / history 일부 경로가 있지만,
    아직 prototype / research-only 성격과 annual strict 대비 contract / replay / 해석 gap이 남아 있다고 정리했다
  - 따라서 첫 작업은 바로 broad backtest search가 아니라
    quarterly productionization frame과 gap inventory를 고정하는 것이다
  - 이후 작업은 UI 문구, payload parity, compare/history/saved replay 복원성, representative smoke validation 순서가 자연스럽다

### 2026-04-16 - `Phase 18~25 Draft Big Picture` 같은 이름은 roadmap 안에서 별도 특수 구간처럼 읽혀서, quick summary 섹션으로 바꾸는 편이 더 자연스럽다
- Request topic:
  - 사용자가 `MASTER_PHASE_ROADMAP.md`의
    `Phase 18~25 Draft Big Picture` 섹션이
    특정 부분만 특별하게 있는 느낌이라 애매하다고 피드백함
- Interpreted goal:
  - `Phase 18~25` 구간을 계속 요약해 주되,
    phase 본문과 별도 roadmap처럼 보이지 않게 만들고 싶음
- Result:
  - 해당 섹션은 없애기보다
    **요약 섹션이라는 성격을 더 분명하게 드러내는 방향**이 맞다고 판단했다
  - 그래서 이름을
    `다음 단계 한눈에 보기 (Phase 18 ~ 25)`
    로 바꾸고,
    이 섹션이 "위 phase 설명을 대체하지 않는 quick-reading summary"라는 점을 먼저 적었다
  - 또한 `Phase 18 ~ 25`를
    각 phase별로 한 줄씩 다시 설명해,
    특정 구간만 따로 떠 있는 느낌보다
    "현재 이후 구간을 빠르게 다시 읽는 안내판"처럼 보이게 정리했다

### 2026-04-16 - roadmap tail에서는 `현재 위치`와 `그 다음 큰 흐름`의 역할을 분리해야 덜 겹친다
- Request topic:
  - 사용자가 `현재 위치` 아래 내용과
    `Phase 18 ~ 25` 요약 섹션이 서로 겹친다고 지적함
- Interpreted goal:
  - roadmap tail을 상태 설명과 next-step 설명으로 나눠,
    한 번 읽을 때 역할이 바로 구분되게 만들고 싶음
- Result:
  - `현재 위치`는
    phase status snapshot과 한 줄 현재 판단만 남기는 것이 맞다고 봤다
  - 별도 summary 섹션은
    `지금부터의 큰 흐름`
    으로 바꿔,
    - 방금 정리된 구현 구간 (`Phase 18 ~ 20`)
    - 병행 보조 트랙 (`Support Track`)
    - 다음 main phase (`Phase 21`)
    - 그 다음 확장 구간 (`Phase 22 ~ 25`)
    을 설명하는 역할로 정리했다
  - 의미:
    - 이제 roadmap tail은
      - `현재 위치` = 상태판
      - `지금부터의 큰 흐름` = 다음 진행 안내판
      으로 읽는 것이 자연스럽다

### 2026-04-16 - `Phase 18 ~ 20`은 같은 묶음으로 읽히더라도 완료 상태는 다르고, global chapter layer를 phase 위에 또 만드는 것은 과하다
- Request topic:
  - 사용자가 roadmap을 읽다가
    `Phase 18 ~ 20`이 다 끝난 것인지,
    `support track`이 정확히 무엇인지,
    `Phase 5 first chapter`가 implying 하는 `second chapter`가 실제로 있는지,
    phase 위에 chapter 구조를 한 번 더 두는 것이 맞는지 질문함
- Interpreted goal:
  - roadmap을 읽는 사람이 상태를 오해하지 않도록 정리하고,
    앞으로 프로젝트 구조를 phase / chapter / support track 기준으로 어디까지 계층화할지 기준을 세우고 싶음
- Result:
  - `Phase 18`은 아직 fully closed가 아니다
    - `PHASE18_CURRENT_CHAPTER_TODO.md` 기준으로 remaining implementation backlog가 남아 있다
  - `Phase 19`, `Phase 20`은 manual checklist까지 완료된 상태다
  - 따라서 roadmap에서는
    - `Phase 18 = 진행형`
    - `Phase 19 = 완료`
    - `Phase 20 = 완료`
    로 읽히게 구분을 더 직접적으로 적는 것이 맞다
  - `support track`은
    - plugin / registry / bootstrap / hygiene 같은 repo-local 지원 tooling 묶음이며
    - main finance feature phase와는 분리해서 보는 것이 맞다
  - `Phase 5 first chapter`는 historical 표현이다
    - 실제 `second chapter`가 formal하게 이어진 것이 아니라,
      후속 큰 흐름은 `Phase 6`으로 분리되었다
  - 구조화 원칙:
    - phase 위에 global chapter layer를 또 만드는 것은 과하다
    - 기본 축은
      - roadmap = phase
      - active long phase 안의 세부 실행 = chapter / workstream
      - main product work가 아닌 repo-local tooling = support track
    - 즉 chapter는 phase 내부에서만 선택적으로 쓰고,
      phase 전체를 다시 chapter 상위 계층으로 감싸는 구조는 권장하지 않는다

### 2026-04-16 - `MASTER_PHASE_ROADMAP.md`는 phase 문서가 쌓일수록 순서와 현재 위치를 다시 정리해 주지 않으면 읽기 난도가 급격히 올라간다
- Request topic:
  - 사용자가 `MASTER_PHASE_ROADMAP.md`를 읽다가,
    phase 순서가 뒤섞여 있고 원활한 작업을 위해 한 번 refresh가 필요하다고 요청함
- Interpreted goal:
  - 단순 문구 수정이 아니라
    현재 기준의 phase 순서, support track 위치, current reading order를 다시 읽기 좋게 만들고 싶음
- Result:
  - roadmap의 실제 문제는 `Phase 6`, `Phase 16`, `현재 위치`가 뒤쪽에 늦게 밀려 있어
    phase 흐름이 순차적으로 읽히지 않는 것이었다
  - 그래서
    - `Phase 6`을 `Phase 5` 뒤로
    - `Phase 16`을 `Phase 15` 뒤로
    - `현재 위치`, `Phase 18~25 Draft Big Picture`, `앞으로의 운영 방식`
      을 tail summary 영역으로 다시 정리했다
  - 추가로
    - `빠른 읽기`
    - 현재 추천 reading order
    - support track은 main phase가 아니라는 점
    도 같이 드러나게 정리했다
  - 의미:
    - roadmap은 phase가 많아질수록 “문서 누적본”이 아니라
      **현재 기준의 읽기 경로를 다시 안내하는 문서**로 주기적으로 refresh해야 한다

### 2026-04-16 - 기존 `Phase 21` automation 묶음은 main phase가 아니라 support track으로 빼고, 새 `Phase 21`은 deep validation으로 다시 잡는 것이 맞다
- Request topic:
  - 사용자가 기존 `Phase 21` checklist를 보고,
    이건 quant project 자체의 개발이 아니라 agent / plugin / skill 환경 정리에 가깝다고 지적함
- Interpreted goal:
  - old automation work는 버리지 않되 main phase sequence에서 빼고,
    roadmap 문서를 기준으로 현재 product에 맞는 새 `Phase 21`을 다시 설계하고 싶음
- Result:
  - 기존 `Research Automation And Experiment Persistence` 묶음은
    main finance phase가 아니라 support track으로 재분류하는 것이 맞다고 판단했다
  - 그 작업은
    - phase bundle bootstrap
    - current candidate registry
    - hygiene / plugin / skill sync
    같은 repo-local support tooling이므로,
    product roadmap 번호를 차지하지 않게 정리했다
  - main roadmap의 새 `Phase 21`은
    `Integrated Deep Backtest Validation`
    으로 다시 설계했다
  - 그 다음 큰 흐름도 다시 정리했다:
    - `Phase 21` deep validation
    - `Phase 22` portfolio-level candidate construction
    - `Phase 23` quarterly / alternate cadence productionization
    - `Phase 24` new strategy expansion
    - `Phase 25` pre-live operating system and deployment readiness
  - 의미:
    - 이제 roadmap이 다시 "이 프로젝트 안에서 실제로 만들어야 할 것" 중심으로 읽히게 되었다

### 2026-04-16 - Phase 21 QA 문서는 Phase 20 UI rename 영향은 작고, 오히려 next-phase handoff 문맥을 업데이트하는 편이 더 중요했다
- Request topic:
  - 사용자가 `Phase 21` QA를 진행하겠다고 하며,
    `Phase 20`에서 수정된 항목이 `Phase 21` checklist에도 영향을 주는지 확인을 요청함
- Interpreted goal:
  - `Phase 21` checklist가 현재 UI/문서 상태와 어긋나지 않는지 확인하고,
    꼭 필요한 부분만 업데이트해서 QA 중 혼선을 줄이고 싶음
- Result:
  - `PHASE21_TEST_CHECKLIST.md`의 핵심 검증 대상은
    script / registry / workflow 문서 재사용성이라서,
    `Phase 20`의 버튼 이름 변경이 직접 테스트 대상을 바꾸지는 않았다
  - 다만 사용자 혼선을 줄이기 위해
    "Phase 20 버튼 이름 변경은 이번 checklist의 핵심 검증 대상이 아니다"라는 안내를 추가했다
  - 반면 `PHASE21_NEXT_PHASE_PREPARATION.md`에는
    아직 `Phase 20` operator workflow가 미해결 질문처럼 남아 있었기 때문에,
    `Phase 20` manual validation completed 상태를 반영해
    다음 자연스러운 방향이 `Phase 22` deep validation 준비라는 쪽으로 handoff를 정리했다

### 2026-04-16 - Phase 20은 manual checklist까지 끝났으므로 operator workflow hardening phase로 닫아도 된다
- Request topic:
  - 사용자가 `Phase 20` checklist 완료 확인을 요청함
- Interpreted goal:
  - `manual_validation_pending`으로 남아 있던 상태를 실제 검수 완료 기준으로 올릴지 판단하고,
    관련 phase 문서와 roadmap을 같은 상태로 맞추고 싶음
- Result:
  - `PHASE20_TEST_CHECKLIST.md` 기준의 user-facing 검수가 완료된 것으로 본다
  - 따라서 `Phase 20` 상태는
    `phase complete / manual_validation_completed`
    로 올리는 것이 맞다
  - `CURRENT_CHAPTER_TODO`, `COMPLETION_SUMMARY`, `phase plan`, `roadmap`, `doc index`, root logs를 이 상태로 함께 동기화했다
  - 의미:
    - `Phase 20`은 current candidate -> compare -> weighted -> saved -> replay/load-back workflow를
      이제 문서상으로도 완료된 operator hardening phase로 다룰 수 있다

### 2026-04-16 - Saved portfolio replay는 저장 record를 그대로 실행하되, 현재 runtime이 받지 않는 legacy compare key는 걸러주는 편이 더 안전하다
- Request topic:
  - `Replay Saved Portfolio`를 눌렀을 때
    `run_quality_value_snapshot_strict_annual_backtest_from_db() got an unexpected keyword argument 'factor_freq'`
    오류가 발생함
- Interpreted goal:
  - 저장된 포트폴리오의 compare context를 최대한 그대로 재사용하되,
    과거 record 형식 때문에 현재 runtime wrapper가 죽지 않도록 replay 경로를 안전하게 만들기
- Result:
  - 원인은 saved portfolio compare context에 남아 있던 legacy strict-annual override key였다
  - `factor_freq` 같은 값은 예전 record에는 들어 있을 수 있지만,
    현재 strict-annual runtime wrapper 시그니처는 받지 않는다
  - 해결:
    - compare runner 호출 직전에 현재 runner signature를 보고,
      지원하지 않는 kwargs는 걸러서 넘기도록 정리했다
  - 의미:
    - saved portfolio replay는 "현재 runtime이 이해할 수 있는 저장 설정"만 사용해 다시 실행되는 경로로 읽는 것이 맞다
    - 따라서 과거 record와 현재 runtime 사이의 얇은 schema drift가 replay 자체를 막지 않게 되었다

### 2026-04-16 - Saved portfolio 재진입 버튼은 "edit"보다 "saved setup을 compare로 다시 불러온다"는 뜻이 먼저 읽혀야 덜 헷갈린다
- Request topic:
  - 사용자가 `Save This Weighted Portfolio`, `Edit In Compare`, `Replay Saved Portfolio`의 역할이 헷갈린다고 피드백함
- Interpreted goal:
  - save / edit / replay의 차이를 버튼 이름만이 아니라, 저장 시점과 재진입 시점의 설명 문구에서 더 명확히 구분하고 싶음
- Result:
  - `Save This Weighted Portfolio`에서는
    `Portfolio Name`이 source label 또는 strategy 조합 기준 추천 이름으로 먼저 채워지고,
    `Description`은 "왜 저장하는지"를 남기는 메모라는 점을 더 직접적으로 설명하게 바꿨다
  - `Edit In Compare`는 이름 자체가 "저장 record를 여기서 직접 수정한다"는 느낌을 줘서 혼동을 만들었다
  - 그래서 버튼 이름을 `Load Saved Setup Into Compare`로 바꿔,
    "저장된 설정을 compare 화면으로 다시 채운다"는 뜻이 먼저 읽히게 정리했다
  - `Load Saved Setup Into Compare`는 단순히 compare 화면 상단으로 이동하는 버튼이 아니라,
    compare 전략/기간/세부 설정과 weighted portfolio의 weight/date alignment를 다시 채우는 동선으로 설명을 수정했다
  - `Replay Saved Portfolio`는
    저장 당시 compare context와 weighted portfolio 구성을 그대로 다시 실행하는 버튼이라는 점을 더 직접적으로 정리했다
  - checklist도 현재 UI 이름과 실제 동작 기준으로 다시 써서,
    saved portfolio QA 항목이 추상적 문장보다 실제 확인 행동에 가깝게 읽히도록 보강했다

### 2026-04-15 - Phase 20 QA에서 current candidate re-entry는 기능 자체보다 "무엇이 바뀌었는지"를 보여주는 UX가 더 중요하다는 점이 드러났다
- Request topic:
  - `Current Candidate Re-entry` QA 진행 중
    quick action 뜻, registry source, load 이후 무엇이 바뀌는지 이해하기 어렵다는 피드백
- Interpreted goal:
  - 기능 설명을 늘리는 것에 그치지 않고,
    사용자가 버튼을 누른 뒤 compare form 어디가 바뀌었는지 바로 확인할 수 있게 만들기
- Result:
  - `Current Candidate Re-entry`는
    compare를 즉시 실행하는 기능이 아니라
    compare form의 전략/기간/override를 다시 채우는 기능이라는 점을 UI에서 먼저 설명하도록 바꿨다
  - `Load Current Anchors`, `Load Lower-MDD Near Misses`의 뜻도 quick action 수준에서 바로 읽히게 보강했다
  - candidate list는 모든 백테스트 결과가 자동으로 쌓이는 것이 아니라,
    `CURRENT_CANDIDATE_REGISTRY.jsonl`에 curate된 active 후보만 보여준다는 점을 명시했다
  - 그리고 load 직후에는
    `What Changed In Compare` card를 띄워
    - selected strategies
    - date range
    - 핵심 override 요약
    - 어디를 확인하면 되는지
    를 바로 보여주게 만들었다

### 2026-04-15 - Quality Strict Annual에서 Coverage 300 + Historical Dynamic + default contract 조합이 높은 CAGR을 보여도, 최근 phase에서 의도치 않게 느슨해진 것은 아니다
- Request topic:
  - `Quality Snapshot (Strict Annual)`에서
    `US Statement Coverage 300` + `Historical Dynamic PIT Universe` + 대부분 default 값으로 실행했을 때
    `CAGR 42%대 / MDD -24%대`가 나온 것이 유효한지, 최근 phase 작업 중 무언가 느슨해진 것은 아닌지 검토 요청
- Interpreted goal:
  - 현재 높은 수익률 결과가 회귀나 unintended loosening 때문인지,
    아니면 원래 이 research-mode contract에서 나올 수 있는 값인지 구분
- Result:
  - 현재 코드 기준 default contract는 여전히 loose research-mode 성격이다
    - `Quality Strict Annual` 기본 `Top N = 2`
    - `Minimum History = 0M`
    - `Min Avg Dollar Volume 20D = 0.0M`
    - underperformance / drawdown guardrail `off`
    - trend filter / market regime도 기본 `off`
  - 여기에 `Historical Dynamic PIT Universe`를 켜면
    wide preset + dynamic membership + concentrated `Top N = 2`
    조합이 되어, 높은 CAGR이 나와도 이상하지 않다
  - 실제로 과거 문서에도 비슷한 계열 결과가 이미 있다:
    `Phase 5` wide-preset sanity check에서
    `Quality Snapshot (Strict Annual)` + `Coverage 300` + overlay off가
    `CAGR 44.43% / MDD -23.93%`로 기록돼 있다
  - 따라서 이번 결과는 "최근 phase에서 몰래 loosened 됐다"기보다,
    원래 loose default research contract에서 나올 수 있는 결과로 보는 것이 맞다
  - 주의할 점:
    - 이 결과가 높게 보여도 promotion이 `hold`인 이유는
      practical contract와 validation/promotion 기준을 통과하지 못하기 때문이며,
      practical candidate one-pager에서 쓰는 계약과는 다르다
  - 정리:
    - 현재 결과는 유효한 research result로 볼 수 있다
    - 다만 실전형 candidate와 직접 비교하면 안 되고,
      apples-to-apples 비교를 하려면
      `12M history`, `5M liquidity`, guardrail `on`, chosen benchmark / trend contract 같은 practical setting을 같이 맞춰야 한다

### 2026-04-15 - strict annual quality backtest error was caused by shadow sample entrypoints lagging behind the new contract argument
- Request topic:
  - `Quality Snapshot (Strict Annual)` backtest raised
    `get_statement_value_snapshot_shadow_from_db() got an unexpected keyword argument 'rejected_slot_handling_mode'`
- Interpreted goal:
  - identify the real mismatch and fix it without changing intended strategy behavior
- Result:
  - the bug was not in the strategy logic itself,
    but in the handoff between runtime wrappers and `finance/sample.py` shadow DB helpers
  - runtime wrappers had already moved to the explicit contract argument
    `rejected_slot_handling_mode`
  - but the three shadow sample entrypoints for
    quality / value / quality+value strict annual
    still only accepted the older boolean pair
    `rejected_slot_fill_enabled` and `partial_cash_retention_enabled`
  - fix:
    - add `rejected_slot_handling_mode` to those sample entrypoints
    - normalize it back into the legacy booleans internally
  - expected outcome:
    - strict annual shadow paths now accept the same contract language as the runtime/UI path,
      so the quality backtest should run again without this argument mismatch

### 2026-04-15 - Phase 20의 핵심은 후보를 더 찾는 일이 아니라, 현재 후보를 다시 쓰는 operator workflow를 다듬는 일이었다
- Request topic:
  - Phase 20을 중간에 끊지 않고 끝까지 진행하고 checklist까지 정리
- Interpreted goal:
  - current candidate -> compare -> weighted portfolio -> saved portfolio 재진입 흐름을 practical closeout 기준으로 정리
- Result:
  - `Phase 20` first work unit에서 current candidate를 compare로 다시 보내는 UI ingress를 열었다
  - second work unit에서 compare source context를 weighted portfolio와 saved portfolio까지 이어,
    현재 compare bundle의 출처와 다음 행동을 더 직접적으로 보이게 만들었다

### 2026-04-15 - compare strict annual에서는 `Guardrail / Reference Ticker` 이동 후 남은 예전 변수 참조가 실제 런타임 에러를 만들 수 있었다
- Request topic:
  - compare strict annual 화면에서
    `NameError: name 'guardrail_reference_ticker' is not defined`
    와 함께 form 경고가 발생함
- Interpreted goal:
  - `Guardrail / Reference Ticker`를 `Guardrails`로 옮긴 뒤 compare path에도 같은 ownership이 끝까지 맞는지 확인하고 에러를 없애고 싶음
- Result:
  - 원인은 compare `Quality Snapshot (Strict Annual)` 경로에 남아 있던 예전 변수 대입 한 줄이었다
  - `Real-Money Contract`에서는 더 이상 `guardrail_reference_ticker`를 직접 만들지 않는데,
    compare quality block만 예전 대입문이 남아 있어 렌더 중 `NameError`가 났다
  - 해당 stale assignment를 제거해 compare strict annual도
    single strict annual과 동일하게
    `Guardrails` expander 안에서만 guardrail reference ticker를 다루도록 정리했다
  - `Missing Submit Button` 경고는 form 전체가 이 예외로 중간에 끊기면서 따라 나온 2차 증상으로 해석하는 것이 맞다

### 2026-04-16 - `Weighted Portfolio Builder` 상단 정보는 compare 메타정보보다 "지금 무엇을 섞는가"를 먼저 보여주는 편이 더 이해하기 쉽다
- Request topic:
  - 사용자가 `Weighted Portfolio Builder`의 `current compare bundle` 및 기타 정보가 UX/UI적으로 잘 읽히지 않는다고 지적함
- Interpreted goal:
  - weighted builder에 들어왔을 때
    - 지금 어떤 compare 결과를 조합하려는지
    - 어떤 전략들을 실제로 섞게 되는지
    - 다음에 무엇을 해야 하는지
    를 먼저 읽히게 만들고 싶음
- Result:
  - 기존의 `Current Compare Bundle` 느낌의 내부 맥락 카드 대신,
    `What You Are Combining` 구조로 다시 정리했다
  - 상단에는
    - 들어온 경로
    - 묶음 이름
    - 비교 기간
    - 조합할 전략 수
    를 보여주고
  - 그 아래에는
    `Strategy / Period / CAGR / MDD / Promotion`
    표를 배치해, 실제로 어떤 compare 결과를 섞는지 한 번에 보이게 했다
  - 마지막에는 "위 전략 표 확인 -> weight 입력 -> date alignment 선택 -> build" 순서의 다음 행동을 명시했다

### 2026-04-16 - `Compare & Portfolio Builder`에서는 divider가 진입 도구 아래가 아니라 각 메인 단계 사이에 있는 편이 더 자연스럽다
- Request topic:
  - 사용자가 `Quick Re-entry From Current Candidates` 아래 line은 빼고,
    `Strategy Comparison`, `Weighted Portfolio Builder`, `Saved Portfolios` 사이에는 line을 넣어달라고 요청함
- Interpreted goal:
  - compare 진입 보조 도구와 실제 주요 작업 단계의 시각적 구분을 더 자연스럽게 만들고 싶음
- Result:
  - `Quick Re-entry From Current Candidates` 바로 아래 divider는 제거했다
  - 대신 compare 결과가 보인 뒤에 divider를 넣어 `Strategy Comparison -> Weighted Portfolio Builder`를 나누고,
    weighted builder 뒤에 한 번 더 divider를 넣어 `Weighted Portfolio Builder -> Saved Portfolios`를 구분하도록 바꿨다
  - 따라서 현재 divider는 보조 ingress가 아니라 세 main workflow stage를 구분하는 역할로 읽히게 되었다

### 2026-04-16 - Phase 20 checklist는 현재 UI 이름 기준으로 다시 써야 테스트 문서 역할을 제대로 한다
- Request topic:
  - 사용자가 영어/한국어 UI 이름이 중간에 바뀌면서 `PHASE20_TEST_CHECKLIST.md`를 따라 테스트하기 어려워졌다고 지적함
- Interpreted goal:
  - checklist를 "예전 대화에서 쓰던 이름"이 아니라 "현재 화면에 실제로 보이는 이름" 기준으로 다시 정리하고 싶음
- Result:
  - checklist 상단에 예전 이름 -> 현재 UI 이름 대응표를 추가했다
  - `Current Candidate Re-entry`, `Current Compare Bundle` 같은 예전 표현 대신
    `Quick Re-entry From Current Candidates`, `What You Are Combining`, `Compare Form Updated`
    같은 현재 화면 기준 이름으로 다시 썼다
  - 각 섹션에 `확인 위치`를 더 구체적으로 적어, tester가 어느 제목/구획을 찾아야 하는지 바로 보이게 정리했다
  - saved portfolio는 `Edit In Compare`, `Replay Saved Portfolio`, `Source & Next Step` 기준으로
    다시 수정할지 그대로 재실행할지 판단이 더 쉬워졌다
  - 따라서 `Phase 20`은
    "새 후보 탐색"보다
    "현재 후보를 operator workflow 안에서 더 쉽게 다시 쓰는 일"
    을 practical closeout 수준으로 정리한 phase로 보는 것이 맞다

### 2026-04-13 - 현재 우선순위는 기능 확장보다 downside-focused practical refinement
- Request topic:
  - 낮은 `MDD`, 높은 수익률, 그리고 실전 사용 가능 전략을 찾는 것이 지금 핵심인지 확인
- Interpreted goal:
  - feature expansion보다 practical candidate quality improvement를 우선순위로 둘지 정리
- Result:
  - 현재 우선순위는 새로운 전략 family나 blanket gate relaxation이 아니라,
    existing strongest candidates를 기준으로 `MDD`를 더 낮추거나
    같은 gate에서 더 좋은 return/MDD tradeoff를 찾는 bounded refinement다
  - 추천 순서는:
    1. `Value`
    2. `Quality + Value`
    3. `Quality`

### 2026-04-13 - Phase 16 first pass에서 `Value`는 lower-MDD near-miss, `Quality + Value`는 stronger practical point를 확보함
- Request topic:
  - Phase 16 downside refinement를 계속 진행
- Interpreted goal:
  - same gate를 유지하며 `MDD`를 낮추거나, 같은 `MDD`에서 `CAGR`를 더 높일 수 있는지 확인
- Result:
  - `Value`:
    - current best practical point는 여전히 `Top N = 14 + psr`
    - 더 낮은 `MDD` near-miss로 `+ pfcr`가 있었지만 gate는 `production_candidate / watchlist`로 약해졌다
  - `Quality + Value`:
    - `operating_income_yield -> por` replacement를 더한 조합이
      `CAGR = 31.82% / MDD = -26.63% / real_money_candidate / small_capital_trial`
      로 current strongest practical point가 됐다

### 2026-04-13 - 지금 시점엔 root 로그 압축과 current candidate one-page가 작업 속도에 더 중요함
- Request topic:
  - 문서 수가 많아져 작업이 느려지는지, 지금 정리할 시점인지 질문
- Interpreted goal:
  - context hygiene 관점에서 무엇을 먼저 정리해야 하는지 판단
- Result:
  - 문제는 문서 개수 자체보다,
    root 로그와 전략 후보 정보가 너무 넓게 퍼져 있어
    다시 context를 잡는 데 시간이 오래 걸리는 구조였다
  - 그래서 우선순위는:
    1. root 로그 압축
    2. current candidate summary one-pager
    3. runtime artifact/session hygiene 정리

### 2026-04-13 - Codex plugin은 이 프로젝트에서 skill 배포 단위로 유용할 가능성이 높다
- Request topic:
  - Codex CLI plugin 도입이 현재 프로젝트에서 실질적으로 도움이 되는지 검토
- Interpreted goal:
  - 반복되는 finance backtest refinement workflow를 plugin/skill 단위로 묶는 것이 효율적인지 판단
- Result:
  - 공식 Codex 안내 기준으로 plugin은 reusable workflow의 installable distribution unit이고,
    skill은 그 안의 authoring format에 가깝다
  - 이 프로젝트는:
    - bounded backtest refinement
    - phase report / hub / one-pager / backtest log 동기화
    - runtime artifact hygiene
    같은 반복 workflow가 분명해서 plugin 적용성이 높다
  - 그래서 repo-local draft plugin
    `.aiworkspace/plugins/quant-finance-workflow`
    와 draft skill
    `finance-backtest-candidate-refinement`
    을 만드는 것이 실용적이라고 판단했다
  - 첫 practical script로
    `check_finance_refinement_hygiene.py`
    를 붙여,
    refinement 이후 문서/산출물 정리가 빠진 곳을 빠르게 점검할 수 있게 하는 방향이 적절하다고 봤다

### 2026-04-13 - finance refinement hygiene script는 앞으로 Codex가 필요 시 우선적으로 호출하는 운영 보조 도구로 본다
- Request topic:
  - 방금 만든 checklist script를 앞으로 어떻게 사용할지,
    사용자 직접 호출용인지 Codex 자동 사용용인지 정리 요청
- Interpreted goal:
  - script를 일회성 도구가 아니라 운영 규칙으로 올릴지 결정
- Result:
  - 이 script는 사용자가 직접 실행할 수도 있지만,
    기본 해석은 Codex가 refinement work unit 중 필요할 때 먼저 호출하는 운영 보조 도구로 두는 것이 맞다
  - 권장 호출 시점은:
    1. refinement 결과 문서 반영 직후
    2. commit 직전
    3. phase closeout 직전
  - 이 기준을 `AGENTS.md`와 runtime hygiene 문서에 반영한다

### 2026-04-13 - Phase 16 closeout 결과, bounded downside refinement는 끝났고 다음 질문은 구조 문제로 이동함
- Request topic:
  - `Value` lower-MDD rescue와 `Quality + Value` strongest-point downside follow-up을 마무리하고 closeout까지 정리
- Interpreted goal:
  - bounded `Top N / one-factor / overlay / benchmark` 범위 안에서
    lower-MDD practical candidate가 더 가능한지 확인하고,
    다음 phase 질문을 분명히 남기기
- Result:
  - `Value`:
    - current best practical point는 여전히 `Top N = 14 + psr`
    - `+ pfcr`는 `MDD`를 `-21.16%`까지 낮췄지만
      `production_candidate / watchlist`를 넘지 못했다
    - `Top N = 15 + psr + pfcr`는 gate를 회복했지만 downside edge를 잃었다
  - `Quality + Value`:
    - strongest practical point는 여전히
      `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
    - `Top N = 9`와 `current_ratio -> cash_ratio`는 더 낮은 `MDD`를 보였지만
      `production_candidate / watchlist`로 내려갔다
    - `Ticker Benchmark = SPY`는 same `CAGR / MDD`를 유지하지만
      `small_capital_trial -> paper_probation`으로 한 단계 내려간다
  - 결론:
    - Phase 16 범위 안에서는 lower-MDD exact rescue가 없었다
    - 다음 phase는 bounded tweak 반복보다
      구조적인 downside improvement를 다루는 편이 맞다

### 2026-04-14 - compare / weighted / saved portfolio는 실전 승격 semantics가 아니라 candidate bridge로 읽는 것이 맞다
- Request topic:
  - compare / weighted portfolio / saved portfolio workflow가 current practical candidates의 structural downside-improvement path로 쓸 수 있는지 검토
- Interpreted goal:
  - weighted bundle가 real-money / promotion / shortlist / deployment 의미를 자체적으로 갖는지,
    그리고 어떤 operator bridge가 이미 있는지 분리해서 확인
- Result:
  - `Compare`는 개별 전략의 backtest 결과를 나란히 보는 연구용 surface다
  - `Weighted Portfolio`는 compare 결과를 월별 composite로 합치는 포트폴리오 합성 surface다
  - `Saved Portfolio`는 compare context + weights + date policy를 저장하고 rerun할 수 있게 하는 재현용 연구 아티팩트다
  - weighted bundle 자체에는 별도의 `promotion / shortlist / deployment` semantics가 새로 붙지 않는다
  - 실전 후보 해석은 여전히 각 구성 전략의 real-money surface에서 읽는 것이 맞다
  - Phase 17에서는 compare -> weighted builder -> saved portfolio -> rerun bridge를
    "후보 개선을 묶는 operator workflow"로 설명하되,
    실전 gate를 대체하는 계층으로 쓰면 안 된다는 점을 명시해야 한다

### 2026-04-14 - Phase 17은 bounded tweak 이후 structural downside improvement를 current code 기준으로 좁히는 phase로 여는 것이 맞다
- Request topic:
  - Phase 16 closeout 이후 다음 단계 진행
- Interpreted goal:
  - 지금부터는 어떤 구조 레버를 우선순위로 볼지와,
    candidate consolidation을 메인/보조 중 어디에 둘지 정리
- Result:
  - strict annual current code 기준으로 가장 먼저 볼 구조 레버는:
    - `partial cash retention`
    - `defensive sleeve risk-off`
    - `concentration-aware weighting`
  - 이 중 first implementation slice 추천은
    `partial cash retention`이다
    - 이유:
      - current architecture와 가장 가깝고
      - `Value`와 `Quality + Value` 둘 다에 공통 적용 가능하며
      - lower-MDD same-gate rescue와 직접 맞닿아 있다
  - weighted portfolio / saved portfolio는 유용하지만
    immediate practical-candidate work의 메인 트랙은 아니고
    operator bridge 보조 트랙으로 두는 편이 맞다

### 2026-04-14 - 새로운 전략과 기존 전략 고도화는 둘 다 예정이지만, 우선순위는 기존 핵심 전략 고도화가 먼저다
- Request topic:
  - 지금은 새로운 기능이나 새 전략을 만드는 단계인지,
    기존 `Value / Quality / Quality + Value` 전략을 고도화하는 단계인지
    그리고 새로운 전략 및 추가 고도화는 언제 할 예정인지 질문
- Interpreted goal:
  - 앞으로의 개발 우선순위를
    기존 전략 고도화 / 구조 개선 / 새 전략 확장
    순서로 분명히 이해하고 싶음
- Result:
  - 현재 Phase 17의 메인 목표는
    새 전략 family를 여는 것이 아니라
    기존 핵심 전략(`Value`, `Quality + Value`, 보조로 `Quality`)을
    실전형 관점에서 더 고도화하는 것이다
  - 특히 지금은
    lower-MDD same-gate practical candidate를 만들기 위한
    구조 레버를 여는 것이 우선순위다
  - 새로운 전략이나 더 넓은 전략 확장은 예정에서 빠진 것이 아니라
    **현재 strongest/current candidates가 충분히 정리된 뒤**
    또는 structural downside-improvement first slice가 안정된 뒤
    다음 우선순위로 다시 열 가능성이 높다
  - 즉 현재 순서는:
    1. existing core strategy structural refinement
    2. practical candidate consolidation / operator bridge 정리
    3. 그 다음 필요하면 새 전략 또는 더 넓은 확장

### 2026-04-14 - Phase 17 first implementation slice로 strict annual partial cash retention을 연결했다
- Request topic:
  - Phase 17 실제 구현 시작
- Interpreted goal:
  - existing strict annual strongest/current candidate를 더 낮은 `MDD`로 개선할 수 있는
    첫 구조 레버를 코드에 연결하고,
    이후 representative rerun이 가능하도록 public UI/runtime contract까지 같이 열기
- Result:
  - strict annual family 3종에 `partial_cash_retention_enabled` contract를 추가했다
  - 현재 동작은:
    - trend filter partial rejection 시
      - `off`:
        survivors reweighted
      - `on`:
        rejected slot share retained as cash
  - 적용 범위는 첫 slice 기준으로
    `Trend Filter`의 부분 탈락에 한정되고,
    `market regime`와 guardrail의 전체 risk-off는 그대로 full cash다
  - UI single / compare, runtime wrapper, sample helper, core strategy, selection interpretation, warning/meta surface까지 같이 동기화했다
  - synthetic smoke에서는 expected behavior가 확인됐고,
    DB-backed live rerun은 현재 로컬 shadow-factor data preflight 상태에 따라 추가 데이터 준비가 필요할 수 있다

### 2026-04-14 - partial cash retention first pass는 downside lever로는 유효하지만 same-gate practical rescue까지는 못 갔다
- Request topic:
  - Phase 17 다음 단계로
    `partial cash retention`을 실제 `Value` / `Quality + Value` anchor에 적용해 representative rerun 진행
- Interpreted goal:
  - 새 구조 레버가 실제 strongest/current candidate를 바꿀 정도로 충분한지 확인하고,
    다음 구현 우선순위를 결정
- Result:
  - `Value` current anchor(`Top N = 14 + psr`, `Trend Filter = on`)에서
    `cash retention on`은
    `MDD = -29.25% -> -15.85%`
    로 큰 개선을 만들었지만,
    `CAGR = 25.92% -> 20.11%`로 내려가고
    `hold / blocked`를 벗어나지 못했다
  - `Quality + Value` strongest point에서도
    `MDD = -29.72% -> -15.07%`
    로 큰 개선이 있었지만,
    `CAGR = 30.01% -> 20.03%`로 크게 내려가고
    역시 `hold / blocked`에 머물렀다
  - 공통 해석:
    - `partial cash retention`은 기능적으로는 분명히 유효한 downside lever다
    - 하지만 current first pass에서는
      cash 비중 증가로 인한 return drag가 너무 커서
      same-gate practical rescue lever로는 부족하다
  - follow-up decision:
    - next structural lever priority는
      idle cash drag를 줄일 수 있는

### 2026-04-15 - Phase 20 첫 구현은 current candidate를 compare로 다시 보내는 재진입 동선이 가장 효과적이다
- Request topic:
  - `Phase 20` 메인 작업 진행
- Interpreted goal:
  - strongest / near-miss candidate를 문서 중심 재참조에서 UI workflow 재진입으로 옮기는 첫 실제 구현 단위를 만든다
- Result:
  - `Compare & Portfolio Builder` 안에 `Current Candidate Re-entry` surface를 추가하는 것이
    Phase 20 첫 work unit으로 가장 자연스럽다고 판단했다
  - 이유:
    - current candidate는 문서화는 잘 되어 있지만 UI 재진입 동선이 길었고
    - compare는 이후 weighted portfolio / saved portfolio로 이어지는 가장 중요한 operator ingress이기 때문이다
  - 현재 구현 결과:
    - `Load Current Anchors`
    - `Load Lower-MDD Near Misses`
    - custom candidate bundle selection
    으로 strict annual current candidate를 compare form으로 바로 불러올 수 있게 되었다
      `defensive sleeve risk-off`
      쪽이 더 자연스럽다

### 2026-04-14 - defensive sleeve risk-off는 구현 가치가 있었지만 current anchor를 더 좋게 만들진 못했다
- Request topic:
  - Phase 17 다음 단계로
    strict annual `defensive sleeve risk-off`를 구현하고
    `Value` / `Quality + Value` current anchor에 representative rerun 적용
- Interpreted goal:
  - `cash_only`보다 return drag를 덜 만들면서
    same-gate lower-MDD rescue가 가능한지 확인
- Result:
  - strict annual family 3종에
    `risk_off_mode = cash_only | defensive_sleeve_preference`
    와 `defensive_tickers` contract를 연결했다
  - 구현 중 defensive sleeve ticker가 candidate-liquidity 계산에 섞여
    false `Liquidity Excluded Count`를 만드는 회귀가 있었고,
    candidate universe와 sleeve ticker를 분리해 수정했다
  - 회귀 수정 후 representative rerun 기준:
    - `Value` current anchor:
      - `cash_only` = `28.21% / -24.55% / real_money_candidate / paper_probation / review_required`
      - `defensive sleeve` = `28.11% / -25.14% / real_money_candidate / paper_probation / review_required`
    - `Quality + Value` current strongest point:
      - `cash_only` = `31.82% / -26.63% / real_money_candidate / small_capital_trial / review_required`
      - `defensive sleeve` = `31.79% / -27.19% / real_money_candidate / small_capital_trial / review_required`
  - 해석:
    - gate는 유지됐다
    - 하지만 `MDD`를 더 낮추진 못했고 오히려 소폭 더 나빠졌다
    - activation도 적어서 current anchor를 바꿀 정도의 구조 변화는 아니었다
  - follow-up decision:
    - next structural lever priority는
      `concentration-aware weighting`
      으로 넘어가는 편이 더 자연스럽다

### 2026-04-14 - concentration-aware weighting은 구현 가치가 있었지만 current anchor의 lower-MDD rescue까지는 못 갔다
- Request topic:
  - Phase 17 다음 단계로
    strict annual `concentration-aware weighting`을 구현하고
    `Value` / `Quality + Value` current anchor에 representative rerun 적용
- Interpreted goal:
  - equal-weight top-N을 조금 더 부드럽게 만들어
    same-gate lower-MDD practical candidate가 가능한지 확인
- Result:
  - strict annual family 3종에
    `weighting_mode = equal_weight | rank_tapered`
    contract를 연결했다
  - current first slice의 `rank_tapered`는
    optimizer가 아니라
    ranked top-N에 mild taper를 주는 bounded weighting mode다
  - representative rerun 기준:
    - `Value` current anchor:
      `rank_tapered`가 gate는 유지했지만
      `MDD = -24.55% -> -25.87%`로 더 나빠졌고
      `Rolling Review = watch -> caution`으로 약해졌다
    - `Quality + Value` current strongest point:
      `rank_tapered`가 gate는 유지했고
      `CAGR = 31.82% -> 32.92%`로 높아졌지만
      `MDD = -26.63% -> -27.60%`로 더 나빠졌다
  - 결론:
    - `concentration-aware weighting`은
      유효한 structural lever로 구현 가치가 있었다
    - 하지만 current first pass에서는
      same-gate lower-MDD rescue를 만들지 못했다
    - 즉 current `Value` / `Quality + Value` anchor는 그대로 유지된다

### 2026-04-14 - Phase 17 closeout 결과, first three structural levers는 다 구현됐지만 current anchor를 바꾸진 못했다
- Request topic:
  - concentration-aware weighting까지 포함한 current structural pass를 마무리하고
    next-phase 방향을 정리
- Interpreted goal:
  - Phase 17을 closeout할 수준인지,
    그리고 다음엔 structural redesign과 candidate consolidation 중 무엇을 더 앞세워야 하는지 판단
- Result:
  - Phase 17은 practical closeout으로 닫는 것이 맞다
  - 이유:
    - `partial cash retention`
    - `defensive sleeve risk-off`
    - `concentration-aware weighting`
    first three structural levers가 모두 구현되고 representative rerun까지 완료됐기 때문이다
  - current common conclusion:
    - `Value` current anchor 유지
    - `Quality + Value` current strongest practical point 유지
    - same-gate lower-MDD exact rescue는 아직 없다
  - next-phase reading:
    - 메인 트랙:
      `larger structural redesign`
    - 보조 트랙:
      `candidate consolidation / operator bridge`
  - 새 major phase는 이 방향을 사용자와 다시 확인한 뒤 여는 것이 맞다

### 2026-04-14 - strict annual에 재사용할 concentration-aware weighting 패턴 탐색
- Request topic:
  - strict annual에 붙일 수 있는 재사용 가능한 weighting pattern과 safe insertion point 확인
- Interpreted goal:
  - equal-weight 외의 기존 allocation logic, rank-based taper/cap 여부, 그리고 UI/runtime contract를 빠르게 분류
- Result:
  - position-level non-equal weighting은 `risk_parity_trend`의 `1/vol` 정규화가 가장 명확한 기존 패턴이었다
  - quality/value strict annual family는 현재 selection 이후 `top N -> equal weight`만 사용하고 있어, rank-based taper/capped weight는 별도 구현이 없었다
  - 가장 안전한 삽입점은 `finance.strategy.quality_snapshot_equal_weight(...)`의 rebalancing 블록에서 `selected_snapshot` 확정 직후, `allocation = base_balance / allocation_base_count` 이전이다
  - UI/runtime 쪽 기존 contract는 `strategy_key`, `snapshot_mode`, `snapshot_source`, `factor_freq`, `universe_contract`, `dynamic_candidate_tickers`, `dynamic_target_size` 조합을 그대로 재사용하는 쪽이 가장 자연스럽다

### 2026-04-14 - strict annual trend rejection slot-fill redesign first-slice review
- Request topic:
  - trend rejection된 raw top-N slot을 next-ranked eligible name으로 채우는 구조의 first slice 후보 검토
- Interpreted goal:
  - strict annual current architecture를 유지하면서 cash drag를 줄일 수 있는 가장 안전한 slot-fill redesign 위치와 충돌 지점을 정리
- Result:
  - insertion point는 `finance/strategy.py`의 `quality_snapshot_equal_weight(...)` rebalancing block에서 `selected_snapshot = ranked.head(top_n)` 직후가 1차 후보다
  - 현재 result surface는 `Raw Selected Ticker/Count`, `Overlay Rejected Ticker/Count`, `Selected Count`, `Cash`, `Partial Cash Retention Active/Base Count`, `Defensive Sleeve Ticker/Count`, `Weighting Mode`, `Next Weight`를 함께 읽어야 한다
  - slot-fill redesign은 `partial cash retention`과 직접 충돌하지 않지만, 같은 trend rejection 이벤트를 서로 다른 철학으로 읽게 만들므로 둘을 동시에 켤 때 해석 문구를 분리해야 한다
  - `defensive sleeve risk-off`와는 부분 reject lane과 full risk-off lane이 다르므로 구조적으로는 분리 가능하지만, full reject를 재채움으로 바꾸지 않도록 조건 분기가 필요하다
  - `rank_tapered`와는 rank 기반 selection/weighting이 겹치므로, slot-fill이 들어가면 `equal_weight`/`rank_tapered`보다 먼저 hold set을 재구성하는 contract로 봐야 한다

### 2026-04-14 - Phase 18 first larger-redesign slice는 의미 있는 rescue lane이지만 current anchor replacement는 아니다
- Request topic:
  - `larger structural redesign` 방향으로 실제 구현과 representative rerun을 진행
- Interpreted goal:
  - Phase 17의 first three levers보다 더 큰 구조 변경으로
    same-gate lower-MDD rescue 또는 gate recovery가 가능한지 확인
- Result:
  - strict annual family 3종에
    `Fill Rejected Slots With Next Ranked Names`
    contract를 연결했다
  - 이 contract는
    raw top-N 일부가 `Trend Filter`에 걸릴 때
    현금 유지나 survivor reweighting 전에
    next-ranked eligible name으로 빈 슬롯을 채우는 redesign이다
  - representative rerun first pass 기준:
    - `Value` trend-on probe:
      cash drag와 downside는 개선되지만
      still `hold / blocked`
    - `Quality + Value` trend-on probe:
      `CAGR`, `MDD`, cash share는 개선되지만
      still `hold / blocked`
  - 결론:
    - `next-ranked eligible fill`은 meaningful larger-redesign lane이다
    - 다만 current practical anchor 자체를 교체하는 결과는 아직 아니다

### 2026-04-14 - Value anchor-near follow-up second pass에서도 fill contract rescue는 없었다
- Request topic:
  - Phase 18 first slice 이후
    `Value` current practical anchor 근처에서
    fill contract를 더 직접 적용
- Interpreted goal:
  - first structural probe가 아니라
    실제 current best practical point 근처에서
    same-gate lower-MDD rescue가 가능한지 확인
- Result:
  - `base + psr`, `Top N = 12~16`
  - `base + psr + pfcr`, `Top N = 12~16`
  를 current practical contract로 다시 돌렸다
  - 공통 결론:
    - 모든 candidate가 still `hold / blocked`
    - best lower-MDD near-miss는
      `base + psr + pfcr`, `Top N = 13`
      의 `24.47% / -24.89% / hold / blocked`
  - therefore:
    - Phase 18 first slice는 meaningful redesign reference이긴 하지만
    - current `Value` practical anchor를 교체하는 rescue contract로 보긴 어렵다

### 2026-04-14 - Phase 18은 당분간 deep backtest보다 implementation-first로 운영하는 것이 맞다
- Request topic:
  - 일단 전체적인 기능/구현을 더 만든 뒤 다시 깊게 백테스트하는 편이 낫다는 방향 전환 요청
- Interpreted goal:
  - Phase 18 진행 방식을 rerun-first에서 implementation-first로 재정렬하고,
    남은 구현 항목을 먼저 닫는 쪽으로 execution mode를 바꾸고 싶음
- Result:
  - 현재 기준으로 이 판단이 맞다
  - 이유:
    - Phase 17과 Phase 18 first slice까지의 깊은 rerun은
      bounded/first larger-redesign 질문에는 충분한 근거를 이미 남겼다
    - 지금 더 필요한 것은
      remaining structural redesign slice와 operator support backlog를 먼저 구현해
      strategy space를 더 넓힌 뒤 다시 integrated deep rerun으로 들어가는 것이다
  - 따라서 current operating rule은:
    1. broad deep backtest pause
    2. 새 구현 slice마다 minimal validation만 수행
    3. remaining implementation backlog가 닫힌 뒤 integrated deeper rerun 재개
  - Phase 18 current reading:
    - main track:
      structural redesign implementation
    - support track:
      candidate consolidation / operator bridge implementation

### 2026-04-14 - Phase 18 이후는 구현 우선 -> deep validation 재개 -> 확장 순서로 보는 것이 자연스럽다
- Request topic:
  - 현재 Phase 18까지의 흐름을 다시 보고,
    `Phase 25`까지의 큰 그림과 방향성을 재정리해 보여달라는 요청
- Interpreted goal:
  - 지금 phase가 어디쯤인지와,
    앞으로 구현 / deep backtest / 확장을 어떤 순서로 진행하는 것이 가장 자연스러운지
    상위 roadmap 수준에서 다시 맞추고 싶음
- Result:
  - 현재 reading:
    - `Phase 18`
      larger structural redesign / implementation-first
  - 추천 future sequence:
    1. `Phase 19`
       structural contract expansion and interpretation cleanup
    2. `Phase 20`
       candidate consolidation and operator workflow hardening
    3. `Phase 21`
       research automation and experiment persistence
    4. `Phase 22`
       integrated deep backtest validation
    5. `Phase 23`
       portfolio-level candidate construction
    6. `Phase 24`
       new strategy expansion
    7. `Phase 25`
       pre-live operating system and deployment readiness
  - 핵심 reasoning:
    - 지금은 구현이 먼저 더 쌓여야 deep rerun도 의미가 커진다
    - deep validation은 기능이 더 열린 뒤 다시 여는 편이 낫다
    - portfolio / new strategy / pre-live workflow는 그 다음에 여는 편이 흔들림이 적다
  - therefore:
    - current recommended order는
      **implement first -> validate deeply later -> expand after validation**
      이다

### 2026-04-14 - Phase 19~25는 기술 제목만이 아니라 왜 필요한지까지 같이 설명되어야 한다
- Request topic:
  - `Phase 19~25` 설명을 더 쉽고, 왜 해야 하는지가 드러나게 다시 문서화 요청
- Interpreted goal:
  - future roadmap을 단순한 기술 phase 목록이 아니라,
    사용자가 보고 방향을 판단할 수 있는 설명 문서로 바꾸고 싶음
- Result:
  - roadmap draft와 master roadmap에
    각 phase마다 아래 설명 층을 추가했다:
    - 쉽게 말하면
    - 왜 필요한가
  - 이로써 future roadmap은:
    - 무엇을 하는 phase인지
    - 왜 지금 순서가 그런지
    - 이 phase를 건너뛰면 무엇이 비는지
    를 더 쉽게 읽을 수 있게 됐다

### 2026-04-14 - quarterly strict family를 prototype에서 실전형으로 키우는 일은 지금 immediate priority로 당기지 않는 편이 맞다
- Request topic:
  - annual strict family는 많이 다듬어졌는데,
    quarterly strict family는 아직 prototype 성격이 강하므로
    이를 지금 바로 실전형 트랙으로 올릴지 질문
- Interpreted goal:
  - quarterly productionization을 `Phase 19` 전후 immediate main track으로 당길지,
    아니면 later phase에서 다시 여는 편이 자연스러운지 판단
- Result:
  - 현재 기준으로는 **later phase로 두는 것이 맞다**
  - 이유:
    1. immediate bottleneck은 quarterly family 부재가 아니라
       annual strongest/current candidates의 same-gate lower-MDD rescue와
       structural/operator backlog다
    2. quarterly는 data/coverage/PIT foundation은 많이 복구됐지만,
       current reading은 여전히 prototype / research-oriented family에 더 가깝다
    3. quarterly productionization을 지금 당기면
       `Phase 19~21`의 structural contract / operator workflow / automation 우선순위와 충돌한다
    4. quarterly production-readiness는
       integrated deep validation 이후나
       new strategy expansion phase에서 다시 여는 편이 더 자연스럽다
  - recommended order:
    - near term:
      annual strict family 중심 구현 (`Phase 19~21`)
    - later:
      deep validation 재개 이후 quarterly production-readiness 재평가

### 2026-04-14 - Phase 19 first slice는 rejected-slot handling semantics를 explicit contract로 정리하는 것이 맞다
- Request topic:
  - `Phase 19`를 바로 시작
- Interpreted goal:
  - `Phase 18`에서 늘어난 strict annual structural levers 중
    먼저 operator가 헷갈리기 쉬운 rejection semantics를 usable contract로 정리하고 싶음
- Result:
  - 첫 slice는 `Rejected Slot Handling Contract`로 확정했다
  - 이유:
    1. current UI는
       `rejected_slot_fill_enabled + partial_cash_retention_enabled`
       두 boolean을 사용자가 직접 조합해서 읽어야 했다
    2. same semantics가 form / payload / history / warning에서 분산되어 있어
       이후 deep validation 해석도 더 흔들릴 수 있었다
    3. 따라서 `Phase 19`의 성격인
       structural contract expansion + interpretation cleanup에 가장 잘 맞는 첫 구현이었다
  - implemented contract:
    - `reweight_survivors`
    - `retain_unfilled_as_cash`
    - `fill_then_reweight`
    - `fill_then_retain_cash`
  - compatibility rule:
    - new payload는 explicit mode와 legacy booleans를 같이 남긴다
    - old payload는 booleans만 있어도 explicit mode로 복원한다

### 2026-04-14 - Phase 19 second slice는 history와 interpretation도 같은 contract 언어로 정리해야 한다
- Request topic:
  - `Phase 19` 다음 작업 진행
- Interpreted goal:
  - first slice에서 정리한 `Rejected Slot Handling Contract`가
    form / warning뿐 아니라 history와 interpretation에서도 같은 언어로 읽히게 만들고 싶음
- Result:
  - selection history row가 이제
    `Rejected Slot Handling`, `Filled Count`, `Filled Tickers`
    를 같이 보존한다
  - interpretation summary가 이제
    `Rejected Slot Handling`, `Filled Events`, `Cash-Retained Events`
    를 함께 보여준다
  - row-level interpretation 문구도
    “fill했는지 / 현금으로 남겼는지 / 생존 종목 재배분이었는지”를
    explicit handling contract 기준으로 직접 설명한다
  - history display에서는 internal boolean column을 계속 숨겨
    operator는 contract 언어 중심으로 읽게 유지했다

### 2026-04-14 - Phase 19 세 번째 slice는 risk-off와 weighting도 interpretation contract 언어로 정리해야 한다
- Request topic:
  - `Phase 19` 다음 단계 진행
- Interpreted goal:
  - previous slice에서 정리한 rejected-slot handling과 같은 수준으로
    `Risk-Off`와 `Weighting`도 history / interpretation에서 읽기 쉽게 만들고 싶음
- Result:
  - selection history에
    `Weighting Contract`, `Risk-Off Contract`, `Risk-Off Reasons`, `Defensive Sleeve Tickers`
    를 추가했다
  - interpretation summary에
    `Weighting Contract`, `Risk-Off Contract`, `Defensive Sleeve Activations`
    를 추가했다
  - row-level interpretation 문구가 이제
    - market regime 때문에 full cash로 갔는지
    - defensive sleeve로 회전했는지
    - 최종 weighting contract가 무엇이었는지
    를 더 직접적으로 설명한다

### 2026-04-14 - Phase 19는 practical closeout / manual_validation_pending 상태로 닫는 것이 맞다
- Request topic:
  - `Phase 19` 다음 단계 진행
- Interpreted goal:
  - 현재까지 구현된 contract cleanup work를 closeout 문서, handoff 문서, checklist까지 포함해 정리하고 싶음
- Result:
  - `Phase 19`는 현재 기준으로 practical closeout으로 보는 것이 맞다
  - 이유:
    - rejected-slot handling contract 정리 완료
    - history / interpretation cleanup 완료
    - risk-off / weighting interpretation cleanup 완료
    - phase plan template와 설명 규칙까지 정리 완료
  - 남은 것은 기능 구현이 아니라 manual UI validation이므로
    상태는 `practical closeout / manual_validation_pending`으로 정리했다
  - closeout 문서:
    - completion summary
    - next phase preparation
    - test checklist
    를 같이 생성했다

### 2026-04-14 - Phase 19 kickoff 문서는 용어와 목적을 더 쉽게 풀어써야 한다
- Request topic:
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md`가 너무 어려워서
    무엇을 하는 phase인지, 왜 필요한지 이해하기 어렵다는 피드백
- Interpreted goal:
  - phase kickoff 문서를
    내부자용 압축 메모가 아니라
    operator도 읽을 수 있는 설명 문서로 바꾸고 싶음
- Result:
  - 문서에 아래를 추가했다
    - 이 phase가 무엇을 하는지
    - 왜 지금 필요한지
    - 끝나면 무엇이 좋아지는지
    - 어려운 표현 짧은 해설
      - `contract`
      - `usable contract`
      - `payload`
      - `boolean combination`
      - `slice`
      - `minimal validation`
      - `structural redesign lane`
  - glossary에도 같은 용어를 추가해,
    이후 phase 문서에서도 반복 설명을 줄이고 공통 해석 기준으로 재사용할 수 있게 했다

### 2026-04-14 - 앞으로 phase plan 문서는 쉬운 설명 섹션을 기본으로 포함해야 한다
- Request topic:
  - 앞으로 phase plan 문서를 만들 때
    `쉽게 말하면`, `왜 필요한가`, `이 phase가 끝나면 좋은 점`
    같은 설명 섹션을 기본 규칙으로 넣어 달라는 요청
- Interpreted goal:
  - phase plan이 내부 구현 메모가 아니라,
    사용자가 방향과 이유를 바로 이해할 수 있는 안내 문서가 되게 하고 싶음
- Result:
  - `AGENTS.md`에 phase plan 문서 작성 규칙을 추가했다
  - `Phase 19` kickoff 문서도 같은 기준에 맞춰
    현재 구현 우선순위에서 쓰는 용어를 inline 설명 형태로 보강했다

### 2026-04-14 - Phase 19 kickoff 문서를 template형 최종본으로 정리하고 future template를 따로 만들었다
- Request topic:
  - `Phase 19` 계획 문서의 용어 설명이 너무 파편화되어 있으니,
    최종적으로 한 번 더 UX 관점에서 정리하고
    다음 phase에서도 같은 형태를 재사용하고 싶다는 요청
- Interpreted goal:
  - phase plan 문서를 읽는 경험 자체를 표준화하고,
    앞으로도 같은 설명 구조를 반복 사용하고 싶음
- Result:
  - `Phase 19` kickoff 문서를
    `이 문서는 무엇인가 -> 목적 -> 쉽게 말하면 -> 왜 필요한가 -> 이 phase가 끝나면 좋은 점 -> 현재 구현 우선순위 -> 용어 -> 운영 원칙`
    흐름으로 다시 정리했다
  - `.aiworkspace/note/finance/PHASE_PLAN_TEMPLATE.md`를 새로 만들어,
    이후 phase plan도 같은 설명 구조를 기본으로 쓰도록 준비했다
  - `AGENTS.md`에도 해당 template를 기본 출발점으로 사용하라는 규칙을 추가했다

### 2026-04-14 - Phase 19 checklist 기준으로 strict annual contract UI를 더 쉽게 읽히게 정리했다
- Request topic:
  - `Phase 19` test checklist를 보다가
    `Rejected Slot Handling Contract`, `Weighting Contract`, `Risk-Off Contract`,
    `Defensive Sleeve Tickers`의 뜻과 위치가 화면에서 바로 이해되지 않는다는 피드백
- Interpreted goal:
  - strict annual single/compare form에서
    사용자가 contract를 "찾을 수 있고", "현재 선택이 무슨 뜻인지 바로 읽을 수 있게" 만들고 싶음
- Result:
  - `Advanced Inputs > Overlay & Defensive Rules` 안에
    contract 위치를 직접 설명하는 안내 문구를 추가했다
  - section 제목을 사용자가 찾는 이름에 맞춰
    - `Weighting Contract`
    - `Risk-Off Contract`
    - `Rejected Slot Handling Contract`
    로 정리했다
  - 각 contract 아래에
    현재 선택이 뜻하는 바를 plain language로 바로 읽을 수 있는 설명을 추가했다
  - `Defensive Sleeve Tickers`는
    `Risk-Off Contract = Defensive Sleeve Preference`일 때만
    full risk-off에서 쓰이는 방어 ETF 목록이라는 설명을 보강했다
  - glossary와 Phase 19 checklist도 같은 관점으로 같이 정리했다

### 2026-04-14 - 앞으로 phase test checklist는 checkbox 기반으로 운영하고, 완료 후 다음 단계로 넘어가기로 정했다
- Request topic:
  - 앞으로 test checklist 문서에 사용자가 직접 체크할 수 있는 `[ ]`를 넣고,
    모든 체크가 끝나면 다음 단계로 넘어가는 흐름으로 맞추고 싶다는 요청
- Interpreted goal:
  - phase handoff 이후의 검수 과정을 더 눈에 보이게 만들고,
    "무엇을 확인했는지"를 문서 안에서 바로 남기고 싶음
- Result:
  - `AGENTS.md`에
    - phase test checklist는 checkbox 형식을 기본으로 쓸 것
    - `.aiworkspace/note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md`를 기본 템플릿으로 사용할 것
    - 특별한 override가 없으면 checklist 완료를 다음 major phase 이동의 기본 gate로 삼을 것
    을 반영했다
  - active `PHASE19_TEST_CHECKLIST.md`도 같은 형식으로 바로 바꿨다

### 2026-04-14 - strict annual contract tooltip은 옵션별 bullet 설명과 always-on 의미를 같이 보여줘야 한다
- Request topic:
  - `Phase 19` test checklist를 보며
    - `Rejected Slot Handling Contract` tooltip이 한 줄 설명으로 이어져 가독성이 떨어진다는 피드백
    - `Risk-Off Contract`의 "portfolio-wide risk-off" 문장이 어렵다는 질문
    - `Weighting / Rejected Slot Handling / Risk-Off Contract`가 토글 없는 always-on 규칙인지 궁금하다는 질문
- Interpreted goal:
  - contract 설명을 화면만 보고도 이해할 수 있게 만들고,
    사용자가 "이 기능은 토글이 없는데 항상 작동하는가?"를 헷갈리지 않게 하고 싶음
- Result:
  - `Rejected Slot Handling Contract` tooltip을 option별 bullet 설명으로 다시 정리했다
  - `Risk-Off Contract` tooltip에
    `portfolio-wide risk-off`가
    개별 종목 몇 개 제외가 아니라
    `Market Regime` 또는 guardrail 때문에 포트폴리오 전체가 보수 모드로 가는 상황이라는 뜻을 plain language로 보강했다
  - overlay contracts intro에
    `Weighting Contract`, `Rejected Slot Handling Contract`, `Risk-Off Contract`는
    enable/disable 토글이 아니라
    백테스트 실행 시 항상 저장되는 기본 처리 규칙이고,
    관련 상황이 실제로 발생할 때 결과에 영향을 준다는 설명을 추가했다

### 2026-04-14 - Overlay & Defensive Rules는 top-level tab보다 내부 section 분리가 더 적합하다
- Request topic:
  - strict annual `Overlay & Defensive Rules` 안에 contract가 늘어난 상황에서,
    별도 탭/섹션으로 분리하는 것이 좋은지 검토 요청
  - `partial trend rejection`, `portfolio-wide risk-off` 표현이 어렵다는 추가 질문
- Interpreted goal:
  - 사용자가 설정 화면에서 길을 잃지 않으면서도,
    `Rejected Slot Handling`과 `Risk-Off`의 역할 차이를 더 쉽게 이해하게 만들고 싶음
- Result:
  - 현재 단계에서는 **top-level tab 분리보다 same expander 안의 내부 section 분리**가 더 적합하다고 판단했다
  - 이유:
    - 이 옵션들은 모두 strict annual 전략의 `Overlay & Defensive Rules`라는 같은 문맥 안에서 읽히는 것이 자연스럽다
    - top-level tab으로 분리하면 설정 위치는 찾기 쉬워질 수 있지만,
      trend filter / partial rejection / full risk-off / weighting의 실행 순서 관계는 오히려 덜 보일 수 있다
    - 대신 내부를 아래처럼 3~4개 section으로 나누면 UX가 가장 좋다
      - `Trend Filter Overlay`
      - `Partial Rejection Handling`
      - `Full Risk-Off Handling`
      - `Weighting Contract`
  - easy explanation 정리:
    - `partial trend rejection`
      - top N 후보 중 일부 종목만 trend filter에 걸려 빠지는 상황
      - 이때 빈 슬롯을 어떻게 처리할지가 `Rejected Slot Handling Contract`
    - `portfolio-wide risk-off`
      - 개별 종목 몇 개가 빠지는 것이 아니라,
        `Market Regime` 또는 guardrail 때문에 그 리밸런싱 시점 포트폴리오 전체를 보수 모드로 돌리는 상황
      - 이때 현금으로 갈지, defensive sleeve로 갈지를 정하는 것이 `Risk-Off Contract`

### 2026-04-14 - strict annual UI는 `Overlay`와 `Portfolio Handling & Defensive Rules`로 실제 분리하는 것이 가장 합리적이다
- Request topic:
  - 위 판단을 기준으로 가장 합리적이고 효율적인 방향으로 UI를 실제 수정해 달라는 요청
- Interpreted goal:
  - 사용자가 overlay trigger와 post-overlay portfolio handling을 화면 구조만 봐도 구분할 수 있게 만들고 싶음
- Result:
  - strict annual single / compare form에서 기존 `Overlay & Defensive Rules`를
    - `Overlay`
    - `Portfolio Handling & Defensive Rules`
    로 실제 분리했다
  - `Overlay`
    - `Trend Filter`
    - `Market Regime`
  - `Portfolio Handling & Defensive Rules`
    - `Rejected Slot Handling Contract`
    - `Weighting Contract`
    - `Risk-Off Contract`
    - `Defensive Sleeve Tickers`
  - 이 구조로 바뀌면서
    overlay를 켜는 규칙과,
    overlay / risk-off가 발생한 뒤 포트폴리오를 어떻게 처리할지를
    다른 층위의 설정으로 읽게 했다

### 2026-04-14 - contract caption은 반복 위치 안내보다 역할과 적용 상황을 설명하는 편이 더 낫다
- Request topic:
  - `Portfolio Handling & Defensive Rules` 안의 각 항목에서
    `위치: ...` 문구를 제거하고,
    항목 정보와 기능을 UX/UI 관점에서 더 잘 정리해 달라는 요청
- Interpreted goal:
  - 사용자가 이미 해당 section 안에 들어와 있을 때는
    위치 반복보다 "이 계약이 정확히 어떤 상황을 처리하는가"를 더 빨리 이해하게 만들고 싶음
- Result:
  - `Rejected Slot Handling Contract`
    - "상위 후보 중 일부 종목만 빠졌을 때 빈 자리를 어떻게 처리하는가" 중심으로 설명을 정리했다
  - `Risk-Off Contract`
    - "이번 리밸런싱에서 포트폴리오 전체를 쉬게 하거나 방어 ETF로 돌릴지" 중심으로 설명을 정리했다
  - `Weighting Contract`
    - "무엇을 살지 정한 뒤 얼마씩 담을지" 중심으로 설명을 정리했다
  - section intro도 bullet-style 역할 요약으로 바꿔,
    각 contract의 차이를 위에서 먼저 읽고 아래 세부 항목으로 내려가게 했다

### 2026-04-14 - `Risk-Off Contract`는 "포트폴리오 전체를 현금 또는 방어 ETF로 전환하는 규칙"으로 설명하는 편이 더 이해하기 쉽다
- Request topic:
  - `포트폴리오 전체를 보수 모드로 돌릴 때`가
    전체 현금 전환을 뜻하는지 헷갈린다는 질문과,
    그 설명을 UI 문구에 더 직접적으로 반영해 달라는 요청
- Interpreted goal:
  - 사용자가 `Risk-Off Contract`를
    추상적인 `보수 모드` 표현 없이,
    "factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF로 전환하는 규칙"
    으로 바로 이해하게 만들고 싶음
- Result:
  - strict annual form에서
    `보수 모드`, `full risk-off` 중심 문구를 줄이고
    `포트폴리오 전체를 쉬어야 할 때`,
    `현금 또는 방어 ETF 쪽으로 전체 전환`
    언어로 재정리했다
  - `Rejected Slot Handling Contract`는
    일부 종목만 빠지는 상황,
    `Risk-Off Contract`는 포트폴리오 전체를 전환하는 상황이라는 구분도 더 직접적으로 남겼다
  - glossary와 package analysis도 같은 표현으로 맞춰,
    UI와 문서가 서로 다른 언어를 쓰지 않게 정리했다

### 2026-04-14 - `History` 화면은 "저장된 실행 기록"과 "live selection-history drilldown"을 구분해서 안내하는 편이 더 낫다
- Request topic:
  - `history run`이 무엇인지 모르겠고,
    `Backtest > History > strict annual run > Selection History / Interpretation`
    위치를 찾기 어렵다는 피드백
- Interpreted goal:
  - 사용자가
    - 저장된 실행 기록 1건을 다시 읽는 화면
    - 최신 실행 결과에서 row-level selection history를 읽는 화면
    을 혼동하지 않게 만들고 싶음
- Result:
  - `Backtest > History` 상단에
    `history run = 저장된 백테스트 실행 기록 1건`
    이라는 설명을 추가했다
  - selected history drilldown은
    `Selected History Run`, `Saved Run Summary`, `Saved Input & Context`
    같은 이름으로 바꿔 목적이 더 분명해지게 했다
  - strict annual record에서는
    자세한 `Selection History`와 `Interpretation Summary`는
    compact history record 안이 아니라
    `Run Again` 또는 `Load Into Form` 후 latest result의 `Selection History` 탭에서 본다는 안내를 추가했다
  - latest result selection tabs도
    `Selection History Table`, `Interpretation Summary`, `Selection Frequency`
    로 직접적으로 보이게 바꿨고,
    `Interpretation` 열이 row-level interpretation이라는 안내를 추가했다

### 2026-04-14 - `Run Again`과 `Load Into Form`은 같은 버튼이 아니므로 후속 화면도 다르게 안내하는 편이 더 낫다
- Request topic:
  - `Run Again`을 눌러도 변화가 없는 것처럼 느껴지고,
    `Load Into Form`은 `Single Strategy`로 바로 이동하는데 되돌아가기 UX가 약하다는 피드백
- Interpreted goal:
  - 사용자가
    - `Run Again`은 결과를 다시 계산하는 버튼
    - `Load Into Form`은 입력만 다시 채우는 버튼
    이라는 차이를 실제 동선에서도 느끼게 만들고 싶음
- Result:
  - `Run Again`은 실행 성공 후 자동으로 `Single Strategy` 패널로 이동하고,
    새 `Latest Backtest Run`을 바로 보게 했다
  - `Load Into Form`은 입력만 불러온다는 안내를 더 분명히 추가했고,
    최신 결과는 아직 이전 run 기준일 수 있으니 form을 다시 실행해야 한다는 설명을 넣었다
  - `Single Strategy`로 이동한 뒤 바로 `Back To History` 버튼도 제공해,
    돌아가는 경로가 불분명한 느낌을 줄였다

### 2026-04-15 - Phase closeout 문서는 실제 검수 상태와 쉬운 설명을 더 분명히 드러내야 한다
- Request topic:
  - `PHASE19_CURRENT_CHAPTER_TODO.md`에 manual validation이 아직 `pending`으로 보이는 점,
    `PHASE19_COMPLETION_SUMMARY.md`의 `쉬운 뜻`이 아직 딱딱하다는 점,
    `PHASE_PLAN_TEMPLATE.md`의 `slice` 표현이 사용자 입장에서 불필요하게 내부 용어처럼 느껴진다는 피드백
- Interpreted goal:
  - closeout 문서와 phase plan template가 실제 진행 상태와 사용자의 읽기 흐름에 더 잘 맞도록 정리하고 싶음
- Result:
  - `PHASE19_CURRENT_CHAPTER_TODO.md`는 manual validation을 `in_progress`로 바꾸고,
    사용자가 실제 체크리스트를 진행 중이라는 점을 같이 적었다
  - `PHASE19_COMPLETION_SUMMARY.md`는 각 `쉽게 말하면` 섹션을 더 쉬운 문장으로 다시 풀어썼다
  - `PHASE_PLAN_TEMPLATE.md`는 `첫 구현 단위` 대신 `이번 phase의 주요 작업 단위`를 쓰도록 바꿨다
  - `AGENTS.md`에도 future phase plan 문서에서 `slice`보다 `작업 단위`, `첫 번째 작업`, `다음 작업` 같은 표현을 우선 쓰도록 반영했다

### 2026-04-15 - Phase 19 checklist 완료 시점에는 manual validation 상태도 완료로 닫아야 한다
- Request topic:
  - 사용자가 `Phase 19` checklist 완료를 선언함
- Interpreted goal:
  - 문서상으로도 `Phase 19`가 더 이상 validation 진행 중이 아니라,
    검수까지 마친 상태라는 점을 분명히 남기고 싶음
- Result:
  - `PHASE19_CURRENT_CHAPTER_TODO.md`에서 manual UI validation actual run을 `completed`로 바꿨다
  - `PHASE19_COMPLETION_SUMMARY.md`도 `manual_validation_completed` 상태로 정리했다
  - 이후에는 `Phase 19`를 fully closed phase로 보고 다음 phase 논의를 이어가면 된다

### 2026-04-15 - Phase 20은 current candidate를 다시 쓰는 operator workflow 정리에 초점을 두는 것이 자연스럽다
- Request topic:
  - `Phase 19` 완료 후 `Phase 20`을 진행해달라는 요청
- Interpreted goal:
  - deep rerun을 다시 크게 열기 전에,
    strongest / near-miss candidate를 다시 보고 비교하고 저장하는 흐름을 먼저 정리하고 싶음
- Result:
  - `Phase 20`을 `Candidate Consolidation And Operator Workflow Hardening`으로 열었다
  - kickoff plan, current TODO, operator workflow inventory first pass를 만들었다
  - 현재 strongest candidate는 이미 잘 문서화되어 있지만,
    compare / weighted portfolio / saved portfolio 재진입 흐름은 여전히 더 다듬을 여지가 있다는 점을 phase kickoff 수준에서 고정했다

### 2026-04-15 - Phase 21은 phase 문서 bootstrap과 current candidate registry를 practical baseline으로 먼저 여는 것이 가장 효율적이다
- Request topic:
  - `Phase 21`을 중간에 끊지 않고 끝까지 진행하고, 마지막에 checklist를 공유해달라는 요청
- Interpreted goal:
  - research automation과 experiment persistence를 막연한 계획이 아니라 실제로 바로 쓸 수 있는 baseline까지 올리고 싶음
- Result:
  - `Phase 21`을 `Research Automation And Experiment Persistence`로 열었다
  - `bootstrap_finance_phase_bundle.py`를 추가해 새 phase 문서를 template 기준으로 한 번에 생성할 수 있게 했다
  - `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`와 `manage_current_candidate_registry.py`를 추가해 current candidate를 machine-readable하게 남기고 다시 읽을 수 있게 했다
  - `check_finance_refinement_hygiene.py`, plugin/skill docs, roadmap, doc index, runtime guidance도 새 workflow에 맞게 갱신했다
  - 현재 판단은 `Phase 21 = practical closeout / manual_validation_pending`이며, 이후에는 `Phase 20` operator workflow hardening 또는 `Phase 22` deep validation 준비로 더 자연스럽게 이어질 수 있다

### 2026-04-15 - Phase 20 compare 화면에서는 current candidate 재진입보다 기본 compare 조작이 먼저 보여야 한다
- Request topic:
  - 사용자가 `Compare Strategies` 제목과 `Strategies` 사이에 있는 `Current Candidate Re-entry`가 UX상 어색하고, 바로 아래 용어 설명도 답답하다고 피드백함
- Interpreted goal:
  - compare 화면의 첫 인상은 전략 선택과 기간 확인이 먼저 보이게 하고,
    current candidate 재진입은 보조 도구처럼 덜 방해되게 두고 싶음
- Result:
  - `Current Candidate Re-entry`를 compare 상단 고정 블록에서 내려서
    `Strategies` 선택 아래의 secondary expander
    `Quick Re-entry From Current Candidates`로 이동했다
  - 설명도 늘 펼쳐진 줄글 대신 `What This Does` expander 안으로 접어,
    필요할 때만 읽을 수 있게 정리했다
  - 현재 판단은 이 흐름이 operator 관점에서 더 자연스럽다.
    compare는 먼저 전략을 고르는 화면이고,
    current candidate 재진입은 그 과정을 빠르게 돕는 shortcut으로 읽히는 편이 맞다

### 2026-04-15 - Saved Portfolios는 현재 별도 top-level 탭보다 Compare workflow 안에 두는 편이 더 자연스럽다
- Request topic:
  - 사용자가 `Compare & Portfolio Builder` 안에 line이 많고, `Saved Portfolios`가 이 탭에 있는 것이 맞는지 검토를 요청함
- Interpreted goal:
  - compare 화면이 덜 조각나 보이게 만들고,
    `Saved Portfolios`의 위치가 workflow 관점에서 타당한지 다시 확인하고 싶음
- Result:
  - top-level divider는 제거하고 각 섹션의 제목으로만 구분하도록 정리했다
  - 현재 판단은 `Saved Portfolios`를 별도 top-level 탭으로 빼기보다
    `Compare & Portfolio Builder` 안에 유지하는 편이 더 맞다
  - 이유는 saved portfolio가 독립 기능이라기보다
    `compare -> weighted portfolio -> save / replay / edit-in-compare`
    흐름의 마지막 operator 단계이기 때문이다

### 2026-04-15 - Current candidate re-entry는 버튼 이름만 봐도 역할이 읽혀야 한다
- Request topic:
  - 사용자가 `Load Current Anchors`, `Load Lower-MDD Near Misses`가 무엇인지,
    왜 버튼이 두 개인지, 아래 직접 선택 문구는 또 무엇인지 잘 모르겠다고 피드백함
- Interpreted goal:
  - current candidate 재진입 도구가 내부 용어를 알아야만 쓸 수 있는 화면이 아니라,
    버튼 이름만 보고도 “대표 후보를 불러오는지 / 더 방어적인 대안을 불러오는지 / 직접 고르는지”
    구분되게 만들고 싶음
- Result:
  - quick action 버튼 이름을 `Load Recommended Candidates`,
    `Load Lower-MDD Alternatives`로 더 직접적으로 바꿨다
  - 각 버튼 아래에 한 줄 설명을 넣어,
    왜 버튼이 둘인지와 어떤 후보 묶음을 불러오는지 바로 읽히게 했다
  - custom picker도 `Pick Specific Candidates Manually`로 바꿔,
    빠른 불러오기와 직접 선택을 더 쉽게 구분하게 했다

### 2026-04-15 - Current candidate re-entry 후보 목록은 문서 생성만으로 자동 노출되지 않는다
- Request topic:
  - 사용자가 current candidate 재진입 UX가 여전히 잘 안 읽히고,
    `Pick Specific Candidates Manually` 목록이 문서만 만들면 자동으로 생기는지,
    아니면 별도 후보 등록이 필요한지 물어봄
- Interpreted goal:
  - UI는 더 단순하게 읽히게 만들고,
    후보 리스트의 source-of-truth가 무엇인지도 사용자 입장에서 분명히 알고 싶음
- Result:
  - current candidate 재진입 surface를
    `Quick Bundles`와 `Pick Manually` 두 탭으로 분리했다
  - `Pick Manually` 탭 안에서 이 목록은
    새 백테스트 실행이나 Markdown 문서 생성만으로 자동 누적되지 않고,
    `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`의 active row를 읽는다고 명시했다
  - 따라서 현재 구조에서는 문서만 만든다고 자동 노출되지 않는다
  - 다만 사용자가 별도로 “노출용 문서”를 하나 더 만들 필요는 없고,
    후보를 UI에 다시 쓰고 싶다면 registry가 갱신되어야 한다.
    이 저장은 앞으로 candidate closeout 작업에서 같이 맞추는 것이 기본 흐름이다

### 2026-04-15 - Compare prefill confirmation은 source/label 같은 짧은 용어보다 행동 중심 설명이 더 낫다
- Request topic:
  - 사용자가 `Load Recommended Candidates` 이후 뜨는 `What Changed In Compare` 카드에서
    표는 괜찮지만 `Source`, `Label`, `확인 위치` 같은 설명은 여전히 잘 정리되지 않았다고 피드백함
- Interpreted goal:
  - compare prefill 이후 사용자가 “방금 뭐가 바뀌었고, 어디를 보면 되고, 다음에 뭘 누르면 되는지”를 더 빨리 이해하게 만들고 싶음
- Result:
  - 카드 제목을 `Compare Form Updated`로 바꾸고,
    `불러온 방식 / 불러온 묶음 이름 / 자동으로 맞춰진 기간`처럼 더 직접적인 표현으로 재구성했다
  - 후보 title이 있으면 카드 안에 바로 보여주고,
    표 위에는 “각 전략에 어떤 핵심 설정이 채워졌는지 요약한 것”이라는 설명을 붙였다
  - 마지막에는 `어디서 확인하면 되나`와 `Run Strategy Comparison` 안내를 분리해,
    다음 행동이 더 분명하게 읽히도록 정리했다

### 2026-04-15 - Current candidate compare prefill은 핵심 strict-annual 계약값과 어긋나지 않는지 같이 점검해야 한다
- Request topic:
  - 사용자가 `Load Recommended Candidates` 이후 `Trend Filter`, `Market Regime` 표기가 실제 전략 설정과 다른 것 같다고 피드백하고, 다른 핵심 값도 차이가 없는지 검토를 요청함
- Interpreted goal:
  - current candidate registry에서 compare form으로 넘어갈 때 핵심 strict-annual 계약값이 중간에 느슨해지거나 잘못 표기되지 않는지 확인하고 싶음
- Result:
  - registry -> compare prefill override -> summary table 경로를 직접 재현해 확인했다
  - 현재 active `current_candidate` 기준으로
    - `Value current anchor`: trend off / regime off
    - `Quality current anchor`: trend on / regime off
    - `Quality + Value current anchor`: trend off / regime off
    가 코드상 일관되게 매핑되고 있었다
  - 즉 현재 코드 기준으로는 핵심 값이 자동으로 풀린 정황은 확인되지 않았다
  - 다만 카드 표가 너무 적은 열만 보여서 오해를 만들 수 있었기 때문에
    `Weighting Contract`, `Risk-Off Contract`도 같이 표기하도록 보강했다

### 2026-04-15 - Compare 고급 설정은 family 선택과 selected variant 설정을 한 섹션으로 읽히게 두는 편이 더 직관적이다
- Request topic:
  - 사용자가 compare `Strategy-Specific Advanced Inputs`에서 family selector와 snapshot 설정이 분리되어 있는 구조가 GTAA 등 다른 전략보다 덜 직관적이라고 피드백함
- Interpreted goal:
  - `Quality`, `Value`, `Quality + Value`도 GTAA처럼 한 섹션 안에서 variant를 고르고 바로 그 variant 설정을 이어서 조정할 수 있게 만들고 싶음
- Result:
  - compare advanced inputs에서 `Quality Family`, `Value Family`, `Quality + Value Family`를 각각 `Quality`, `Value`, `Quality + Value` 섹션으로 정리했다
  - 각 섹션 안에 variant selector를 두고,
    선택된 variant의 세부 설정이 같은 expander 안에 바로 이어서 보이도록 바꿨다
  - 이로써 family를 먼저 고른 뒤 아래 다른 위치에서 snapshot expander를 다시 찾는 흐름이 사라졌고,
    compare form이 GTAA / Equal Weight 등과 더 비슷한 “한 전략(또는 한 family) 한 덩어리” 구조로 읽히게 되었다

### 2026-04-15 - Benchmark Contract는 옵션 이름보다 비교 의미를 먼저 설명해야 이해가 빠르다
- Request topic:
  - 사용자가 `Candidate Universe Equal-Weight`가 무엇인지 간단히 설명해 달라고 요청했고,
    strict annual `Real-Money Contract`의 `Benchmark Contract` tooltip 보강도 함께 요청함
- Interpreted goal:
  - operator가 `Benchmark Contract`를 볼 때 용어 자체보다
    "무엇과 비교하는 방식인가"를 먼저 이해하게 만들고 싶음
- Result:
  - `Benchmark Contract` tooltip을
    - `Ticker Benchmark`: `SPY` 같은 기준 ETF 1개와 비교
    - `Candidate Universe Equal-Weight`: 같은 후보 universe에서 투자 가능 종목을 단순 equal-weight로 담은 기준선과 비교
    로 다시 작성했다
  - `Candidate Universe Equal-Weight` 선택 시 캡션도
    "같은 후보군 안에서 복잡한 ranking 없이 그냥 고르게 샀을 때"와 비교하는 의미라는 점이 드러나도록 보강했다
  - glossary에는 `Candidate Universe Equal-Weight` 항목을 별도로 추가해,
    이후 다른 화면이나 문서에서도 같은 용어를 재사용할 수 있게 했다

### 2026-04-15 - `Candidate Universe Equal-Weight / SPY`는 하나의 benchmark가 아니라 contract와 reference ticker가 같이 보인 상태다
- Request topic:
  - 사용자가 `Candidate Universe Equal-Weight / SPY`를 `Ticker Benchmark / SPY`와 같은 뜻으로 이해해도 되는지 물었고, 그 표기가 UX상 혼동을 준다고 지적함
- Interpreted goal:
  - equal-weight benchmark contract와 `SPY` reference ticker를 화면에서 구분해 보이게 만들어,
    둘을 같은 benchmark로 오해하지 않게 하고 싶음
- Result:
  - runtime code를 확인한 결과, `Candidate Universe Equal-Weight`는 실제로는 후보군 종목들의 equal-weight benchmark를 생성하고,
    `SPY`는 그 benchmark 자체가 아니라 separate benchmark/reference ticker로 남는다
  - compare prefill summary는
    - `Benchmark Contract`
    - `Benchmark Ticker / Reference`
    두 열로 분리했다
  - current candidate registry summary도
    `Benchmark Candidate Equal-Weight | Reference Ticker SPY`
    처럼 읽히도록 정리했다
  - 따라서 `Candidate Universe Equal-Weight / SPY == Ticker Benchmark / SPY`는 아니며,
    전자는 "후보군 equal-weight benchmark + SPY reference ticker"에 가깝다

### 2026-04-15 - Candidate Universe Equal-Weight를 고르면 SPY는 benchmark가 아니라 별도 reference ticker일 수 있다
- Request topic:
  - 사용자가 `Benchmark Contract = Candidate Universe Equal-Weight`일 때 `Benchmark Ticker = SPY`를 신경 안 써도 되는지 질문함
- Interpreted goal:
  - equal-weight benchmark와 `SPY`의 역할을 실전 설정 관점에서 구분해 이해하고 싶음
- Result:
  - runtime code 기준으로 `Benchmark Contract = Candidate Universe Equal-Weight`이면
    benchmark curve 자체는 후보군 종목들로 equal-weight benchmark를 생성한다
  - 즉 이 경우 `SPY`가 equal-weight benchmark를 만드는 재료는 아니다
  - 다만 underperformance guardrail / drawdown guardrail이 켜져 있으면
    `Benchmark Ticker = SPY`는 여전히 별도 reference ticker로 사용될 수 있다
  - 따라서 실무적으로는
    - benchmark curve 관점에서는 `SPY`를 덜 신경 써도 되지만
    - guardrail을 쓰는 경우에는 `SPY`를 계속 의미 있는 설정값으로 봐야 한다

### 2026-04-15 - Equal-weight benchmark일 때는 입력 필드 이름도 `Benchmark Ticker` 대신 `Guardrail / Reference Ticker`가 더 적합하다
- Request topic:
  - 사용자가 equal-weight benchmark contract를 고른 경우 `SPY`가 benchmark 자체가 아니라는 설명을 보고,
    필드 이름도 그렇게 바꾸는 편이 덜 헷갈린다고 피드백함
- Interpreted goal:
  - 입력 단계부터 `SPY`의 역할을 더 정확히 보여주고 싶음
- Result:
  - 처음에는 contract에 따라 필드 이름을 다르게 보이게 바꾸려 했지만,
    현재 Streamlit submit-form 구조에서는 이 라벨이 사용자가 기대하는 방식으로 즉시 바뀌지 않았다
  - 그래서 최종적으로는 입력 필드 이름을
    `Benchmark / Guardrail / Reference Ticker`
    로 고정하고,
    바로 아래 캡션과 help text에서 contract별 의미를 설명하는 방식으로 정리했다
  - prefill summary line은 계속 equal-weight 케이스에서 `Reference Ticker` 언어를 사용하도록 유지했다
  - 결과적으로 입력 단계에서 오해를 줄이면서도,
    form 특성 때문에 생기는 "왜 라벨이 안 바뀌지?" 문제를 피할 수 있게 되었다

### 2026-04-15 - 최종적으로는 benchmark ticker와 guardrail/reference ticker를 실제 입력 단계에서 분리하는 편이 더 직관적이었다
- Request topic:
  - 사용자가 중립적인 단일 ticker 필드도 여전히 직관적이지 않다고 판단했고,
    UX 관점에서는 benchmark와 guardrail reference를 아예 별도 입력으로 나누는 편이 더 낫지 않은지 검토를 요청함
- Interpreted goal:
  - `무엇과 직접 비교하는가`와 `guardrail이 무엇을 기준으로 쉬는가`를 입력 단계에서부터 혼동 없이 읽히게 만들고 싶음
- Result:
  - final implementation에서는 strict annual `Real-Money Contract`를
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker`
    두 필드로 실제 분리했다
  - `Candidate Universe Equal-Weight`일 때도 benchmark curve는 후보군 equal-weight로 생성되고,
    `Guardrail / Reference Ticker`는 underperformance / drawdown guardrail이 따로 참고하는 기준 ticker로 남는다
  - 이 분리는 single strategy, compare prefill, history/meta, runtime bundle input, shadow sample entrypoint까지 같이 반영되었다
  - 따라서 현재의 durable rule은
    - benchmark baseline과
    - guardrail reference
    를 같은 필드의 다른 해석으로 보지 않고, 처음부터 별도 operator decision으로 다루는 것이다

### 2026-04-15 - `Ticker Benchmark`일 때는 guardrail ticker를 선택 입력처럼 읽히게 하고, `Candidate Universe Equal-Weight`일 때는 benchmark ticker를 숨기는 쪽이 더 직관적이다
- Request topic:
  - 사용자가 실제 UX 관점에서
    - `Ticker Benchmark`일 때는 `Benchmark Ticker`만 필수처럼 보이고
    - `Candidate Universe Equal-Weight`일 때는 `Guardrail / Reference Ticker`만 핵심처럼 보이게 만들 수 있는지 요청함
- Interpreted goal:
  - benchmark contract에 따라 어떤 입력이 핵심인지 화면 자체가 먼저 말해주게 만들고 싶음
- Result:
  - `Ticker Benchmark` 모드에서는
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker (Optional)`
    구조로 정리했고, 비워두면 benchmark와 동일하게 쓴다는 설명을 붙였다
  - `Candidate Universe Equal-Weight` 모드에서는 benchmark ticker 입력을 숨기고,
    benchmark curve가 후보군 equal-weight로 자동 생성된다는 안내와 함께
    `Guardrail / Reference Ticker`만 보이게 정리했다
  - compare form update, prefill summary, history/meta surface에서는
    별도 guardrail ticker를 입력하지 않은 경우 `Same as Benchmark Ticker`로 보여주도록 바꿨다
  - 따라서 현재 UX rule은
    - `Ticker Benchmark`: benchmark ticker 중심 + optional separate guardrail ticker
    - `Candidate Universe Equal-Weight`: auto-built benchmark + explicit guardrail/reference ticker
    로 이해하면 된다

### 2026-04-15 - `Benchmark Contract`를 바꿔도 입력이 즉시 숨겨지지 않는 것은 현재 form 구조 제약 때문이었다
- Request topic:
  - 사용자가 `Benchmark Contract`를 변경해도 `Benchmark Ticker` / `Guardrail / Reference Ticker` 입력이 바로 숨겨지지 않는다고 확인 요청함
- Interpreted goal:
  - 현재 UI가 실제로 버그인지, 아니면 Streamlit form 구조상 즉시 반영되지 않는 것인지 파악하고 싶음
- Result:
  - 원인은 현재 strict annual `Real-Money Contract`가 `st.form` 안에 있기 때문이었다
  - 이 구조에서는 dropdown 값을 바꾸는 것만으로는 즉시 rerun되지 않아, contract-dependent hide/show가 바로 반영되지 않는다
  - 초기에는 버튼으로 레이아웃을 다시 반영하는 방식을 시험했지만, UX가 오히려 어색하다는 피드백이 나왔다
  - 최종적으로는 버튼과 숨김/노출 시도를 걷어내고,
    `Benchmark Contract`, `Benchmark Ticker`, `Guardrail / Reference Ticker (Optional)`를 항상 보여주되
    각 contract에서 어떤 값이 실제로 중요한지 설명 문구로 분리하는 쪽으로 정리했다
  - 현재 durable interpretation은:
    - `Ticker Benchmark`: `Benchmark Ticker`가 직접 비교 baseline
    - `Candidate Universe Equal-Weight`: equal-weight benchmark는 자동 생성되므로 `Benchmark Ticker`는 직접 baseline 계산에는 쓰이지 않음
    - `Guardrail / Reference Ticker (Optional)`: contract와 무관하게 underperformance / drawdown guardrail 기준과 연결됨

### 2026-04-15 - `Guardrail / Reference Ticker`는 결국 `Real-Money Contract`가 아니라 `Guardrails` 탭에 두는 편이 더 자연스럽다
- Request topic:
  - 사용자가 `Guardrail / Reference Ticker (Optional)`는 benchmark와 직접 관련이 없고, 오히려 guardrail 처리와만 연결되는 값처럼 보인다고 지적함
- Interpreted goal:
  - benchmark baseline 설정과 guardrail 기준 설정을 화면 구조 차원에서 분리해 더 직관적으로 만들고 싶음
- Result:
  - 최종적으로 `Guardrail / Reference Ticker (Optional)`를 `Real-Money Contract`에서 제거하고 `Guardrails` 탭으로 옮겼다
  - `Real-Money Contract`에는
    - `Benchmark Contract`
    - `Benchmark Ticker`
    만 남겼다
  - `Guardrails` 탭에서는
    - `Underperformance Guardrail`
    - `Drawdown Guardrail`
    - `Guardrail / Reference Ticker (Optional)`
    를 함께 읽게 정리했다
  - 따라서 현재 durable interpretation은:
    - `Benchmark Contract` / `Benchmark Ticker` = 무엇과 직접 비교하는가
    - `Guardrail / Reference Ticker (Optional)` = guardrail이 무엇을 기준으로 쉬는가

### 2026-04-15 - compare summary에서는 실제로 쓰이지 않는 ticker 값은 빈칸으로 두는 편이 더 합리적이다
- Request topic:
  - 사용자가 `Compare Form Updated` 표에서
    - `Candidate Universe Equal-Weight`일 때는 `Benchmark Ticker`가 사실상 안 쓰이고
    - guardrail이 꺼져 있을 때는 `Guardrail / Reference Ticker`도 의미가 없으니
    빈칸으로 처리하는 편이 더 낫다고 제안함
- Interpreted goal:
  - compare summary를 "실제로 활성화된 설정" 중심으로 읽히게 만들고 싶음
- Result:
  - `Benchmark Contract = Candidate Universe Equal-Weight`이면 compare summary의 `Benchmark Ticker`는 빈칸으로 보이게 바꿨다
  - underperformance / drawdown guardrail이 둘 다 꺼져 있으면 `Guardrail / Reference Ticker`도 빈칸으로 보이게 바꿨다
  - 단, guardrail이 켜져 있고 별도 reference ticker를 입력하지 않은 경우에는 `Same as Benchmark Ticker`를 유지해 fallback 의미를 드러내도록 했다

### 2026-04-16 - 남아 있는 `Phase 18`을 더 진행할지, 아니면 `Phase 21`로 넘어갈지 판단
- Request topic:
  - 사용자가 refreshed roadmap 기준으로 현재는 `Phase 18`을 더 마무리해야 하는지, 아니면 `Phase 21`로 가야 하는지 판단을 요청함
- Interpreted goal:
  - phase 상태를 다시 정리한 뒤, 다음 main track을 문서와 실제 진행 모두에서 일관되게 맞추고 싶음
- Result:
  - `Phase 18`은 larger structural redesign first slice까지는 충분히 수행되었고,
    remaining second-slice idea는 current blocker보다 future structural backlog로 읽는 편이 맞다고 판단했다
  - 이유:
    - next-ranked fill first slice는 meaningful redesign evidence를 남겼다
    - 하지만 current anchor replacement나 same-gate rescue까지는 아니었다
    - `Phase 19`, `Phase 20`에서 contract language와 operator workflow도 이미 practical 기준으로 정리되었다
  - 따라서 권고 방향은:
    - `Phase 18`은 `practical_closeout / manual_validation_pending`으로 정리
    - immediate next main phase는 `Phase 21` integrated deep validation으로 전환
  - 이 판단에 맞춰:
    - `PHASE18_COMPLETION_SUMMARY.md`
    - `PHASE18_NEXT_PHASE_PREPARATION.md`
    - `PHASE18_TEST_CHECKLIST.md`
    를 만들고,
    `Phase 21` plan / TODO / roadmap / doc index를 새 상태에 맞춰 동기화했다

### 2026-04-16 - `Phase 21` 첫 작업은 deep rerun보다 validation frame을 먼저 고정하는 편이 맞다
- Request topic:
  - 사용자가 `Phase 21` 진행을 요청했고, 다음 실제 작업으로 무엇을 먼저 해야 하는지 정리할 필요가 생김
- Interpreted goal:
  - annual strict family와 portfolio bridge를 다시 돌리기 전에,
    같은 phase 안에서 무엇을 어떤 이름으로 검증할지 먼저 고정하고 싶음
- Result:
  - `Phase 21`의 first work unit은 actual rerun보다 먼저
    **validation frame definition**
    으로 정리하는 것이 맞다고 판단했다
  - 고정한 공통 기준은 아래와 같다:
    - 기간:
      - `2016-01-01 ~ 2026-04-01`
    - universe frame:
      - `US Statement Coverage 100`
      - `Historical Dynamic PIT Universe`
    - family rerun pack:
      - `Value`: `value_current_anchor_top14_psr`, `value_lower_mdd_near_miss_pfcr`
      - `Quality`: `quality_current_anchor_top12_lqd`, `quality_cleaner_alternative_top12_spy`
      - `Quality + Value`: `quality_value_current_anchor_top10_por`, `quality_value_lower_mdd_near_miss_top9`
    - representative bridge frame:
      - `Load Recommended Candidates`
      - near-equal weighted bundle
      - representative saved portfolio replay
  - 또한 rerun report와 strategy log의 naming도 먼저 고정해,
    phase 결과가 다시 phase별 임시 문맥으로 흩어지지 않게 했다
  - 이 판단은
    `PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md`
    에 문서화했고,
    `Phase 21` plan / TODO / checklist / roadmap / doc index에도 반영했다

### 2026-04-16 - 지금 바로 `Phase 21 QA`를 시작하는 것보다 actual rerun pack execution이 먼저다
- Request topic:
  - 사용자가 validation frame 정의 이후, 이제 바로 `Phase 21 QA`를 진행하면 되는지 질문함
- Interpreted goal:
  - 현재 `Phase 21`이 QA-ready 상태인지, 아니면 아직 본 작업이 더 남아 있는지 분명히 알고 싶음
- Result:
  - 현재 시점에서는 **바로 full `Phase 21 QA`로 들어가는 것은 아직 이르다**고 판단했다
  - 이유:
    - 지금까지 완료된 것은 `validation frame definition first work unit`이다
    - 즉 무엇을 어떤 기준으로 다시 볼지 정리한 상태이지,
      family별 integrated rerun 결과와 portfolio bridge validation 결과가 아직 쌓이지 않았다
  - 따라서 지금 순서는:
    1. `Value -> Quality -> Quality + Value -> portfolio bridge` actual rerun pack execution
    2. family report / strategy hub / backtest log / candidate summary sync
    3. 그 다음 `PHASE21_TEST_CHECKLIST.md` 기준으로 phase QA 진행
  - 다만 checklist의 `1. validation frame 정의 확인` 섹션은
    지금 시점에서도 부분적으로 미리 확인할 수 있다
  - 정리하면:
    - 지금은 `Phase 21` 본작업 실행 단계
    - QA는 rerun 결과가 나온 뒤 진행

### 2026-04-16 - `Phase 21` first actual rerun pack에서 `Value` current anchor 유지가 다시 확인되었다
- Request topic:
  - `Phase 21` next step으로 actual rerun pack execution을 시작함
- Interpreted goal:
  - first family인 `Value`를 current anchor와 lower-MDD alternative 기준으로 같은 frame에서 다시 돌려,
    current candidate 유지 여부를 먼저 확인하고 싶음
- Result:
  - `Value` current anchor `Top N = 14 + psr`는
    `28.13% / -24.55% / real_money_candidate / paper_probation / review_required`
    로 current practical point를 그대로 유지했다
  - lower-MDD alternative `Top N = 14 + psr + pfcr`는
    `27.22% / -21.16% / production_candidate / watchlist / review_required`
    로 이번 frame에서도 더 낮은 drawdown을 보였지만,
    여전히 weaker-gate alternative로 남았다
  - 즉 `Value` family first-pass conclusion은:
    - current anchor 유지
    - lower-MDD alternative는 still near-miss
    - same-gate replacement는 없음
  - 이 결과를
    - `PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
    - `VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
    - `VALUE_STRICT_ANNUAL.md`
    - `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
    에 반영했다

### 2026-04-16 - `Phase 21` second actual rerun pack에서 `Quality` current anchor 유지가 다시 확인되었다
- Request topic:
  - `Phase 21` next step으로 `Quality` family rerun pack execution을 이어감
- Interpreted goal:
  - `Quality` current anchor와 cleaner alternative를 같은 frame에서 다시 돌려,
    current practical point를 유지할지 아니면 cleaner alternative 쪽으로 읽어야 할지 정리하고 싶음
- Result:
  - `Quality` current anchor
    `capital_discipline + LQD + trend on + regime off + Top N 12`
    는 `26.02% / -25.57% / real_money_candidate / paper_probation / review_required`
    로 그대로 current practical point를 유지했다
  - cleaner alternative
    `capital_discipline + SPY + trend on + regime off + Top N 12`
    는 `25.18% / -25.57% / real_money_candidate / paper_probation / paper_only`
    로 validation/rolling surface는 더 깨끗했지만,
    deployment가 `paper_only`라서 replacement candidate로 올라오지는 않았다
  - 즉 `Quality` family second-pass conclusion은:
    - current anchor 유지
    - cleaner alternative는 still comparison surface
    - actual replacement는 없음
  - 이 결과를
    - `PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
    - `QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`
    - `QUALITY_STRICT_ANNUAL.md`
    - `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
    에 반영했다

### 2026-04-17 - `Phase 21` third actual rerun pack에서 `Quality + Value` current strongest point 유지가 다시 확인되었다
- Request topic:
  - `Phase 21` next step으로 `Quality + Value` family rerun pack execution을 이어감
- Interpreted goal:
  - blended family의 current strongest point와 `Top N 9` lower-MDD alternative를 같은 frame에서 다시 돌려,
    current representative anchor를 유지할지 확인하고 싶음
- Result:
  - `Quality + Value` current strongest point
    `operating_margin + pcr + por + per + Top N 10`
    은 `31.82% / -26.63% / real_money_candidate / small_capital_trial / review_required`
    로 current representative anchor를 유지했다
  - lower-MDD alternative `Top N 9`는
    `32.21% / -25.61% / production_candidate / watchlist / review_required`
    로 수익률과 낙폭은 모두 매력적이지만,
    gate가 한 단계 내려가서 replacement candidate로 보긴 어렵다
  - 즉 `Quality + Value` family third-pass conclusion은:
    - current strongest point 유지
    - `Top N 9`는 very strong but weaker-gate alternative
    - actual representative replacement는 없음
  - 이 결과를
    - `PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
    - `QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
    - `QUALITY_VALUE_STRICT_ANNUAL.md`
    - `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
    에 반영했다

### 2026-04-17 - `Phase 21` portfolio bridge validation에서 Phase 22 방향이 portfolio-level construction으로 정리되었다
- Request topic:
  - annual strict family rerun 3종 이후, representative portfolio bridge validation을 진행함
- Interpreted goal:
  - `Load Recommended Candidates -> weighted portfolio -> saved portfolio replay` 흐름이
    실제 다음 phase의 후보 construction 대상으로 볼 만큼 의미 있는지 확인하고 싶음
- Result:
  - representative weighted portfolio는
    `Value / Quality / Quality + Value` current anchor를
    `33 / 33 / 34`, `intersection`으로 섞어 만들었다
  - 결과는:
    - `CAGR = 28.66%`
    - `MDD = -25.42%`
    - `Sharpe = 1.51`
    - `End Balance = $132,063.56`
  - saved portfolio replay는
    `CAGR`, `MDD`, `End Balance` 모두 exact match로 재현됐다
  - 해석:
    - bridge는 단순 UI artifact가 아니라 재현 가능한 portfolio construction lane이다
    - 단, portfolio-level promotion / shortlist / deployment semantics는 아직 없기 때문에
      production candidate로 바로 승격하기보다 Phase 22에서 별도 설계하는 것이 맞다
  - 이 결과를
    - `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`
    - `PHASE21_COMPLETION_SUMMARY.md`
    - `PHASE21_NEXT_PHASE_PREPARATION.md`
    - `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
    에 반영했다

### 2026-04-17 - `Phase 21` QA에서 validation frame과 후보 판단 용어를 더 쉽게 정리했다
- Request topic:
  - Phase 21 checklist를 보며 `validation frame`, `current anchor`, `rescue candidate`, Phase 18 backlog 관련 표현이 이해하기 어렵다고 지적함
- Interpreted goal:
  - Phase 21 문서가 내부 개발자 메모가 아니라 사용자가 직접 QA를 진행할 수 있는 설명 문서처럼 읽히도록 용어와 문장을 정리하고 싶음
- Result:
  - `Validation Frame`을 "여러 후보를 같은 조건에서 비교하기 위해 미리 고정해 두는 검증 기준표"로 glossary에 추가했다
  - Phase 21 plan에서 `Phase 18`의 남은 구조 실험은 지금 당장 막고 있는 필수 작업이 아니라 나중 선택지로 둔다는 뜻으로 풀어썼다
  - `current anchor 유지 / 교체`는 대표 후보를 계속 기준점으로 둘지 바꿀지 판단한다는 의미로 정리했다
  - `rescue candidate`는 낙폭이 낮은 대안이 실제 대체 후보인지, 단순 참고 후보인지 구분하는 표현으로 정리했다

### 2026-04-17 - `Phase 21` family별 integrated rerun 확인 위치를 checklist에 명확히 표시했다
- Request topic:
  - Phase 21 checklist의 `family별 integrated rerun 결과 확인`을 어디서 해야 하는지 모르겠다고 문의함
- Interpreted goal:
  - 사용자가 체크리스트를 보며 바로 클릭해서 검수할 수 있도록 확인 위치와 읽는 순서를 명확히 하고 싶음
- Result:
  - 확인 시작점은 `.aiworkspace/note/finance/backtest_reports/phase21/README.md`로 정리했다
  - 실제 family별 결과는 아래 3개 report에서 확인하도록 명시했다
    - `PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
    - `PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
    - `PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - strategy hub와 strategy backtest log는 장기 기록 동기화 확인용 보조 위치로 설명했다

### 2026-04-17 - `Phase 21` QA에서 유지 / 교체 / 보류 판단 기준과 backtest log 관리 방식을 명확히 했다
- Request topic:
  - `결과를 보고 유지 / 교체 / 보류 판단이 가능한 정도로 해석이 적혀 있는지`를 무엇을 보고 체크해야 하는지 문의함
  - annual strict backtest log가 날짜순으로 읽히지 않고, 마지막에 간단한 표가 있으면 좋겠다고 요청함
- Interpreted goal:
  - 사용자가 raw 수익률만 보고 판단하지 않고, gate와 해석까지 포함해 current anchor 유지 / 대체 / 보류 여부를 확인할 수 있게 만들고 싶음
- Result:
  - `PHASE21_TEST_CHECKLIST.md`에 유지 / 교체 / 보류 판단 기준을 추가했다
  - 유지 판단은 `CAGR / MDD`, `Promotion / Shortlist / Deployment`, `Validation / Rolling / OOS`, report 해석과 다음 액션을 함께 보는 것으로 정리했다
  - `Value`, `Quality`, `Quality + Value` annual strict backtest log 3종에 최신 날짜순 기록 규칙과 `최근 판단 요약표`를 추가했다
  - `Value`, `Quality + Value` 로그에서 뒤쪽에 있던 `2026-04-14` concentration-aware weighting 항목을 날짜순 위치로 옮겼다
  - `BACKTEST_LOG_TEMPLATE.md`, `FINANCE_DOC_INDEX.md`, `BACKTEST_REPORT_INDEX.md`에도 앞으로 같은 방식으로 관리한다는 기준을 반영했다

### 2026-04-17 - `Phase 21` portfolio bridge validation의 문서 report와 UI 확인 위치를 분리했다
- Request topic:
  - Phase 21 checklist의 `weighted portfolio / saved portfolio rerun report`가 `Weighted Portfolio Result`인지, `Weighted Portfolio Builder`인지, 다른 위치인지 문의함
- Interpreted goal:
  - 공식 검증 문서와 UI 재현 위치를 구분해서 사용자가 체크리스트를 보며 바로 확인할 수 있게 만들고 싶음
- Result:
  - 공식 rerun report는 `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`로 명시했다
  - UI 확인 경로는 `Backtest > Compare & Portfolio Builder` 아래의
    `Load Recommended Candidates -> Strategy Comparison -> Weighted Portfolio Builder -> Weighted Portfolio Result -> Saved Portfolios -> Replay Saved Portfolio`로 정리했다
  - `Weighted Portfolio Builder`는 구성 입력 영역, `Weighted Portfolio Result`는 결과 표시 영역, `Saved Portfolios / Replay Saved Portfolio`는 저장된 구성 재실행 영역으로 설명했다

### 2026-04-17 - `Phase 21` portfolio bridge report를 읽기 쉬운 검증 보고서 흐름으로 재정리했다
- Request topic:
  - `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`가 내용은 괜찮지만, 용어와 흐름이 AI가 만든 문서처럼 딱딱하고 `first pass` 표현도 어렵다고 지적함
- Interpreted goal:
  - 문서가 "결과표 모음"이 아니라, 왜 이 검증을 했고 무엇을 확인했으며 무엇을 아직 확인하지 않았는지 자연스럽게 읽히도록 정리하고 싶음
- Result:
  - 문서 제목을 본문상 `Phase 21 Portfolio Bridge Validation Report`로 바꾸고, 파일명에 남은 `FIRST_PASS`는 "첫 검증"이라는 뜻으로 풀어썼다
  - 앞부분에 "최종 포트폴리오 후보 확정 문서가 아니라 workflow 재현성 검증 문서"라는 결론을 먼저 배치했다
  - `Portfolio Bridge`, `Weighted Portfolio`, `Saved Portfolio Replay`, `First Pass` 용어를 문서 안에서 설명했다
  - `Value / Quality / Quality + Value` 3개를 묶은 이유와 한계를 분리해 설명했다
  - 결과 해석을 Phase 22에서 다룰 portfolio-level candidate construction 질문으로 자연스럽게 연결했다

### 2026-04-17 - portfolio bridge report 리라이트에 맞춰 Phase 21 checklist도 조정했다
- Request topic:
  - portfolio bridge report를 크게 정리했으니 checklist도 수정이 필요한지 문의함
- Interpreted goal:
  - checklist가 이전 문서 구조가 아니라 새 보고서 흐름을 기준으로 QA할 수 있게 맞추고 싶음
- Result:
  - `PHASE21_TEST_CHECKLIST.md` section 3의 읽는 방법을 보강했다
  - 새 체크 항목은 다음을 확인하도록 정리했다
    - 최종 portfolio winner 선정이 아니라 workflow 첫 검증인지
    - 왜 3개 annual strict 전략을 묶었는지와 그 한계가 같이 설명되는지
    - `Load Recommended Candidates -> Weighted Portfolio Builder -> Save Portfolio -> Replay Saved Portfolio` 흐름이 이해되는지
    - 아직 확인하지 않은 것과 `Phase 22` 질문이 분리되어 있는지

### 2026-04-17 - `Phase 21` checklist 전체를 처음부터 끝까지 다시 읽기 쉽게 정리했다
- Request topic:
  - `PHASE21_TEST_CHECKLIST.md`의 section 3이 확인 위치와 UI 경로가 섞여 난잡하므로, 전체 checklist를 다시 깔끔하게 정리해 달라고 요청함
- Interpreted goal:
  - 사용자가 QA를 할 때 "무엇을 확인하면 되는지"와 "어디서 확인하면 되는지"를 문서만 보고 바로 따라갈 수 있게 만들고 싶음
- Result:
  - checklist 전체를 `무엇을 확인하나 / 어디서 확인하나 / 체크 항목` 구조로 재작성했다
  - validation frame, family rerun, portfolio bridge, closeout 확인 위치를 표로 정리했다
  - portfolio bridge section은 공식 Markdown report와 UI 재현 경로를 분리하고, UI 순서도 별도 순서형 안내로 정리했다
  - 기존 사용자가 표시한 `[x]` QA 진행 상태는 유지했다

### 2026-04-17 - `Phase 21`을 검수 완료로 닫고 `Phase 22`를 portfolio-level candidate construction으로 열었다
- Request topic:
  - 사용자가 `Phase 21` checklist 완료를 알리고, Phase 21 마무리 후 Phase 22 진행을 요청함
- Interpreted goal:
  - Phase 21을 실제 완료 상태로 정리하고, 다음 main phase를 빈 템플릿이 아니라 실행 가능한 계획과 첫 작업 단위로 시작하고 싶음
- Result:
  - Phase 21 상태를 `phase_complete / manual_validation_completed`로 업데이트했다
  - Phase 22를 `Portfolio-Level Candidate Construction`으로 열었다
  - Phase 22의 핵심은 "weighted portfolio 결과를 바로 최종 후보라고 부르지 않고, source / weight / date alignment / saved replay / 해석이 남은 재현 가능한 portfolio-level candidate로 관리할 기준을 세우는 것"으로 정리했다
  - 첫 작업 단위에서는 `Portfolio-Level Candidate`, `Portfolio Bridge`, `Component Strategy`, `Date Alignment`, `Saved Portfolio Replay`를 정의했다
  - 다음 작업은 Phase 21의 `33 / 33 / 34` bridge를 baseline portfolio candidate pack으로 다시 검증할지 확정하고, 첫 portfolio-level validation report를 만드는 것이다

### 2026-04-17 - `Phase 22` 첫 portfolio baseline은 equal-third candidate pack으로 정리했다
- Request topic:
  - Phase 22 다음 단계로 baseline portfolio candidate pack 작업을 진행함
- Interpreted goal:
  - Phase 21 portfolio bridge 결과를 최종 winner가 아니라 Phase 22에서 비교 기준으로 쓸 baseline 후보 pack으로 정리하고 싶음
- Result:
  - `PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`를 작성했다
  - 저장된 portfolio definition은 `[33.33, 33.33, 33.33]`이며 normalized 기준으로 정확한 equal-third라는 점을 확인했다
  - Phase 21 문서의 `33 / 33 / 34`는 near-equal shorthand로 정리하고, Phase 22에서는 `equal-third baseline` 표현을 쓰기로 했다
  - 현재 status는 `baseline_candidate / portfolio_watchlist / not_deployment_ready`로 정리했다
  - 다음 질문은 portfolio-level benchmark / guardrail policy와 weight alternative 비교 범위다

### 2026-04-18 - `GTAA` 실전형 후보를 current runtime 기준으로 다시 찾았다
- Request topic:
  - 사용자가 `GTAA` 전략으로 preset에 국한되지 않은 ETF 조합을 다양하게 백테스트하고,
    `promotion`이 `hold`가 아닌 실제 투자 가능 후보를 추천해 Markdown으로 저장해 달라고 요청함
- Interpreted goal:
  - 단순 raw CAGR 상위 조합이 아니라 current DB/runtime의 ETF operability, validation, promotion, deployment gate를 유지한 채
    `real_money_candidate`까지 올라갈 수 있는 GTAA 후보를 찾는 것
- Result:
  - 서브에이전트 3개를 사용해 실행 경로, 보수형 universe, 공격형 universe를 나눠 탐색했다
  - broader universe는 raw 성과가 좋아도 ETF profile / AUM / spread coverage 부족 때문에 `hold / blocked`가 반복됐다
  - main runtime 재검증에서 `SPY, QQQ, GLD, IEF`, `Top = 2`, `Interval = 4`, `Score = 1M / 3M`, `Risk-Off = defensive_bond_preference` 후보를 추천 기본 후보로 정했다
  - 결과는 `CAGR = 17.46%`, `MDD = -8.39%`, `Promotion = real_money_candidate`, `Shortlist = paper_probation`, `Deployment = paper_only`
  - durable report는 `.aiworkspace/note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md`에 저장했다
- Follow-up:
  - 이 후보는 `hold`가 아니지만 deployment가 `paper_only`이므로, 실제 live allocation 전에는 월별 paper tracking과 quote/profile refresh가 필요하다

### 2026-04-17 - `Phase 22` portfolio-level benchmark와 guardrail은 baseline 비교 중심으로 정리했다
- Request topic:
  - Phase 22 다음 작업으로 portfolio-level benchmark / guardrail interpretation과 weight alternative 범위를 정리함
- Interpreted goal:
  - weight 대안을 돌리기 전에 무엇과 비교하고 어떤 기준으로 보수적으로 읽을지 고정하고 싶음
- Result:
  - Phase 22 primary portfolio benchmark는 `SPY`가 아니라 `phase22_annual_strict_equal_third_baseline_v1`로 정했다
  - `SPY`는 market context로만 두고, component benchmark는 component 품질 해석으로만 유지한다
  - portfolio-level guardrail은 아직 actual trading rule이 아니라 report-level warning으로 둔다
  - 다음 weight alternative는 넓은 brute-force가 아니라 `25 / 25 / 50`, `40 / 40 / 20` 두 개로 좁혔다
  - 따라서 다음 실제 validation report는 equal-third baseline과 이 두 weight alternative를 같은 frame에서 비교하는 방식으로 진행한다

### 2026-04-17 - `Phase 22` weight alternative first-pass에서는 baseline 교체를 하지 않기로 정리했다
- Request topic:
  - Phase 22 다음 단계로, 정해 둔 weight alternative를 실제로 비교하고 다음 판단을 진행함
- Interpreted goal:
  - portfolio-level candidate construction에서 baseline을 유지할지,
    `Quality + Value` tilt 또는 defensive tilt로 교체할지 숫자와 해석을 함께 남기고 싶음
- Result:
  - saved portfolio compare context를 code runner로 다시 실행해 세 component와 세 portfolio weight를 같은 frame에서 계산했다
  - Phase 21의 `$132,063.56`은 `33 / 33 / 34` near-equal 입력 결과이고,
    Phase 22 official baseline `[33.33, 33.33, 33.33]` 결과는 `$131,721.23`임을 분리했다
  - `25 / 25 / 50`은 CAGR과 End Balance가 좋아졌지만 Sharpe가 약간 낮고 `Quality + Value` contribution이 50%를 넘으므로 watch alternative로 보류했다
  - `40 / 40 / 20`은 MDD가 조금 낮아졌지만 CAGR / End Balance를 포기하므로 comparison-only defensive alternative로 보류했다
  - 결론은 `equal-third baseline 유지 / immediate replacement 없음`이다

### 2026-04-18 - `Phase 22` plan 문서를 QA 관점에서 다시 읽기 쉽게 정리했다
- Request topic:
  - 사용자가 `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md`의 섹션이 많고 중복되어 보이며,
    checklist 1번을 무엇을 보고 어떻게 확인해야 할지 모르겠다고 지적함
- Interpreted goal:
  - phase plan을 내부 task memo가 아니라 사용자가 checklist QA를 시작할 수 있는 orientation 문서로 바꾸고 싶음
- Result:
  - `목적`과 `쉽게 말하면`을 분리된 반복 섹션처럼 두지 않고 `목적: 쉽게 말하면`으로 통합했다
  - plan 문서를 현재 상태, 왜 필요한가, 이 phase가 끝나면 좋은 점, 확인한 질문, portfolio 후보 최소 조건, 실제 진행 순서, checklist에서 확인하는 방법 중심으로 재작성했다
  - checklist 1번에는 각 문서의 어느 섹션을 보면 되는지와 체크 방법을 명시했다
  - 핵심 확인 기준은 "weighted result는 후보가 아니며, source / weight / date alignment / replay / 해석이 남아야 portfolio-level candidate"라는 점이다

### 2026-04-18 - `Phase 22`는 투자 분석 phase가 아니라 portfolio workflow 개발 검증 phase로 다시 경계 설정했다
- Request topic:
  - 사용자가 Phase 22가 갑자기 `Value / Quality / Quality + Value` 3개를 실제 포트폴리오 분석 대상으로 삼는 것처럼 보이고,
    현재 프로젝트 목적이 퀀트 프로그램 개발인지 투자 후보 선정인지 흐려졌다고 지적함
- Interpreted goal:
  - Phase 22의 목적을 "실전 투자 포트폴리오 선정"이 아니라
    "포트폴리오 구성 / 저장 / replay / 비교 기능을 검증하는 개발 phase"로 다시 명확히 해야 함
- Result:
  - `equal-third baseline`은 투자 benchmark가 아니라 개발 검증용 fixture baseline이라고 정리했다
  - `Value / Quality / Quality + Value` 3개는 최종 투자 조합이 아니라,
    Phase 21에서 같은 frame으로 검증된 대표 전략이라 portfolio workflow 테스트 fixture로 쓴 것이라고 명시했다
  - 단일 포트폴리오 실전 투자 기능이 완료됐거나 live deployment 가능한 상태라고 해석하면 안 된다고 정리했다
  - Phase 22 문서의 QA 기준도 "투자해도 되는가"가 아니라
    "프로그램이 portfolio workflow를 재현 가능하게 다루는가"로 수정했다

### 2026-04-18 - master roadmap을 개발 중심 방향으로 다시 정렬했다
- Request topic:
  - 사용자가 phase가 포트폴리오 분석 쪽으로 벗어나는 것 같다고 보고,
    먼저 master roadmap을 수정해 `Phase 25`까지의 구현 방향과 "투자 분석 아님" 경계를 문서화하자고 요청함
- Interpreted goal:
  - 프로젝트의 기본 방향을 `투자 후보 분석`이 아니라
    `데이터 수집 + 백테스트 제품 개발`로 다시 고정하고,
    사용자가 명시적으로 요청한 분석은 예외적으로 수행하되 phase 방향 자체와 구분하고 싶음
- Result:
  - `MASTER_PHASE_ROADMAP.md`에 product development direction을 추가했다
  - 제품 레이어를 data, engine, strategy library, UX, portfolio workflow, validation/review, paper/pre-live, live trading으로 분리했다
  - `Phase 22` 이후 기본 방향을 portfolio optimization 확대가 아니라
    `Phase 23 Quarterly And Alternate Cadence Productionization`으로 되돌렸다
  - `Phase 24`는 new strategy implementation bridge,
    `Phase 25`는 live trading이 아닌 validation / review / paper-readiness scaffolding으로 재정리했다
  - `Development Validation`, `Fixture`, `User-Requested Analysis` 용어를 glossary에 추가했다

### 2026-04-19 - master roadmap에는 특정 phase 경계보다 전체 제품 방향을 먼저 둬야 한다
- Request topic:
  - 사용자가 `MASTER_PHASE_ROADMAP.md`의 `지금 중요한 경계`가 Phase 22 중심으로 되어 있는 것이 상위 로드맵 문서상 적절한지,
    그리고 Phase 25까지면 프로그램 완성에 충분한지 질문함
- Interpreted goal:
  - master roadmap을 단기 phase memo가 아니라 전체 제품 개발 방향을 읽을 수 있는 문서로 유지하고 싶음
- Result:
  - master roadmap에는 특정 phase의 상세 설명을 오래 남기기보다
    전체 원칙과 제품 레이어, 현재 상태, 다음 3~5개 phase 방향만 두는 것이 더 적절하다고 판단했다
  - 현재 `지금 중요한 경계`는 Phase 22 드리프트를 바로잡기 위한 임시 성격이 강하므로,
    다음 문서 정리 때는 `투자 분석과 개발 검증의 구분` 같은 일반 원칙으로 승격하고
    Phase 22 상세는 phase22 문서로 내리는 편이 좋다
  - Phase 25는 전체 프로그램 완성이 아니라
    `pre-live readiness`까지의 1차 로드맵으로 보는 것이 맞다
  - 완성형 프로그램에는 Phase 26 이후로 production hardening, broader strategy library, portfolio/risk analytics,
    data quality monitoring, paper/live operations, user workflow polish 같은 추가 축이 필요할 가능성이 높다

### 2026-04-19 - 방향 변경 전 Phase 22와 Phase 23의 원래 연결 의도를 정리했다
- Request topic:
  - 사용자가 방향 변경 전에는 Phase 22를 마친 뒤 Phase 23에서 무엇을 하려 했는지,
    그리고 Phase 22가 `portfolio-level candidate report`를 통해 포트폴리오 검증 기준을 만들려던 phase가 맞는지 질문함
- Interpreted goal:
  - Phase 22가 투자 분석으로 흐른 것인지,
    아니면 포트폴리오 workflow와 후보 기준을 만들기 위한 개발 검증이었는지 구분하고 싶음
- Result:
  - 방향 변경 전 Phase 22의 의도는 `portfolio-level candidate` 기준을 만들고,
    equal-third baseline / benchmark / guardrail / weight alternative를 통해 포트폴리오 후보를 어떻게 기록하고 비교할지 정하는 것이었다
  - 방향 변경 전 Phase 23은 이 portfolio baseline을 바탕으로
    quarterly prototype과 alternate cadence를 practical lane으로 올릴지 검토하는 흐름이었다
  - 다만 이 연결은 portfolio baseline을 투자 benchmark처럼 읽히게 만들 위험이 있었고,
    현재는 Phase 22를 portfolio workflow 개발 검증으로 제한하고 Phase 23을 quarterly / alternate cadence 제품 기능화로 재정렬했다

### 2026-04-19 - portfolio workflow 개발은 취소가 아니라 우선순위와 의미가 재정렬된 것이다
- Request topic:
  - 사용자가 원래는 portfolio 검증 기능을 만들 생각이었는데,
    이후 요청 때문에 방향이 반대로 바뀐 것인지,
    아니면 지금도 이 개발을 이어가는 것인지 질문함
- Interpreted goal:
  - portfolio workflow layer가 폐기된 것인지,
    아니면 투자 분석으로 확대하지 않도록 범위를 제한한 것인지 명확히 알고 싶음
- Result:
  - portfolio workflow 개발 자체는 취소되지 않았다
  - 바뀐 것은 `지금 바로 portfolio 투자 가능성 분석을 확장한다`는 해석을 멈추고,
    portfolio workflow를 제품 기능 layer로 유지하되 다음 main implementation 우선순위는 quarterly / alternate cadence productionization으로 돌리는 것이다
  - 따라서 Phase 22의 산출물은 이후에도 portfolio 저장 / replay / 비교 / 후보 기록 기준으로 재사용된다
  - 다만 본격적인 portfolio 투자 가능성 검토나 diversified portfolio construction은
    전략/cadence 기능이 더 성숙한 뒤 별도 phase에서 여는 것이 맞다

### 2026-04-19 - Phase 22 checklist 완료에 따라 closeout 처리했다
- Request topic:
  - 사용자가 `PHASE22_TEST_CHECKLIST.md` 확인을 완료했다고 알림
- Interpreted goal:
  - Phase 22를 manual validation completed 상태로 닫고,
    다음 main phase로 넘어갈 수 있게 roadmap과 handoff 문서를 맞추고 싶음
- Result:
  - Phase 22 checklist의 주요 항목이 모두 `[x]` 처리된 것을 확인했다
  - Phase 22 상태를 `phase complete / manual_validation_completed`로 정리했다
  - Phase 22는 투자 포트폴리오 승인 phase가 아니라
    portfolio workflow development validation phase로 닫았다
  - 다음 기본 방향은 portfolio optimization 확대가 아니라
    `Phase 23 Quarterly And Alternate Cadence Productionization`으로 정리했다

### 2026-04-19 - Phase 23 quarterly smoke validation에서 meta 보존이 핵심 검증 지점임을 확인했다
- Request topic:
  - 사용자가 Phase 23 다음 작업 진행을 요청했고, quarterly strict family의 실제 실행 검증을 이어감
- Interpreted goal:
  - quarterly portfolio handling contract가 UI/payload에만 붙은 것이 아니라
    실제 DB-backed runtime과 history/load-into-form에 필요한 result meta까지 이어지는지 확인해야 함
- Result:
  - `Quality / Value / Quality + Value` quarterly prototype 3개 family를
    `AAPL / MSFT / GOOG`, 2021-01-01~2024-12-31, non-default contract 조합으로 smoke run했다
  - 계산은 통과했지만 초기 확인에서 `weighting_mode`, `rejected_slot_handling_mode`,
    `rejected_slot_fill_enabled`, `partial_cash_retention_enabled`가 result bundle meta에 빠져 있었다
  - 공통 bundle builder를 수정해 해당 meta를 보존하도록 했고,
    재실행 결과 세 family 모두 contract meta가 남는 것을 확인했다
  - 이 결과는 투자 분석이 아니라 quarterly 기능의 개발 검증 결과로 기록했다

### 2026-04-19 - Phase 23 manual QA 전 history / saved replay contract roundtrip을 보강했다
- Request topic:
  - 사용자가 Phase 23 다음 단계 진행을 요청했고,
    남은 history / saved replay 흐름을 manual QA 전에 더 안전하게 만들 필요가 있었음
- Interpreted goal:
  - quarterly portfolio handling contract가 result bundle에만 남는 것이 아니라
    history record, history payload, saved portfolio replay override까지 유지되어야 함
- Result:
  - `append_backtest_run_history()`가 `weighting_mode`, `rejected_slot_handling_mode`,
    `rejected_slot_fill_enabled`, `partial_cash_retention_enabled`를 저장하도록 보강했다
  - `Run Again` / `Load Into Form` payload rebuild와 saved portfolio strategy override에도 같은 값을 연결했다
  - representative quarterly smoke bundle로 roundtrip을 검증했고,
    Phase 23을 `manual_validation_ready` 상태로 정리했다

### 2026-04-19 - Compare 화면의 Annual / Quarterly variant 변경은 form 밖에서 처리해야 한다
- Request topic:
  - 사용자가 Phase 23 checklist QA 중 Compare 화면에서 Annual -> Quarterly variant를 바꿔도
    아래 advanced option UI가 즉시 바뀌지 않는다고 지적함
- Interpreted goal:
  - 버튼을 추가하지 않고, variant 변경 즉시 하단 옵션 UI가 해당 annual/quarterly 경로로 바뀌어야 함
- Result:
  - 원인은 variant selectbox가 `st.form()` 안에 있어 Streamlit이 submit 전까지 widget tree를 즉시 재구성하지 않는 구조였다고 판단했다
  - `Strategy Variants` 섹션을 form 밖에 만들고,
    `Quality / Value / Quality + Value` variant selector를 그곳으로 이동했다
  - `Advanced Inputs > Strategy-Specific Advanced Inputs`는 현재 선택된 variant의 세부 입력만 보여주는 영역으로 정리했다
  - Phase 23 checklist의 모호한 문구도 실제 화면 위치 기준으로 수정했다

### 2026-04-19 - Compare 공용 입력과 전략별 입력은 분리해서 보여주는 것이 더 자연스럽다
- Request topic:
  - 사용자가 `Strategy Variants`를 form 밖에 둔 방식은 좋지만,
    `Timeframe`, `Option`, 전략별 세부 입력이 여전히 분산되어 보여 UX가 아쉽다고 지적함
- Interpreted goal:
  - 버튼을 추가하지 않고,
    공용 실행 입력과 전략별 세부 입력을 화면 구조상 명확히 나누어
    Annual / Quarterly 변경 즉시 하단 옵션이 갱신되게 만들고 싶음
- Result:
  - `Start Date`, `End Date`, `Timeframe`, `Option`은 모든 compare 전략이 공유하는 값이므로
    `Compare Period & Shared Inputs`로 묶는 것이 맞다고 판단했다
  - 기존 `Advanced Inputs` expander / compare form wrapper는 제거했다
  - `Strategy Variants` 별도 상단 섹션도 제거하고,
    `Quality / Value / Quality + Value` variant selector를 각 strategy box 안으로 이동했다
  - strategy-level expander는 border box로 바꾸고,
    하위 `Overlay`, `Portfolio Handling`, real-money, guardrail 그룹은 기존 접기/펼치기로 유지했다
  - 실제 실행은 `Run Strategy Comparison` 버튼 하나로 유지하고,
    별도 Apply / Refresh 버튼은 만들지 않았다
  - Phase 23 checklist와 관련 문서도 새 화면 구조 기준으로 정리했다

### 2026-04-19 - Phase 23 QA 용어는 history와 saved portfolio를 분리해서 설명해야 한다
- Request topic:
  - 사용자가 Phase 23 checklist section 3에서 saved compare / saved portfolio context,
    history run, load-into-form, rerun, saved replay가 각각 어디서 무엇을 확인하라는 말인지 헷갈린다고 지적함
- Interpreted goal:
  - 실제 UI 위치와 버튼 의미를 기준으로 QA checklist를 다시 써야 함
- Result:
  - quarterly compare prototype도 annual strict처럼 `Overlay` expander 안에 trend filter와 market regime 설정을 넣었다
  - `Portfolio Handling & Defensive Rules`는 quarterly rejected-slot handling, weighting, risk-off / defensive tickers를 확인하는 곳으로 설명했다
  - `Backtest > History`의 `Run Again` / `Load Into Form`과
    `Saved Portfolios`의 `Replay Saved Portfolio`는 서로 다른 흐름이라고 checklist에 분리해 적었다
  - `Load Into Form` 후 `Back To History`가 더 확실히 History panel로 돌아가도록
    radio widget 렌더 전에 panel request를 세팅하는 callback 방식으로 수정했다

### 2026-04-19 - 체크리스트는 별도 용어 블록보다 항목별 확인 위치를 우선한다
- Request topic:
  - 사용자가 checklist에 `용어 기준` 블록을 따로 넣지 말고,
    각 체크 항목에 어디서 확인해야 하는지를 더 자세히 적는 방식으로 지침을 요청함
- Interpreted goal:
  - checklist를 읽을 때 별도 용어 설명을 먼저 해석하지 않고,
    각 checkbox만 보고 바로 UI에서 확인할 수 있어야 함
- Result:
  - `PHASE23_TEST_CHECKLIST.md` section 3에서 `용어 기준` 블록을 제거했다
  - 각 체크 항목에 `Backtest > History > ...`, `Saved Portfolios > ...` 같은 실제 화면 경로를 직접 넣었다
  - `PHASE_TEST_CHECKLIST_TEMPLATE.md`와 `FINANCE_DOC_INDEX.md`에도 future checklist 작성 지침으로 반영했다

### 2026-04-20 - quarterly real-money contract / guardrails는 추후 parity 작업으로 다루는 것이 맞다
- Request topic:
  - 사용자가 Phase 24가 new strategy expansion으로 보이는데,
    annual에는 `Real-Money Contract`와 `Guardrails`가 있고 quarterly prototype에는 아직 없으므로
    이것도 추후 개발 예정인지 질문함
- Interpreted goal:
  - Phase 24로 넘어가기 전에 quarterly가 annual과 같은 promotion / guardrail surface를 가져야 하는지,
    아니면 research-only 상태로 두고 나중에 별도 작업으로 다루는 것이 맞는지 확인하고 싶음
- Result:
  - quarterly strict family는 아직 `prototype / research-only hold`이므로,
    annual의 real-money / guardrail 옵션을 지금 즉시 1:1 복제하는 것은 우선순위가 높지 않다
  - Phase 23의 기본 목표는 quarterly 실행, compare, history, saved replay 재현성을 제품 기능 수준으로 끌어올리는 것이다
  - quarterly real-money contract / guardrails parity는 추후 `quarterly promotion readiness` 또는 `pre-live readiness` 성격의 작업으로 다루는 것이 자연스럽다
  - 다만 Phase 23 closeout 또는 Phase 24 kickoff에서는 이 차이를 명시해,
    사용자가 quarterly에 real-money / guardrail 옵션이 없는 것을 구현 누락으로 오해하지 않게 해야 한다

### 2026-04-20 - Phase 24는 신규 전략 구현 경로를 만드는 개발 phase로 시작한다
- Request topic:
  - 사용자가 Phase 23 완료를 알리고 Phase 24 진행을 요청함
- Interpreted goal:
  - Phase 23을 manual validation completed 상태로 닫고,
    `Phase 24 New Strategy Expansion`을 새 전략 성과 분석이 아니라
    신규 전략을 제품에 붙이는 구현 경로로 열고 싶음
- Result:
  - Phase 23 checklist 완료를 closeout gate로 받아들였다
  - Phase 24 문서 번들을 생성하고 plan / TODO / checklist / first work-unit을 실제 내용으로 정리했다
  - 첫 구현 후보는 `Global Relative-Strength Allocation With Trend Safety Net`으로 정했다
  - 선정 이유는 성과 우수성이 아니라,
    ETF 가격 데이터만으로 구현 가능하고 monthly cadence / trend safety net / cash fallback 구조가
    현재 DB-backed price strategy infrastructure와 가장 잘 맞기 때문이다

### 2026-04-20 - GTAA compact 후보의 ticker 부족 문제를 확장 universe로 보강한다
- Request topic:
  - 사용자가 기존 GTAA 후보가 4~5개 ticker 중 2개를 고르는 방식이라 universe가 부족해 보인다고 지적하고,
    같은 GTAA 전략 안에서 더 넓은 ticker 조합을 백테스트해 새 포트폴리오를 요청함
- Interpreted goal:
  - 기존 `real_money_candidate` compact 후보를 무작정 대체하지 않고,
    ticker universe를 넓혔을 때도 investability / validation gate를 통과하는 후보가 있는지 확인한다
- Result:
  - `TLT`를 추가한 clean 6 ETF core `SPY / QQQ / GLD / IEF / LQD / TLT`가 가장 현실적인 확장 방향으로 확인됐다
  - 신규 확장 `Top = 1`, `Interval = 8`, `1M / 3M / 6M` 후보는
    `21.50% CAGR`, `-6.49% MDD`, `Sharpe 3.66`, `real_money_candidate / paper_probation / paper_only`로 등록했다
  - 같은 6 ETF core의 `Top = 2`, `Interval = 4`, `1M / 3M / 6M` 후보는
    `16.79% CAGR`, `-8.39% MDD`, `production_candidate / watchlist / watchlist_only`라서 현재 기본 후보를 대체하지 않는다
  - 결론적으로 2개 보유 기본 후보는 기존 `SPY / QQQ / GLD / IEF`를 유지하고,
    신규 확장 후보는 공격형 paper probation candidate로 별도 tracking한다

### 2026-04-20 - Phase 24 첫 구현은 core/runtime과 UI 연결을 분리해서 진행한다
- Request topic:
  - Phase 24 신규 전략 확장 진행 중 첫 구현 후보를 실제 코드에 넣는 범위를 정리함
- Interpreted goal:
  - 새 전략을 한 번에 모든 UI 경로까지 붙이기보다,
    먼저 core strategy와 DB-backed runtime이 제대로 실행되는지 확인한 뒤
    다음 작업에서 UI / compare / history / replay를 붙이는 단계적 진행이 필요함
- Result:
  - `Global Relative Strength` core simulation, strategy class, DB-backed sample helper,
    web runtime wrapper를 추가했다
  - compile / import / synthetic smoke / DB-backed smoke를 통과했다
  - 이 결과는 투자 분석이 아니라 신규 전략 추가 경로의 개발 검증으로 기록했다
  - 아직 `Backtest` UI selector, compare, history, saved replay에는 연결하지 않았으므로
    Phase 24 다음 작업은 제품 UI surface 연결이다

### 2026-04-20 - GTAA 6개월 이상 리밸런싱은 느린 cadence로 별도 경고가 필요하다
- Request topic:
  - 사용자가 GTAA 후보 중 `Interval = 6`처럼 반기 단위로 바꾸는 방식은 백테스트 성과가 좋아도 너무 느린 리밸런싱이 아니냐고 질문함
- Interpreted goal:
  - 좋은 백테스트 수치와 실제 운용 cadence 적합성을 분리해서 판단해야 함
- Result:
  - repo GTAA runtime에서 `option = month_end`일 때 `interval`은 score lookback이 아니라 리밸런싱 row 선택 간격이므로,
    `6`은 반기, `8`은 약 8개월 cadence에 가깝다
  - GTAA 문헌의 기본 구현은 월말 기준 monthly update / monthly rebalance에 가깝기 때문에,
    `Interval = 6` 또는 `8`은 일반적인 tactical allocation보다 느린 저회전 변형으로 봐야 한다
  - 확장 6 ETF core 민감도에서는 `Top = 1 / Interval = 4`와 `Top = 1 / Interval = 8`만 `real_money_candidate`였고,
    monthly / quarterly cadence는 `hold`로 약했다
  - 결론적으로 느린 cadence 후보는 registry에 남기되, 기본 실전 후보로 바로 승격하지 않고
    월별 paper tracking과 `Interval = 4` 대안 비교를 먼저 진행하는 것이 맞다

### 2026-04-20 - Phase 24 신규 전략은 UI / replay까지 연결한 뒤 manual QA로 넘긴다
- Request topic:
  - 사용자가 Phase 24 다음 작업 진행을 요청함
- Interpreted goal:
  - `Global Relative Strength`가 core/runtime 단계에서 멈추지 않고,
    실제 `Backtest` 제품 화면에서 single 실행, compare, history, saved replay까지 이어지게 만들고 싶음
- Result:
  - `Global Relative Strength`를 single / compare strategy catalog에 등록했다
  - `Backtest > Single Strategy`에 신규 전략 form을 추가했다
  - compare strategy-specific box와 compare runner override를 연결했다
  - history record / payload에 `cash_ticker`, `research_source`, interval, score, trend filter 설정이 보존되도록 했다
  - saved portfolio replay가 신규 전략 override를 복원할 수 있게 했다
  - compile, catalog/history smoke, DB-backed runtime smoke, compare runner smoke를 통과했다
  - Phase 24 상태는 `practical_closeout / manual_validation_pending`으로 정리했고,
    다음 단계는 사용자가 `PHASE24_TEST_CHECKLIST.md`로 실제 화면 QA를 진행하는 것이다

### 2026-04-20 - Global Relative Strength 실행 오류는 기본 preset 내 데이터 부족 티커에서 발생했다
- Request topic:
  - 사용자가 `Global Relative Strength` 실행 시 `Backtest execution failed: 공통 Date가 없습니다.` 오류가 발생한다고 보고함
- Interpreted goal:
  - 신규 전략 자체의 계산 오류인지, DB 가격 데이터 / 전처리 coverage 문제인지 확인하고 UI 실행이 중단되지 않게 만들고 싶음
- Result:
  - 기본 preset 중 `EEM`이 현재 DB에서 2026년 이후 일부 가격 행만 가지고 있었다
  - `MA200`과 12개월 relative-strength score를 만들고 나면 `EEM`의 transformed DataFrame이 비어 전체 티커 `Date` 교집합이 0개가 되었다
  - 코드는 risky ticker 중 transformed history가 비는 항목을 제외하고, `excluded_tickers`와 warning에 남기도록 수정했다
  - 기본 preset smoke는 `EEM` 제외 상태로 정상 실행되며, 이 결과는 투자 판단 전에 DB 가격 보강이 필요하다는 경고를 포함한다

### 2026-04-20 - Global Relative Strength 결과 종료일이 2026-02-27에서 멈춘 원인과 경고 문구를 정리했다
- Request topic:
  - 사용자가 `EEM` 가격 데이터를 보강한 뒤에도 `2016-01 ~ 2026-04-20` 실행 결과가 `2026-02-27`까지만 보이고, 주의사항 문구가 영어로 나온다고 보고함
- Interpreted goal:
  - 결과 종료일이 왜 2026년 4월까지 확장되지 않는지 확인하고, UI 주의사항을 사용자가 읽기 쉬운 한국어로 바꾸고 싶음
- Result:
  - 현재 DB에서 `EEM`은 2025-04-21 이후 가격만 조회되어, 2016년 시작 Global Relative Strength에는 아직 포함될 만큼의 이동평균/12개월 상대강도 이력이 부족했다
  - 별도로 `IWM`에는 2026-03-17 하루치 `Close` 결측 행이 있었고, 기존 `add_ma`가 이 결측값 때문에 이후 이동평균 행을 과도하게 제거해 공통 월말 날짜가 `2026-02-27`에서 멈췄다
  - `add_ma`는 이동평균 계산 전 기준 가격 결측 행을 제거하도록 수정했다
  - 같은 조건의 runtime smoke는 최신 DB 거래일인 `2026-04-17`까지 결과가 생성되며, `IWM 1건(2026-03-17)` 결측 가격 행도 주의사항과 metadata에 표시된다
  - 주의사항 문구도 한국어 중심으로 표시된다

### 2026-04-20 - `FINANCE_COMPREHENSIVE_ANALYSIS`의 상세 구현 메모는 legacy archive로 관리한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 `3-3. 상세 구현 메모`가 계속 누적되면 관리되지 않는 기록 창고가 될 수 있다고 지적하고, 향후 기록 방식까지 정리해 달라고 요청함
- Interpreted goal:
  - 기존 상세 구현 기록은 잃지 않되, 현재 상태와 과거 기록을 구분하고 앞으로 어떤 내용을 어디에 기록할지 명확히 해야 함
- Result:
  - `3-3`을 현재 사양 문서가 아니라 legacy archive로 명시했다
  - 새 긴 구현 이력은 `3-3`에 직접 append하지 않고, 현재 동작은 관련 주제 섹션, phase 진행은 phase 문서와 `WORK_PROGRESS.md`, 설계 판단은 `QUESTION_AND_ANALYSIS_LOG.md`, backtest 결과는 `backtest_reports/`, 후보 기록은 `CURRENT_CANDIDATE_REGISTRY.jsonl`로 분산 기록하도록 정리했다
  - 기존 긴 메모는 삭제하지 않고 주제별 색인과 기록 템플릿을 붙여, future agent와 사용자가 참고 기록과 현재 상태를 혼동하지 않도록 했다

### 2026-04-20 - 코드 분석은 별도 `docs/architecture/` 계층으로 관리한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md` 하단의 script / code analysis 내용까지 한 파일에서 계속 관리하는 것이 맞는지 묻고, 앞으로 코드 수정이나 신규 script가 생길 때 기록할 체계를 만들자고 요청함
- Interpreted goal:
  - 종합 분석 문서는 큰 지도 역할을 유지하고, 실제 코드 수정자가 따라야 하는 runtime / DB / UI / strategy / automation flow는 별도 developer-facing 문서로 관리해야 함
- Result:
  - `.aiworkspace/note/finance/docs/architecture/`를 새 canonical code flow 위치로 만들었다
  - `BACKTEST_RUNTIME_FLOW.md`, `DATA_DB_PIPELINE_FLOW.md`, `BACKTEST_UI_FLOW.md`, `STRATEGY_IMPLEMENTATION_FLOW.md`, `AUTOMATION_SCRIPTS.md`, `README.md`를 추가했다
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`는 high-level system map으로 유지하고 상세 code flow는 `docs/architecture/`를 보도록 정리했다
  - 앞으로 code analysis 문서는 모든 변경을 기록하는 history가 아니라, durable code flow가 바뀔 때만 갱신하는 evergreen 개발자 문서로 운영한다

### 2026-04-20 - 종합 분석 문서의 코드 상세는 요약으로 줄이고 상세는 `docs/architecture/`가 담당한다
- Request topic:
  - 사용자가 `docs/architecture/`를 만든 이상 `FINANCE_COMPREHENSIVE_ANALYSIS.md` 안의 코드 관련 상세를 삭제하거나 옮겨도 되는지 확인하고, 종합 문서는 간단한 요약만 남기자고 요청함
- Interpreted goal:
  - 종합 문서가 다시 비대해지지 않도록 코드 세부 설명을 줄이고, 개발자용 상세 흐름은 `docs/architecture/`로 일원화해야 함
- Result:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 파일 역할, 중요 함수, automation baseline 섹션을 간단한 요약 / entrypoint map으로 줄였다
  - strict annual contract, ETF runtime warning, real-money / guardrail / pre-live runtime 기준은 `STRATEGY_IMPLEMENTATION_FLOW.md`와 `BACKTEST_RUNTIME_FLOW.md` 쪽에 보강했다
  - 앞으로 종합 문서는 current system map으로 읽고, 코드 수정 순서와 상세 계약은 `docs/architecture/`에서 관리하는 방향으로 고정했다

### 2026-04-20 - DB 구조와 데이터 흐름은 별도 `data_architecture/` 계층으로 관리한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 `5. 데이터 흐름`, `6. DB 구조 요약`, `7. 테이블별 역할`도 table이 많아지기 전에 별도 체계로 관리하는 것이 좋지 않냐고 요청함
- Interpreted goal:
  - 종합 문서에는 데이터/DB 상위 지도만 남기고, 실제 data flow, schema map, table semantics, PIT/data-quality notes는 별도 canonical 문서로 분리해야 함
- Result:
  - `.aiworkspace/note/finance/data_architecture/`를 새 canonical data / DB architecture 위치로 만들었다
  - `DATA_FLOW_MAP.md`, `DB_SCHEMA_MAP.md`, `TABLE_SEMANTICS.md`, `DATA_QUALITY_AND_PIT_NOTES.md`, `README.md`를 추가했다
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 sections 5~7은 요약과 링크 중심으로 줄였다
  - 앞으로 DB/table/source-of-truth/PIT/data-quality 의미 변경은 `data_architecture/`를 갱신하고, 코드 수정 flow는 `docs/architecture/`에서 관리하는 방향으로 분리했다

### 2026-04-20 - 종합 분석 문서의 8~18번은 현재 제품 지도와 문서 라우팅 역할로 정리한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 8번부터 18번까지가 현재 프로젝트 상태와 맞게 업데이트 / 정리되어야 한다고 요청함
- Interpreted goal:
  - 종합 분석 문서 후반부가 오래된 sample-strategy / 초기 구조 설명에 머물지 않고, 현재 제품 레이어, 남은 한계, 코드 / 데이터 문서 체계, Phase 25 pre-live 방향을 한 번에 안내해야 함
- Result:
  - 8~9번을 현재 제품 / 전략 / portfolio / pre-live layer와 시스템 강점 중심으로 다시 썼다
  - 10~11번을 현재 남은 한계와 데이터 품질 / PIT 요약으로 줄이고, 상세 판단은 `data_architecture/`를 우선하도록 정리했다
  - 12번을 함수 나열이 아니라 `docs/architecture/`와 대표 코드 진입점으로 이어지는 지도 형태로 정리했다
  - 13~18번을 투자 분석이 아닌 제품 개발 경계, Phase 25 pre-live 방향, 다음 개발 우선순위, 추가 데이터, 문서 사용법, automation / persistence baseline 중심으로 갱신했다
  - 앞으로 `FINANCE_COMPREHENSIVE_ANALYSIS.md`는 큰 지도 역할을 유지하고, 상세 code flow / DB semantics / phase execution / backtest result는 전용 문서로 관리한다

### 2026-04-20 - `FINANCE_COMPREHENSIVE_ANALYSIS.md`는 큰 그림이 바뀔 때만 업데이트한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`를 어떤 상황에 업데이트해야 하는지 기준을 먼저 확인한 뒤, 그 기준을 지침으로 추가해 달라고 요청함
- Interpreted goal:
  - 종합 분석 문서가 다시 상세 기록 저장소처럼 비대해지지 않도록, high-level current-state map 역할과 업데이트 조건을 명확히 고정해야 함
- Result:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`는 `finance` 시스템의 큰 그림, 제품 표면, 주요 layer, data flow, strategy family, runtime / UI workflow, Real-Money / Pre-Live 경계가 바뀔 때만 갱신하는 문서로 정리했다
  - 일회성 backtest 결과, phase checklist 상태, 상세 call flow, table별 상세 의미, 작은 UI copy, minor bug-fix 기록은 각각 `backtest_reports/`, `phases/phase*/`, `docs/architecture/`, `data_architecture/`, `WORK_PROGRESS.md` 등으로 분산 관리하기로 했다
  - `AGENTS.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, active `finance-doc-sync` skill에 같은 기준을 반영했다

### 2026-04-20 - 종합 분석 문서의 legacy 상세 메모는 archive로 분리한다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 `3. 현재 시스템 구조와 phase별 구현 히스토리`, 레거시 문서, 앞으로 기록될 메모를 같은 문서에서 계속 관리하는 것이 맞는지 검토하고 정리해 달라고 요청함
- Interpreted goal:
  - `3-1` 현재 시스템 구조와 `3-2` phase별 큰 흐름은 유지하되, 긴 legacy 상세 구현 메모는 root 문서에서 분리해 current-state map의 가독성을 회복해야 함
- Result:
  - 기존 `3-3. 상세 구현 메모` 원문을 `.aiworkspace/note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`로 이동했다
  - root `FINANCE_COMPREHENSIVE_ANALYSIS.md`에는 archive 위치와 앞으로의 기록 위치 기준만 짧게 남겼다
  - archive index와 finance doc index를 갱신해 legacy 구현 메모를 찾을 수 있게 했다

### 2026-04-20 - finance의 최종 목표는 투자 후보 / 포트폴리오 구성 제안 프로그램이다
- Request topic:
  - 사용자가 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 “투자 추천 시스템이 아니라 데이터 수집 + 백테스트 제품 개발 프로젝트”라는 문구가 최종 목표를 잘못 설명한다고 지적함
- Interpreted goal:
  - 현재 phase는 개발 / 검증 중심이지만, 프로젝트의 최종 목표는 데이터 수집과 백테스트를 기반으로 투자 후보와 포트폴리오 구성안을 제안하는 프로그램이라는 점을 명확히 해야 함
- Result:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`와 `MASTER_PHASE_ROADMAP.md`를 수정해 최종 목표와 현재 개발 단계의 경계를 분리했다
  - `AGENTS.md`와 active `finance-doc-sync` skill도 같은 기준으로 수정했다
  - 앞으로 “투자 추천이 아니다”라고 표현하지 않고, “강한 백테스트 결과가 자동으로 최종 투자 추천 / live deployment 승인이 되는 것은 아니다”라고 구분한다

### 2026-04-21 - `.aiworkspace/note/finance/` root Markdown은 상위 문서 중심으로 유지한다
- Request topic:
  - 사용자가 `.aiworkspace/note/finance/` 루트에 정리되지 않은 Markdown 파일들이 있으니, 폴더로 관리할 수 있는 파일은 폴더를 만들어 관리해 달라고 요청함
- Interpreted goal:
  - root에는 큰 지도 / 활성 로그 / 템플릿만 남기고, 운영성 문서, research 참고 자료, support-track 문서, developer flow 문서를 목적별 폴더로 이동해야 함
- Result:
  - 운영성 문서는 `.aiworkspace/note/finance/operations/`, daily market update 문서는 `.aiworkspace/note/finance/operations/daily_market_update/`, research 문서는 `.aiworkspace/note/finance/researches/`, support 논의 문서는 `.aiworkspace/note/finance/support_tracks/`, 기존 backtest refinement flow guide는 `.aiworkspace/note/finance/docs/architecture/`로 이동했다
  - `FINANCE_DOC_INDEX.md`와 관련 링크를 새 위치로 갱신했다
  - 앞으로 root `.aiworkspace/note/finance/`는 `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, glossary, active logs, phase templates 중심으로 유지한다

### 2026-04-21 - phase 상태값은 구현 상태와 사용자 QA 상태를 분리해서 읽는다
- Request topic:
  - 사용자가 `FINANCE_DOC_INDEX.md`의 `Phase별 빠른 지도`에 `completed`, `practical closeout`, `manual validation pending` 등 여러 상태값이 섞여 있어 각각의 의미를 설명하고 정형화해 달라고 요청함
- Interpreted goal:
  - phase 상태값이 "구현 완료", "사용자 QA 대기", "완전 종료"를 명확히 구분하도록 문서와 지침을 정리해야 함
- Result:
  - `FINANCE_DOC_INDEX.md`에 `Phase 상태값 읽는 법`과 권장 상태 진행 순서를 추가했다
  - `MASTER_PHASE_ROADMAP.md`의 현재 위치 상태 요약도 같은 표기 체계로 맞췄다
  - `FINANCE_TERM_GLOSSARY.md`에 `Phase Status` 용어를 추가했다
  - 이후 사용자 피드백에 따라 하나의 결합 상태값 대신 `진행 상태`와 `검증 상태`를 별도 column으로 나누는 방식으로 다시 정리했다

### 2026-04-21 - phase 상태는 진행 상태와 검증 상태를 별도 column으로 관리한다
- Request topic:
  - 사용자가 phase 상태값을 하나의 긴 값으로 합치는 것보다, `completed`, `practical_closeout`, `active` 같은 진행 상태와 manual QA 여부를 별도 column으로 분리하는 것이 더 맞지 않냐고 확인함
- Interpreted goal:
  - phase status를 더 읽기 쉬운 운영 표로 바꾸고, `first_chapter_completed`가 실제 chapter 체계를 뜻하는지 명확히 정리해야 함
- Result:
  - `FINANCE_DOC_INDEX.md`의 phase quick map을 `진행 상태`, `검증 상태`, `다음 확인` column으로 분리했다
  - `MASTER_PHASE_ROADMAP.md`의 현재 위치도 같은 구조로 바꿨다
  - `FINANCE_TERM_GLOSSARY.md`, `AGENTS.md`, active `finance-doc-sync` skill을 split status 기준으로 갱신했다
  - `first_chapter_completed`는 정식 chapter 체계가 아니라 legacy partial-completion 표현으로 정의했고, 새 문서에는 사용하지 않기로 했다

### 2026-04-21 - Phase 25 Pre-Live 후보 기록은 current candidate와 분리된 운영 registry로 관리한다
- Request topic:
  - 사용자가 문서 정리가 충분하니 Phase 25를 계속 진행하자고 요청함
- Interpreted goal:
  - Phase 25 첫 작업의 경계 정의 다음 단계로, 후보를 실전 전 어떤 운영 상태에 둘지 기록하는 포맷과 저장 위치를 확정해야 함
- Result:
  - `.aiworkspace/note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 Pre-Live 운영 상태 전용 append-only registry로 정했다
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`은 후보 자체를 정의하고, Pre-Live registry는 해당 후보의 `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 운영 상태를 기록하는 것으로 분리했다
  - `source_candidate_registry_id`로 두 registry를 연결할 수 있게 했다
  - `manage_pre_live_candidate_registry.py` helper와 `PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`를 추가했다
  - 아직 UI entry point나 실제 seed record는 추가하지 않았다. 다음 작업은 operator review workflow와 UI/report entry point 구체화다

### 2026-04-21 - Phase 25 operator review는 먼저 helper 기반 초안 생성 흐름으로 시작한다
- Request topic:
  - 사용자가 Phase 25의 다음 작업 진행을 요청함
- Interpreted goal:
  - Pre-Live registry만 만든 상태에서 멈추지 않고, current candidate를 보고 `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중 어떤 운영 상태로 둘지 초안을 만드는 흐름이 필요함
- Result:
  - `manage_pre_live_candidate_registry.py draft-from-current <registry_id>` 명령을 추가했다
  - 이 명령은 `CURRENT_CANDIDATE_REGISTRY.jsonl`의 후보를 읽어 Pre-Live 기록 초안을 출력한다
  - 기본값은 출력만 하며, 실제 `.aiworkspace/note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 저장은 `--append`가 있을 때만 수행한다
  - 기본 상태 추천은 `paper_probation -> paper_tracking`, `watchlist -> watchlist`, blocker -> `hold`, reject/fail 계열 -> `reject`, 그 외 애매한 경우 -> `re_review`로 정리했다
  - Backtest UI 버튼이나 dashboard는 아직 만들지 않았고, 다음 검토 대상으로 남겼다

### 2026-04-21 - Phase 25 Pre-Live Review는 Backtest UI에서 QA 가능한 상태로 만든다
- Request topic:
  - 사용자가 Phase 25 다음 단계 진행을 요청함
- Interpreted goal:
  - helper만으로는 사용자 QA가 불편하므로 Backtest 화면에서 current candidate를 골라 Pre-Live 운영 기록을 저장하고 확인할 수 있어야 함
- Result:
  - `Backtest` panel에 `Pre-Live Review`를 추가했다
  - `Create From Current Candidate`에서 후보 선택, Real-Money 신호 확인, Pre-Live 상태 선택, operator reason / next action / review date 수정, 저장 전 JSON 초안 확인, 명시 저장을 지원한다
  - `Pre-Live Registry`에서 저장된 active record를 확인할 수 있다
  - Phase 25 상태는 `implementation_complete / manual_qa_pending`으로 전환했다
  - 이 UI는 live trading이나 투자 승인 기능이 아니라 실전 전 운영 상태 기록 기능으로 고정했다

### 2026-04-21 - Pre-Live는 상태값이 아니라 다음 행동 기록으로 Real-Money와 구분한다
- Request topic:
  - 사용자가 Phase 25 첫 작업 문서의 `Watchlist`, `Paper Tracking`, `Hold`, `Reject`, `Re-Review`가 Real-Money의 promotion 단계와 유사해 보이며, Pre-Live에서 말하는 "다음 행동 기록"이 무엇인지 불명확하다고 지적함
- Interpreted goal:
  - Pre-Live를 단순 상태 label이 아니라 운영 action package로 정의해 Real-Money 검증 신호와의 차이를 문서상 명확히 해야 함
- Result:
  - Phase 25 첫 작업 문서에 `Real-Money와 Pre-Live의 실제 차이`와 `다음 행동 기록 정의`를 추가했다
  - Pre-Live 다음 행동 기록은 `operator_reason`, `next_action`, `review_date`, `tracking_plan.cadence`, `tracking_plan.stop_condition`, `tracking_plan.success_condition`, `docs`를 포함하는 것으로 정의했다
  - Phase 25 plan, Pre-Live registry guide, glossary, checklist를 같은 기준으로 갱신했다
  - 결론적으로 `pre_live_status`는 Real-Money와 비슷해 보일 수 있지만, Pre-Live의 핵심은 "무엇을 언제 다시 확인하고, 어떤 조건이면 중단/진행할지"를 남기는 운영 기록이다

### 2026-04-21 - Phase 25는 사용자 QA 완료 후 closeout한다
- Request topic:
  - 사용자가 Phase 25 QA checklist를 완료했으니 phase 마무리를 진행해 달라고 요청함
- Interpreted goal:
  - Phase 25를 `implementation_complete / manual_qa_pending` 상태에서 `complete / manual_qa_completed`로 전환하고, roadmap / index / closeout 문서가 같은 상태를 말하도록 동기화해야 함
- Result:
  - Phase 25 TODO, completion summary, next-phase preparation, checklist를 closeout 상태로 갱신했다
  - `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 Phase 25 상태도 같은 기준으로 맞췄다
  - Phase 25의 결론은 Pre-Live 운영 기록 workflow 완료이며, live trading 또는 자동 투자 승인 기능은 여전히 열지 않는 것으로 유지했다

### 2026-04-21 - Phase 26~30은 제품 기반 강화 구간으로 구성한다
- Request topic:
  - 사용자가 Phase 25 이후 Phase 26~30을 어떤 방향으로 구성할지 협의했고, 추천한 방향대로 진행하자고 확정함
- Interpreted goal:
  - Live Readiness / Final Approval로 바로 가지 않고, 그 전 단계로 데이터 신뢰성, 전략 parity, 후보 검토, 포트폴리오 제안 기반을 순서대로 강화해야 함
- Result:
  - Phase 26은 `Foundation Stabilization And Backlog Rebase`로 열었다
  - Phase 27은 `Data Integrity And Backtest Trust Layer`
  - Phase 28은 `Strategy Family Parity And Cadence Completion`
  - Phase 29는 `Candidate Review And Recommendation Workflow`
  - Phase 30은 `Portfolio Proposal And Pre-Live Monitoring Surface`로 정했다
  - Live Readiness / Final Approval은 Phase 30 이후 별도 phase 후보로 분리했다

### 2026-04-21 - Phase 26은 과거 pending phase를 현재 기준으로 재분류한다
- Request topic:
  - 사용자가 Phase 26을 끝까지 진행하고 마지막에 checklist를 공유해 달라고 요청함
- Interpreted goal:
  - Phase 8, 9, 12~15, 18의 오래된 `manual_qa_pending` / `practical_closeout` 상태가 현재 Phase 27 진입을 막는지 재분류해야 함
- Result:
  - 해당 phase들은 현재 immediate blocker가 아니라 이후 phase 구현과 QA에 흡수된 historical gate로 판단했다
  - roadmap / index에서는 `complete / superseded_by_later_phase`로 재분류했다
  - Phase 27 입력은 data integrity / backtest trust, Phase 28 입력은 strategy family parity, Phase 29 입력은 candidate review workflow, Phase 30 입력은 portfolio proposal / pre-live monitoring으로 나눴다
  - Live Readiness / Final Approval은 여전히 Phase 30 이후 별도 phase로 둔다
### 2026-04-22 - Phase 26 QA 완료 및 Phase 27 진입 준비
- User request:
  - Phase 26 QA 완료를 선언함
- Interpreted goal:
  - Phase 26을 `complete / manual_qa_completed`로 closeout하고 Phase 27로 넘어갈 수 있게 문서 상태를 동기화
- Analysis result:
  - Phase 26은 과거 backlog / pending 상태를 현재 제품 기준으로 재분류했고, 사용자가 checklist QA를 완료했다
  - 다음 phase는 `Data Integrity And Backtest Trust Layer`로 여는 것이 맞다
- Follow-up:
  - Phase 27 시작 시 데이터 가능 범위, stale/missing ticker, malformed row, common-date truncation, backtest preflight 설명을 우선 다룬다

### 2026-04-22 - Phase 27은 backtest 결과의 데이터 신뢰 조건을 먼저 보이게 만든다
- User request:
  - Phase 26 완료 후 다음 단계 진행을 요청함
- Interpreted goal:
  - Phase 27을 열고, 사용자가 백테스트 결과를 볼 때 "이 결과가 어떤 데이터 범위와 품질 조건에서 나온 것인지"를 먼저 확인할 수 있게 해야 함
- Analysis result:
  - 첫 작업 단위는 새 전략 개발이나 투자 분석이 아니라 trust-layer 표시다
  - Backtest result bundle에 요청 종료일, 실제 결과 종료일, 결과 row 수, excluded ticker, malformed price row, price freshness 정보를 남긴다
  - Latest Backtest Run 상단에는 `Data Trust Summary`를 보여 결과 해석 전에 데이터 가용성 / 최신성 / 제외 사유를 확인하게 한다
  - Global Relative Strength는 Phase 24에서 stale ticker 이슈가 실제로 드러났으므로 Phase 27 price-freshness preflight의 첫 적용 대상으로 삼는다
- Follow-up:
  - Phase 27 QA에서는 Data Trust Summary가 사용자의 실제 해석 흐름에 충분히 도움이 되는지 확인하고, 필요하면 다른 strategy family에도 같은 trust-layer 표현을 확장한다

### 2026-04-22 - Phase 27 QA 완료 후 Phase 28로 넘긴다
- User request:
  - Phase 27 QA 완료를 선언하고 phase 마무리를 요청함
- Interpreted goal:
  - Phase 27을 `complete / manual_qa_completed`로 closeout하고, 다음 단계인 Phase 28로 넘어갈 수 있게 문서 상태를 맞춘다
- Analysis result:
  - 사용자는 Global Relative Strength preflight, Latest Backtest Run의 Data Trust Summary, Data Quality Details, Meta/history 연결을 확인했다
  - Phase 27의 핵심 성과는 성과 개선이 아니라 "백테스트 결과가 어떤 데이터 조건에서 나온 것인지 먼저 보이는 trust layer"를 만든 것이다
  - 남은 확장 주제는 Phase 28에서 annual / quarterly / 신규 전략의 family parity 관점으로 다룬다
- Follow-up:
  - Phase 28을 열 때는 `Data Trust Summary`, `price_freshness`, history/load/replay 보존, Real-Money/Guardrail parity 범위를 함께 검토한다

### 2026-04-22 - Phase 28은 strategy family 차이를 먼저 보이게 만든다
- User request:
  - Phase 28 진행을 요청함
- Interpreted goal:
  - annual strict, quarterly strict, price-only ETF 전략이 같은 Backtest 화면 안에서 다르게 보이는 이유를 먼저 설명해야 함
- Analysis result:
  - 첫 작업 단위는 새 전략 개발이 아니라 `Strategy Capability Snapshot`이다
  - annual strict는 가장 성숙한 Real-Money / Guardrail surface로 설명한다
  - strict quarterly prototype은 Data Trust와 Portfolio Handling은 지원하지만 Real-Money promotion / Guardrail 판단은 아직 annual 중심이라고 설명한다
  - Global Relative Strength는 재무제표 selection history 대상이 아니라 price-only ETF relative strength 전략이라고 설명한다
  - 이 snapshot은 Single Strategy와 Compare strategy box에서 확인하게 한다
- Follow-up:
  - 다음 작업은 history / load-into-form / run-again / saved replay에서 strategy별 핵심 설정이 실제로 빠지지 않는지 점검하는 것이다

### 2026-04-22 - Phase 28 history 재진입은 먼저 저장 상태를 보여줘야 한다
- User request:
  - Phase 28 다음 단계 진행을 요청함
- Interpreted goal:
  - annual strict, quarterly prototype, GRS 등 전략별 history record가 `Load Into Form` / `Run Again`에서 핵심 설정을 잃지 않는지 확인 가능해야 함
- Analysis result:
  - history 재실행 로직을 크게 바꾸기보다, selected history record에 어떤 값이 저장되어 있는지 먼저 보여주는 표가 가장 안전한 다음 단위라고 판단했다
  - 새 `History Replay / Load Parity Snapshot`은 strategy key, 기간, universe, result window, data trust, factor cadence, overlay, portfolio handling, real-money / guardrail, GRS score 설정의 저장 여부를 보여준다
  - 새 history record는 `guardrail_reference_ticker`, `actual_result_start/end`, `result_rows`, `price_freshness`, `excluded_tickers`, `malformed_price_rows`를 추가 보존한다
- Follow-up:
  - 다음 Phase 28 작업은 saved portfolio replay parity와 compare / saved replay에서 Data Trust Summary를 어디까지 확장할지 결정하는 것이다

### 2026-04-22 - Phase 28 saved portfolio 재진입도 저장 상태를 먼저 보여줘야 한다
- User request:
  - Phase 28 다음 단계 진행을 요청함
- Interpreted goal:
  - 저장된 포트폴리오를 다시 불러오거나 재실행하기 전에 compare 공용 입력, strategy override, weight/date alignment가 남아 있는지 확인 가능해야 함
- Analysis result:
  - Saved Portfolio는 투자 승인 기록이 아니라 compare + weighted portfolio 재현용 artifact다
  - 따라서 `Saved Portfolio Replay / Load Parity Snapshot`을 추가해 selected strategy, compare period, weights, date policy, strategy override map, 전략별 핵심 설정 저장 상태를 보여주게 했다
  - replay history context에는 `weights_percent`를 함께 남겨 나중에 saved portfolio replay 결과를 읽을 때 weight 구성을 더 쉽게 추적할 수 있게 했다
- Follow-up:
  - 다음 Phase 28 판단은 Data Trust Summary를 compare / saved replay까지 확장할지, Real-Money / Guardrail parity를 어떤 전략군까지 맞출지다

### 2026-04-22 - Phase 28 compare / weighted 결과도 component data trust가 보여야 한다
- User request:
  - Phase 28 다음 단계 진행을 요청함
- Interpreted goal:
  - single strategy 결과에서 확인하던 Data Trust Summary를 compare, weighted portfolio, saved replay에서도 해석 가능한 형태로 확장해야 함
- Analysis result:
  - compare는 여러 전략 결과를 나란히 보는 화면이므로, 성과표만 보면 실제 결과 기간이나 데이터 품질 차이를 놓칠 수 있다
  - `Strategy Comparison > Data Trust`를 추가해 전략별 requested end, actual result end, result rows, price freshness, excluded/malformed ticker, warning count를 보여주게 했다
  - `Weighted Portfolio Result > Component Data Trust`를 추가해 composite 결과를 보기 전에 구성 전략별 데이터 조건을 확인하게 했다
  - compare / weighted / saved replay history context에도 data trust rows를 남긴다
- Follow-up:
  - 다음 Phase 28 판단은 Real-Money / Guardrail parity를 quarterly와 ETF 전략군에 어디까지 맞출지 정하는 것이다

### 2026-04-23 - Phase 28 Real-Money / Guardrail parity는 같은 기능 강제 적용이 아니라 scope 구분이다
- User request:
  - Phase 28 다음 단계 진행을 요청함
- Interpreted goal:
  - annual strict, quarterly prototype, price-only ETF 전략군의 Real-Money / Guardrail 지원 차이를 사용자가 같은 화면에서 혼동하지 않게 해야 함
- Analysis result:
  - quarterly prototype에는 annual strict 수준의 promotion / guardrail surface를 억지로 붙이지 않는다
  - annual strict는 full strict equity Real-Money / Guardrail 기준 surface로 유지한다
  - Global Relative Strength는 ETF operability + cost / benchmark first pass로 보며, dedicated ETF underperformance / drawdown guardrail은 아직 없다
  - GTAA, Risk Parity Trend, Dual Momentum은 ETF Real-Money + ETF guardrail first pass로 구분한다
  - compare, history, saved portfolio에 `Real-Money / Guardrail Scope` 표를 추가해 replay 전에 어떤 검증 범위의 결과인지 확인하게 했다
- Follow-up:
  - Phase 28 checklist QA에서 compare tab, history scope table, saved portfolio scope table이 실제로 이해되는지 확인한다

### 2026-04-23 - Phase 28 QA 완료 후 closeout한다
- User request:
  - Phase 28 QA 완료를 선언하고 최종 확인 후 종료를 요청함
- Interpreted goal:
  - Phase 28을 `complete` / `manual_qa_completed` 상태로 닫고 Phase 29 handoff 문서를 정리한다
- Analysis result:
  - Phase 28의 핵심 완료 기준은 새 전략 추가가 아니라 strategy family별 기능 범위, cadence 차이, history / saved portfolio 재진입, compare / weighted data trust, Real-Money / Guardrail scope가 사용자가 이해할 수 있게 보이는지였다
  - 사용자가 checklist QA 완료를 선언했으므로 remaining QA 항목을 완료 처리하고 roadmap / index / closeout 문서를 같은 상태로 동기화한다
- Follow-up:
  - 다음 단계는 Phase 29 `Candidate Review And Recommendation Workflow`를 열고, 백테스트 결과를 후보 검토 / 추천 workflow로 넘기는 절차를 설계하는 것이다

### 2026-04-23 - Phase 29 첫 작업은 Candidate Review Board다
- User request:
  - Phase 28 종료 후 다음 단계 진행을 요청함
- Interpreted goal:
  - Phase 29를 열고 current candidate를 후보 검토 workflow로 읽는 첫 UI / 문서 단위를 구현한다
- Analysis result:
  - Phase 29는 최종 투자 승인이나 live trading을 여는 단계가 아니다
  - 첫 작업은 `Backtest > Candidate Review` panel을 추가해 active current candidate registry row를 review board로 보여주는 것이다
  - Candidate Board는 후보별 review stage, 존재 이유, suggested next step을 보여주고, Inspect Candidate에서 Pre-Live Review로 넘길 수 있게 한다
  - `Send To Compare`에서는 기존 current candidate re-entry를 재사용해 compare form으로 후보 묶음을 넘긴다
- Follow-up:
  - Phase 29 QA에서는 Candidate Review가 투자 추천처럼 보이지 않고, compare / Pre-Live Review로 넘기는 중간 workflow로 읽히는지 확인한다
  - 다음 작업 후보는 Latest Backtest Run 또는 History record를 candidate review 초안으로 넘기는 handoff다

### 2026-04-23 - Latest / History 결과는 후보 검토 초안으로 먼저 보낸다
- User request:
  - Phase 29 다음 작업 진행을 요청함
- Interpreted goal:
  - 새 백테스트 결과나 history run을 바로 current candidate registry에 저장하지 않고, 먼저 후보 검토 초안으로 읽는 handoff를 만든다
- Analysis result:
  - `Latest Backtest Run`과 `History`에 `Review As Candidate Draft`를 추가했다
  - `Candidate Review > Candidate Intake Draft`는 suggested record type, result snapshot, Real-Money signal, data trust snapshot을 보여준다
  - 이 draft는 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 자동 저장되지 않으며, 투자 추천이나 live approval도 아니다
- Follow-up:
  - 다음 판단은 Candidate Intake Draft를 실제 registry row, near-miss record, scenario note 중 어디로 남길지 기준을 정하는 것이다

### 2026-04-23 - Candidate Intake Draft는 먼저 Review Note로 남긴다
- User request:
  - Phase 29 다음 작업 진행을 요청함
- Interpreted goal:
  - 후보 검토 초안을 current candidate registry에 자동 등록하지 않고, 사람이 판단한 내용과 다음 행동을 안전하게 저장할 중간 기록이 필요함
- Analysis result:
  - `Candidate Review Note`를 `CURRENT_CANDIDATE_REGISTRY.jsonl`과 별도인 `.aiworkspace/note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl`에 저장하는 구조로 정했다
  - Review Note는 review decision, operator reason, next action, optional review date, result snapshot, Real-Money signal, data trust snapshot을 담는다
  - 이 기록은 투자 추천, live approval, current candidate 자동 승격이 아니다
- Follow-up:
  - 다음 판단은 review note 중 어떤 것을 실제 current candidate registry row로 남길지 기준을 정하는 것이다

### 2026-04-23 - Review Note는 명시적 preview 후 후보 registry에 append한다
- User request:
  - Phase 29 다음 작업 진행을 요청함
- Interpreted goal:
  - 저장된 Candidate Review Note 중 후보 목록에 남길 만한 것을 current candidate registry row로 만드는 기준과 UI 흐름이 필요함
- Analysis result:
  - `Candidate Review > Review Notes`에 `Prepare Current Candidate Registry Row` 영역을 추가했다
  - registry id, record type, strategy family, strategy name, candidate role, title, notes를 저장 전 확인하게 했다
  - `Append To Current Candidate Registry`를 눌러야만 `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`에 append된다
  - `Reject For Now` note는 registry append를 막아 거절 판단이 후보 목록에 섞이지 않게 했다
- Follow-up:
  - Phase 29 QA에서는 review note 저장, registry row preview, explicit append가 투자 추천이나 live approval처럼 보이지 않는지 확인한다

### 2026-04-23 - Phase 29는 구현 완료 후 사용자 QA 대기 상태다
- User request:
  - 다음 단계 진행을 요청함
- Interpreted goal:
  - Phase 29에서 더 붙일 구현이 남았는지 확인하고, 남지 않았다면 QA handoff 상태를 명확히 해야 함
- Analysis result:
  - Phase 29의 네 구현 단위는 완료됐다
    - Candidate Review Board
    - Result To Candidate Review Handoff
    - Candidate Review Note
    - Review Note To Registry Draft
  - 따라서 진행 상태는 `implementation_complete`, 검증 상태는 `manual_qa_pending`으로 정리하는 것이 맞다
  - 사용자 checklist QA 완료 전에는 Phase 30으로 넘어가지 않는다
- Follow-up:
  - 사용자는 `.aiworkspace/note/finance/phases/phase29/PHASE29_TEST_CHECKLIST.md` 기준으로 QA를 진행하고, 완료되면 Phase 29 closeout 후 Phase 30으로 넘어간다

### 2026-04-23 - Candidate Board의 기존 후보는 Phase 29 QA용 sample candidate set으로 본다
- User request:
  - Candidate Board 후보가 Single Strategy 백테스트 결과가 자동 검증되어 올라온 것인지 확인하고, 추후 개발 필요성을 기록해 달라고 요청함
- Interpreted goal:
  - 현재 Candidate Board의 기존 후보군 성격을 명확히 하고, 향후 실제 후보 lifecycle board로 고도화해야 한다는 backlog를 남긴다
- Analysis result:
  - 현재 Candidate Board의 기존 row는 최신 Single Strategy 결과 자동 선별물이 아니다
  - 이전 phase에서 문서화한 후보를 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 seed처럼 남겨 둔 sample / registry 후보군이다
  - Phase 29 QA에서는 이 후보들을 workflow 확인용 sample candidate set으로 본다
  - 추후 phase에서는 sample 후보와 실제 사용자 append 후보를 구분하고, 후보 lifecycle / source / archive 상태를 더 잘 관리하는 Candidate Board 고도화가 필요하다
- Follow-up:
  - 이 내용은 `PHASE29_NEXT_PHASE_PREPARATION.md`의 future development note와 `PHASE29_TEST_CHECKLIST.md`의 Candidate Board 확인 항목에 반영했다

### 2026-04-23 - GTAA sample 후보도 Compare로 보낼 수 있어야 한다
- User request:
  - Phase 29 QA 중 `Load Recommended Candidates`와 `Load Lower-MDD Alternatives`를 누르면 GTAA 후보에 대해 "compare prefill contract가 준비되지 않았습니다" 경고가 나오며, 현재 환경에서 사용자가 해결할 방법이 없다고 보고함
- Interpreted goal:
  - Candidate Review의 Send To Compare 흐름에서 sample / seed GTAA 후보도 실제 compare form으로 옮겨져야 한다
- Analysis result:
  - 원인은 GTAA 후보 row에 `contract`는 있지만 explicit `compare_prefill`이 없고, 기존 변환 로직이 strict annual seed 후보만 처리했기 때문이다
  - GTAA registry `contract`를 compare override로 변환하는 fallback을 추가했다
  - registry에 남은 복합 표현 `cash_only_or_defensive_bond_preference`는 GTAA 실행 가능 값인 `defensive_bond_preference`로 정규화한다
- Follow-up:
  - Phase 29 QA에서는 `Load Recommended Candidates`와 `Load Lower-MDD Alternatives`가 GTAA 후보를 경고 없이 compare form에 채우는지 확인한다
  - 향후 GTAA 외 신규 전략 후보도 compare로 보내려면 registry row에 explicit `compare_prefill` 또는 변환 가능한 `contract`를 남기는 규칙이 필요하다

### 2026-04-28 - Phase 30 전에 product-flow 이해와 리팩토링 경계를 먼저 재정렬한다
- User request:
  - Phase 29 QA 완료 후, Candidate Review / Review Note / Registry Draft 같은 새 기능의 실제 사용 이유가 흐려졌고, `backtest.py`가 16k lines 이상으로 커져 리팩토링이 필요해 보인다고 문제 제기함
- Interpreted goal:
  - 최종 목표인 실전 포트폴리오 및 가이드 제시까지 가기 전에, 만드는 사람도 전체 흐름을 충분히 이해하고 갈 수 있는 합리적 진행 순서를 정해야 함
- Analysis result:
  - Phase 30을 기능 구현으로 바로 진행하면 Portfolio Proposal이 Candidate Review / Pre-Live 위에 또 얹혀 이해 부채와 UI 복잡도가 커질 위험이 있다
  - 반대로 지금 전면 리팩토링만 시작하면 어떤 product boundary를 기준으로 나눌지 불명확해지고, 투자 후보 / 포트폴리오 제안 목표와 멀어질 수 있다
  - 가장 합리적인 방향은 Phase 29 closeout 후 곧바로 Phase 30 구현을 시작하지 않고, 짧은 `Phase 30 준비 작업`을 먼저 두는 것이다
  - 준비 작업의 핵심은 `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 Phase 29 이후 기준으로 다시 쓰고, `Backtest Run -> Candidate Draft -> Candidate Review Note -> Current Candidate Registry -> Compare / Pre-Live -> Portfolio Proposal -> Live Readiness` 흐름을 canonical product map으로 고정하는 것이다
  - 리팩토링은 stop-the-world 방식이 아니라 이 product map에 맞춰 `Candidate Review`, `Pre-Live Review`, `History`, `Compare / Weighted / Saved Portfolio`, `Single Strategy latest result`, registry persistence helper를 점진적으로 분리하는 방식이 적절하다
- Follow-up:
  - Phase 29 closeout 때 checklist 상태 불일치를 정리하고, Phase 30을 열기 전 첫 작업을 `사용 흐름 재정렬 + backtest.py module boundary plan`으로 잡는 것을 권장한다

### 2026-04-28 - Phase 29 QA 완료에 따라 closeout한다
- User request:
  - Phase 29 QA checklist 완료를 선언하고 Phase 29 완료 처리를 요청함
- Interpreted goal:
  - Phase 29를 `complete / manual_qa_completed` 상태로 닫고, roadmap / index / phase closeout 문서가 같은 상태를 말하도록 동기화해야 함
- Analysis result:
  - Phase 29의 구현 단위인 Candidate Review Board, Result To Candidate Review Handoff, Candidate Review Note, Review Note To Registry Draft는 구현과 QA가 끝난 것으로 처리한다
  - Phase 29는 투자 승인이나 live trading phase가 아니라 후보 검토 workflow phase로 닫힌다
  - 다음 단계는 Phase 30 기능 구현 직행이 아니라, Phase 29 이후 기준의 사용 흐름 재정렬과 `backtest.py` 리팩토링 경계 검토를 먼저 하는 것이 안전하다
- Follow-up:
  - Phase 30을 열기 전 `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 새 canonical flow로 다시 쓰고, Backtest UI 모듈 분리 계획을 세운다

### 2026-04-28 - Phase 30 첫 작업은 사용 흐름 재정렬과 `backtest.py` 리팩토링 경계다
- User request:
  - Phase 29가 마무리되었으니 `사용 흐름 재정렬 + backtest.py 리팩토링 경계 검토`를 진행하자고 요청함
- Interpreted goal:
  - Portfolio Proposal 기능을 바로 붙이기 전에, Phase 29 이후의 후보 검토 흐름을 다시 이해 가능하게 만들고 큰 Backtest UI 파일을 어떤 경계로 나눌지 정해야 함
- Analysis result:
  - Phase 30을 active로 열되 첫 작업은 기능 구현이 아니라 product-flow reorientation으로 둔다
  - 기준 흐름은 `Ingestion / Data Trust -> Single Strategy Backtest -> Real-Money Signal -> Hold / Blocker Resolution -> Compare -> Candidate Draft -> Candidate Review Note -> Current Candidate Registry -> Candidate Board / Compare / Pre-Live Review -> Portfolio Proposal -> Live Readiness / Final Approval`이다
  - `backtest.py` 리팩토링은 stop-the-world 방식이 아니라 Candidate Review, Pre-Live Review, registry helper, History, Saved Portfolio / Weighted Portfolio, result display, strategy forms 순서로 점진 분리하는 것이 안전하다
  - 실제 Portfolio Proposal 저장소나 UI 구현은 다음 작업 단위에서 계약을 먼저 정한 뒤 진행한다
- Follow-up:
  - 다음 작업은 Candidate Review / Pre-Live / registry helper 중 작은 모듈 분리를 먼저 할지, Portfolio Proposal row 계약을 먼저 정의할지 선택한다

### 2026-04-28 - 현재 흐름은 포트폴리오 발견 엔진이 아니라 후보 검증 운영 흐름이다
- User request:
  - `테스트에서 상용화 후보 검토까지 사용하는 흐름`이 실제로 실전 포트폴리오를 찾기 위한 올바른 흐름인지, 프로그램 취지와 맞는지 판단을 요청함
- Interpreted goal:
  - Phase 30의 product-flow가 단순히 기능을 이어 붙인 절차인지, 아니면 최종 목표인 실전 포트폴리오 / 가이드 제시로 가는 합리적인 제품 경로인지 검토해야 함
- Analysis result:
  - 현재 흐름은 실전 포트폴리오를 자동으로 찾아내는 discovery engine이라기보다, 좋은 백테스트 결과를 바로 투자 후보로 착각하지 않게 만드는 evidence handling / candidate governance flow에 가깝다
  - 이 방향은 프로그램 취지와 맞다. 데이터 신뢰성, Real-Money 신호, compare, 후보 초안, review note, registry, Pre-Live 기록을 거치게 하므로 실전 후보 검토에 필요한 안전장치를 만든다
  - 다만 "실전 포트폴리오를 찾는 과정"으로 완성되려면 아직 Portfolio Proposal 단계에서 목적 함수, 위험 예산, 후보 간 상관/중복, 비중 산정, benchmark / drawdown / turnover / capacity / paper tracking feedback을 함께 다루는 발견 및 구성 layer가 추가되어야 한다
  - 따라서 현재 흐름은 올바른 기반이지만 최종 완성형은 아니다. 지금 만든 것은 후보를 안전하게 보존하고 검토하는 레일이고, Phase 30 후속 작업에서 portfolio construction layer를 붙여야 진짜 포트폴리오 발견 흐름이 된다
- Follow-up:
  - Phase 30 다음 작업은 단순 UI 추가보다 Portfolio Proposal row 계약을 먼저 정의해, 어떤 후보 묶음이 어떤 목적과 위험 역할로 포트폴리오 제안이 되는지 명확히 하는 것이 중요하다

### 2026-04-28 - 모델 변경과 컨텍스트 유실에도 현재 방향성은 최종 목표와 대체로 정렬되어 있다
- User request:
  - 이전 개발 모델과 현재 모델이 다르고, 토큰 부족이나 과거 정보 유실로 개발 방향이 잘못 흘렀을 가능성이 있으니 현재 방향성이 최종 목표와 맞는지 검증을 요청함
- Interpreted goal:
  - 현재 phase 흐름이 우연히 기능을 붙인 결과인지, 아니면 `실전 포트폴리오 및 가이드 제시`라는 north star에 맞게 진행되고 있는지 재평가해야 함
- Analysis result:
  - 현재 방향성은 대체로 올바르다. 데이터 수집, DB-backed backtest, 전략 실행, 결과 재현, data trust, Real-Money 신호, candidate review, pre-live 기록 순서가 최종 포트폴리오 제안 전에 필요한 기반을 만든다
  - 특히 `좋은 백테스트 = 즉시 투자`로 흐르지 않게 Data Trust / Real-Money / Review Note / Registry / Pre-Live를 둔 것은 실전 포트폴리오 개발 방향에 맞는 보수적 설계다
  - 다만 모델 변경과 장기 개발의 영향으로 기능과 문서가 많이 늘었고, `backtest.py`가 16k lines 이상으로 커졌으며, 포트폴리오 구성 논리는 아직 명시적 계약으로 정리되지 않았다
  - 따라서 현재 상태는 "방향을 잃었다"가 아니라 "올바른 기반을 많이 만들었지만, 이제 portfolio construction contract와 code boundary를 명확히 하지 않으면 길을 잃을 수 있는 시점"으로 보는 것이 맞다
- Follow-up:
  - Phase 30의 다음 핵심 작업은 Portfolio Proposal 계약 정의와 Backtest UI 점진 리팩토링이다
  - 앞으로 phase closeout 때마다 현재 작업이 north star, 즉 데이터 기반 투자 후보 / 포트폴리오 제안으로 이어지는지 간단한 direction check를 남기는 것이 좋다

### 2026-04-28 - Guide 흐름은 전체 흐름이지만 Phase 29 구간이 촘촘해 보일 수 있다
- User request:
  - `테스트에서 상용화 후보 검토까지 사용하는 흐름`의 6~10번이 Phase 29 내용만 추가된 것처럼 보이는데, 전체 흐름으로 정리된 것이 맞는지 독립적으로 확인해 달라고 요청함
- Interpreted goal:
  - 사용자 의문을 그대로 따라가지 말고, Guide가 전체 테스트 -> 후보 검토 흐름인지 또는 Phase 29 기능 나열로 치우쳤는지 검토해야 함
- Analysis result:
  - 현재 Guide는 1~5단계가 데이터 최신화 / Single Strategy / Real-Money / Hold 해결 / Compare로 이어지는 테스트 및 검증 구간이고, 6~10단계가 Candidate Draft / Review Note / Registry / Candidate Board / Pre-Live로 이어지는 후보 검토 및 운영 기록 구간이다
  - 따라서 전체 흐름 자체는 맞다. 다만 6~10단계가 Phase 29에서 구현된 기능을 촘촘히 반영하므로, 구간 구분 없이 읽으면 Phase 29 기능 설명처럼 보일 수 있다
  - Guide와 Phase 30 checklist에 `1~5 = 테스트 / 검증`, `6~10 = 후보 검토 / 운영 기록`, `11 = 포트폴리오 제안 / live readiness 경계`라는 큰 구간 설명을 추가했다
- Follow-up:
  - 사용자는 checklist에서 각 세부 기능보다 먼저 큰 구간 구분이 납득되는지 확인한다

### 2026-04-28 - Phase 30 다음 작업은 Portfolio Proposal 계약 정의로 진행한다
- User request:
  - Phase 30의 다음 단계를 진행하고, 최종 QA는 마지막에 진행하겠다고 요청함
- Interpreted goal:
  - 첫 작업 QA를 지금 완료 gate로 삼지 않고, Phase 30 후속 작업을 계속 진행해야 함
- Analysis result:
  - Phase 30의 다음 작업은 UI를 바로 만드는 것보다 Portfolio Proposal row 계약을 먼저 정의하는 것이 적절하다
  - 계약에는 proposal objective, candidate refs, proposal roles, target weights, construction method, risk constraints, evidence snapshot, open blockers, operator decision이 포함되어야 한다
  - 향후 저장소 후보는 `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이지만, 이번 작업에서는 파일 생성 / append helper / UI 구현을 하지 않는다
  - Portfolio Proposal은 saved portfolio replay나 current candidate registry를 대체하지 않고, 후보 묶음을 왜 제안 초안으로 보는지 설명하는 별도 검토 단위다
- Follow-up:
  - 다음 작업은 Proposal UI / persistence 구현 또는 current candidate registry helper 모듈 분리 중 하나로 이어진다

### 2026-04-28 - Phase 30 전체 목표와 첫 작업 단위를 구분해야 한다
- User request:
  - Phase 30이 `사용 흐름 재정렬 + backtest.py 리팩토링 경계 검토` 작업으로 진행되는 것으로 이해했는데, 왜 갑자기 `Portfolio Proposal Contract Second Work Unit`이 진행되는지 설명을 요청함
- Interpreted goal:
  - Phase 30 전체 목표와 첫 번째 작업 단위, 두 번째 작업 단위의 관계를 명확히 해야 함
- Analysis result:
  - Phase 30 전체 목표는 후보 묶음을 Portfolio Proposal / Pre-Live Monitoring으로 연결하는 것이다
  - `사용 흐름 재정렬 + backtest.py 리팩토링 경계 검토`는 Phase 30 전체가 아니라 첫 번째 작업 단위였다
  - 첫 번째 작업에서 Portfolio Proposal이 흐름상 어디에 오는지 정했으므로, 두 번째 작업에서는 UI / 저장소 구현 전에 Proposal row 계약을 정의했다
  - 따라서 `Portfolio Proposal Contract Second Work Unit`은 첫 작업을 건너뛴 것이 아니라, 첫 작업 이후 이어지는 설계 단계다
- Follow-up:
  - Phase 30 TODO와 plan, second work-unit 문서에 `Phase 30 전체 목표 / 첫 번째 작업 / 두 번째 작업 / 이후 작업 후보` 구분을 명시했다

### 2026-04-28 - Phase 30 안에서 작은 `backtest.py` 리팩토링을 먼저 시작한다
- User request:
  - 이전에 제안한 방향대로 그대로 진행해 달라고 요청함
- Interpreted goal:
  - Portfolio Proposal UI를 붙이기 전에 `backtest.py`가 더 커지는 것을 막기 위해 작고 안전한 helper split을 먼저 진행한다
- Analysis result:
  - 대규모 `backtest.py` 분리는 위험하므로, UI rendering과 session state를 건드리지 않는 registry JSONL I/O helper부터 분리한다
  - `app/web/runtime/candidate_registry.py`를 추가해 current candidate registry, candidate review notes, pre-live registry read / append helper를 담당하게 했다
  - Candidate Review UI, Pre-Live UI, compare prefill behavior, row schema, JSONL path, append-only semantics는 유지했다
  - 이번 작업은 전체 Backtest UI refactor가 아니라 Phase 30의 첫 실제 code split이다
- Follow-up:
  - 다음 리팩토링 후보는 Candidate Review display / draft helper 또는 Pre-Live Review display / draft helper다
  - Portfolio Proposal UI를 먼저 구현한다면 새 `candidate_registry.py` helper pattern을 재사용한다

### 2026-04-28 - Phase 30 네 번째 작업은 Portfolio Proposal Draft UI / persistence로 진행한다
- User request:
  - Phase 30에서 이전에 진행하려던 방향대로 다음 단계를 진행해 달라고 요청함
- Interpreted goal:
  - registry helper split 이후에는 계약으로만 남아 있던 Portfolio Proposal을 실제 Backtest 화면에서 작성하고 저장할 수 있게 만들어야 함
- Analysis result:
  - `Backtest > Portfolio Proposal` panel을 추가해 current candidate 여러 개를 proposal draft로 묶는 흐름을 구현했다
  - proposal draft에는 objective, proposal type/status, candidate refs, proposal role, target weight, weight reason, Real-Money / Pre-Live 상태, blocker, operator decision을 남긴다
  - 저장소는 `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이며 첫 proposal 저장 시 생성되는 append-only registry다
  - 이 기능은 saved portfolio replay, live trading approval, automatic optimizer를 대체하지 않는다
- Follow-up:
  - 다음 작업 후보는 proposal monitoring surface 또는 Candidate Review / Pre-Live / History / Saved Portfolio의 추가 모듈 분리다

### 2026-04-28 - Phase 30 다섯 번째 작업은 Proposal Monitoring Review로 진행한다
- User request:
  - Phase 30 다음 단계를 계속 진행해 달라고 요청함
- Interpreted goal:
  - Proposal Draft UI 다음에는 저장된 proposal을 단순 JSON inspect로만 두지 않고, 검토 상태와 남은 확인 항목을 볼 수 있는 monitoring surface가 필요함
- Analysis result:
  - `Backtest > Portfolio Proposal > Monitoring Review` tab을 추가했다
  - 저장된 proposal draft를 monitoring state, component table, blocker, review gap, operator decision 기준으로 다시 읽을 수 있게 했다
  - `blocked`, `needs_review`, `review_ready`는 review summary일 뿐 live approval 상태가 아니다
  - proposal monitoring은 current candidate / pre-live registry / saved portfolio를 자동 변경하지 않는다
- Follow-up:
  - 다음 작업 후보는 paper / pre-live tracking feedback을 proposal에 연결하거나, Candidate Review / Pre-Live / History / Saved Portfolio의 추가 모듈 분리를 진행하는 것이다

### 2026-04-28 - Phase 30 여섯 번째 작업은 Proposal Pre-Live Feedback으로 진행한다
- User request:
  - Phase 30 다음 작업을 계속 진행해 달라고 요청함
- Interpreted goal:
  - Proposal Monitoring Review 다음에는 저장된 proposal이 현재 Pre-Live 운영 상태와 어긋나는지 확인할 수 있어야 함
- Analysis result:
  - `Backtest > Portfolio Proposal > Pre-Live Feedback` tab을 추가했다
  - proposal 저장 당시 component별 `pre_live_status` snapshot과 현재 active Pre-Live registry record를 비교한다
  - status drift, missing active Pre-Live record, active weight가 있는 hold / reject / re_review 상태, overdue review date를 feedback gap으로 보여준다
  - 이 surface는 proposal row나 Pre-Live record를 자동 수정하지 않고, 상태 변경은 `Backtest > Pre-Live Review`에서 별도 저장해야 한다
- Follow-up:
  - 다음 작업 후보는 paper tracking performance feedback loop 또는 Candidate Review / Pre-Live / History / Saved Portfolio 추가 모듈 분리다

### 2026-04-28 - Phase 30은 paper tracking feedback까지 마무리한 뒤 QA로 가고 리팩토링은 별도 태스크로 분리한다
- User request:
  - Phase 30에서 남은 `Paper tracking performance feedback loop`는 마무리하고 QA로 가는 것이 좋은지, `backtest.py` 추가 모듈 분리는 별도 특별 태스크로 빼는 것이 맞는지 확인 요청함
- Interpreted goal:
  - Phase 30 closeout 전에 남은 제품 기능과 구조 리팩토링을 같은 phase에 묶을지 분리할지 판단해야 함
- Analysis result:
  - `Paper tracking performance feedback loop`는 Portfolio Proposal / Pre-Live Monitoring이라는 Phase 30 목표에 직접 연결되므로 Phase 30 안에서 마무리하는 것이 자연스럽다
  - Candidate Review / Pre-Live / History / Saved Portfolio 추가 모듈 분리는 제품 기능 완성보다 codebase 구조 개선에 가깝고, 변경 범위가 커질 수 있으므로 Phase 30 QA gate에 섞지 않는 것이 안전하다
  - 따라서 Phase 30은 paper tracking performance feedback loop를 마지막 기능 단위로 완료한 뒤 checklist QA로 넘기는 것이 적절하다
- Follow-up:
  - `backtest.py` 추가 분리는 Phase 30 closeout 이후 별도 special refactor task 또는 다음 지원 트랙으로 열어 진행한다

### 2026-04-28 - Phase 30 마지막 기능 단위는 Paper Tracking Feedback으로 닫고 manual QA로 넘긴다
- User request:
  - Phase 30을 먼저 마무리하는 것이 좋으니 1번 기능을 완료하고 사용자가 QA를 진행하겠다고 요청함
- Interpreted goal:
  - Portfolio Proposal / Pre-Live Monitoring이라는 Phase 30 목표에 직접 연결되는 마지막 제품 기능을 구현하고, 구조 리팩토링은 별도 작업으로 분리해야 함
- Analysis result:
  - `Backtest > Portfolio Proposal > Paper Tracking Feedback` tab을 추가해 proposal 저장 당시 evidence snapshot과 현재 Pre-Live `result_snapshot`의 CAGR / MDD를 비교하게 했다
  - 이 기능은 실제 paper PnL 자동 계산이나 live approval이 아니라, 현재 Pre-Live registry에 저장된 최신 성과 snapshot을 proposal 관점에서 다시 읽는 보조 surface다
  - performance signal은 `needs_paper_tracking`, `missing_current_result`, `missing_saved_snapshot`, `worsened`, `stable_or_better`로 제한해 QA에서 해석 가능한 범위로 두었다
  - Phase 30 상태는 `implementation_complete` / `manual_qa_pending`으로 전환하고, 추가 `backtest.py` 모듈 분리는 별도 special refactor task로 남겼다
- Follow-up:
  - 사용자는 `.aiworkspace/note/finance/phases/phase30/PHASE30_TEST_CHECKLIST.md` 기준으로 final manual QA를 진행한다

### 2026-04-28 - Reference Guide는 Phase 30 기능 목록이 아니라 최종 포트폴리오 탐색 흐름이어야 한다
- User request:
  - Reference / Guides의 `테스트에서 상용화 후보 검토까지 사용하는 흐름`에 Phase 30 내용이 반영되었는지 확인하되, Phase 30 내용을 11~20단계처럼 쪼개 추가하지 말라고 요청함
- Interpreted goal:
  - 사용자가 단계대로 진행해 최종적으로 실전투자 가능한 포트폴리오 후보를 찾는 큰 흐름을 보존해야 함
- Analysis result:
  - 기존 Guide는 Portfolio Proposal을 11단계에 두고 있어 큰 구조는 맞았지만, path가 `Phase 30 이후`로 되어 있어 Phase 30 구현 완료 상태와 어긋났다
  - 11단계를 `Backtest > Portfolio Proposal`로 갱신하고, Monitoring Review / Pre-Live Feedback / Paper Tracking Feedback은 별도 단계가 아니라 11단계 안에서 보는 확인 항목으로만 반영했다
  - Live Readiness / Final Approval은 여전히 이후 별도 단계로 남겨, Portfolio Proposal이 투자 승인처럼 읽히지 않게 했다
- Follow-up:
  - Phase 30 QA 때 Guide 11단계가 구현 기능을 충분히 반영하면서도 과도하게 세분화되지 않았는지 확인한다

### 2026-04-28 - 11단계 실습은 GTAA Balanced Top-2 후보로 시작한다
- User request:
  - Phase 30까지 구현된 기능을 실제로 어떻게 11단계까지 밟아야 하는지 모르겠고, 먼저 4단계 `Hold면 먼저 막히는 항목 해결`을 통과할 만한 가상 포트폴리오 후보를 제시해 달라고 요청함
- Interpreted goal:
  - 6~10단계의 Candidate Draft / Review Note / Registry / Candidate Board / Pre-Live Review 흐름을 실습할 수 있도록, 현재 registry와 runtime 기준으로 `hold`가 아닌 후보 하나를 고른다
- Analysis result:
  - 첫 실습 후보는 `gtaa_real_money_balanced_top2_ief_20260418`로 둔다
  - 설정은 `GTAA`, `SPY / QQQ / GLD / IEF`, `Top=2`, `Signal Interval=4`, `Score Horizons=1M / 3M`, `Risk-Off=defensive_bond_preference`, `Benchmark=SPY`, `Transaction Cost=10bps`, `Min ETF AUM=1.0B`, `Max Spread=0.50%`다
  - current DB runtime 재실행 결과는 `2016-01-29 ~ 2026-04-27`, `CAGR=17.88%`, `MDD=-8.39%`, `Benchmark CAGR=13.60%`, `Net CAGR Spread=+4.28%p`, `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Probation=paper_tracking`, `Deployment=paper_only`, `Validation=normal`, `ETF Operability=normal`, blocker 없음이었다
  - 따라서 4단계 판단은 `Hold 해결 필요 없음`; 바로 투자 승인이 아니라 5단계 Compare와 6~10단계 후보 검토 / 운영 기록으로 넘기기에 적합하다
- Follow-up:
  - 다음 실습에서는 이 후보를 기준으로 `Single Strategy -> Real-Money -> Compare -> Candidate Draft -> Review Note -> Current Candidate Registry -> Candidate Board -> Pre-Live Review -> Portfolio Proposal` 순서로 하나씩 확인한다
  - 실제 Pre-Live feedback / Paper Tracking feedback을 보려면 Pre-Live record와 Portfolio Proposal draft를 명시적으로 저장해야 하며, 둘 다 live approval은 아니다

### 2026-04-28 - GTAA Risk-Off 후보군 해석을 Guides에 별도 추가한다
- User request:
  - `Trend Filter Window`, `Fallback Mode`, `Defensive Tickers`가 실제 후보군과 어떻게 연결되는지 헷갈리므로 Guides에 별도 정리를 추가해 달라고 요청함
- Interpreted goal:
  - GTAA `Risk-Off Contract`에서 defensive ticker가 자동으로 universe에 추가되는 것이 아니라, GTAA universe와 defensive ticker 목록의 교집합만 실제 fallback 후보가 된다는 점을 사용자-facing Guide에서 바로 확인하게 한다
- Analysis result:
  - `Reference > Guides`에 `GTAA Risk-Off 후보군 보는 법` 섹션을 추가했다
  - Guide는 GTAA Tickers, Top Assets, Trend Filter Window, Fallback Mode, Defensive Tickers의 역할을 표로 설명하고, `Top=2`일 때 최종 후보 / cash 비중을 어떻게 읽는지 정리한다
  - 현재 실습 후보 예시에서는 `GTAA Tickers = SPY, QQQ, GLD, IEF`, `Defensive Tickers = TLT, IEF, LQD, BIL`이므로 실제 usable defensive 후보는 `IEF`뿐이라고 명시했다
  - Phase 30 checklist에도 해당 Guide 항목을 확인하도록 추가했다
- Follow-up:
  - 향후 GTAA 방어 후보를 넓히려면 `Defensive Tickers`뿐 아니라 `GTAA Tickers`에도 `TLT / LQD / BIL` 같은 후보를 포함해야 한다

### 2026-04-28 - 4단계 pass 기준은 Promotion만이 아니라 blocker 해소 여부다
- User request:
  - Real-Money 단계에서 `승격판단 = REAL_MONEY_CANDIDATE`가 나오면 4단계를 pass로 봐도 되는지, 아니면 다른 확인이 필요한지 질문함
- Interpreted goal:
  - 4단계 `Hold면 먼저 막히는 항목 해결`의 완료 조건을 실습 기준으로 분명히 정한다
- Analysis result:
  - `Promotion Decision = real_money_candidate`면 보통 4단계는 pass로 볼 수 있다
  - 다만 실습 기준의 정확한 pass는 `Promotion != hold`, `Deployment != blocked`, Hold 해결 가이드 / blocker가 남아 있지 않음, 그리고 주요 실행 부담 항목이 error / caution으로 막고 있지 않음을 함께 확인하는 것이다
  - `production_candidate`나 `watchlist`는 hold 해결 관점에서는 pass일 수 있지만, 바로 paper tracking 후보로 강하게 보지는 않고 Compare / Candidate Review에서 더 보수적으로 읽는다
  - `real_money_candidate`도 투자 승인이 아니라 5단계 Compare와 6~10단계 후보 검토 / Pre-Live 운영 기록으로 넘길 수 있다는 신호다
- Follow-up:
  - 현재 GTAA Balanced Top-2 실습 후보는 `real_money_candidate`, `paper_probation`, `paper_tracking`, `paper_only`, blocker 없음이므로 4단계 pass 사례로 사용한다

### 2026-04-28 - 4단계 pass 기준을 Guide에 명시한다
- User request:
  - 투자 승인 기준이 아니라 5단계 Compare로 넘어갈 수 있는 명시적 Real-Money 기준을 Guide에 두고 싶다고 요청함
- Interpreted goal:
  - 사용자가 임의의 포트폴리오 후보를 볼 때 4단계에서 멈출지, 5단계 Compare로 넘길지 반복적으로 판단할 수 있는 최소 기준을 화면에 고정한다
- Analysis result:
  - `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`에 `4단계에서 5단계로 넘어가는 최소 기준` 표를 추가했다
  - 기준은 `Promotion Decision != hold`, `Deployment Readiness / Deployment Status != blocked`, 핵심 blocker 없음이다
  - `real_money_candidate`는 강한 pass 신호이고, `production_candidate`도 hold 해결 관점에서는 5단계로 넘겨 비교할 수 있지만 더 보수적으로 읽는다
  - 이 기준은 Compare 진입 기준이지 live trading approval이나 최종 투자 승인 기준이 아니다
- Follow-up:
  - Phase 30 manual QA에서는 이 기준이 1~5단계 검증 구간의 종료 조건으로 읽히는지 확인한다

### 2026-04-28 - Real-Money 탭에 5단계 Compare 진입 평가 박스를 추가한다
- User request:
  - Real-Money 탭에서 다음 단계로 넘어가도 되는지 한눈에 알기 어렵기 때문에, 10점 만점의 시각적 평가 박스를 추가해 달라고 요청함
- Interpreted goal:
  - `Checklist 상세 보기`를 열기 전에 4단계 Hold 해결이 끝났는지, 5단계 Compare로 넘어갈 수 있는지 빠르게 판단할 수 있어야 함
- Analysis result:
  - `Real-Money > 현재 판단` 상단에 `5단계 Compare 진입 평가` 박스를 추가했다
  - 점수는 10점 만점이며 `Promotion Decision`, `Deployment Readiness`, `Core Blocker` 세 기준을 합산한다
  - 판정은 `5단계 Compare 진행 가능`, `5단계 Compare 진행 가능, 개선 항목 동시 확인`, `4단계에서 먼저 blocker 해결`로 표시한다
  - 이 평가는 Compare 진입 보조 신호이며 live trading approval이나 주문 지시가 아니다
  - GTAA Balanced Top-2 실습 후보는 현재 runtime 기준 `8.5 / 10`, `5단계 Compare 진행 가능`으로 계산됐다
- Follow-up:
  - Phase 30 manual QA에서 이 박스가 4단계 pass 기준을 명확하게 보여주는지 확인한다

### 2026-04-29 - Compare 진입 점수의 통과 기준을 명시한다
- User request:
  - 8.5점이 나온 현재 포트폴리오 사례에서 몇 점부터 5단계 진행으로 보면 되는지 질문함
- Interpreted goal:
  - Readiness Score가 단순 숫자가 아니라 어떤 기준으로 pass / conditional pass / stop으로 읽히는지 명확히 해야 함
- Analysis result:
  - `8.0 / 10` 이상은 깔끔한 5단계 Compare 진행으로 읽는다
  - `8.0 / 10` 미만이어도 `Promotion Decision != hold`, `Deployment != blocked`, 핵심 blocker 없음이면 조건부로 Compare 진행 가능하다
  - 핵심 3조건을 만족하지 못하면 점수와 무관하게 4단계에서 먼저 멈춘다
  - Real-Money `5단계 Compare 진입 평가` 박스와 code flow 문서에 이 해석을 추가했다
- Follow-up:
  - 점수는 투자 승인 기준이 아니라 Compare 진입 보조 기준으로 유지한다

### 2026-04-29 - 5단계 Compare는 후보를 상대 비교해 Candidate Draft로 넘길지 정하는 단계다
- User request:
  - 4단계가 통과된 GTAA Balanced Top-2 포트폴리오로 5단계에서 무엇을 확인하고 어떻게 통과하는지 안내를 요청함
- Interpreted goal:
  - 5단계 Compare를 투자 승인 단계가 아니라 후보 간 상대 비교와 Candidate Draft handoff 준비 단계로 정의해야 함
- Analysis result:
  - 5단계의 목적은 기준 후보가 단독 결과 착시가 아니라 같은 기간 / 같은 Real-Money 해석 기준에서도 계속 볼 만한지 확인하는 것이다
  - 최소 비교 묶음은 GTAA Balanced Top-2를 중심으로 GTAA Low-MDD 대안, GTAA High-CAGR 대안, 필요하면 Equal Weight 또는 SPY benchmark 성격의 기준을 함께 놓는 방식이 적절하다
  - 통과 기준은 compare run이 정상 실행되고, 기준 후보의 Data Trust / Real-Money가 깨지지 않으며, 후보가 목적에 맞는 상대 우위를 설명할 수 있고, 다음 단계로 넘길 후보 역할이 정리되는 것이다
  - 5단계 통과는 `Review As Candidate Draft`로 넘길 수 있는 상태라는 뜻이지 current candidate registry 저장이나 Pre-Live / live approval을 뜻하지 않는다
- Follow-up:
  - 현재 실습에서는 GTAA Balanced Top-2를 기본 후보로 두고, Low-MDD 대안과 High-CAGR 대안을 비교한 뒤 Candidate Draft로 넘길 후보를 하나 고른다

### 2026-04-29 - 4→5 통과 기준은 단계형 흐름 밖의 별도 Guide로 분리한다
- User request:
  - `테스트에서 상용화 후보 검토까지 사용하는 흐름` 안에 갑자기 `4단계에서 5단계로 넘어가는 최소 기준`이 나오면, 단계별 흐름을 읽다가 기준 설명으로 끊겨 어색하다고 피드백함
- Interpreted goal:
  - 1~11단계 흐름은 순서대로 읽히게 유지하고, 단계 통과 / 중단 기준은 별도 분류에서 확인하도록 정보 구조를 정리해야 함
- Analysis result:
  - `4단계에서 5단계로 넘어가는 최소 기준`을 `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름` 본문에서 제거했다
  - 같은 기준은 `Reference > Guides > 단계 통과 기준`이라는 별도 section으로 이동했다
  - `테스트에서 상용화 후보 검토까지 사용하는 흐름`은 안내 문단 뒤 곧바로 1단계부터 시작하도록 정리했다
  - Phase 30 checklist와 current TODO, doc index도 새 위치를 기준으로 갱신했다
- Follow-up:
  - 이후 5→6, 10→11처럼 추가 통과 기준이 필요해지면 같은 `단계 통과 기준` section에 누적하고, 단계형 흐름 본문은 계속 순서형 Guide로 유지한다

### 2026-04-29 - 실습 세션 내용은 Phase 30 QA와 분리해서 관리한다
- User request:
  - 이번 세션에서 한 질문과 수정은 Phase 30 자체 QA가 아니라 별도 실습성 내용인데, 왜 Phase 30 문서를 갱신했는지 지적하고 별도 관리해 달라고 요청함
- Interpreted goal:
  - 1~11단계 walkthrough 실습에서 나온 질문, 예시 후보, Guide / Real-Money 보조 기능은 Phase 30 checklist나 TODO가 아니라 별도 운영 문서에 모아야 함
- Analysis result:
  - `.aiworkspace/note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md`를 만들고 GTAA 실습 후보, Risk-Off 해석, 4->5 기준, 5단계 Compare 기준, 이번 세션에서 추가된 UI 보조 기능을 모았다
  - Phase 30 checklist와 current TODO에서는 GTAA Risk-Off, 4->5 pass 기준, Real-Money readiness 평가 같은 실습 세션 항목을 제거했다
  - `FINANCE_DOC_INDEX.md`와 `operations/README.md`에는 새 walkthrough 문서를 운영 문서로 등록했다
- Follow-up:
  - 앞으로 사용자가 Phase 문서 갱신을 명시하지 않으면, 이런 실습 질문은 operations walkthrough 문서나 question log로만 관리한다

### 2026-04-29 - 신규 전략의 5단계 Compare는 registry shortcut이 아니라 직접 Compare 재현으로 시작한다
- User request:
  - 4단계를 통과한 신규 전략을 5단계에서 확인한다고 가정하면, `Candidate Review > Send To Compare > Load Recommended Candidates` 경로는 이미 registry에 있는 후보에 의존하므로 이상하지 않느냐고 질문함
- Interpreted goal:
  - 신규 전략이 아직 current candidate registry에 없을 때 5단계 Compare를 어떻게 시작해야 하는지 정확히 정리해야 함
- Analysis result:
  - 사용자의 지적이 맞다. `Load Recommended Candidates`는 이미 registry에 기록된 대표 후보 묶음을 compare form에 다시 채우는 quick re-entry 도구이지, 신규 전략의 첫 Compare 경로가 아니다
  - 신규 전략은 `Backtest > Compare & Portfolio Builder`로 직접 이동한 뒤, 4단계 single run의 기간과 strategy-specific contract를 Compare form에 재현해서 실행한다
  - 비교 기준은 Equal Weight, benchmark 성격 후보, 다른 ETF 전략, 또는 이미 registry에 있는 기존 대표 후보 중 목적에 맞게 고른다
  - 현재 compare form은 같은 strategy family 후보를 여러 개 동시에 비교하는 데 제한이 있으므로, 같은 family 파라미터 변형끼리의 정밀 비교는 single run / history 기반 수동 비교 또는 이후 별도 지원 과제로 남긴다
- Follow-up:
  - walkthrough 문서의 5단계 설명을 신규 전략 기본 경로와 registry shortcut 경로로 분리했다

### 2026-04-29 - 5단계 Compare 결과에서 6단계 Candidate Draft 진입 기준을 점수화한다
- User request:
  - 신규 전략을 Compare에서 1~3개 비교 기준과 함께 테스트한 뒤, 6단계 Candidate Draft로 넘어갈 수 있는 조건을 명확히 보여주는 점수형 UI를 요청함
- Interpreted goal:
  - 4->5 Real-Money readiness처럼, 5->6도 Compare 결과를 보고 통과 / 조건부 통과 / 재확인을 한눈에 판단할 수 있어야 함
- Analysis result:
  - `Backtest > Compare & Portfolio Builder` 결과 상단에 `6단계 Candidate Draft 진입 평가` 박스를 추가했다
  - 사용자가 Compare 후보 중 하나를 선택하면 Compare Run 2점, Data Trust 2점, Real-Money Gate 3점, Relative Evidence 3점으로 10점 만점 평가를 보여준다
  - `8.0 / 10` 이상은 Candidate Draft 진행 가능, `6.5 / 10` 이상은 조건부 진행, 그 아래는 Compare에서 추가 확인으로 표시한다
  - 통과 또는 조건부 통과 상태에서는 `Send Selected Strategy To Candidate Draft` 버튼으로 `Candidate Review > Candidate Intake Draft`에 초안을 보낼 수 있다
  - 실습용 비교 구성은 GTAA Balanced Top-2, Equal Weight same universe, Global Relative Strength same universe, 선택적으로 Risk Parity Trend로 정리했다
- Follow-up:
  - 사용자는 해당 비교 구성을 UI에서 실행한 뒤 Draft Score와 막는 항목을 보고 6단계 진입 여부를 판단한다

### 2026-04-29 - GTAA 실습용 Compare smoke 결과를 남긴다
- User request:
  - 6단계 진입 평가 기능을 만든 뒤, 실전 테스트에서 어떤 비교 포트폴리오를 썼는지 알 수 있어야 한다고 요청함
- Interpreted goal:
  - 사용자가 같은 compare 구성을 UI에서 재현할 수 있도록 실제 smoke에 사용한 전략과 핵심 결과를 별도 walkthrough 문서에 남긴다
- Analysis result:
  - GTAA Balanced Top-2, Equal Weight same universe, Global Relative Strength same universe, Risk Parity Trend default universe를 같은 기간으로 실행했다
  - GTAA Balanced Top-2는 CAGR 17.88%, MDD -8.39%, Promotion `real_money_candidate`, Deployment `paper_only`로 가장 강한 후보로 남았다
  - 새 Draft Score는 `9.0 / 10`, 판정은 `6단계 Candidate Draft 조건부 진행 가능`으로 계산됐다
- Follow-up:
  - UI 수동 테스트에서는 같은 비교 구성을 재현하고, `Send Selected Strategy To Candidate Draft`로 6단계 이동을 확인한다

### 2026-04-29 - Reference Guides를 실습 흐름에 맞게 재정리한다
- User request:
  - Guides의 `실전 승격 흐름`, `Real-Money Contract`, `GTAA Risk-Off` 설명을 큰 카테고리로 묶고, `테스트에서 상용화 후보 검토까지 사용하는 흐름`과 `단계 통과 기준`은 각 단계를 클릭해 펼쳐보게 만들며, 문서/파일 목록도 최신화해 달라고 요청함
- Interpreted goal:
  - 1~11단계 실습 중 필요한 개념 설명, 단계별 절차, stop/go 기준, 참고 문서가 한 화면에서 구분되어야 함
- Analysis result:
  - `Reference > Guides`에 `핵심 개념 가이드` 묶음을 만들고 실전 승격 흐름, Real-Money Contract, GTAA Risk-Off 설명을 expander로 정리했다
  - `1~11 단계 실행 흐름`에서는 1~11단계를 각각 expander로 바꿔 필요한 단계만 펼쳐 읽게 했다
  - `단계 통과 기준`에서는 4->5, 5->6 기준을 각각 expander로 바꿨다
  - `문서와 파일`에는 현재 먼저 볼 문서로 walkthrough session, web backtest UI flow, glossary, doc index, roadmap, registry 파일을 최신화했다
  - Phase 30 QA 문서는 건드리지 않고 operations walkthrough와 code analysis 문서만 동기화했다
- Follow-up:
  - 사용자는 Guides에서 `핵심 개념 -> 1~11 단계 -> 단계 통과 기준 -> 문서와 파일` 순서로 실습 안내를 확인한다

### 2026-04-29 - month_end interval은 주 단위가 아니라 row cadence다
- User request:
  - `Equal Weight Same Universe`를 `SPY, QQQ, GLD, IEF, 4주 리밸런싱`이라고 했을 때 interval이 `1`인지 `12`인지 질문함
- Interpreted goal:
  - Compare 실습에서 `Interval`과 `Rebalance Interval` 숫자가 어떤 시간 단위를 뜻하는지 명확히 해야 함
- Analysis result:
  - 현재 walkthrough는 `option=month_end` 기준이므로 interval 숫자는 주 단위가 아니라 월말 row 간격이다
  - `1`은 매월 리밸런싱 / 매월 신호 갱신이며 대략 4주 cadence로 볼 수 있다
  - `4`는 4번째 월말 row마다 갱신하는 느린 cadence이고, `12`는 연 1회 cadence다
  - 기존 GTAA 실습 후보는 registry 계약이 `Interval = 4`라서 Compare smoke에서 Equal Weight도 `4`로 후보 cadence를 맞췄지만, literal 4주 / 월간 Equal Weight benchmark라면 `Rebalance Interval = 1`을 써야 한다
  - Guides, Equal Weight input help, walkthrough 문서에 이 구분을 추가했다
- Follow-up:
  - 사용자가 후보 cadence를 맞출지, 월간 benchmark를 둘지에 따라 Equal Weight interval을 `4` 또는 `1`로 선택한다

### 2026-04-29 - Compare에서 interval은 비교 목적에 맞춰 맞추거나 분리한다
- User request:
  - 5단계에서 추천한 4개 비교 포트폴리오가 모두 interval `4`인데, 비교할 때 interval도 동일하게 해야 하는지 질문함
- Interpreted goal:
  - 5단계 Compare에서 cadence를 통제해야 하는 경우와 benchmark 성격으로 다르게 둘 수 있는 경우를 구분해야 함
- Analysis result:
  - 같은 cadence에서 전략 로직 차이를 비교하려면 interval을 맞추는 것이 좋다
  - 이번 GTAA 실습 smoke는 후보 계약이 `Interval = 4`였기 때문에 Equal Weight, Global Relative Strength, Risk Parity도 `4`로 맞춰 cadence-matched compare로 실행했다
  - 후보의 실제 운용 계약끼리 비교한다면 각 후보의 원래 interval을 유지해도 되지만, 그 경우 성과 차이에 strategy logic과 cadence 차이가 함께 섞였다고 기록해야 한다
  - Equal Weight를 월간 / 대략 4주 benchmark로 쓰고 싶다면 `option=month_end`에서 `Rebalance Interval = 1`을 쓰는 것이 맞다
  - walkthrough 문서에 `cadence-matched compare`와 `benchmark compare`의 차이를 추가했다
- Follow-up:
  - 수동 실습에서는 먼저 `Interval = 4`로 후보 cadence를 맞춘 비교를 하고, 필요하면 Equal Weight `1`을 별도 월간 benchmark로 추가 비교한다

### 2026-04-29 - Candidate Draft 점수와 Data Trust gate를 분리한다
- User request:
  - `Data Trust hard blocker cap = 6.4 / 10`을 점수에 섞지 말고 경고로 구별하는 것이 어떠냐고 제안함
- Interpreted goal:
  - 사용자가 Draft Score를 전략/비교 근거의 강도로 읽고, Data Trust 문제는 별도 gate로 확인할 수 있어야 함
- Analysis result:
  - `6단계 Candidate Draft 진입 평가`에서 hard `6.4` score cap을 제거했다
  - 요청 종료일보다 실제 결과 종료일이 1-2일 짧은 케이스는 `Data Trust WARNING`으로 표시하고, 조건부로 Candidate Draft 이동이 가능하게 했다
  - 가격 최신성 error 또는 실제 결과 기간이 31일 넘게 비는 경우는 `Data Trust BLOCKED`로 유지한다
  - UI에는 `Draft Score` 옆에 `Data Trust` gate metric을 추가했다
  - 점수 계산표에는 Data Trust 점수를 남기되, gate 상태는 별도 warning/error 메시지로 보여준다
- Follow-up:
  - 사용자는 `Draft Score`와 `Data Trust` gate를 함께 보고, warning이면 Review Note에 근거를 남긴 뒤 6단계로 넘긴다

### 2026-04-29 - 5단계 Compare는 기술적 필수 조건이 아니라 상대 근거 검증 단계다
- User request:
  - 5단계 pass 조건이 Compare, Data Trust, Real-Money, Relative Evidence라면 이 네 조건이 꼭 Compare를 해야 판단 가능한지, 4단계에서 바로 6단계로 넘어가도 되는지 질문함
- Interpreted goal:
  - 5단계 Compare가 반드시 필요한 이유와, single run에서 바로 Candidate Draft로 넘기는 예외 경로를 구분해야 함
- Analysis result:
  - Data Trust와 Real-Money Gate는 single run만으로도 상당 부분 확인 가능하다
  - Compare Run과 Relative Evidence는 비교군이 있어야 판단 가능하다
  - 따라서 5단계는 Candidate Draft를 만드는 기술적 필수 조건은 아니지만, registry / Pre-Live / Portfolio Proposal로 이어질 후보라면 상대 근거를 붙이기 위한 기본 검증 단계다
  - 4단계에서 바로 6단계로 가는 것은 `single-run draft` 또는 `compare_pending` 상태로 허용할 수 있다
  - 단, 이 경우 Review Note에 Compare가 아직 없고 상대 근거가 pending이라는 점을 남겨야 한다
- Follow-up:
  - walkthrough 문서에 `4단계에서 바로 6단계로 가도 되나` 구분을 추가했다

### 2026-04-29 - 5단계 Compare는 비교할 만한 대상 선정이 핵심이다
- User request:
  - 5단계에서 무의미한 전략들과 비교하면 Compare 자체가 의미 없으므로, "비교할 만한 대상"을 어떻게 설정해야 하는지 질문함
  - 앞으로 질문에 바로 수정 반영하지 말고 먼저 답한 뒤 수정 진행 여부를 물어보라는 작업 방식도 요청함
- Interpreted goal:
  - 5단계의 본질을 "아무 비교 실행"이 아니라 "의미 있는 comparator set 구성"으로 정의해야 함
- Analysis result:
  - 비교 대상은 같은 투자 문제를 풀거나 후보의 약점 / 대체 가능성 / 단순 기준 대비 우위를 설명할 수 있어야 한다
  - 의미 있는 comparator role은 naive baseline, market benchmark, 가까운 대안 전략, 위험 기준 대안, 기존 강한 후보로 정리했다
  - GTAA 실습에서는 같은 universe Equal Weight, Global Relative Strength, Risk Parity Trend, 필요 시 SPY 또는 60/40이 비교할 만한 대상이다
  - 사용자가 수정 진행을 승인한 뒤 `Reference > Guides > Compare 대상 선정법`과 walkthrough의 5단계 설명을 갱신했다
- Follow-up:
  - 이후 사용자가 해석 / 설계 질문을 하면 먼저 답변하고, 문서나 코드 수정은 명시 승인을 받은 뒤 진행한다

### 2026-04-29 - Compare 대상 선정법에 GTAA 상황 예시를 추가한다
- User request:
  - `Compare 대상 선정법` 설명은 마음에 들지만, 예시 칸만으로 충분한지 묻고 상황 예시를 추가해 달라고 요청함
- Interpreted goal:
  - comparator role 개념뿐 아니라 실제 후보를 놓고 어떤 비교군을 고르고 어떻게 해석하는지 보여줘야 함
- Analysis result:
  - 예시 칸만으로는 개념 구분은 가능하지만, 실제 5단계에서 비교군을 구성하기에는 조금 부족하다고 판단했다
  - 사용자의 승인 후 `GTAA Balanced Top-2` 상황 예시를 Guides와 walkthrough 문서에 추가했다
  - 예시는 Equal Weight Same Universe, Global Relative Strength, Risk Parity Trend, SPY 또는 60/40을 비교군으로 두고 각각의 비교 목적과 통과 해석을 설명한다
- Follow-up:
  - 사용자는 GTAA 실습에서 이 상황 예시를 기준으로 5단계 comparator set을 구성한다

### 2026-04-29 - 6단계와 7단계는 Draft 확인 / Note 저장 / Registry 결정으로 재정리한다
- User request:
  - `Candidate Intake Draft`에서 통과되면 `Save Candidate Review Note`를 활성화하고, 사실상 6단계와 7단계를 하나로 묶는 것이 맞지 않느냐고 질문함
- Interpreted goal:
  - 이미 4단계 / 5단계에서 확인한 성과와 gate를 다시 반복하는 단계가 아니라, 후보 초안이 저장 가능한 검토 기록으로 전환되는지 명확히 보여줘야 함
- Analysis result:
  - 6단계는 `Candidate Intake & Review Note 저장`으로 재정의했다
  - 6단계는 Draft 수신 상태 확인과 operator reason / next action 저장을 함께 처리한다
  - `Save Candidate Review Note`는 후보 이름/source, result snapshot, Data Trust, Real-Money signal, settings snapshot, operator reason / next action이 준비된 경우에만 활성화된다
  - 7단계는 저장된 Review Notes를 보고 실제 current candidate registry row로 남길지 결정하는 단계로 분리했다
  - 8단계는 여전히 `Append To Current Candidate Registry`를 명시적으로 누르는 registry 저장 단계다
- Follow-up:
  - 사용자는 5단계 통과 후보를 Candidate Intake Draft로 보낸 뒤 `6단계 Intake 저장 준비`가 `READY_TO_SAVE`인지 확인하고 Review Note를 저장한다

### 2026-04-29 - 7단계는 registry 후보 범위를 정한 뒤 8단계로 넘긴다
- User request:
  - 6단계에서 Review Note 저장까지 끝냈으니, 7단계에서 무엇을 하고 어떤 범위를 정해야 다음 단계로 진행할 수 있는지 개발해 달라고 요청함
- Interpreted goal:
  - 7단계가 단순히 저장된 note를 append하는 화면이 아니라, 해당 note를 `current_candidate`, `near_miss`, `scenario`, 또는 append 보류 중 어디로 둘지 판단하는 gate가 되어야 함
- Analysis result:
  - `Backtest > Candidate Review > Review Notes`에 `7단계 Registry 후보 범위 판단` 박스를 추가했다
  - Review Note의 decision, result snapshot, Data Trust, Real-Money gate, settings snapshot, compare evidence, operator reason / next action을 확인해 scope를 정한다
  - Current Candidate는 가장 엄격하게 보고, Compare 근거와 Real-Money gate가 충분하지 않으면 Near Miss / Scenario / Stop으로 분리한다
  - 선택한 Record Type이 scope와 맞지 않으면 `Append To Current Candidate Registry`가 비활성화된다
- Follow-up:
  - 사용자는 저장된 Review Note를 고른 뒤 scope가 Current / Near Miss / Scenario 중 하나인지 확인하고, 추천 Record Type과 맞춘 뒤 8단계 append로 진행한다

### 2026-04-29 - registry 범위 판단과 append는 하나의 사용자-facing 단계로 합친다
- User request:
  - 7단계 조건이 통과되면 `Append To Current Candidate Registry` 버튼이 활성화되는 구조라면, 7단계와 8단계는 사실상 하나의 단계로 보는 것이 맞다고 지적하고 합쳐 달라고 요청함
- Interpreted goal:
  - 버튼 단위 저장 액션을 별도 단계로 쪼개지 말고, 사용자가 다른 종류의 판단을 하는 큰 단계만 남겨야 함
- Analysis result:
  - 이전 7단계 `Review Notes에서 registry 후보 범위 판단`과 8단계 `Current Candidate Registry append`를 하나의 7단계로 합쳤다
  - 새 7단계는 `Current Candidate Registry에 남길 범위 결정 및 저장`이며, scope 판단이 통과하고 Record Type이 맞으면 같은 단계 안에서 append한다
  - 이후 Candidate Board / Pre-Live / Portfolio Proposal 단계는 하나씩 당겨서 표시한다
  - `Append To Current Candidate Registry`는 독립 검증 단계가 아니라 7단계의 명시적 저장 버튼으로 설명한다
- Follow-up:
  - 앞으로 Guides의 큰 흐름은 기능 단위가 아니라 사용자 판단 단위로만 나눈다

### 2026-04-29 - 8단계는 Candidate Board에서 다음 운영 경로를 읽는 단계다
- User request:
  - `Append To Current Candidate Registry`를 두 번째 클릭했을 때 작동하지 않는 것처럼 보이는 현상이 정상인지 확인하고, 8단계에서 무엇을 해야 하며 통과 과정은 어떻게 되는지 개발해 달라고 요청함
- Interpreted goal:
  - 같은 Review Note를 반복 append하는 혼란을 막고, registry 저장 뒤 Candidate Board에서 Pre-Live로 갈 후보와 Compare로 돌아갈 후보를 명확히 구분해야 함
- Analysis result:
  - 반복 클릭은 실제로 작동하지 않은 것이 아니라, append-only registry에 같은 `source_review_note_id` / `registry_id`의 새 revision을 여러 번 추가한 상태였다
  - Candidate Board는 `registry_id` 기준 latest row만 보여주므로 두 번째 이후 클릭은 화면 변화가 작게 보였다
  - 이 UX는 정상 의도라고 보기 어렵기 때문에, 같은 Review Note가 이미 registry에 있으면 append 버튼을 기본 비활성화하고 의도적 revision 저장 체크박스를 켠 경우에만 다시 저장하도록 했다
  - 8단계는 후보를 다시 백테스트하는 단계가 아니라, Candidate Board에서 route를 읽는 단계로 정의했다
  - `PRE_LIVE_READY`는 9단계 Pre-Live Review로 이동 가능, `COMPARE_REVIEW_READY`는 Compare 재검토 경로, `BOARD_HOLD`는 registry row 보강 또는 Review Note 재검토 상태다
- Follow-up:
  - 사용자는 7단계 저장 뒤 `Candidate Board`에서 `8단계 Candidate Board 운영 판단`의 Route를 확인한다
  - `PRE_LIVE_READY`이면 Pre-Live Review로 열고, `COMPARE_REVIEW_READY`이면 Compare에서 비교 후보를 추가한다

### 2026-04-29 - 6/7/8은 Candidate Packaging 하나의 단계로 합친다
- User request:
  - 6단계 Review Note, 7단계 registry 저장, 8단계 Candidate Board 확인이 사실상 하나의 기능처럼 보이며, 사용자-facing 단계로 쪼개져 있는 것이 프로그램 흐름을 이상하게 만든다고 지적함
  - 세 단계를 하나로 합치고, 이 단계가 정확히 무엇을 하며 다음 단계로 넘어가는 조건이 무엇인지 통합적으로 보여 달라고 요청함
- Interpreted goal:
  - Draft / Review Note / Registry / Board route는 별도 퀀트 검증 단계가 아니라 Pre-Live 전달을 위한 후보 패키징 작업으로 보여야 함
- Analysis result:
  - 기존 6 / 7 / 8 user-facing 단계를 `6단계 Candidate Packaging` 하나로 합쳤다
  - Candidate Packaging은 후보 초안 확인, Review Note 저장, registry row 저장, Candidate Board route 확인을 한 단계에서 처리한다
  - 최종 통과 기준은 `Candidate Packaging 종합 판단`의 Route가 `PRE_LIVE_READY`인지 여부다
  - `COMPARE_REVIEW_READY`는 실패가 아니라 Compare 재검토 경로이고, `BOARD_HOLD`는 Review Note 또는 registry row 보강 상태다
  - Guides는 1~8 단계로 재정리했다: 6 Candidate Packaging, 7 Pre-Live Review, 8 Portfolio Proposal
- Follow-up:
  - 사용자는 5단계 Compare 통과 후보를 Candidate Packaging으로 보낸 뒤, Review Note / registry 저장을 마치고 Candidate Board의 Route가 `PRE_LIVE_READY`인지 확인한다

### 2026-04-29 - Candidate Review는 탭이 아니라 순서형 Packaging 화면이어야 한다
- User request:
  - 기존 `Candidate Board`, `Candidate Intake Draft`, `Review Notes`, `Inspect Candidate`, `Send To Compare` 탭 구조가 사용자가 따라가기 어렵고 순서가 엉망이라고 지적함
  - 탭을 없애고, 사용자가 5단계 Compare 이후 6단계 Candidate Packaging을 자연스럽게 진행한 뒤 Pre-Live로 넘어갈 수 있는 UX/UI 개편을 요청함
- Interpreted goal:
  - 검증 로직을 새로 만들기보다 기존 저장 준비 / registry scope / route 판단을 하나의 화면에 순서대로 배치해야 함
  - 각 저장 버튼은 자동화가 아니라 사람이 확인 후 누르는 명시적 기록 버튼으로 유지해야 함
- Analysis result:
  - `Backtest > Candidate Review`를 `1. Draft 확인 / Review Note 저장`, `2. Registry 저장`, `3. Pre-Live 진입 평가` 순서형 화면으로 개편했다
  - 기존 탭에서 흩어져 있던 Review Note 저장, registry append, route 판단을 한 화면에 배치했다
  - saved board와 compare re-entry는 하단 보조 도구로 낮춰, 주 흐름을 방해하지 않게 했다
- Follow-up:
  - 사용자는 5단계에서 보낸 candidate draft를 Candidate Review 한 화면에서 위에서 아래로 처리하고, `PRE_LIVE_READY`일 때만 7단계 Pre-Live Review로 이동한다

### 2026-04-29 - Registry 저장 직후 3단계에서 방금 저장한 후보를 바로 알아볼 수 있어야 한다
- User request:
  - `Append To Current Candidate Registry` 이후 `3. Pre-Live 진입 평가`의 `Packaging 확인 후보`에 GTAA 후보가 여러 개 보여 어떤 후보가 방금 저장한 것인지 알 수 없다고 지적함
  - 텍스트 설명이 아니라 2단계 저장 후 3단계 평가가 자연스럽게 이어지도록 UX/UI 기능 개선을 요청함
- Interpreted goal:
  - registry append 결과가 3단계 route 평가의 선택 상태로 직접 이어져야 함
  - 후보 label만 봐도 같은 family 후보를 구분할 수 있어야 함
- Analysis result:
  - current candidate 선택 label에 `registry_id`를 포함했다
  - registry append 직후 새 row의 `registry_id`와 `revision_id`를 session state에 저장하고, 3단계에서 해당 후보를 자동 선택하도록 했다
  - 3단계 선택 영역 아래에 방금 저장한 후보의 Registry ID, Revision ID, Record Type, Strategy, Title, Source Review Note, Recorded At을 보여주는 요약 카드를 추가했다
- Follow-up:
  - 사용자는 append 직후 3단계에서 자동 선택된 후보 요약을 확인한 뒤 `Candidate Packaging 종합 판단` Route를 읽으면 된다

### 2026-04-29 - Candidate Review를 별도 모듈로 먼저 분리한다
- User request:
  - `backtest.py`가 너무 커져 수정 시간이 오래 걸린다는 문제의식에서, 전체 리팩토링보다 최근 작업한 `Candidate Review` 부분만 별도 스크립트로 관리하는 방향을 제안하고 진행을 승인함
- Interpreted goal:
  - 7단계 Pre-Live 작업을 더 얹기 전에 Candidate Review의 화면 render 코드를 집중된 파일로 옮겨 이후 수정 비용을 줄여야 함
  - 이번 작업은 기능 변경 없이 추출 리팩토링으로 제한해야 함
- Analysis result:
  - `app/web/pages/backtest_candidate_review.py`를 추가하고 Candidate Review / Candidate Packaging render flow를 옮겼다
  - `backtest.py`에는 `_render_candidate_review_workspace()` wrapper만 남겨 기존 panel routing을 유지했다
  - shared helper와 registry 변환 helper는 1차 리팩토링에서는 `backtest.py`에 남겨 import 위험을 줄였다
- Follow-up:
  - 다음 Pre-Live 운영 점검 개발은 Candidate Review 화면 코드가 분리된 상태에서 진행한다

### 2026-04-29 - Candidate Review는 render와 helper를 분리해서 관리한다
- User request:
  - Candidate Review를 별도 파일로 뺀 뒤에도 helper / registry 변환 일부가 `backtest.py`에 남아 있으므로, 화면 렌더링 코드와 기능 helper 코드를 나눠 관리하는 방향이 좋다고 보고 진행을 승인함
- Interpreted goal:
  - Candidate Review 화면 수정과 후보 판단 / 변환 로직 수정을 서로 덜 건드리게 만들어, 이후 Pre-Live 작업을 더 얹기 전에 `backtest.py` 의존도를 줄여야 함
- Analysis result:
  - `app/web/pages/backtest_candidate_review.py`는 Candidate Packaging 화면 render를 맡는다
  - `app/web/pages/backtest_candidate_review_helpers.py`는 Candidate Review decision option, readiness evaluation, Review Note 생성, registry row 변환, display DataFrame helper를 맡는다
  - `backtest.py`에는 panel routing wrapper와 cross-panel handoff 함수만 남기고, Candidate Review helper 함수들은 새 helper 모듈에서 import한다
- Follow-up:
  - 다음 리팩토링 후보는 Pre-Live Review module 또는 current-candidate compare prefill helper 분리다

### 2026-04-29 - 코드 수정 전 script 책임 지도를 먼저 보도록 지침화한다
- User request:
  - 코드 수정이 들어갈 때 현재 프로젝트의 스크립트 구조와 각 스크립트가 관리하는 기능을 문서에 기록하고, 에이전트가 그 문서를 먼저 확인한 뒤 작업하도록 지침을 추가해 달라고 요청함
  - 새 함수가 만들어질 때 그 함수가 어떤 기능을 하는지 상단에 간략히 표시하는 지침도 추가해 달라고 요청함
- Interpreted goal:
  - 큰 파일이 다시 비대해지거나 기능 위치가 흐려지는 문제를 줄이고, 다음 작업자가 파일 책임을 빠르게 파악한 뒤 수정하게 만들어야 함
- Analysis result:
  - `AGENTS.md`에 finance 코드 수정 전 `SCRIPT_STRUCTURE_MAP.md`와 관련 code analysis 문서를 먼저 확인하는 규칙을 추가했다
  - `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`를 새로 만들어 app/web, runtime, finance core, loaders, data/DB, repo-local automation의 script별 책임을 요약했다
  - 새 script 추가, 이동, 분리, 책임 변경 시 해당 map과 상세 flow 문서를 같이 갱신하도록 했다
  - 새 non-trivial domain / workflow / persistence / scoring 함수에는 목적 주석 또는 간결한 docstring을 남기되, 자명한 trivial helper에는 억지 주석을 달지 않는 기준으로 정리했다
- Follow-up:
  - 앞으로 Backtest UI나 finance core를 리팩토링할 때 먼저 script map에서 책임 위치를 확인하고, 경계가 바뀌면 같은 커밋에서 map을 갱신한다

### 2026-04-30 - Pre-Live Review는 순서형 7단계 운영 점검 화면으로 본다
- User request:
  - Candidate Packaging에서 `Open Selected Candidate In Pre-Live Review`로 넘어온 뒤, 7단계가 왜 필요한지 / 무엇을 확인하는지 / 다음 단계로 갈 수 있는지 UI에서 잘 보이지 않는다고 지적함
  - 기존 `Create From Current Candidate / Pre-Live Registry` 탭 구조가 사용자에게 의미가 잘 전달되지 않으므로, 유지가 꼭 필요한지 검토하고 더 자연스러운 UX로 개선해 달라고 요청함
- Interpreted goal:
  - 7단계는 후보를 다시 검증하는 단계가 아니라, Pre-Live 운영 상태와 추적 계획을 저장하고 Portfolio Proposal로 보낼 수 있는지 판단하는 단계로 보여야 함
  - 6단계에서 넘어온 후보는 자동으로 이어지되, 직접 Pre-Live로 들어와 후보를 고르는 사용 경로도 막지 않아야 함
- Analysis result:
  - `Backtest > Pre-Live Review`를 탭 구조에서 `1. 운영 후보 확인`, `2. 운영 상태 / 추적 계획 결정`, `3. Portfolio Proposal 진입 평가`, `4. 저장 및 다음 단계` 순서형 화면으로 개편했다
  - Candidate Packaging에서 넘어온 후보는 session state로 자동 선택하고, 직접 진입한 사용자는 current candidate를 선택할 수 있게 유지했다
  - `Portfolio Proposal 진입 평가`는 10점 readiness와 route를 보여준다: `PORTFOLIO_PROPOSAL_READY`, `WATCHLIST_ONLY`, `PRE_LIVE_HOLD`, `REJECTED`, `SCHEDULED_REVIEW`
  - saved Pre-Live record inspect는 하단 보조 도구로 낮춰 주 흐름을 방해하지 않게 했다
  - Candidate Review render/helper 모듈은 Streamlit standalone page 노출을 피하기 위해 `app/web/` 하위로 이동했다
- Follow-up:
  - 사용자는 7단계에서 `paper_tracking` 상태와 필요한 reason / next action / review date / tracking plan을 저장한 뒤, `PORTFOLIO_PROPOSAL_READY`이면 8단계 Portfolio Proposal로 이동한다

### 2026-04-30 - Pre-Live status는 후보별 추천값과 운영자 최종값을 분리해 보여야 한다
- User request:
  - `2. 운영 상태 / 추적 계획 결정`에서 `Pre-Live Status`를 사용자가 직접 결정하는지, 후보 선택마다 자동으로 바뀌어야 하는지 확인함
  - 시스템 추천값과 운영자가 최종 저장하는 값을 UI에서 분리하는 개선을 승인함
- Interpreted goal:
  - 후보별 Real-Money 신호와 blocker에 따른 추천 상태는 자동으로 보여주되, 최종 저장되는 운영 판단은 사용자가 명시적으로 결정해야 함
  - 추천과 다른 판단을 내릴 때는 이유를 남기게 만들어 운영 기록의 해석 가능성을 높여야 함
- Analysis result:
  - `System Suggested Status`는 current candidate 선택이 바뀔 때 해당 후보의 `promotion`, `shortlist`, `deployment`, `blockers`에서 계산되는 추천값이다
  - `Operator Final Status`가 실제 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 저장되는 값이다
  - 두 값이 다르면 UI에서 경고를 보여주고, `Operator Reason`에 override 근거를 남기도록 안내한다
- Follow-up:
  - 사용자는 후보를 바꾸면 추천 status와 추천 근거가 바뀌는지 확인하고, 필요하면 final status를 조정한 뒤 이유와 next action을 저장한다

### 2026-04-30 - Pre-Live Review도 Candidate Review와 같은 module split으로 관리한다
- User request:
  - Candidate Review를 별도 render/helper 파일로 분리한 것처럼, Pre-Live Review도 신규 스크립트 파일을 만들어 관리하도록 리팩토링을 요청함
- Interpreted goal:
  - `backtest.py`의 추가 비대화를 막고, 7단계 Pre-Live 운영 점검 화면과 판단 helper를 독립적으로 수정할 수 있게 만들어야 함
  - 이번 작업은 behavior 변경이 아니라 파일 책임 분리여야 함
- Analysis result:
  - `app/web/backtest_pre_live_review.py`가 `Backtest > Pre-Live Review` 화면 render를 맡는다
  - `app/web/backtest_pre_live_review_helpers.py`가 status 추천, 추천 근거, operator default, Pre-Live draft 생성, Portfolio Proposal 진입 readiness 평가, registry display helper를 맡는다
  - `app/web/pages/backtest.py`에는 `_render_pre_live_review_workspace()` wrapper만 남겨 panel routing과 cross-panel handoff를 유지한다
- Follow-up:
  - 다음 7단계 UX 수정은 우선 `backtest_pre_live_review.py` / `backtest_pre_live_review_helpers.py`에서 확인한다

### 2026-04-30 - Pre-Live Review summary는 긴 status 문자열을 카드로 보여준다
- User request:
  - `st.metric` 기반 요약값이 화면 폭이 줄면 `...`로 잘려 상태 문자열을 읽기 어렵다고 지적함
  - dashboard card처럼 title별 박스를 만들어 더 시각적으로 표시해 달라고 요청함
- Interpreted goal:
  - 숫자 metric보다 긴 운영 상태 문자열에 적합한 wrapping card UI가 필요함
  - Pre-Live Review의 핵심 status 신호를 화면 폭이 좁아도 읽을 수 있어야 함
- Analysis result:
  - Pre-Live Review 상단 summary와 `2. 운영 상태 / 추적 계획 결정`의 Promotion / Shortlist / Deployment / System Suggested Status 표시를 wrapping card grid로 바꿨다
  - card 값은 `overflow-wrap: anywhere` / `word-break: break-word`로 긴 snake_case 상태도 줄바꿈되도록 했다
- Follow-up:
  - 같은 문제가 다른 Backtest panel의 long status summary에서도 반복되면 동일한 card pattern을 해당 panel에 적용한다

### 2026-04-30 - Route/readiness 판정도 말줄임 없이 보여야 한다
- User request:
  - `Portfolio Proposal 진입 평가`의 `Route` 값이 `PORTFOLIO_...`처럼 잘려 보이고, 이런 긴 상태 문자열 요약이 여러 곳에 있다고 지적함
  - 카드 방식이 아니어도 더 시각적으로 읽기 좋은 UI로 개선해 달라고 요청함
- Interpreted goal:
  - route label은 숫자 metric이 아니라 운영 경로 판정이므로, 말줄임 없이 읽히는 decision panel이 더 적합함
  - 동일한 문제가 반복되지 않게 Candidate Review와 Pre-Live Review가 같은 공용 UI component를 쓰도록 해야 함
- Analysis result:
  - `app/web/backtest_ui_components.py`를 추가해 wrapping status card와 route/readiness decision panel을 공용화했다
  - `Candidate Review > Pre-Live 진입 평가`와 `Pre-Live Review > Portfolio Proposal 진입 평가`의 `Route / Readiness / Blockers / 판정 / 다음 행동` 영역을 새 route panel로 교체했다
  - 기존 score, progress bar, criteria table, route별 버튼 활성화 조건은 바꾸지 않았다
- Follow-up:
  - 이후 다른 Backtest panel에서 긴 status label이 `st.metric`에 들어가는 경우 `backtest_ui_components.py`의 component를 재사용한다

### 2026-04-30 - Backtest navigation에서 History는 주 흐름이 아니라 보조 도구로 둔다
- User request:
  - Backtest page에 `Backtest` 제목과 설명이 중복되어 보이고, panel navigation에서 `Candidate Review` 다음에 `History`가 나오는 구조가 후보 검토 흐름을 어색하게 만든다고 지적함
  - Streamlit에서 더 보기 좋은 탭 / 내비게이션 방식이 있으면 바꾸고, History는 다른 위치로 옮기는 방향을 검토해 달라고 요청함
- Interpreted goal:
  - Backtest는 최종 후보를 찾아 Candidate Review, Pre-Live, Portfolio Proposal로 이어지는 작업 공간으로 읽혀야 함
  - History는 여전히 rerun, load into form, candidate draft handoff에 필요하지만 후보 검토의 본 단계처럼 보이면 안 됨
- Analysis result:
  - 상위 `Backtest` page title만 남기고 내부 중복 title/caption을 제거했다
  - 현재 Streamlit 1.56.0에서 지원하는 `st.segmented_control`을 사용해 메인 workflow를 `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Pre-Live Review -> Portfolio Proposal`로 표시했다
  - `History`는 메인 workflow에서 제외하고 `Run History` utility 버튼으로 분리했다
  - 기존 `_request_backtest_panel("History")`, `Back To History`, history inspect / replay / load / candidate draft 기능은 유지했다
- Follow-up:
  - 이후 History 자체가 더 커지면 `app/web/pages/backtest.py`에서 별도 History module로 분리하는 것이 다음 자연스러운 리팩토링 후보이다

### 2026-04-30 - Backtest Run History는 Operations의 운영 / 재현 화면으로 분리한다
- User request:
  - Backtest workflow 옆에 `Run History` 버튼을 두는 대신, history 관련 정보를 별도 스크립트로 관리하고 `Operations` 아래 새 대분류 탭으로 옮기는 것이 어떠냐고 제안함
- Interpreted goal:
  - Backtest는 후보를 만들고 검토하는 주 흐름에 집중해야 함
  - 저장된 백테스트 실행 기록은 운영 감사, 재현, form 복원, 후보 검토 초안 전달 기능이므로 Operations에서 관리하는 편이 사용자가 흐름을 이해하기 쉽다
- Analysis result:
  - `app/web/backtest_history.py`를 추가해 `Operations > Backtest Run History` page shell을 분리했다
  - `streamlit_app.py`의 Operations navigation에 `Backtest Run History`를 추가했다
  - Backtest 화면에서는 `Run History` 버튼과 History panel route를 제거하고, 과거 실행 기록은 Operations에서 관리한다고 안내한다
  - 기존 history action은 유지한다: `Load Into Form`, `Run Again`, `Review As Candidate Draft`는 필요한 session state를 만든 뒤 Backtest page로 이동한다
  - Candidate Review 안내 문구도 `Operations > Backtest Run History`에서 넘어온 초안으로 표현을 바꿨다
- Follow-up:
  - History helper 본문은 아직 `app/web/pages/backtest.py`에 많이 남아 있으므로, 다음 리팩토링에서는 history helper / replay helper를 `backtest_history_helpers.py`로 추가 분리하는 것이 자연스럽다

### 2026-04-30 - Backtest Run History 본문도 render/helper로 분리한다
- User request:
  - `app/web/backtest_history.py`가 아직 shell만 있고 실제 history code는 `backtest.py`에 남아 있는지 확인하고, 2차 분리를 진행하면 `backtest.py` 길이가 줄어드는지 질문한 뒤 리팩토링을 승인함
- Interpreted goal:
  - Operations로 옮긴 History 화면의 실제 render와 replay helper를 별도 모듈로 옮겨야 함
  - Backtest page는 후보 생성 / 검토 workflow shell에 집중하고, 과거 실행 기록 inspect / replay / load / candidate draft handoff는 History module이 관리해야 함
- Analysis result:
  - `app/web/backtest_history.py`가 `Operations > Backtest Run History`의 persistent history inspector, selected record detail, replay parity snapshot, action button render를 맡는다
  - `app/web/backtest_history_helpers.py`가 history table row, replay payload 복원, History replay parity, Real-Money / Guardrail scope table helper를 맡는다
  - 실제 `Run Again`의 전략 실행은 여전히 `backtest.py`의 `_handle_backtest_run`에 위임한다. History는 실행 UI와 저장 기록 해석을 담당하고 strategy runtime owner가 되지는 않는다
  - `backtest.py`에서는 History render/helper 본문을 제거하고, Compare / saved portfolio가 쓰는 Real-Money / Guardrail parity renderer만 import해 사용한다
- Follow-up:
  - 다음 구조 개선 후보는 Saved Portfolio / Weighted Portfolio 또는 Portfolio Proposal render/helper 분리다

### 2026-04-30 - Pre-Live Review는 별도 탭보다 Candidate Review 안의 운영 기록으로 합친다
- User request:
  - Candidate Review와 Pre-Live Review가 실제로 분리될 만큼 다른 단계인지 질문했고, Pre-Live Review 탭과 전용 스크립트를 없애고 Candidate Review로 합치는 방향을 승인함
- Interpreted goal:
  - 후보 정의와 운영 상태 기록의 개념 차이는 유지하되, 사용자가 6단계 이후 별도 탭을 오가며 같은 후보를 다시 찾아야 하는 UX는 없애야 함
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은 Portfolio Proposal이 읽는 운영 record로 유지해야 함
- Analysis result:
  - 별도 `Pre-Live Review` Backtest panel을 제거하고, Candidate Review 3번 구간을 `운영 상태 저장 및 Portfolio Proposal 진입 평가`로 확장했다
  - `Save Pre-Live Record`와 `Open Portfolio Proposal`이 Candidate Review 안에서 이어지므로, Review Note / current candidate registry / pre-live record / proposal handoff가 한 화면의 순서형 flow로 보인다
  - `app/web/backtest_pre_live_review.py`와 `app/web/backtest_pre_live_review_helpers.py`는 삭제했고, Pre-Live status 추천 / draft / readiness helper는 `app/web/backtest_candidate_review_helpers.py`로 통합했다
- Follow-up:
  - 다음 Candidate Review UX 수정은 별도 Pre-Live script가 아니라 `app/web/backtest_candidate_review.py`와 `app/web/backtest_candidate_review_helpers.py`에서 확인한다

### 2026-04-30 - Candidate Review 설명은 긴 텍스트보다 중간 밀도의 시각 구조로 푼다
- User request:
  - Candidate Review의 3개 큰 단계가 왜 필요한지 더 잘 보여야 하지만, 텍스트 설명을 많이 추가하면 UI가 비대해진다고 우려함
  - 너무 짧은 칩만 쓰는 것도 의미가 부족하니 중간 밀도의 표현을 요청함
- Interpreted goal:
  - 사용자가 `Draft -> Review Note -> Current Candidate -> Pre-Live Record -> Proposal Ready` 산출물 흐름을 한눈에 읽어야 함
  - 각 단계는 긴 문단 대신 무엇을 입력으로 받아 무엇을 만들고 끝나는지 구조적으로 보여줘야 함
- Analysis result:
  - Candidate Review 상단에 다섯 개 산출물 card pipeline을 추가했다
  - 각 큰 단계에는 `Input / Action / Output` summary cards를 추가했다
  - `Registry 후보 범위 판단`은 `Candidate Packaging 종합 판단`과 같은 route/readiness panel로 바꿔 Scope, Score, Blockers, 판정, 다음 행동을 같은 시각 언어로 보여준다
- Follow-up:
  - 이후 다른 Backtest workflow도 설명문이 길어지면, 먼저 artifact card 또는 input/action/output summary로 줄이는 방식을 우선 검토한다

### 2026-04-30 - Candidate Review 단계 내부는 더 얇은 안내와 접힌 상세로 정리한다
- User request:
  - Artifact pipeline은 괜찮지만 각 단계별 Input / Action / Output 카드는 오히려 복잡해 보인다고 지적함
  - Registry 저장과 운영 상태 저장 구간은 처음 사용하는 사람이 보기에는 정보가 너무 많이 펼쳐져 있어 핵심 행동이 흐려진다고 봄
  - 웹에서 Cmd+C를 누를 때 Streamlit `Clear caches` modal이 뜨는 문제도 확인을 요청함
- Interpreted goal:
  - 상단 산출물 흐름은 유지하되, 단계 내부는 긴 설명이나 카드 grid가 아니라 얇은 목적/결과 표시와 핵심 판정 중심으로 정리해야 함
  - 상세 기준 표, 기존 저장 row, 추천 근거는 필요할 때만 열어보는 보조 정보여야 함
- Analysis result:
  - Input / Action / Output 카드를 제거하고 각 섹션 상단은 `왜 / 결과` brief strip으로 축소했다
  - Registry 저장 구간은 Scope route panel과 저장값 form 중심으로 정리하고, 판단 기준과 기존 저장 기록은 collapsed expander로 이동했다
  - Registry row 저장 form은 먼저 찾아야 할 이름과 후보 범위를 확인하도록 줄이고, strategy family / strategy name / candidate role 같은 고급 식별값은 접힘 영역으로 보냈다
  - 운영 상태 저장 구간은 promotion / shortlist / deployment / suggested status를 compact badge로 보여주고, 방금 저장한 후보 식별값, Pre-Live 추천 근거, proposal route 기준은 접어 두었다
  - Cmd+C cache modal은 repo 코드가 만든 것이 아니라 Streamlit 기본 단축키 계열 동작으로 판단했고, 앱에서 Cmd/Ctrl+C keydown 이벤트가 Streamlit handler까지 전파되지 않도록 guard를 설치했다
- Follow-up:
  - Playwright smoke에서는 Cmd/Ctrl+C 후 clear-cache modal이 뜨지 않았다. 실제 브라우저 사용 중에도 다시 뜨면 Streamlit shortcut 처리 변경 여부를 추가로 확인한다

### 2026-04-30 - Candidate Review 3번은 운영 기록 저장과 다음 단계 판단을 한 블록으로 본다
- User request:
  - Candidate Review 3번 내부의 `운영 상태 / 추적 계획 저장`과 `다음 단계 이동`이 분리되어 보이는 것이 애매하다고 지적함
  - 다음 단계 이동 가능 여부가 확정되어야 저장하고 이동할 수 있는 것 아니냐고 질문함
- Interpreted goal:
  - 3번 내부에서 다시 새로운 전략 평가를 하는 느낌을 줄이고, 저장 전에는 저장 가능 여부와 저장 후 이동 가능 여부를 미리 보여줘야 함
  - `Portfolio Proposal 진입 평가`를 별도 큰 단계처럼 보이게 하기보다 운영 기록 저장 결과로 흡수해야 함
- Analysis result:
  - Candidate Review 3번을 `운영 기록 저장 및 Portfolio Proposal 이동`으로 이름을 바꿨다
  - `Candidate Packaging 종합 판단`은 `선택 후보 확인`으로 축소해 Route / Record Type / Promotion / Deployment만 먼저 보여준다
  - `Pre-Live 운영 상태 / 추적 계획 저장`과 `Portfolio Proposal 진입 평가`는 `운영 기록 저장 및 다음 단계 판단`으로 합쳤다
  - 저장 버튼 위에서 `Save Record`, `Next Route`, `Proposal`, `Blockers`를 compact badge로 보여주며, 상세 기준은 접힘 영역으로 둔다
- Follow-up:
  - 이후 3번 UI를 더 줄일 때도 핵심은 `저장 가능 여부`와 `저장된 record 기준 다음 단계 이동 가능 여부`를 분리해서 보여주는 것이다

### 2026-04-30 - Candidate Review 3번에도 공통 판정 panel은 유지한다
- User request:
  - `저장 범위 판단` 같은 시각적 판정 장치는 다음 단계 판단 공통 요소로 필요하니 3번에서도 없애면 안 된다고 지적함
  - 다만 `운영 기록 / 다음 단계 판단 기준`, `Pre-Live Record JSON Preview`, `Selected Candidate Detail`이 버튼 주변에 흩어져 있어 Save / Open 버튼을 찾기 어렵다고 봄
- Interpreted goal:
  - 다음 단계로 넘어갈 수 있는지 보는 공통 route/readiness panel은 유지해야 함
  - secondary detail은 버튼보다 앞에 흐름을 방해하지 않도록 하나로 묶어야 함
- Analysis result:
  - `운영 기록 저장 및 다음 단계 판단` 안에 route/readiness panel을 다시 배치했다
  - `Save Record`, `Proposal`, `Blockers` badge는 panel 아래의 보조 신호로 남겼다
  - `Save Pre-Live Record`와 `Open Portfolio Proposal`은 `저장 및 이동` action block으로 묶어 상세 보기보다 먼저 배치했다
  - 판단 기준, Pre-Live JSON, 선택 후보 detail은 하나의 `상세 보기` expander 내부 tab으로 통합했다
- Follow-up:
  - 이후 Candidate Review의 다른 하단 보조 도구도 같은 기준으로, action은 먼저 보이고 raw/detail은 접힘 영역으로 보내는 방향이 좋다

### 2026-04-30 - 다음 단계 판단은 운영 기록 입력 위에서 먼저 읽히게 한다
- User request:
  - 다음 단계 판단 panel의 긴 route label이 카드 안에서 잘려 의미를 읽기 어렵다고 지적함
  - 이 판정은 운영 기록을 저장할 수 있는 이유를 설명하므로 `운영 기록 저장 및 다음 단계 판단` 아래보다 위에 있어야 한다고 봄
- Interpreted goal:
  - `저장 범위 판단`과 같은 포맷의 공통 판정 장치는 유지하되, 긴 route label은 mid-word로 깨지지 않아야 함
  - 사용자는 먼저 통과/보류 여부를 보고, 그 다음 운영 상태 / 추적 계획을 입력하고 저장 버튼을 찾아야 함
- Analysis result:
  - route/readiness panel을 더 넓게 배치하고 route label은 underscore 기준으로 줄바꿈되게 고쳤다
  - Candidate Review 3번의 `다음 단계 진행 판단`을 `운영 상태 / 추적 계획 입력` 위로 올렸다
  - 판정 panel은 현재 입력값으로 계산되지만, 화면상으로는 저장 가능 여부를 먼저 읽을 수 있게 배치했다
- Follow-up:
  - 다른 route panel에서도 긴 enum 값은 글자 중간이 아니라 의미 단위에서 줄바꿈되도록 같은 공통 컴포넌트를 사용한다

### 2026-04-30 - Portfolio Proposal은 후보를 Live Readiness용 포트폴리오 초안으로 바꾸는 한 단계다
- User request:
  - Portfolio Proposal 초안 작성 기능이 필요한지, Candidate Review 이후 바로 Live Readiness / Final Approval로 가도 되는지 검토 요청
  - 기능이 필요하다면 전체 흐름에서 하나의 단계로 유지하고 UX를 개편해 달라고 요청
- Interpreted goal:
  - 후보를 계속 저장만 하는 단계가 아니라, Live Readiness가 읽을 수 있는 포트폴리오 형태를 만드는 최소 단계로 재정의한다
  - 단일 후보는 빠르게 지나갈 수 있고, 여러 후보는 목적 / 역할 / 비중을 명시하게 한다
- Analysis result:
  - Candidate Review는 “후보가 볼 만한가”를 판단하고, Portfolio Proposal은 “후보를 어떤 목적 / 역할 / 비중의 포트폴리오 초안으로 볼 것인가”를 판단하는 경계로 유지한다
  - Portfolio Proposal 화면은 `후보 확인 -> 목적 / 역할 / 비중 설계 -> Live Readiness 진입 평가 -> 저장` 순서로 재구성했다
  - saved proposal monitoring / Pre-Live feedback / paper tracking feedback은 주 단계가 아니라 접힌 보조 도구로 낮췄다
- Follow-up:
  - 다음 단계 개발 시 `Open Live Readiness`를 실제 Live Readiness 화면으로 연결하고, proposal readiness row를 입력 계약으로 사용한다

### 2026-04-30 - Portfolio Proposal은 단일 후보 저장 반복과 다중 후보 구성 초안을 분리해야 한다
- User request:
  - Portfolio Proposal을 실제로 사용해 보니 단일 후보를 넣어도 Candidate Review와 비슷하게 또 저장하고 넘기는 느낌이라고 지적함
  - `Proposal Components`, 목적 / 역할 / 비중 설계, 후보별 role / target weight / reason이 언제 필요한지 불명확하다고 봄
  - 단일 후보라면 Candidate Review 이후 바로 Live Readiness로 가는 것이 낫지 않느냐고 질문함
- Interpreted goal:
  - Portfolio Proposal이 필요한 경우와 불필요한 경우를 UX에서 분리해야 함
  - 단일 후보는 저장을 반복하지 않고 Live Readiness 직행 가능성만 확인하고, 여러 후보를 묶을 때만 proposal draft를 저장해야 함
- Analysis result:
  - 단일 후보는 `단일 후보 직행 평가` 경로로 처리한다. role은 `core_anchor`, target weight는 `100%`, capital scope는 `paper_only`로 자동 전제한다.
  - 여러 후보는 `포트폴리오 초안 작성` 경로로 처리한다. 여기서만 Proposal ID, Status, Type, Capital Scope, 목적, review cadence, weighting, benchmark policy, 후보별 role / weight / reason이 의미 있는 입력이 된다.
  - `Proposal Components`는 비교가 아니라 구성 후보 선택이다. 좋은지 나쁜지 비교하는 작업은 5단계 Compare에서 끝내고, 이 단계는 선택한 후보를 포트폴리오 형태로 묶을 때만 사용한다.
- Follow-up:
  - 향후 Live Readiness 화면이 구현되면 `Open Live Readiness`는 direct candidate 또는 saved proposal draft를 입력으로 받을 수 있어야 한다.

### 2026-04-30 - Workspace Overview는 정적 시작 가이드보다 후보 / 다음 행동 dashboard가 되어야 한다
- User request:
  - Workspace Overview가 방치되어 있고 실제로 하는 일이 없으니, 현재 테스트한 포트폴리오 Top 후보, 추천성 정보, 그래프, 필요한 요소가 있는 대시보드 앞단으로 개편하고 싶다고 요청함
  - Overview도 별도 스크립트로 분리해서 관리하는 것이 좋은지 검토 요청
- Interpreted goal:
  - Overview는 가이드 페이지가 아니라 현재 후보 상태와 다음 행동을 한눈에 보여주는 front dashboard가 되어야 함
  - `streamlit_app.py`가 더 커지지 않도록 Overview render와 집계 helper를 별도 모듈로 분리해야 함
- Analysis result:
  - Overview는 `Current Candidates`, `Paper Tracking`, `Proposal Drafts`, `Recent Runs` KPI를 상단에 둔다
  - `검토 우선 후보 Top 3`은 투자 추천이 아니라 Real-Money signal, Pre-Live status, deployment blocker, CAGR/MDD 기반 운영 검토 우선순위로 표시한다
  - Candidate funnel chart와 Next Actions를 나란히 두어 후보들이 어디에 쌓였고 다음에 어느 탭으로 가야 하는지 보여준다
  - Runtime / Build 정보는 디버깅에 유용하므로 제거하지 않고 `System Snapshot`으로 접어 둔다
- Follow-up:
  - 이후 Live Readiness가 구현되면 Overview Top 후보와 Next Actions에 direct Live Readiness / saved proposal 입력 경로를 연결할 수 있다.

### 2026-04-30 - Backtest page는 page shell이고 workflow 본문은 module별로 관리한다
- User request:
  - `backtest.py`가 다시 커졌으니 Single Strategy와 Compare / Portfolio Builder도 Candidate Review, Portfolio Proposal처럼 별도 스크립트로 분리해 달라고 요청함
  - 향후 새 phase나 새 전략이 추가될 때도 대응 가능한 module 구조를 원함
- Interpreted goal:
  - 단순 helper 하나로 빼는 것이 아니라, Single Strategy form / runner / result display / Compare / saved replay 책임을 분리해 수정 위치를 명확하게 한다
  - 기존 session state key와 저장 / replay / candidate handoff behavior는 유지한다
- Analysis result:
  - `app/web/pages/backtest.py`는 page shell과 workflow navigation만 남기는 구조가 맞다
  - Single Strategy는 `backtest_single_strategy.py`, `backtest_single_forms.py`, `backtest_single_runner.py`로 나눠 orchestration / form / 실행 dispatch 책임을 분리했다
  - Compare & Portfolio Builder는 `backtest_compare.py`가 담당하고, 결과 표시 공통부는 `backtest_result_display.py`로 분리했다
  - 공용 preset, session state, 입력 component, status label은 `backtest_common.py`에 모았다. 이 파일은 다음 리팩토링에서 `state / strategy_inputs / presets`로 더 나눌 수 있는 transitional shared module이다
- Follow-up:
  - 새 전략 추가 시에는 catalog, single form, runner dispatch, compare default / override 경계를 우선 확인한다
  - `backtest_common.py`가 다시 커지면 다음 작업 단위에서 `backtest_state.py`, `backtest_strategy_inputs.py`, `backtest_presets.py`로 추가 분리한다

### 2026-04-30 - fresh registry에서 7단계까지 도달 가능한 GTAA 후보 선정
- User request:
  - 기존 runtime JSONL을 archive한 뒤 처음부터 다시 실습하기 위해, GTAA에서 6개 이상 ETF, `MDD <= 20%`, `CAGR >= 10%`, `interval < 3` 조건을 만족하고 현재 7단계까지 도달 가능한 후보를 찾아 저장해 달라고 요청함
- Interpreted goal:
  - 단순히 CAGR/MDD가 좋은 후보가 아니라, Candidate Review / Current Candidate Registry / Pre-Live paper tracking / Portfolio Proposal 단일 후보 직행 평가까지 앱이 읽을 수 있는 후보가 필요함
- Analysis result:
  - 숫자 성과만 보면 공격적인 broader GTAA universe 후보들이 더 높았지만, ETF profile coverage 또는 SPY rolling validation 경고 때문에 `hold / blocked`가 반복됐다
  - clean ETF profile을 가진 `SPY, QQQ, GLD, IEF, LQD, TLT` 6개 universe를 사용하고, 다중자산 GTAA formal benchmark를 `AOR`로 두면 `real_money_candidate / paper_probation / paper_only`까지 통과했다
  - 최종 후보는 `top=1`, `interval=2`, `score=3M/12M`, `MA200`, `risk_off=cash_only`, 기간 `2016-01-29 ~ 2026-04-01`, `CAGR=15.3395%`, `MDD=-13.9675%`, `Sharpe=1.6054`
  - 같은 후보는 SPY full-period CAGR/MDD도 앞서지만, SPY를 formal benchmark로 쓰면 rolling worst-excess validation caution으로 `hold`가 된다
- Follow-up:
  - 사용자가 UI에서 재현할 때 benchmark는 `AOR`로 두고, SPY는 reference benchmark로 해석한다
  - 후보 저장 ID는 `gtaa_current_candidate_clean6_aor_top1_i2_3m12m`, Pre-Live ID는 `pre_live_gtaa_current_candidate_clean6_aor_top1_i2_3m12m`이다

### 2026-05-01 - top 2~4 / interval < 4 조건의 추가 GTAA 후보 선정
- User request:
  - GTAA 전략에서 `interval < 4`, `top = 2 / 3 / 4`, universe 6~15개 조건을 만족하면서 7단계까지 갈 수 있는 후보를 하나 더 찾아 달라고 요청함
- Interpreted goal:
  - 기존 top-1 후보와 달리, 여러 자산을 동시에 들고 가는 top-N GTAA 후보를 current candidate / Pre-Live / Portfolio Proposal 직행 평가까지 이어지게 한다
- Analysis result:
  - clean ETF profile을 유지하기 위해 `SPY, QQQ, GLD, IEF, LQD, TLT` universe를 사용했다
  - `top=2`, `interval=3`, `score=1M/3M/6M`, `MA200`, `risk_off=cash_only`, benchmark `AOR` 후보가 `real_money_candidate / paper_probation / paper_only`까지 통과했다
  - 결과는 `CAGR=12.8073%`, `MDD=-11.5626%`, `Sharpe=2.0147`, `AOR 대비 CAGR spread=+7.3363%p`
  - 같은 탐색 중 `top=2 / interval=1 / 3M+6M+12M` 후보가 CAGR은 더 높았지만 MDD가 깊어, 추가 실습 후보로는 interval-3 후보를 선택했다
- Follow-up:
  - 저장 ID는 `gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`, Pre-Live ID는 `pre_live_gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`이다

### 2026-05-01 - CAGR 15% 이상 / 낮은 MDD 조건의 GTAA 후보 재탐색
- User request:
  - 직전 top-2 interval-3 후보의 CAGR이 조금 아쉬우니, 같은 조건을 유지하면서 CAGR 15% 이상이고 MDD는 11~12%대 또는 더 낮은 후보를 다시 찾아 달라고 요청함
- Interpreted goal:
  - `top=2/3/4`, `interval<4`, universe 6~15개 조건을 유지하면서 더 높은 CAGR을 확보하되, 7단계까지 갈 수 있는 Real-Money gate와 ETF operability를 유지한다
- Analysis result:
  - clean ETF profile universe `SPY, QQQ, GLD, IEF, LQD, TLT` 안에서 `top=2`, `interval=2`, `score=1M/12M`, `MA150`, `risk_off=cash_only`, benchmark `AOR` 후보가 조건을 가장 잘 만족했다
  - 결과는 `CAGR=15.2174%`, `MDD=-8.8783%`, `Sharpe=1.9630`, `AOR 대비 CAGR spread=+9.7464%p`
  - Real-Money 신호는 `real_money_candidate / paper_probation / paper_only`, `Validation=normal`, `ETF Operability=normal`이었다
- Follow-up:
  - 저장 ID는 `gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`, Pre-Live ID는 `pre_live_gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`이다

### 2026-05-01 - 저장 후보를 다시 열어 그래프와 결과표로 확인하는 방법
- User request:
  - 탐색으로 찾은 후보군을 나중에 다시 로드해 Single Strategy 결과처럼 summary, equity curve, balance extremes, period extremes, result table과 함께 보고 싶다고 요청함
  - Compare 탭의 saved portfolio가 후보 보관함 역할까지 하는 것이 맞는지 검토 요청함
- Interpreted goal:
  - 저장 후보 자체를 재검토하는 보조 화면이 필요하며, 이를 새 workflow 단계로 만들지 않고 Operations 보조 도구로 분리해야 함
  - saved candidate와 saved weighted portfolio의 의미를 UI에서 분리해야 함
- Analysis result:
  - `Backtest Run History`는 과거 실행 기록을 다시 여는 도구이고, `Saved Weighted Portfolios`는 Compare의 weighted portfolio builder 산출물이다
  - current candidate registry에는 compact snapshot과 contract가 저장되므로, 그래프 / result table을 보려면 저장 contract로 DB-backed 백테스트를 다시 실행하는 replay surface가 필요하다
  - `Operations > Candidate Library`를 추가해 current / Pre-Live 후보를 inspect하고, ETF 후보 family는 저장 contract로 result curve를 재생성하도록 했다
- Follow-up:
  - 이후 필요하면 Candidate Library에 여러 후보 선택 후 같은 전략 family 변형끼리 직접 비교하는 candidate-to-candidate compare mode를 추가할 수 있다

### 2026-05-01 - Quality 전략에서 7단계까지 갈 수 있는 실습 후보 탐색
- User request:
  - `Quality` 전략에서 `US Statement Coverage 100 / 300 / 500`, `dynamic PIT`, `topN 3~10`,
    `CAGR >= 20%`, `MDD >= -15%` 조건을 만족하고 현재 7단계 workflow까지 갈 수 있는 후보를 찾아 달라고 요청함
- Interpreted goal:
  - 단순 성과가 좋은 Quality run이 아니라, Candidate Review / Registry / Pre-Live / Portfolio Proposal 실습 흐름에서 사용할 수 있는 non-blocked 후보가 필요함
- Analysis result:
  - Coverage 100에서 조건 충족 후보를 찾았다
  - 설정은 `topN=8`, `AOR` formal benchmark, default quality factors,
    `MA250 trend`, `retain_unfilled_as_cash`, `cash_only`,
    underperformance guardrail `3M / -5%`,
    drawdown guardrail `12M / -12% / 5% gap`
  - 결과는 `CAGR=20.02%`, `MDD=-13.42%`, `Sharpe=1.3957`,
    `real_money_candidate / paper_probation / review_required`
  - Coverage 300은 exact hit가 없었고, Coverage 500은 같은 성공 조합에서도 `CAGR 7~9%`, MDD `-18~-23%` 수준으로 탈락했다
- Follow-up:
  - 사용자가 저장을 원하면 이 후보를 review note, current candidate registry, pre-live record 순서로 저장한다

### 2026-05-01 - Quality 후보를 GTAA처럼 paper_only까지 낮출 수 있는지 재검토
- User request:
  - 직전 Quality 후보가 `review_required`라면, GTAA 후보처럼 registry에 추가하기 쉬운 `paper_only` 후보로 재구성하거나 더 조사해 달라고 요청함
- Interpreted goal:
  - 단순히 숫자 조건을 만족하는 후보보다, Candidate Review / Current Candidate Registry / Pre-Live paper tracking 흐름에서 더 자연스럽게 사용할 수 있는 Quality 후보가 필요한지 확인
- Analysis result:
  - `CAGR >= 20%`, `MDD >= -15%`, `Deployment = paper_only`를 동시에 만족하는 후보는 bounded search에서 찾지 못했다
  - `paper_only`로 내려오는 가장 깔끔한 후보는 `US Statement Coverage 100`, `dynamic PIT`,
    factors `roe, roa, cash_ratio, debt_to_assets`, `topN=10`, `MA250`, `retain_unfilled_as_cash`, `cash_only`, benchmark `AOR`
  - 결과는 `CAGR=14.38%`, `MDD=-14.56%`, `Sharpe=1.2490`,
    `real_money_candidate / paper_probation / paper_only`, `Monitoring=routine_review`
- Follow-up:
  - 사용자는 높은 CAGR을 우선하면 `review_required` 후보를, 깨끗한 registry 실습 흐름을 우선하면 `paper_only` 후보를 선택하면 된다

### 2026-05-01 - Quality + Value 전략에서 CAGR 25% / MDD -20% 조건 후보 탐색
- User request:
  - Quality 단독으로는 좋은 후보를 찾기 어려우므로 `Quality + Value` 전략으로 스펙트럼을 넓혀
    `US Statement Coverage 100 / 300 / 500 / 1000`, `dynamic PIT`, `topN 3~10`,
    `CAGR >= 25%`, `MDD >= -20%` 조건을 만족하는 후보를 찾아 달라고 요청함
- Interpreted goal:
  - factor를 최소 3개 이상 섞은 blended 전략 중에서 단순 성과뿐 아니라
    Candidate Review / Portfolio Proposal 실습 흐름에 올릴 수 있는 non-blocked 후보를 찾는다
- Analysis result:
  - 최종 후보는 `US Statement Coverage 100`, `Historical Dynamic PIT`,
    `topN=10`, ticker benchmark `SPY` 조합이다
  - quality factors:
    `roe, roa, operating_margin, asset_turnover, current_ratio`
  - value factors:
    `book_to_market, earnings_yield, sales_yield, pcr, por`
  - portfolio / guardrail:
    `equal_weight`, `reweight_survivors`, `cash_only`,
    underperformance guardrail `12M / -5%`,
    drawdown guardrail `12M / -15% strategy threshold / 3% gap`
  - 결과는 `CAGR=29.25%`, `MDD=-18.64%`, `Sharpe=1.5222`,
    `real_money_candidate / paper_probation / review_required`,
    `Validation=normal`, `Liquidity Clean Coverage=100%`
  - Coverage 500에서도 숫자 조건 exact hit가 있었지만 full runtime에서
    `liquidity_clean_coverage`가 낮고 validation caution이 남아 `hold / blocked`로 제외했다
- Follow-up:
  - 사용자가 7단계 통과 여부와 등록을 요청해 다음 기록까지 저장했다
    - `candidate_review_note_qv_cov100_top10_spy_mdd20`
    - `quality_value_current_candidate_cov100_top10_spy_mdd20`
    - `pre_live_quality_value_current_candidate_cov100_top10_spy_mdd20`
  - Candidate Library 목록에는 표시된다
  - 2026-05-02 기준 Candidate Library의 full replay가 strict annual equity strategy까지 지원하도록 개선됐다

### 2026-05-01 - review_required를 paper_only로 낮추기 위한 후보 재탐색
- User request:
  - 직전 후보가 `review_required` 상태라면 전략 설정을 다시 검증하거나 새 전략을 찾아
    `Promotion = real_money_candidate`, `Shortlist = paper_probation`, `Deployment = paper_only` 상태가 나오도록 요청함
- Interpreted goal:
  - 단순히 높은 CAGR 후보를 찾는 것이 아니라, Candidate Review에서 더 깔끔하게 Current Candidate / Pre-Live 흐름으로 넘어갈 수 있는 운영 상태를 찾는다
- Analysis result:
  - `Quality + Value` 후보는 CAGR/MDD 조건은 강했지만 guardrail / monitoring 신호 때문에 exact `paper_only`까지 내려오지 못했다
  - exact hit는 `Quality Snapshot (Strict Annual)`에서 찾았다
  - 설정은 `US Statement Coverage 100`, `Historical Dynamic PIT`, factors `roe, roa, cash_ratio, debt_to_assets`,
    `topN=10`, `MA250`, `retain_unfilled_as_cash`, `cash_only`, benchmark `AOR`
  - 결과는 `CAGR=14.38%`, `MDD=-14.56%`, `Sharpe=1.2490`,
    `real_money_candidate / paper_probation / paper_only`, `Monitoring=routine_review`
- Follow-up:
  - 다음 기록까지 저장했다
    - `candidate_review_note_quality_cov100_top10_aor_ma250_paper_only`
    - `quality_current_candidate_cov100_top10_aor_ma250_paper_only`
    - `pre_live_quality_current_candidate_cov100_top10_aor_ma250_paper_only`
  - Candidate Library 목록에서 `paper_tracking` 후보로 확인된다

### 2026-05-02 - Candidate Library strict annual 후보 replay 경고 해결
- User request:
  - Candidate Library에서 `Quality + Value` 후보를 선택하고 `Rebuild Result Curve`를 누르면
    ETF strategy만 지원한다는 replay input warning이 발생한다고 보고함
- Interpreted goal:
  - 저장 후보 보관함에서 strict annual equity 후보도 ETF 후보처럼 summary, equity curve, result table로 다시 열 수 있어야 한다
- Analysis result:
  - 원인은 `app/web/backtest_candidate_library_helpers.py`의 replay 허용 목록과 runtime dispatch가
    `equal_weight`, `gtaa`, `global_relative_strength`, `risk_parity_trend`, `dual_momentum`만 지원했기 때문이었다
  - replay 지원 범위를 `quality_snapshot_strict_annual`, `value_snapshot_strict_annual`, `quality_value_snapshot_strict_annual`까지 확장했다
  - 저장된 current candidate contract에서 factor set, dynamic PIT universe, topN, benchmark, guardrail, liquidity, promotion threshold를 복원해 strict annual runtime으로 넘기도록 했다
- Follow-up:
  - `Quality + Value Coverage 100 Top-10` replay가 124 result rows로 재생성되고,
    기존 gate인 `real_money_candidate / paper_probation / review_required`가 유지됨을 확인했다
  - `Quality Coverage 100 Top-10 AOR MA250 paper-only` replay도 124 result rows와
    `real_money_candidate / paper_probation / paper_only`로 확인했다

### 2026-05-02 - Quality + Value replay의 2026-03-31 row와 주의사항 한글화
- User request:
  - Candidate Library에서 `Quality + Value Coverage 100 Top-10`을 replay한 뒤 Result Table에 `2026-03-31` 데이터가 보이지 않는 것 같다고 확인 요청
  - replay 주의사항이 영어로 나오는 부분을 한국어로 바꿔 달라고 요청
- Interpreted goal:
  - 실제 result row 누락인지, UI 표시 문제인지 확인하고 strict annual 후보 replay의 operator-facing warning을 한국어로 정리한다
- Analysis result:
  - backend replay result에는 `2026-03-31` row가 존재한다
  - 마지막 네 날짜는 `2026-01-30`, `2026-02-27`, `2026-03-31`, `2026-04-01`이다
  - `2026-04-01`은 요청된 종료일 평가 row이고, `2026-03-31`은 정상적인 3월 month-end row다
- Follow-up:
  - strict annual runtime warning 문구를 한국어로 변경했다
  - `Quality + Value` replay에서 dynamic PIT, 최소 이력, 유동성, 상대성과 guardrail, drawdown guardrail, 실전 검토 보강 안내가 한국어로 출력됨을 확인했다

### 2026-05-02 - finance phase 문서 상위 폴더 정리
- User request:
  - `.aiworkspace/note/finance` root에 `phase1`~`phase30` 폴더가 직접 흩어져 있어 문서가 파편화되어 보이므로, phase 문서를 상위 폴더로 묶고 기존 링크도 정리해 달라고 요청함
- Interpreted goal:
  - root에는 top-level map, glossary, template, registry, operations entry만 남기고 phase 실행 문서는 한 곳에서 찾을 수 있게 만든다
- Analysis result:
  - canonical phase path를 `.aiworkspace/note/finance/phases/phase<N>/`로 정했다
  - 새 phase 생성 helper도 이 위치로 생성하도록 바꿔야 이후 문서 구조가 다시 흩어지지 않는다
  - `FINANCE_DOC_INDEX.md`에는 folder map을 추가해 phase / operations / backtest_reports / architecture / flows docs / data_architecture / research / support_tracks / archive의 역할을 바로 구분하게 했다
- Follow-up:
  - old `.aiworkspace/note/finance/phaseN` 링크는 `.aiworkspace/note/finance/phases/phaseN`으로 갱신했다
  - `.aiworkspace/note/finance/phases/README.md`를 새 phase 문서 landing page로 추가했다

### 2026-05-02 - finance JSONL 저장 파일 폴더화
- User request:
  - `.jsonl` 파일도 별도 폴더를 만들어 관리하는 것이 좋지 않겠냐고 질문했고, 제안한 구조대로 진행을 승인함
- Interpreted goal:
  - `.aiworkspace/note/finance` root에 실행 이력, registry, saved portfolio 파일이 섞이지 않게 하고, 앱 / helper / 문서가 같은 저장 위치를 바라보게 만든다
- Analysis result:
  - app-readable durable registry는 `.aiworkspace/note/finance/registries/`에 둔다
  - 로컬 실행 이력은 `.aiworkspace/note/finance/run_history/`에 둔다
  - 사용자가 명시적으로 저장한 weighted portfolio 설정은 `.aiworkspace/note/finance/saved/`에 둔다
- Follow-up:
  - runtime path constants, helper scripts, hygiene classification, UI 안내 문구, durable docs를 새 경로 기준으로 갱신했다
  - 각 JSONL 폴더에 README를 추가해 registry / run history / saved setup의 의미를 분리했다

### 2026-05-02 - 실전투자 포트폴리오 선정을 위한 다음 phase 방향 재정리
- User request:
  - 리팩토링과 구조 개선 이후 실전투자 포트폴리오 선정을 위한 phase를 다시 진행하기 전에, 현재 흐름과 남은 검증 / 테스트 / 향후 기능을 정리해 달라고 요청함
- Interpreted goal:
  - Phase 30의 Portfolio Proposal 이후 바로 투자 승인으로 뛰지 않고, Live Readiness / Final Approval / 실제 paper tracking / portfolio risk validation을 어떤 순서로 만들지 정해야 함
- Analysis result:
  - 현재 제품 흐름은 `Data Trust -> Single Strategy -> Real-Money -> Compare -> Candidate Packaging -> Current Candidate / Pre-Live -> Portfolio Proposal`까지 구현되어 있다
  - Phase 30은 `implementation_complete / manual_qa_pending`이며, 아직 최종 승인 체계는 없다
  - 실전투자 포트폴리오 선정까지는 최소 5개 phase가 자연스럽다:
    1. Live Readiness decision record / approval ledger
    2. Portfolio construction risk engine
    3. Robustness / validation pack
    4. Paper portfolio tracking / shadow execution
    5. Final portfolio selection guide
  - 전문 플랫폼 조사 기준으로도 research/backtest/optimization/live/paper/performance attribution이 분리되어 있으므로, 우리 프로그램도 최종 선정 전에 optimizer보다 검증, 추적, 승인 기록을 먼저 분리해야 한다
- Follow-up:
  - 다음 구현을 시작할 때는 Phase 31을 `Live Readiness Decision Record`로 열고, 실제 주문 / broker integration은 후속 post-approval 영역으로 둔다

### 2026-05-03 - Phase31~35 역할과 Phase31 필요성 clarification
- User request:
  - Phase31이 왜 필요한지, 이미 Portfolio Proposal / 단일 후보 기록이 있는데 무엇을 새로 기록하는지, Phase31~35에서 정확히 무엇을 하는지 자세한 설명을 요청함
- Interpreted goal:
  - 기존 후보 / Pre-Live / Proposal 저장소와 새 Live Readiness decision record의 차이를 명확히 해야 함
- Analysis result:
  - 기존 저장소는 후보 정의, 운영 기록, proposal 초안이지 “실전 검토 후보로 공식 접수했다”는 승인 전 decision ledger가 아니다
  - Phase31은 Candidate Review Note가 candidate registry append 전 사람 판단을 남겼던 것처럼, Portfolio Proposal 또는 단일 후보를 Live Readiness 검토 대상으로 공식 접수 / 보류 / 거절하는 기록을 만든다
  - 단일 후보도 Phase31 대상이다. 단일 후보는 proposal draft 저장 없이 current candidate + Pre-Live record + direct readiness 평가를 입력으로 Live Readiness record를 남길 수 있다
  - Phase32~35는 각각 portfolio risk engine, robustness validation pack, paper portfolio tracking, final portfolio selection guide로 분리해 최종 포트폴리오 후보 선정까지 이어진다
- Follow-up:
  - Phase31을 열 때는 `.aiworkspace/note/finance/registries/LIVE_READINESS_REVIEW_REGISTRY.jsonl` 같은 별도 decision registry와 `Backtest > Live Readiness` 또는 Portfolio Proposal handoff UI를 우선 정의한다

### 2026-05-03 - Phase31 독립 단계 중복 가능성 재판단
- User request:
  - Candidate Review의 `다음 단계 진행 판단`이 이미 사용자가 해당 포트폴리오에 대한 기록을 남기는 용도처럼 보이는데, Phase31이 굳이 필요한지 재질문함
- Interpreted goal:
  - 기존 Candidate Review / Portfolio Proposal 흐름과 새 Phase31이 실제로 다른 일을 하는지, 아니면 기록 UI를 중복해서 만드는 위험이 있는지 확인해야 함
- Analysis result:
  - 사용자의 판단이 맞다. 현재 Candidate Review는 Pre-Live 운영 기록과 Portfolio Proposal 이동 판단을 이미 제공한다
  - 현재 Portfolio Proposal도 단일 후보 Live Readiness 직행 평가와 다중 후보 Live Readiness 진입 평가를 이미 제공한다
  - 따라서 Phase31을 단순히 `다음 단계 판단 사유를 한 번 더 저장하는 단계`로 만들면 중복이다
  - Phase31이 필요하다면 별도 수동 기록 화면이 아니라, 이후 risk / robustness / paper tracking이 같은 후보를 추적할 수 있도록 `Live Readiness intake`, `case id`, `evidence freeze`를 얇게 정의하는 정도여야 한다
- Follow-up:
  - 다음 구현 계획은 독립 `Live Readiness Decision Record` phase보다 `Portfolio Risk & Live Readiness Validation` phase로 재정의하는 편이 더 합리적이다
  - 단일 후보는 기존 `LIVE_READINESS_DIRECT_READY` 경로를 입력으로 바로 다음 검증 phase에 넘기는 방식이 자연스럽다

### 2026-05-03 - Phase31~35 최종 실전 포트폴리오 선정 로드맵 확정과 Phase31 준비
- User request:
  - Phase31~35를 최종 실전투자 포트폴리오 선정 흐름으로 다시 구성하고, Phase31 개발 준비를 진행하라고 승인함
- Interpreted goal:
  - Phase31을 기존 Candidate Review / Portfolio Proposal 판단과 중복되지 않는 다음 검증 phase로 열고, 이후 Phase32~35의 역할을 최종 선정 흐름에 맞게 정렬해야 함
- Analysis result:
  - Phase31은 `Portfolio Risk And Live Readiness Validation`으로 연다
  - Phase31은 새 approval registry나 decision note를 먼저 만드는 단계가 아니라, current candidate / Pre-Live / Portfolio Proposal을 읽는 read-only validation pack으로 시작한다
  - Phase32~35는 각각 robustness / stress validation, paper portfolio tracking ledger, final selection decision pack, post-selection operating guide로 이어진다
  - 사용자-facing Guide 단계는 phase 수만큼 잘게 쪼개지 않고, 최종적으로 Portfolio Risk / Robustness+Paper Tracking / Final Selection 정도의 큰 흐름으로 유지하는 것이 맞다
- Follow-up:
  - Phase31 문서 bundle을 `.aiworkspace/note/finance/phases/phase31/` 아래에 생성했다
  - 첫 작업 단위는 `Portfolio Risk Input And Validation Contract`로 잡았다
  - Phase30은 아직 manual QA pending이므로 closeout 상태는 변경하지 않는다

### 2026-05-03 - Phase31 Validation Pack 구현 완료와 QA handoff
- User request:
  - Phase31 TODO에 있는 내용을 모두 개발하고, 전체 개발이 끝나면 checklist 기준으로 테스트할 수 있게 지시해 달라고 요청함
- Interpreted goal:
  - Phase31을 새 수동 판단 기록이나 approval registry가 아니라, 기존 current candidate / Pre-Live / Portfolio Proposal을 읽는 read-only risk validation surface로 구현해야 함
- Analysis result:
  - `Backtest > Portfolio Proposal`에 Validation Pack을 추가했다
  - 단일 후보 direct path, 작성 중 proposal draft, 저장 proposal 모두 같은 validation input / result schema로 읽는다
  - Validation Pack은 route, score, hard blockers, paper tracking gaps, review gaps, component risk table, Phase32 handoff summary를 보여준다
  - 경계는 유지한다: live approval, 주문 지시, 자동 optimizer, 신규 approval registry가 아니다
- Follow-up:
  - Phase31은 `implementation_complete / manual_qa_pending` 상태다
  - 사용자 QA는 `.aiworkspace/note/finance/phases/phase31/PHASE31_TEST_CHECKLIST.md` 기준으로 진행한다
  - Phase32는 Phase31 `handoff_summary`를 robustness / stress validation 입력 기준으로 삼아 설계한다

### 2026-05-03 - Phase31 Proposal Role / PROPOSAL_BLOCKED QA clarification
- User request:
  - GTAA와 Quality 후보 2개를 섞으면 `PROPOSAL_BLOCKED`와 `Portfolio Construction, Blocking Scope`가 뜨는 것이 정상인지 확인 요청
  - Proposal Role 옵션의 의미와 `core_anchor`를 `return_driver`로 바꿨을 때 blocker가 늘어나는 이유를 설명해 달라고 요청
  - Validation Pack이 proposal 저장이나 live approval을 자동 수행하지 않는지 확인하라는 checklist 문구가 모호하다고 지적함
- Interpreted goal:
  - 기능 로직은 정상이어도 사용자가 무엇을 고쳐야 하는지 알 수 있게 UI와 checklist 설명을 보강해야 함
- Analysis result:
  - `PROPOSAL_BLOCKED`는 target weight 합계가 100%가 아니거나 active component에 `core_anchor`가 없으면 정상적으로 뜨는 route다
  - `core_anchor`는 포트폴리오의 중심 후보이고, `return_driver`는 수익 기여 후보라서 중심 후보를 대체하지 않는다
  - 기존 `Blocking Scope` 표시는 비중 합계 문제를 중복으로 보여줘 원인 파악이 어려웠다
- Follow-up:
  - UI에 Proposal Role / Target Weight 사용법 expander와 actionable blocker guidance를 추가했다
  - checklist에는 Validation Pack을 펼쳐도 save가 자동 실행되지 않고 `Open Live Readiness`가 비활성 상태로 남는지 확인하라고 구체화했다

### 2026-05-03 - Phase31 Save Portfolio Proposal Draft 반응 없음 QA 확인
- User request:
  - `GTAA Clean-6 AOR Top-1 (3M/12M, i2)`와 `Quality Coverage 100 Top-10 AOR MA250 paper-only candidate`를 선택한 뒤 `Save Portfolio Proposal Draft`를 눌러도 반응이 없어 보인다고 보고함
- Interpreted goal:
  - 실제 저장 실패인지, 저장은 되지만 UI feedback이 사라지는 문제인지 확인해야 함
- Analysis result:
  - proposal row는 `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append되고 있었다
  - 문제는 `st.success()` 직후 `st.rerun()`이 실행되어 성공 메시지가 보이지 않는 UX였다
  - 같은 Proposal ID로 반복 클릭하면 중복 row가 쌓일 수 있는 보완점도 확인했다
- Follow-up:
  - 저장 성공 메시지를 session state에 담아 rerun 이후에도 표시되게 했다
  - 저장 후 다음 proposal id는 새 기본값으로 바뀌게 했다
  - 이미 존재하는 Proposal ID는 저장 blocker로 막고, ID 변경 안내를 표시한다

### 2026-05-03 - Phase31 저장된 Proposal UX 위치 재정리
- User request:
  - `보조도구: Saved Proposals / Feedback`에 저장한 draft가 보이지만, 단일 후보 direct path 아래에도 표시되어 UX가 어색하다고 지적함
  - 단일 후보는 저장 없이 다음 단계로 진행하고, 포트폴리오 후보군 작성 흐름에서만 저장 버튼과 저장된 proposal 목록이 자연스럽게 보이도록 개편 요청
- Interpreted goal:
  - 단일 후보 direct path와 다중 후보 proposal construction path를 UI에서 더 분명히 분리해야 함
- Analysis result:
  - 단일 후보에는 이미 `4. Portfolio Risk / Validation Pack`이 있으므로 저장된 proposal feedback을 아래에 붙이면 저장하지 않는 direct path의 의미가 흐려진다
  - 저장된 proposal 목록은 `Save Portfolio Proposal Draft`와 같은 다중 후보 작성 흐름 안에서 보여야 한다
- Follow-up:
  - saved proposal validation / monitoring / feedback section을 단일 후보 path에서 제거했다
  - 다중 후보 proposal draft path 안에 `4. 저장된 Portfolio Proposal 확인` section으로 이동했다
  - save success copy도 새 section을 가리키게 바꿨다

### 2026-05-03 - Phase31 manual QA closeout
- User request:
  - Phase31을 마무리하라고 승인함
- Interpreted goal:
  - Phase31 checklist QA 완료 신호를 반영하고, roadmap / index / phase closeout 문서가 모두 같은 상태를 말하게 정리해야 함
- Analysis result:
  - Phase31은 `Portfolio Risk And Live Readiness Validation`을 read-only validation pack으로 구현했고, live approval / 주문 지시 / 신규 approval registry는 만들지 않았다
  - 사용자 QA 완료 신호에 따라 Phase31은 `complete / manual_qa_completed`로 닫는다
  - Phase30은 별도 phase이므로 계속 `implementation_complete / manual_qa_pending`으로 남긴다
- Follow-up:
  - Phase31 checklist, TODO, completion summary, next phase preparation, roadmap, doc index, README, comprehensive analysis, work log를 closeout 상태로 동기화했다
  - 다음 major phase는 사용자 승인 후 Phase32 `Robustness And Stress Validation Pack`으로 열 수 있다

### 2026-05-03 - finance-doc-sync skill 운영 방식 검토
- User request:
  - 현재 세션에서 finance-doc-sync만 자주 호출되는 것이 효율적인지, 스킬을 개편하거나 쪼개는 것이 나은지 검토 요청
- Interpreted goal:
  - finance-doc-sync를 구현용 메인 스킬로 계속 쓰는 것이 맞는지 판단하고, 더 효율적인 finance 개발 스킬 구조를 제안해야 함
- Analysis result:
  - finance-doc-sync는 문서 동기화 / phase QA / closeout / durable analysis 기록을 위한 meta skill로는 유효하다
  - 최근 Phase31 후반 작업은 대부분 QA checklist, 라벨, roadmap/index closeout이어서 finance-doc-sync 호출이 자연스러웠다
  - 다만 Backtest UI 구현, registry/runtime 작업, phase 운영, portfolio validation 개발까지 모두 finance-doc-sync 하나로 처리하면 스킬이 너무 넓어져 context 사용과 작업 판단이 둔해질 수 있다
- Follow-up:
  - finance-doc-sync는 좁게 유지하고, Phase32 전에 `finance-backtest-web-workflow`와 `finance-phase-management` 계열 스킬을 분리하는 것이 효율적이다
  - 기존 `finance-db-pipeline`, `finance-factor-pipeline`, `finance-strategy-implementation`은 그대로 domain implementation skill로 사용하고, finance-doc-sync는 마무리 동기화 skill로 두는 방향이 합리적이다
  - 사용자가 승인해 local Codex skill `finance-backtest-web-workflow`, `finance-phase-management`를 생성했고, `finance-doc-sync` 설명은 final sync 중심으로 좁혔다

### 2026-05-03 - Phase32 Robustness / Stress Validation Pack 시작
- User request:
  - Phase31이 마무리되었으니 Phase32를 진행해 달라고 요청함
- Interpreted goal:
  - 최종 실전 포트폴리오 선정으로 바로 뛰지 않고, Phase31 Validation Pack 이후 후보 / proposal이 robustness 검증을 실행할 입력을 갖고 있는지 먼저 확인해야 함
- Analysis result:
  - Phase32는 `Robustness And Stress Validation Pack`으로 열었다
  - 첫 작업은 실제 stress sweep engine이 아니라 `Robustness / Stress Validation Preview`다
  - 단일 후보, 작성 중 proposal, 저장 proposal에서 period / contract / benchmark / CAGR / MDD / compare evidence를 읽어 `READY_FOR_STRESS_SWEEP`, `NEEDS_ROBUSTNESS_INPUT_REVIEW`, `BLOCKED_FOR_ROBUSTNESS`로 나눈다
  - suggested sweep은 다음에 실행할 검증 질문이며, 현재 preview가 기간 분할 backtest나 parameter sweep을 이미 수행했다는 뜻은 아니다
- Follow-up:
  - Phase32는 `active / not_ready_for_qa` 상태로 시작했다
  - 다음 작업은 stress / sensitivity result contract 정의와 실제 summary surface 확장이다
  - Phase30은 계속 `implementation_complete / manual_qa_pending` 상태로 별도 유지한다

### 2026-05-03 - Phase32 구현 완료와 QA handoff
- User request:
  - Phase32의 2번째부터 4번째 작업까지 순서대로 진행하고, checklist 단계가 되면 알려 달라고 요청함
- Interpreted goal:
  - Phase32를 실제 승인 단계가 아니라 robustness / stress summary와 Phase33 paper ledger 준비 상태를 읽는 검증 pack으로 완성해야 함
- Analysis result:
  - `phase32_stress_summary_v1` result contract를 정의했다
  - `Stress / Sensitivity Summary` table은 period split, recent window, benchmark sensitivity, parameter sensitivity, weight sensitivity, leave-one-out scenario를 같은 row 언어로 보여준다
  - 현재 `Result Status = NOT_RUN`은 실제 stress runner가 아직 실행되지 않았다는 의미다
  - `Phase 33 Handoff`는 `READY_FOR_PAPER_LEDGER_PREP`, `NEEDS_STRESS_INPUT_REVIEW`, `BLOCKED_FOR_PAPER_LEDGER`로 paper ledger 준비 상태를 구분한다
- Follow-up:
  - Phase32는 `implementation_complete / manual_qa_pending` 상태가 되었다
  - 사용자는 `.aiworkspace/note/finance/phases/phase32/PHASE32_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다
  - QA 완료 후 Phase33 `Paper Portfolio Tracking Ledger`를 열 수 있다

### 2026-05-03 - Phase32 manual QA closeout
- User request:
  - Phase32 checklist 완료를 알림
- Interpreted goal:
  - Phase32 manual QA 완료 신호를 반영하고, phase status와 closeout 문서가 모두 같은 상태를 말하게 정리해야 함
- Analysis result:
  - Phase32는 `Robustness And Stress Validation Pack`을 read-only validation pack으로 구현했다
  - 사용자 QA 완료에 따라 Phase32는 `complete / manual_qa_completed`로 닫는다
  - 이 closeout은 Phase33을 자동으로 여는 것이 아니며, 다음 phase는 사용자 승인 후 시작한다
- Follow-up:
  - Phase32 checklist, TODO, completion summary, next phase preparation, roadmap, doc index, comprehensive analysis, work log를 closeout 상태로 동기화했다
  - Phase33 후보 방향은 `Paper Portfolio Tracking Ledger`다
### 2026-05-03 - Phase34 Final Selection Decision 구현 완료
- User request:
  - Phase34 TODO의 첫 번째 작업부터 네 번째 작업까지 모두 완료하고 checklist 확인 단계까지 진행해 달라고 요청함
- Interpreted goal:
  - Phase33 paper ledger를 바로 주문이나 승인으로 연결하지 않고, 최종 실전 후보 선정 / 보류 / 거절 / 재검토 판단을 별도 append-only decision record로 남겨야 함
- Analysis result:
  - Paper Ledger는 관찰 대상 등록이고, Final Selection Decision은 그 관찰 기록을 바탕으로 한 사람의 최종 판단 기록이다
  - Final Decision은 `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 별도로 저장하며 current candidate, Pre-Live, Portfolio Proposal, Paper Ledger registry를 덮어쓰지 않는다
  - `SELECT_FOR_PRACTICAL_PORTFOLIO`도 live approval이나 broker order가 아니라 Phase35 운영 가이드 입력이다
- Follow-up:
  - Phase34는 `implementation_complete / manual_qa_pending` 상태가 됐다
  - 사용자는 `.aiworkspace/note/finance/phases/phase34/PHASE34_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다
  - QA 완료 후 Phase35 `Post-Selection Operating Guide`를 시작하는 것이 자연스럽다

### 2026-05-03 - Phase34 반복 저장 UX와 Final Review 탭 분리 판단
- User request:
  - `Save Portfolio Proposal Draft`, `Save Paper Tracking Ledger`, `Save Final Selection Decision`이 반복되는 패턴이 설득력 있는지 문제 제기
  - 특히 Paper Ledger와 Final Decision을 꼭 별도로 저장해야 하는지, Portfolio Proposal 탭 안에서 계속 확장하는 것이 맞는지 검토 요청
- Interpreted goal:
  - 최종 투자 포트폴리오 선정 흐름이 사용자가 이해할 수 있는 큰 단계로 보이도록 제품 경계를 다시 잡아야 함
- Analysis result:
  - Portfolio Proposal은 후보 묶음의 목적 / 역할 / 비중을 정하는 초안 작성 단계로 유지하는 것이 맞다
  - 최종 validation, robustness, paper observation, 선정 / 보류 / 거절 / 재검토 판단은 별도 Final Review 탭으로 빼는 것이 더 자연스럽다
  - Paper Ledger는 기존 Phase33 QA와 운영 호환성을 위해 남기되, main flow에서 별도 저장 버튼으로 강제하지 않는다
  - paper observation 기준은 final review record 안에 포함하고, 사용자-facing 최종 저장 액션은 `최종 검토 결과 기록` 하나로 정리한다
- Follow-up:
  - `Backtest > Final Review` panel과 helper를 추가했다
  - Portfolio Proposal active flow에서 Paper Ledger / Final Selection 저장 surface를 제거했다
  - Phase34 checklist와 durable docs를 Final Review 기준으로 개편했다

### 2026-05-04 - Phase34 closeout and Phase35 start preparation
- User request:
  - Phase34 checklist 완료를 알리고, Phase34를 마무리한 뒤 Phase35 시작 준비를 요청함
- Interpreted goal:
  - Phase34 manual QA 완료 신호를 반영하고, 다음 phase를 구현이 아니라 시작 가능한 문서 / 로드맵 상태로 열어야 함
- Analysis result:
  - Phase34는 `complete / manual_qa_completed` 상태로 닫는다
  - Phase35는 `Post-Selection Operating Guide`로 시작한다
  - Phase35는 Phase34에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장된 final review record를 읽어 리밸런싱 / 중단 / 축소 / 재검토 운영 기준을 만드는 단계다
  - 이 단계도 live approval, broker order, 자동매매, optimizer가 아니다
- Follow-up:
  - Phase35 문서 bundle을 `.aiworkspace/note/finance/phases/phase35/` 아래에 만들었다
  - Phase35는 `active / not_ready_for_qa` 상태이며, 첫 작업은 operating policy contract 정리다

### 2026-05-04 - Phase35 Post-Selection Operating Guide 구현 완료
- User request:
  - Phase35의 첫 번째 작업부터 마지막 작업까지 순서대로 진행하고, checklist 확인 단계가 되면 알려 달라고 요청함
- Interpreted goal:
  - 최종 선정 후보를 바로 주문이나 승인으로 연결하지 않고, 사용자가 따라갈 리밸런싱 / 축소 / 중단 / 재검토 운영 기준을 UI와 append-only 기록으로 만들어야 함
- Analysis result:
  - Phase35 입력은 `SELECT_FOR_PRACTICAL_PORTFOLIO`와 `READY_FOR_POST_SELECTION_OPERATING_GUIDE`를 만족하는 final review record로 제한한다
  - 운영 가이드는 final decision 원본을 덮어쓰지 않고 `.aiworkspace/note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`에 별도 append-only row로 남긴다
  - `Backtest > Post-Selection Guide`에서 selected final decision, target components, operating readiness, operating policy, saved guide review를 확인한다
  - `운영 가이드 기록`도 live approval, broker order, 자동매매가 아니다
- Follow-up:
  - Phase35는 `implementation_complete / manual_qa_pending` 상태가 됐다
  - 사용자는 `.aiworkspace/note/finance/phases/phase35/PHASE35_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다

### 2026-05-04 - Phase35 반복 저장 UX 보정 판단
- User request:
  - Phase35에도 또 저장 흐름이 생긴 이유를 문제 제기하고, Final Review와 Post-Selection Guide의 차이 및 저장 필요성을 재검토해 달라고 요청함
- Interpreted goal:
  - 최종 투자 포트폴리오 선정 흐름에서 사용자가 이해하기 어려운 반복 저장 패턴을 제거하고, Final Review와 Phase35의 역할을 더 선명하게 해야 함
- Analysis result:
  - Phase35의 별도 operating guide registry는 장기 추적성 측면에서는 설명 가능하지만, 현재 제품 목표인 "최종 투자 가능 후보 선정 + 운영 전 지침 확인"에는 과한 UX로 판단했다
  - Final Review의 final selection decision을 최종 판단 원본으로 두고, Post-Selection Guide는 그 기록을 읽는 no-extra-save preview surface로 보정하는 것이 더 적절하다
  - 최종 판단은 `투자 가능 후보`, `투자하면 안 됨`, `내용 부족 / 관찰 필요`, `재검토 필요`로 사용자가 바로 이해할 수 있어야 한다
- Follow-up:
  - `Backtest > Post-Selection Guide`에서 `운영 가이드 기록` save flow와 saved guide review를 제거했다
  - `app/web/runtime/post_selection_guides.py`를 삭제했다
  - Phase35 checklist와 durable docs를 no-extra-save final investment guide 기준으로 개편했다

### 2026-05-04 - Phase35 후속 가이드 제거와 Final Review 종료 흐름 확정
- User request:
  - `Portfolio Proposal -> Final Review -> 최종 판단 완료`로 가는 것이 더 좋겠고, 별도 Post-Selection Guide는 현재 상황에서 과하다고 판단해 수정 요청
- Interpreted goal:
  - 최종 투자 포트폴리오 선정 흐름을 더 단순하고 사용자가 이해하기 쉬운 active workflow로 정리해야 함
- Analysis result:
  - Final Review가 이미 validation, robustness, paper observation, operator judgment, final decision 저장 / review를 담당하므로 별도 후속 guide panel은 현재 제품 단계에서 중복이다
  - 최종 판단 원본은 `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다
  - 사용자가 마지막에 확인해야 할 것은 투자 가능 후보 / 내용 부족 / 투자하면 안 됨 / 재검토 필요와 live approval / order disabled 경계다
- Follow-up:
  - Backtest workflow에서 별도 후속 guide panel을 제거했다
  - Final Review saved decision review에 투자 가능성 label과 Final Review Status 해석을 보강했다
  - Phase35 문서와 checklist를 `Portfolio Proposal -> Final Review -> 최종 판단 완료` 기준으로 개편했다

### 2026-05-04 - Final Review 저장 결과의 legacy Phase35 문구 표시 문제
- User request:
  - `기록된 최종검토 결과 확인`의 판정에 `Phase 35 운영 가이드 작성 가능`과 운영 가이드 정리 next action이 보여 현재 흐름과 맞지 않는다고 지적함
- Interpreted goal:
  - 기존 저장 row에 남아 있는 legacy handoff 문구가 Final Review UI에서 현재 제품 방향과 충돌하지 않게 해야 함
- Analysis result:
  - 문제는 최종 검토 단계 자체가 아니라 과거 Phase35 설계 때 저장된 `phase35_handoff` 문구를 UI가 그대로 표시한 것이다
  - 현재 기준에서는 Final Review가 최종 판단 완료 지점이며, selected route는 `최종 판단 완료: 실전 후보로 선정됨`으로 읽혀야 한다
- Follow-up:
  - saved final decision display에 현재 Final Review end-state 문구 변환 layer를 추가했다
  - raw JSON은 호환성 때문에 유지하지만 route panel은 legacy Phase35 운영 가이드 문구를 보여주지 않도록 했다

### 2026-05-04 - Reference Guides 최종 10단계 흐름 정렬
- User request:
  - 현재 단계 기준으로 Guides를 최종 10단계 흐름, 핵심 개념 가이드, 단계 통과 기준, 문서 / 파일 안내까지 업데이트해 달라고 요청함
- Interpreted goal:
  - 사용자가 `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 따라가면 마지막에 실전 후보 선정 여부를 확인할 수 있어야 하며, Phase35에서 제거한 Post-Selection Guide나 별도 Live Readiness / Final Approval 흐름이 다시 살아나 보이면 안 됨
- Analysis result:
  - 현재 사용자-facing end state는 `Portfolio Proposal -> Final Review -> 최종 판단 완료`다
  - Guides 실행 흐름은 1~10단계로 정리한다: 데이터 최신화, Single Strategy, Real-Money, Hold 해결, Compare, Candidate Packaging, Portfolio Proposal, Final Review 검증, 최종 판단 기록, 기록된 최종 검토 결과 확인
  - `SELECT_FOR_PRACTICAL_PORTFOLIO`는 실전 후보로 선정되었다는 최종 확인 신호지만, live approval / broker order / 자동매매 지시는 아니다
  - Portfolio Proposal 내부에 남아 있는 `Live Readiness` route label은 Phase31 legacy naming으로 보고, 현재 가이드에서는 Final Review 입력 준비로 해석한다
- Follow-up:
  - `Reference > Guides`의 핵심 개념, 1~10 단계 실행 흐름, 단계 통과 기준, 문서 / 파일 안내를 갱신했다
  - `BACKTEST_UI_FLOW.md`, historical walkthrough note, `FINANCE_DOC_INDEX.md`를 같은 기준으로 동기화했다

### 2026-05-04 - Guides JSONL 저장소 설명 UX 개선
- User request:
  - `Reference > Guides > 주요 파일 경로`에서 JSONL 파일들이 어떤 데이터를 말하는지 시각적으로 더 잘 설명되도록 UX/UI 개선을 요청함
- Interpreted goal:
  - 사용자가 경로 목록만 보고 registry / run history / saved setup의 차이를 추측하지 않게 해야 함
- Analysis result:
  - JSONL은 모두 같은 확장자지만 역할이 다르다: 후보 검토 기록, current candidate 정의, Pre-Live 운영 상태, portfolio proposal draft, paper ledger 호환 기록, final selection decision, run history, saved portfolio setup으로 나뉜다
  - 최종 실전 후보 선정 여부는 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에서 확인해야 하며, run history나 saved portfolio는 재현 / 재사용 보조 기록이다
- Follow-up:
  - Guides의 `주요 파일 경로`를 탭 기반 JSONL 저장소 지도로 바꾸고, 각 파일의 데이터 의미 / 생성 화면 / 읽는 법을 표와 요약 카드로 설명했다

### 2026-05-04 - 반복되는 operator judgment 입력 구조 재검토
- User request:
  - Candidate Review, Portfolio Proposal, Final Review마다 Operator Final Status / Operator Decision / 최종 판단을 사람이 입력하고 저장하는 구조가 왜 필요한지, 과한 UX는 아닌지 재검토 요청
- Interpreted goal:
  - 백테스트와 검증 결과가 자동으로 최종 투자 가능 여부를 말해 주는 프로그램을 원했는데, 사람이 여러 번 판단 사유를 입력하는 구조가 사용 부담으로 보이므로 제품 방향이 맞는지 확인해야 함
- Analysis result:
  - 판단 기록 자체는 필요하다. 백테스트 모델은 검증 신호를 줄 수 있지만, 실제 후보 선정은 목적, 제약, capital scope, 관찰 조건, 사용 범위 같은 사람의 운영 판단을 포함하기 때문이다.
  - 다만 현재 UI처럼 세 단계가 모두 동등한 "결정"처럼 보이면 과하다.
  - 올바른 역할 분리는 Candidate Review = 후보를 관찰 대상으로 남길지, Portfolio Proposal = 여러 후보를 어떤 역할/비중으로 묶을지, Final Review = 실전 후보로 최종 선정할지다.
  - 장기적으로는 중간 단계의 메모 입력을 "자동 추천 + 기본값 + 필요한 경우만 수정"으로 낮추고, 최종 판단만 진짜 사람이 명시적으로 기록하는 UX가 더 적절하다.
- Follow-up:
  - 다음 UX 개선 후보는 Candidate Review / Portfolio Proposal의 operator field를 advanced / optional로 낮추고, Final Review만 `최종 판단`의 주 decision surface로 강조하는 방향이다.

### 2026-05-04 - 중간 operator judgment UX 경량화 구현
- User request:
  - 반복 판단 입력 구조는 개선하는 것이 맞다는 판단에 동의하고, 그 방향으로 진행 요청
- Interpreted goal:
  - 저장 계약은 유지하되 Candidate Review / Portfolio Proposal이 최종 결정처럼 보이지 않게 하고, Final Review만 최종 판단 지점으로 강조해야 함
- Analysis result:
  - Candidate Review의 Pre-Live status는 후보 관찰 상태 확인이지 최종 투자 판단이 아니다
  - Portfolio Proposal의 decision은 proposal draft 저장 상태 확인이지 최종 선정 판단이 아니다
  - Final Review의 `최종 판단`만 실전 후보 선정 / 보류 / 거절 / 재검토를 명시하는 주 decision surface로 유지한다
- Follow-up:
  - Candidate Review와 Portfolio Proposal의 operator memo 입력을 기본값이 있는 접힘 영역으로 낮췄다
  - Final Review에는 이 구간이 실제 최종 판단이라는 안내를 추가했고, 저장 ID / 운영 전 조건 / 다음 행동은 고급 접힘 영역으로 이동했다

### 2026-05-04 - 완성형 퀀트 운용 플랫폼으로 가기 위한 기능 gap
- User request:
  - 현재 최소 후보 선정 workflow 이후, 완성형 퀀트 운용 플랫폼을 구현하려면 어떤 기능이 더 필요한지 질문함
- Interpreted goal:
  - 지금의 `전략 실행 -> 후보 선정 -> Final Review` 흐름과 실제 운용 플랫폼 사이의 남은 제품 gap을 정리해야 함
- Analysis result:
  - 현재 시스템은 실전 후보 포트폴리오를 찾는 최소 workflow까지 도달했다
  - 완성형 플랫폼이 되려면 후보 선정 이후의 운영 영역이 필요하다: live/paper portfolio monitoring, rebalance engine, execution/order workflow, risk/limit/alert framework, performance attribution, model governance/versioning, data quality automation, reporting
  - SR 11-7류 model risk guidance도 model development / validation / governance와 ongoing monitoring을 함께 본다. 즉 후보 선정만으로 끝나지 않고, 사용 중 성능과 환경 변화 추적이 필요하다
- Follow-up:
  - 다음 주요 제품 방향 후보는 `Final-selected portfolio monitoring & rebalance operations`가 가장 자연스럽다
  - 사용자가 나중에 다시 확인할 수 있도록 `.aiworkspace/note/finance/operations/FINAL_SELECTED_PORTFOLIO_OPERATIONS_DASHBOARD_GAP_20260504.md`에 요약 문서를 생성했다
  - 사용자 판단상 1순위 기능은 `최종 선정 포트폴리오 운영 대시보드`로 기록했다

### 2026-05-05 - Compare & Portfolio Builder 저장 Mix UX 재구성
- User request:
  - GTAA 70 + Equal Weight 30 mix를 확인하고 저장하려는데, Weighted Portfolio Builder / Result / Save 영역과 저장된 파일 관리 위치가 한 화면에서 잘 드러나지 않는다고 지적함
- Interpreted goal:
  - 새 전략 비교와 저장된 mix 다시 열기를 분리해, 사용자가 `비교 -> 비중 조합 -> 결과 확인 -> 저장` 흐름과 `저장된 mix load / replay` 흐름을 혼동하지 않게 해야 함
- Analysis result:
  - saved portfolio row는 후보 registry가 아니라 재사용 가능한 weighted portfolio setup이다
  - 따라서 저장 위치는 `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl` 유지가 적절하며, UI에서 `Portfolio Mix`와 저장 위치를 명확히 보여주는 편이 registry semantics를 흐리지 않는다
  - `전략 비교` 탭은 새 mix 생성에 집중하고, `저장 Mix 다시 열기` 탭은 기존 mix load / replay / delete에 집중하는 구조가 가장 자연스럽다
- Follow-up:
  - Compare workspace를 내부 탭 구조로 나누고, GTAA / Equal Weight quick allocation과 저장 CTA를 result 확인 바로 아래에 배치했다

### 2026-05-05 - Equal Weight Real-Money 판정 누락 해소
- User request:
  - Equal Weight 후보에서 `5단계 Compare에서 먼저 추가 확인` 안내가 뜨는 이유를 묻고, 다른 전략처럼 Real-Money 판정을 추가해 달라고 요청함
- Interpreted goal:
  - Equal Weight도 static ETF basket baseline에 머물지 않고, Candidate Review / Compare 진입 판단이 읽을 수 있는 promotion / shortlist / deployment 메타를 생성해야 함
- Analysis result:
  - 기존 Equal Weight runtime은 성과표와 기본 contract만 남겨 Real-Money gate가 비어 있었고, Compare readiness는 이를 blocker로 해석했다
  - GTAA 등 ETF 전략군과 같은 first-pass 수준으로 비용, 벤치마크, ETF 운용 가능성, 가격 최신성, promotion / deployment metadata를 붙이면 UI가 같은 방식으로 pass / hold를 판단할 수 있다
  - 다만 ETF asset profile coverage가 부족하면 Equal Weight도 명시적으로 `hold/blocked`가 될 수 있으며, 이것은 누락이 아니라 운용 가능성 데이터 경고다
- Follow-up:
  - Equal Weight Single / Compare 입력, runtime hardening, saved Portfolio Mix override, Candidate Library replay payload에 Real-Money 필드를 연결했다

### 2026-05-06 - 복구된 registries 기준 후보 / 포트폴리오 참조 검토
- User request:
  - `.aiworkspace/note/finance/registries/` 폴더가 없어졌다가 복구되었으므로, 복구된 registry 내용을 기준으로 현재 후보와 포트폴리오 해석을 다시 검토해 달라고 요청함
- Interpreted goal:
  - 복구된 JSONL registry가 필수 필드를 갖추고 있는지, Current Candidate / Pre-Live / Candidate Review Note가 서로 연결되는지, saved portfolio가 registry id를 정상 참조하는지 확인해야 함
- Analysis result:
  - `CURRENT_CANDIDATE_REGISTRY.jsonl` 5개 row와 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 5개 row는 repo helper validation을 통과했고, 각 Pre-Live row는 current candidate row와 1:1로 연결되어 있다
  - `CANDIDATE_REVIEW_NOTES.jsonl` 5개 row도 current candidate의 `source_review_note_id`와 모두 연결된다
  - 다만 `SAVED_PORTFOLIOS.jsonl`의 annual strict equal-third baseline은 과거 registry id인 `value_current_anchor_top14_psr`, `quality_current_anchor_top12_lqd`, `quality_value_current_anchor_top10_por`를 참조하지만, 현재 복구된 current registry에는 이 3개 row가 없다
  - 현재 복구된 registry는 최근 GTAA 3개, Q+V MDD20 1개, Quality AOR MA250 1개 후보 중심이며, 과거 annual strict baseline candidate registry snapshot은 복구되지 않은 상태로 보인다
  - `PORTFOLIO_PROPOSAL_REGISTRY.jsonl`, `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`, `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`도 현재 registry 폴더에는 없다
- Follow-up:
  - 현재 candidate / pre-live review는 사용 가능하지만, saved annual strict baseline을 Candidate Library / Portfolio Proposal에서 registry-linked bundle로 다시 쓰려면 과거 annual strict candidate row 3개를 복원하거나, saved portfolio의 embedded compare context 기반 replay로만 해석해야 한다

### 2026-05-06 - master 병합 후 registries 기준 백테스트 후보 재분석
- User request:
  - `master` 병합으로 registry JSONL이 채워졌으니, 병합된 registries 기준으로 백테스트 후보 데이터를 다시 분석해 달라고 요청함
- Interpreted goal:
  - Current Candidate, Pre-Live, Portfolio Proposal, Paper Ledger, Final Decision registry를 함께 읽어 실제 후보군, 유효한 Equal Weight 후보, 최종 선택된 후보, 남은 주의점을 구분해야 함
- Analysis result:
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`은 10개 row validation을 통과했지만, `equal_weight_current_candidate_dividend_growth_4_schd_tdiv`는 active row와 inactive row가 함께 있는 append-only 중복 기록이다
  - 현재 유효 후보군은 GTAA 4개, Equal Weight 2개, Quality 1개, Quality + Value 1개로 읽는 것이 적절하다. 배당 ETF Equal Weight 후보는 `hold / blocked`라 reference로만 본다
  - 최종 선택 / paper ledger는 `gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150` 단일 후보를 가리킨다. 핵심 수치는 `CAGR 15.22%`, `MDD -8.88%`, `Sharpe 1.96`, `AOR` benchmark, `paper_only`이다
  - 새로 들어온 Equal Weight 후보 중 `QQQ/SOXX/XLE/IAU`는 `CAGR 19.96%`, `MDD -19.71%`, `real_money_candidate / paper_probation / paper_only`이고, `IAU/QQQ/SOXX/VIG/XLE`는 `CAGR 18.31%`, `MDD -19.27%`로 더 방어적인 balanced 대안이다
  - `PORTFOLIO_PROPOSAL_REGISTRY.jsonl`의 4개 row는 같은 `proposal_20260503_0fb12b`의 반복 저장으로 보이며, 최신 row 기준 GTAA Top-1 50% + Quality AOR MA250 50% proposal draft다. Final Decision과 Paper Ledger는 이 proposal이 아니라 GTAA Top-2 High CAGR 단일 후보로 이어진다
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`의 `decision_id`는 `quality_current...`로 시작하지만 source는 GTAA Top-2 High CAGR 후보다. ID naming은 legacy / 생성 당시 label artifact로 보이고, 실제 source fields를 기준으로 읽어야 한다
- Follow-up:
  - 현재 실전 후보 탐색 해석은 `GTAA Top-2 High CAGR`을 최종 선택된 paper-only 단일 후보로 두고, Equal Weight growth/commodity 후보들은 GTAA와 섞어볼 ETF diversifier / comparison candidate로 유지하는 방향이 가장 자연스럽다

### 2026-05-06 - Phase36 최종 선정 포트폴리오 운영 대시보드 구현 방향
- User request:
  - Phase36에서 `최종 선정 포트폴리오를 위한 대시보드`를 어떻게 만들지 구체화하고, 진행해 달라고 요청함
- Interpreted goal:
  - Final Review 이후에 또 다른 판단 저장 단계를 만들지 않고, 이미 선정된 최종 포트폴리오를 운영자가 다시 찾아볼 수 있는 Operations surface가 필요함
- Analysis result:
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`은 Phase36에서 새로 만드는 파일이 아니라 Final Review가 이미 저장하는 최종 판단 원본이다
  - Phase36 dashboard는 이 파일 중 `SELECT_FOR_PRACTICAL_PORTFOLIO` 또는 `selected_practical_portfolio=true` row만 read-only로 읽는다
  - Backtest workflow는 Final Review에서 끝나야 하므로, 새 화면은 `Backtest` 주 흐름이 아니라 `Operations > Selected Portfolio Dashboard`로 둔다
  - current price / holding 기반 drift 계산과 주문 초안은 Phase36 first pass가 아니라 후속 phase에서 별도 계약을 정한 뒤 다룬다
- Follow-up:
  - `app/web/runtime/final_selected_portfolios.py`, `app/web/final_selected_portfolio_dashboard.py`, `app/web/final_selected_portfolio_dashboard_helpers.py`를 추가했다
  - Phase36 문서 bundle과 roadmap / index / code analysis를 Selected Portfolio Dashboard 기준으로 동기화했다

### 2026-05-06 - Phase36 QA deferred and drift check continuation
- User request:
  - Phase36 checklist 확인은 모든 작업이 마무리된 뒤 진행할 것이므로, 다음 작업을 계속 진행해 달라고 요청함
- Interpreted goal:
  - Phase36 first pass에서 멈추지 않고, 선정 포트폴리오의 target weight와 현재 비중 차이를 읽는 운영 기능까지 이어가야 함
- Analysis result:
  - 실제 계좌 / broker / current price 자동 연결 없이도 Phase36 안에서 구현 가능한 안전한 범위는 `현재 비중 수동 입력 -> target 대비 drift 계산 -> 리밸런싱 검토 필요 여부 표시`다
  - 이 결과는 주문 지시가 아니라 read-only 운영 신호로 둔다
  - DB current price 자동 조회와 account holding 연결은 후속 phase에서 별도 계약을 정해야 한다
- Follow-up:
  - `Current Weight / Drift Check` UI와 `build_selected_portfolio_drift_check` helper를 추가했다
  - Phase36 checklist와 handoff 문서를 manual current weight drift 기준으로 갱신했다

### 2026-05-06 - Phase36 value / holding input contract extension
- User request:
  - Phase36의 다음 단계를 계속 진행해 달라고 요청함
- Interpreted goal:
  - 수동 current weight 입력만으로는 실제 운영 점검에 부족하므로, 평가금액이나 보유 수량과 현재가를 current weight로 바꿔 drift를 볼 수 있어야 함
- Analysis result:
  - 실제 account holding 자동 연결이나 주문 생성은 아직 안전한 범위가 아니다
  - Phase36에서 안전하게 확장할 수 있는 범위는 operator가 current value 또는 shares x price를 입력하고, 선택적으로 DB latest close를 현재가 보조값으로 불러오는 read-only 계약이다
  - DB latest close는 가격 입력 보조일 뿐이고, 최종 drift 판단은 여전히 dashboard에서 저장하지 않는 operator review 신호다
- Follow-up:
  - `build_selected_portfolio_current_weight_inputs`와 `load_latest_selected_portfolio_prices`를 추가했다
  - `Operations > Selected Portfolio Dashboard`의 drift check 입력 모드를 current weight / current value / shares x price로 확장했다
  - Phase36 문서를 account holding 자동 연결 전 단계의 value / holding input contract 기준으로 갱신했다

### 2026-05-06 - Phase36 drift alert preview continuation
- User request:
  - Phase36에 남은 작업이 있다면 QA 전에 계속 진행해 달라고 요청함
- Interpreted goal:
  - drift 숫자와 `REBALANCE_NEEDED` route만 보여주는 것에서 한 단계 더 나아가, 운영자가 어떤 review trigger를 같이 봐야 하는지 읽을 수 있어야 함
- Analysis result:
  - 실제 alert persistence, 자동 알림, stop / re-review workflow 저장은 별도 phase 경계가 필요하다
  - Phase36에서 안전하게 구현할 수 있는 범위는 drift check 결과를 read-only alert preview로 해석하고, Final Review에 저장된 review trigger를 함께 표시하는 것이다
- Follow-up:
  - `build_selected_portfolio_drift_alert_preview` helper와 `Drift Alert / Review Trigger Preview` UI를 추가했다
  - alert preview는 registry 저장, 주문 생성, 자동 리밸런싱을 하지 않는 read-only 운영 해석으로 문서화했다

### 2026-05-06 - Guides 포트폴리오 플로우 맵 필요성
- User request:
  - 1~10단계 guide는 설명이 있지만, 단일 후보 / 여러 후보 / 저장 Mix처럼 포트폴리오 유형에 따라 달라지는 실제 흐름을 리스트만으로 이해하기 어렵다고 지적함
- Interpreted goal:
  - 사용자가 어떤 포트폴리오를 만들고 있는지 먼저 고르고, 그 경로에서 지나가는 화면과 생략되는 단계를 시각적으로 확인할 수 있어야 함
- Analysis result:
  - 선형 단계 목록은 공통 기준 설명에는 적합하지만, `단일 후보 직행`, `여러 후보 proposal 저장`, `saved mix -> Portfolio Proposal`, `blocker 재검토` 같은 분기 ownership을 드러내기 어렵다
  - Guide 상단에 경로 선택형 시각 플로우 맵을 두고, 상세 1~10단계는 그 아래 reference로 유지하는 구조가 가장 작은 UX 개선이다
- Follow-up:
  - `Reference > Guides`에 포트폴리오 플로우 맵을 추가하고, `BACKTEST_UI_FLOW.md`를 해당 Guide 구조에 맞춰 동기화했다

### 2026-05-06 - Guides 제품형 UX 개편 방향
- User request:
  - 포트폴리오 플로우 맵의 내용은 맞지만 시각적으로 실습용 UI처럼 보이며, Guides 전체가 제품형 안내 화면보다 문서 목록처럼 느껴진다고 지적함
- Interpreted goal:
  - 사용자가 문서 목록을 읽기 전에 지금 하려는 포트폴리오 경로와 다음 화면, 멈춤 기준을 제품형 guide 화면에서 먼저 이해해야 함
- Analysis result:
  - Runtime / Build가 최상단에 있는 구조는 운영자 / 개발자에게는 유용하지만 첫 사용자 guide 경험에는 부적절하다
  - `핵심 개념`, `1~10단계`, `단계 통과 기준`, `문서와 파일`을 같은 위계로 나열하면 사용자가 먼저 무엇을 해야 하는지 판단하기 어렵다
  - Streamlit native에서는 `st.graphviz_chart`가 flowchart에 가장 적합하고, 외부 React Flow 계열 component는 더 강하지만 dependency와 state 관리 부담이 커서 1차 개편에는 과하다
- Follow-up:
  - `Reference > Guides`를 hero / route selector / GraphViz flow / Decision Gates / Reference Drawer / System status 구조로 개편했다

### 2026-05-06 - Guides 1~10 단계 복원 방식
- User request:
  - GraphViz flowchart는 이해하기 쉬워졌지만, chart 내용이 빈약하고 기존 1~10 단계 설명이 사라져 현재 위치를 파악하기 아쉽다고 지적함
- Interpreted goal:
  - 제품형 Guide의 간결함은 유지하면서도, 사용자가 단일 후보 / 여러 후보 / 저장 Mix / 막힘 해결 경로에서 전체 1~10 단계 중 어디에 있는지 읽을 수 있어야 함
- Analysis result:
  - flowchart node 안에 긴 설명을 넣으면 시각성이 떨어지므로 chart는 큰 경로 지도 역할만 맡기는 것이 적절하다
  - 1~10 단계는 문서형 긴 목록으로 되돌리기보다 compact timeline으로 복원하고, 선택 경로별로 `필수`, `반복`, `직행`, `선행`, `생략`, `보류` 상태를 다르게 보여주는 것이 가장 자연스럽다
- Follow-up:
  - `Reference > Guides`에 경로별 checkpoint 카드와 1~10 단계 timeline을 추가해 시각적 흐름과 단계 해석을 함께 보강했다

### 2026-05-06 - Guides 경로 라벨과 단계 ownership 정리
- User request:
  - `이 경로의 핵심 단계`, `현재 경로 / 다음 행동 / 주의할 점 / 읽는 기록`, `저장 Mix`, `막힘 해결`의 의미가 애매하고 여러 후보 포트폴리오 경로에서 Candidate Review와 Portfolio Proposal 순서가 충돌해 보인다고 지적함
- Interpreted goal:
  - 선택 버튼이 포트폴리오 유형만이 아니라 현재 진행 상황을 고르는 장치임을 명확히 하고, 전체 1~10 단계와 선택 경로 요약의 위계를 분리해야 함
- Analysis result:
  - `저장 Mix`는 후보가 아니라 Saved Portfolio의 재사용 weight setup이므로 `저장된 비중 조합`이 더 정확하다
  - `막힘 해결`은 포트폴리오 구성 경로가 아니라 hold / blocked / insufficient evidence 상태에서 원인 화면으로 돌아가는 문제 해결 경로이므로 `보류 / 재검토`가 더 정확하다
  - 여러 후보 경로는 Candidate Review에서 후보별 current candidate를 먼저 저장하고, Portfolio Proposal은 이미 저장된 후보를 역할 / 비중으로 묶는 후속 화면으로 설명해야 한다
- Follow-up:
  - Guide 선택지, 1~10 단계 배치, 선택 경로 요약 카드 문구, 여러 후보 묶음 경로 설명을 위 ownership에 맞게 정리했다

### 2026-05-05 - Equal Weight 후보 정리와 배당 포함 후보 재탐색
- User request:
  - hold 상태였던 `Equal Weight Dividend Growth 4 (DGRW/SCHD/TDIV/VIG)`를 Candidate Library에서 제거하고, `Equal Weight Growth/Commodity 4 (QQQ/SOXX/XLE/IAU)`를 10단계 기준으로 검증한 뒤, 배당 ETF가 포함되면서 SPY보다 좋고 MDD 20% 이하인 Equal Weight 후보를 다시 찾아 달라고 요청함
- Interpreted goal:
  - 단순히 성과가 좋은 조합이 아니라 현재 Equal Weight Real-Money gate와 Candidate Library 관점에서 통과 가능한 후보인지 구분해야 함
- Analysis result:
  - Candidate Library 제거는 append-only registry 원칙을 유지하기 위해 기존 row 삭제가 아니라 같은 `registry_id`의 최신 `inactive` tombstone row로 처리하는 것이 맞다
  - `QQQ/SOXX/XLE/IAU`는 처음에는 ETF profile coverage 부족 때문에 `hold/blocked`로 떨어졌지만, AUM / bid / ask metadata를 보강한 뒤에는 CAGR 19.96%, MDD -19.71%, `real_money_candidate / paper_probation / paper_only`로 통과했다
  - 배당 포함 후보 중 가장 깨끗한 신규 후보는 `IAU / QQQ / SOXX / VIG / XLE`, annual rebalance다. CAGR 18.31%, MDD -19.27%이며 SPY CAGR 13.67%, SPY MDD -24.80% 대비 우위가 있고 Real-Money 상태도 paper-only로 정리된다
  - SCHD 포함 후보는 일부 성과 조건을 만족했지만, 현재 rolling validation에서 `hold/blocked` 또는 `watchlist_only`로 남아 바로 10단계 실습 후보로 쓰기에는 VIG 포함 후보보다 약하다
- Follow-up:
  - 신규 VIG 포함 후보를 Candidate Library에 등록할지는 사용자 선택으로 둔다. 이미 등록된 `QQQ/SOXX/XLE/IAU` 후보는 ETF profile 보강 후 runtime 기준으로 다시 사용할 수 있다

### 2026-05-05 - SPY benchmark GTAA 통과 후보 탐색
- User request:
  - 기존 `GTAA Clean-6 AOR Top-2 High CAGR`처럼 AOR를 benchmark로 쓰지 말고, SPY를 formal benchmark로 두었을 때 10단계까지 통과 가능한 GTAA 후보를 찾아 달라고 요청함
- Interpreted goal:
  - 단순히 CAGR/MDD가 좋은 후보가 아니라 `SPY` 기준 Real-Money gate에서 `Promotion`, `Shortlist`, `Deployment`, `Validation`이 모두 실습 가능한 후보를 찾아야 함
- Analysis result:
  - SPY benchmark에서는 기존 clean-6 GTAA가 rolling validation에서 자주 hold로 내려간다. 이유는 방어자산을 섞은 GTAA가 SPY 강세장에서 12개월 상대성과 기준으로 크게 뒤처지는 구간이 생기기 때문이다
  - 병렬 탐색 결과 가장 깨끗한 후보는 `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`, `top=2`, `interval=3`, `1M/6M/12M`, `MA250`, `cash_only`, `Benchmark=SPY`였다
  - Runtime 재검증 기준 `CAGR=18.97%`, `MDD=-18.10%`, `SPY CAGR=13.36%`, `SPY MDD=-15.90%`, `worst rolling excess=-9.84%`, `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`, `Validation=normal`이다
  - 더 높은 CAGR 후보(`SPY / QQQ / SOXX / XLE / XLU / XLV / IEF / IAU`)는 `CAGR=20.86%`, `MDD=-13.04%`였지만 `Deployment=review_required`라 최종 실습 후보로는 덜 깔끔하다
- Follow-up:
  - 후보를 Candidate Library에 등록하려면 Current Candidate Registry append를 별도로 진행한다

### 2026-05-05 - SPY benchmark GTAA 저MDD 후보 재탐색
- User request:
  - SPY benchmark GTAA 후보 중 수익률을 조금 낮추더라도 MDD 15% 이하, CAGR 16~17% 이상, `top=2~4`, `interval<=3`, 10단계 통과가 가능한 후보를 더 깊게 찾아 달라고 요청함
- Interpreted goal:
  - 단순히 MDD가 낮은 후보가 아니라 `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`, `Validation=normal`까지 유지되는 실습 후보를 찾아야 함
- Analysis result:
  - 가장 좋은 후보는 기존 style universe `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`를 유지하되, `top=3`, `interval=3`, `1M/6M`, `MA250`, `cash_only`, `Benchmark=SPY`로 바꾼 조합이다
  - Runtime 재검증 기준 `CAGR=19.35%`, `MDD=-11.03%`, `Sharpe=2.42`, `SPY CAGR=13.36%`, `SPY MDD=-15.90%`, `rolling underperformance share=3.33%`, `Deployment=paper_only`로 조건을 충족했다
  - `top=4`, `1M/6M`, `MA250`도 `CAGR=17.01%`, `MDD=-10.93%`로 더 보수적인 대안이지만, 대표 후보는 수익률과 방어력의 균형이 더 좋은 `top=3`이다
- Follow-up:
  - 후보를 Candidate Library에 등록하려면 Current Candidate Registry append를 별도로 진행한다

### 2026-05-05 - GTAA SPY Low-MDD 후보 Candidate Library 등록
- User request:
  - `GTAA SPY Low-MDD Style Top-3` 후보를 Candidate Library에 추가해 달라고 요청함
- Interpreted goal:
  - 후보를 삭제/수정하지 않고 append-only 방식으로 Current Candidate Registry에 active row를 남겨 Operations > Candidate Library에서 inspect / rebuild 가능하게 해야 함
- Analysis result:
  - 등록 row는 `registry_id=gtaa_current_candidate_spy_low_mdd_style_top3_i3_1m6m_ma250`로 저장했다
  - replay contract에는 `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`, `top=3`, `interval=3`, `1M/6M`, `MA250`, `cash_only`, `Benchmark=SPY`를 포함했다
  - Registry validation 결과 required field 누락 없이 통과했다
- Follow-up:
  - Candidate Library에서 해당 title `GTAA SPY Low-MDD Style Top-3 (1M/6M, i3, MA250)`를 선택해 Rebuild Result Curve로 그래프와 result table을 다시 열 수 있다

### 2026-05-05 - GTAA Low-MDD 후보와 함께 쓸 Equal Weight sleeve 탐색
- User request:
  - `GTAA SPY Low-MDD Style Top-3`와 함께 60:40 또는 70:30으로 섞었을 때 시너지가 나는 Equal Weight 후보를 찾아 달라고 요청함
- Interpreted goal:
  - 단독 성과만 좋은 ETF basket이 아니라, 현재 Equal Weight Real-Money gate를 통과하면서 GTAA와 섞었을 때 전체 포트폴리오의 drawdown / Sharpe가 좋아지는 후보를 찾아야 함
- Analysis result:
  - Equal Weight 단독 `MDD<=15%`와 `SPY benchmark 10단계 gate 통과`는 현재 조건에서 충돌한다
  - 방어형 후보(`DGRW / XLU / GLD` 등)는 MDD는 낮지만 SPY 상대 rolling underperformance가 커서 `hold / blocked`가 된다
  - 성장 / 섹터 / 금 조합은 10단계 gate를 통과하지만 단독 MDD가 18~19% 수준까지 올라간다
  - 대표 실사용 후보는 `QQQ / SOXX / XLE / XLU / GLD`, annual rebalance다. 단독 `CAGR=17.55%`, `MDD=-18.98%`, `Promotion=real_money_candidate`, `Deployment=paper_only`, `Validation=normal`이고, GTAA와 70:30으로 섞으면 `CAGR=18.74%`, `MDD=-10.30%`, 60:40으로 섞으면 `CAGR=18.52%`, `MDD=-10.04%`가 된다
- Follow-up:
  - 사용자가 단독 Equal Weight MDD 15%를 절대 조건으로 유지하면 후보 등록은 보류하고, mix-level MDD 15%를 목표로 해석하면 위 후보를 Candidate Library에 등록할 수 있다

### 2026-05-06 - 워크트리 기반 병렬 개발 운영 가이드
- Request topic:
  - 사용자가 현재 프로젝트의 목적 / 방향 / 개발 정도를 파악한 뒤, Git worktree를 어떻게 구성하고 개발 환경을 세팅하면 좋을지 가이드를 요청함
- Interpreted goal:
  - 처음부터 여러 기능을 무리하게 병렬 구현하기보다, 현재 phase 상태와 dirty worktree 상태를 기준으로 안전한 병렬 작업 단위를 정해야 함
- Analysis result:
  - 현재 `finance`는 데이터 수집, DB persistence, loader/runtime, 전략 / backtest engine, Streamlit Backtest UI, candidate / proposal / final review 운영 기록까지 이어진 quant research workspace다
  - Phase 35는 `implementation_complete / manual_qa_pending`이며, 다음 큰 후보는 Portfolio Monitoring / Paper-Live Tracking, Live Approval Boundary, Portfolio Construction Quality Upgrade다
  - 워크트리 분리는 `data-db`, `strategy-runtime`, `web-backtest-ui`, `docs-phase`처럼 파일 소유권이 겹치지 않는 축으로 나누는 것이 자연스럽다
  - 현재 기본 worktree는 `master`가 `origin/master`보다 55 commits 앞서 있고 문서 / registry / run-history 변경이 많으므로, 새 worktree를 만들기 전 기준 브랜치와 local artifact 처리 방침을 먼저 정하는 것이 안전하다
- Follow-up:
  - 첫 운영 방식은 `master`를 기준선으로 두고, `../quant-data-pipeline-worktrees/<topic>` 아래에 topic branch별 worktree를 추가하는 구조를 권장한다
  - `strategy-runtime`은 실전 후보를 찾는 탐색 브랜치가 아니라 전략 / 엔진 / runtime 구현 안정화 브랜치로 두고, 실전 후보 탐색은 `research-candidates` 또는 `candidate-search`처럼 별도 실험 브랜치로 분리하는 것이 안전하다
  - 실제 병렬 작업은 각 worktree별로 별도 터미널이나 별도 Codex 세션을 열고, 요청마다 worktree path / branch / 담당 범위 / 건드리면 안 되는 파일 / 검증 명령을 명시하는 방식이 가장 안전하다
  - 첫 세팅은 `docs-phase`, `web-backtest-ui`, `candidate-search` 3개 worktree를 만들고, 각 worktree마다 `uv sync`로 독립 `.venv`를 둔 뒤, main worktree는 통합 / merge / final smoke 확인용으로 유지하는 방식이 적합하다
  - 각 worktree에서 Codex를 처음 실행한 직후에는 바로 큰 작업을 맡기기보다 `pwd`, branch, clean status, role, 수정 가능 / 금지 범위, 기본 검증 명령을 한 번 고정한 뒤 작은 첫 작업부터 시작하는 것이 좋다
  - `docs-phase -> web-backtest-ui`처럼 의존성이 있는 흐름은 첫 범위 결정까지는 순차적이지만, 후보 탐색 / QA 정리 / 이미 범위가 확정된 UI 개선처럼 독립 가능한 작업은 병렬로 진행할 수 있다. 따라서 worktree 운영은 완전 동시 작업이라기보다 충돌을 줄이는 병렬 / 파이프라인 운영으로 이해하는 것이 맞다
  - 장기 운영 구조는 사용자가 제안한 `phase`, `ux_ui-polishing`, `candidate-search` 축이 더 자연스럽다. `phase`는 문서와 실제 phase 개발을 끝까지 소유하고, `ux_ui-polishing`은 이미 구현된 기능의 사용성 / 흐름 / 화면 polish를 맡으며, `candidate-search`는 프로그램을 활용한 후보 탐색을 맡는다. 단, `phase`와 `ux_ui-polishing`은 같은 UI 파일을 건드릴 수 있으므로 동시에 같은 화면을 수정하지 않는 규칙이 필요하다
  - 기존 `docs-phase`, `web-backtest-ui`, `candidate-search` worktree는 clean 상태에서 제거했고, `master` 기준으로 `codex/phase`, `codex/ux-ui-polishing`, `codex/candidate-search` worktree를 새로 만들었다
  - worktree별 고정 문서는 반복 운영이 안정된 뒤 만들고, 초기에는 세션 첫 메시지로 역할 / 수정 가능 범위 / 수정 금지 범위 / 현재 충돌 주의 파일을 지정하는 방식이 낫다. 아직 운영 규칙이 변하는 중이라 문서를 너무 빨리 고정하면 오히려 stale guidance가 생길 수 있다

### 2026-05-06 - Phase36 Selected Portfolio Dashboard 목적 보정
- User request:
  - `Selected Portfolio Dashboard`가 최종 선정 포트폴리오의 성과를 판단하는 화면이어야 하는데, 현재는 JSON과 drift 입력이 중심처럼 보여 사용자가 무엇을 검증해야 하는지 알기 어렵다고 지적함
- Interpreted goal:
  - Final Review에서 선정된 포트폴리오를 단순히 다시 보는 화면이 아니라, 원래 검증 기간 이후의 데이터를 포함해 사용자가 새 기간을 잡고 성과 유지 여부를 즉시 확인하는 운영 dashboard가 필요함
- Analysis result:
  - dashboard의 주 목적은 `JSON inspection`이 아니라 `선정 포트폴리오 performance recheck`로 재정의하는 것이 맞다
  - 기본 화면은 Snapshot / Performance Recheck / What Changed / Allocation Check / Audit 순서가 적합하다
  - Performance Recheck는 원래 선정일 이후만 보는 것이 아니라, 사용자가 지정한 start / end 범위로 selected component replay contract를 다시 실행해야 한다
  - raw JSON은 기본 화면에서 제거하고 접힘 Audit 영역으로 이동해야 하며, drift check는 실제 보유 또는 가정 보유가 있을 때만 쓰는 optional advanced 기능이어야 한다
- Follow-up:
  - Phase36에서는 performance recheck와 가상 투자금 기반 현재 평가를 구현하고, 후속 Phase37 후보는 성과 악화 원인 분석 / review alert / attribution 강화로 잡는다

### 2026-05-07 - Phase36 Selected Portfolio Dashboard UX 구조 개선
- User request:
  - 개편 후에도 데이터 출처 카드, 운영 대상 목록, Snapshot, Performance Recheck 결과, Allocation 위치, Operator Context / 실행 경계 연결이 좁은 화면과 사용자 이해 관점에서 아쉽다고 개선 방향을 요청함
- Interpreted goal:
  - 단순 copy 수정이 아니라 dashboard의 사용자 작업 순서를 `선택 -> 정의 확인 -> 기간 재검증 -> 운영 점검 -> 실행 경계 확인`으로 재배치해야 함
- Analysis result:
  - 긴 source path와 selected filter 설명은 metric column이 아니라 wrapping card + 접힘 registry path로 처리하는 것이 맞다
  - 운영 대상 목록은 많은 audit column을 보여주는 표가 아니라 compact selection board여야 한다
  - target allocation은 Performance 뒤가 아니라 Snapshot의 Portfolio Blueprint에 있어야 한다
  - Performance Recheck 결과는 Backtest 결과 화면과 같은 tab 구조가 맞으며, Result Table도 별도 tab으로 노출해야 한다
  - Operator Context는 독립 설명 카드가 아니라 Monitoring Playbook으로 바꾸고 Selection Evidence, Review Triggers, Holding Drift Check, Execution Boundary를 같은 흐름에 둬야 한다
- Follow-up:
  - Phase36 QA는 새 구조 기준으로 `PHASE36_TEST_CHECKLIST.md`에서 확인한다

### 2026-05-07 - Monitoring Playbook / Review Triggers 의미 정리
- User request:
  - Monitoring Playbook에서 무엇을 해야 하는지 설명을 요청했고, 특히 Review Triggers tab이 너무 대충 만든 느낌이라 정리가 필요하다고 지적함
- Interpreted goal:
  - Monitoring Playbook은 설명 모음이 아니라 선정 포트폴리오의 운영 상태를 판단하는 board가 되어야 함
- Analysis result:
  - Selection Evidence는 선정 근거 확인, Performance Recheck는 성과 유지 확인, Holding Drift Check는 보유 비중 이탈 확인, Execution Boundary는 실행 금지 경계 확인 역할을 가진다
  - Review Triggers는 원본 trigger list를 그대로 나열하는 탭이 아니라 Performance Recheck와 Holding Drift Check의 현재 상태를 운영 trigger row로 번역해야 한다
  - 기본 trigger는 Final Review evidence, CAGR deterioration, MDD expansion, Benchmark underperformance, Holding drift가 적합하다
  - 각 trigger는 `Clear`, `Watch`, `Breached`, `Needs Input` 상태와 Suggested Action을 가져야 한다
- Follow-up:
  - Phase36 dashboard에서 Review Triggers tab을 `Trigger Board`로 변경하고, 원본 operator note는 `Original Operator Notes` 접힘 영역으로 낮춘다

### 2026-05-07 - Selected Portfolio Dashboard 흐름 / Actual Allocation 의미 재정리
- User request:
  - `GTAA Clean-6 AOR Top-2 High CAGR (1M/12M, i2, MA150)` 단일 포트폴리오를 기준으로 dashboard 사용 흐름을 검토했고, source boundary, 운영 대상 선택, Portfolio Blueprint, Monitoring Playbook, Holding Drift Check, Execution Boundary가 사용자 입장에서 무엇을 하는지 불명확하다고 지적함
- Interpreted goal:
  - dashboard는 Final Review 통과 포트폴리오를 최신 기간으로 다시 분석하는 화면이어야 하며, 보유금액 배분 점검은 기본 성과 재검증 흐름을 방해하지 않는 optional 기능이어야 함
- Analysis result:
  - 데이터 출처 / selected filter / write policy는 사용자 분석 흐름의 핵심이 아니라 audit 정보이므로 기본 화면에서 내려야 한다
  - 운영 대상이 하나뿐일 때는 filter table보다 현재 선택된 포트폴리오 badge가 더 적합하다
  - 단일 component 100% 포트폴리오에서 `Holding Drift Check`는 component 간 리밸런싱 기능처럼 보이면 혼란스럽다. 실제 의미는 "이 포트폴리오에 배정한 실제 또는 가상 금액이 target allocation과 다른가"를 보는 optional Actual Allocation 점검이다
  - Review Signals는 성과 재검증 결과를 중심으로 하되, Actual Allocation은 사용자가 명시적으로 반영할 때만 signal board에 들어가야 한다
- Follow-up:
  - Phase36 dashboard를 `Selected Portfolio -> Snapshot -> Performance Recheck -> Portfolio Monitoring(Review Signals / Why Selected / Actual Allocation / Audit)` 흐름으로 재정렬한다

### 2026-05-06 - Ops Review 개편 방향과 1번 구현
- User request:
  - 완성된 프로그램 기능을 기준으로 `Operations > Ops Review`를 어떻게 개편하면 좋을지 분석한 뒤, 1번 개편을 UX/UI와 시각성을 고려해 진행해 달라고 요청함
- Interpreted goal:
  - 방치된 로그 모음 화면을 단순 운영 artifact viewer가 아니라, 사용자가 지금 무엇을 먼저 봐야 하는지 판단할 수 있는 운영 대시보드로 바꿔야 함
- Analysis result:
  - Ops Review의 적절한 책임은 ingestion / refresh / factor job의 run health, failure artifact, related logs, runtime build 상태를 한 화면에서 판독하는 것이다
  - job 실행은 `Ingestion`, backtest replay / form 복원은 `Backtest Run History`, 저장 후보 replay는 `Candidate Library`가 담당해야 하므로 Ops Review가 action 실행 화면으로 확장되면 흐름이 다시 혼재된다
  - 화면 구조는 `triage flow -> status cards -> action inbox -> selected run inspector -> logs / artifacts -> next screen guidance` 순서가 가장 자연스럽다
- Follow-up:
  - `app/web/ops_review.py`를 추가하고 `streamlit_app.py`의 Ops Review page entry에서 호출하게 했다
  - README와 Backtest UI flow 문서에는 Ops Review가 운영 상태 판독 화면이며 실행 / replay / 후보 재검토는 전용 화면으로 이동한다는 경계를 남겼다

### 2026-05-07 - Compare / 저장 mix 검증 ownership 재정리
- User request:
  - Compare & Portfolio Builder에서 개별 전략 5단계 검증과 저장 mix 검증이 섞여 보이는 UX를 개선하고, Guides도 함께 맞춰 달라고 요청함
- Interpreted goal:
  - 5단계 Compare는 개별 전략 후보를 Candidate Review로 보낼 수 있는지 판단하는 보드로 고정하고, weighted / saved mix는 Portfolio Mix 검증 보드와 Portfolio Proposal 경로로 읽히게 해야 함
- Analysis result:
  - 기존 `Load Saved Mix Into Compare`는 저장 mix 검증 버튼처럼 보였지만 실제로는 개별 전략 비교 form을 다시 채우는 편집 경로였다
  - 저장 mix를 열고 바로 `Run Strategy Comparison`을 누르면 GTAA / Equal Weight 각각의 5단계 보드가 떠서, 사용자가 mix-level 검증 실패로 오해할 수 있었다
  - GTAA `interval=3`, `month_end`처럼 정상 cadence 때문에 result end가 요청 end보다 짧은 경우는 DB 부족이 아니라 cadence-aligned review로 분리하는 것이 맞다
- Follow-up:
  - Compare workspace label을 `개별 전략 비교` / `저장된 비중 조합`으로 바꾸고, saved mix primary action을 `Mix 재실행 및 검증`으로 조정했다
  - `전략 비교에서 수정하기`는 검증이 아니라 저장 mix 구성을 편집 / 재구성하는 경로로 설명했다
  - Guides와 `BACKTEST_UI_FLOW.md`에 mix는 Candidate Review가 아니라 Portfolio Proposal 초안으로 연결된다는 ownership을 반영했다

### 2026-05-08 - Backtest 후보 선정 workflow는 3단계로 재설계해야 한다
- User request:
  - 사용자가 Candidate Review와 Portfolio Proposal의 역할이 불분명하고 메모 / 저장 단계가 반복되므로, 구현 전에 현재 코드를 깊게 분석하고 개발 가이드를 문서화해 달라고 요청함
- Interpreted goal:
  - `Single / Compare 백테스트 분석 -> 실전 검증 -> Final Review` 흐름으로 재정리하되, 기존 registry와 saved mix / final decision 호환성을 깨지 않는 구현 계획이 필요함
- Analysis result:
  - 현재 Candidate Review는 투자 검증 화면이라기보다 Review Note, Current Candidate, Pre-Live record를 저장하는 후보 포장 UI에 가깝다
  - Portfolio Proposal은 Current Candidate 기반 weight builder, Saved Mix prefill, Validation Pack, saved proposal review가 섞여 있어 Compare의 weight 조합 기능과 목적이 충돌해 보인다
  - Saved Mix는 이미 mix-level 검증 source를 갖고 있지만 Final Review / risk helper가 Current Candidate와 Pre-Live 존재를 기대해 마지막 단계에서 막힐 수 있다
  - 5개 panel label을 바로 3개 label로 바꾸면 `backtest_requested_panel`, history replay, saved mix handoff가 깨질 수 있으므로 visible stage와 internal route를 먼저 분리해야 한다
- Follow-up:
  - `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`에 route / session key / registry dependency / source contract / 단계별 구현 순서를 정리했다
  - 제품 코드는 아직 수정하지 않았고, 사용자 확인 후 route foundation부터 구현한다

### 2026-05-10 - 기존 JSONL은 archive하고 Clean V2 저장 구조로 다시 시작할 수 있다
- User request:
  - 사용자가 기존 JSONL을 반드시 활용하지 않아도 되며, archive로 보관하고 새 workflow 기준으로 새 저장 파일을 만들 수 있다고 설명함
- Interpreted goal:
  - 3단계 workflow redesign이 기존 registry chain에 과도하게 묶이지 않도록, 새 source-of-truth와 사용자 end-to-end flow를 명확히 해야 함
- Analysis result:
  - 대규모 개편에서는 `Compatibility Mode`보다 `Clean V2 Mode`가 더 적합하다
  - 기존 `Review Note -> Current Candidate -> Pre-Live -> Portfolio Proposal -> Final Decision` chain은 archive / legacy inspector로 내리고, 새 main flow는 `Selection Source -> Practical Validation Result -> Final Decision V2 -> Monitoring Log`로 단순화한다
  - 사용자 플로우는 `Backtest Analysis`에서 만들고 선택, `Practical Validation`에서 실전 검증, `Final Review`에서 최종 판단과 메모 저장, `Selected Portfolio Dashboard`에서 선정 이후 성과와 review signal 확인으로 정리한다
- Follow-up:
  - `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`에 Clean V2 저장소 설계, legacy archive 정책, 새 JSONL 파일 역할, 사후관리 flow를 보강했다

### 2026-05-10 - Clean V2 구현은 legacy 삭제보다 stage / storage 병행 전환이 맞다
- User request:
  - 사용자가 새 스크립트를 만들고 기존 스크립트는 리팩토링 과정에서 정리하는 방식인지 확인한 뒤 작업 진행을 요청함
- Interpreted goal:
  - 기존 Candidate Review / Portfolio Proposal 파일을 즉시 삭제하지 않고, 새 Clean V2 stage와 저장소를 먼저 세워 사용 경로를 전환해야 함
- Analysis result:
  - 1차 구현에서는 `backtest_workflow_routes`, `backtest_analysis`, `backtest_practical_validation`, `portfolio_selection_v2`를 추가하고 기존 route request를 새 stage로 매핑하는 것이 안전하다
  - 기존 JSONL과 UI 파일은 legacy compatibility로 남기되 새 main workflow의 필수 join 조건에서는 제거한다
  - Selected Portfolio Dashboard는 Final Review V2 decision row를 source-of-truth로 읽는 것이 맞다
- Follow-up:
  - Backtest stage routing, Clean V2 source / validation / final decision persistence, Practical Validation UI, Final Review V2 저장, Selected Dashboard V2 read path를 1차 구현했다

### 2026-05-10 - Compare weighted mix도 바로 Practical Validation으로 가야 한다
- User request:
  - 사용자가 Backtest Analysis > Compare & Portfolio Builder에서 개별 전략만 Practical Validation으로 보낼 수 있고, mix 상태에서는 다음 행동으로 보낼 수 없는 것인지 확인함. 또한 저장 mix의 `전략 비교에서 수정하기`가 기존 5단계 결과를 먼저 보여주는 UX가 어색하다고 지적함
- Interpreted goal:
  - 개별 전략 handoff와 mix handoff를 분리하되, 새로 만든 mix도 저장 후 재실행을 강제하지 않고 바로 Practical Validation source로 보낼 수 있어야 함
- Analysis result:
  - 개별 전략 Compare 보드는 단일 후보 전용으로 유지하는 것이 맞다
  - weighted mix는 별도 Clean V2 source로 Practical Validation에 보내는 primary action이 필요하다
  - saved mix edit mode는 검증 경로가 아니라 편집 / 재구성 경로이므로 stale compare 결과보다 저장된 설정이 반영된 form을 먼저 보여주는 것이 맞다
- Follow-up:
  - 현재 weighted mix 직접 handoff를 추가하고, saved mix edit mode에서 기존 result state를 clear하도록 구현했다

### 2026-05-10 - Portfolio Mix 검증 보드의 5~10단계 문구는 legacy 표현이다
- User request:
  - 사용자가 Portfolio Mix 검증 보드 판정에 `성과 replay는 가능하지만, 5~10단계 workflow 통과 기록은 아직 없습니다.`라고 표시되는 점을 지적함
- Interpreted goal:
  - Clean V2 전환 이후 saved mix 검증 보드는 5~10단계 legacy workflow가 아니라 Practical Validation / Final Review V2 기록 유무를 기준으로 설명해야 함
- Analysis result:
  - 해당 문구는 과거 workflow copy가 남은 것이며, 참조 확인도 legacy registry 중심이었다
- Follow-up:
  - 판정 문구와 기준명을 Clean V2 기준으로 바꾸고 V2 registry 참조 확인을 추가했다

### 2026-05-10 - Practical Validation은 실전 후보 검증 evidence pack으로 확장해야 한다
- User request:
  - 사용자가 Practical Validation이 현재 어떤 검증을 하는지, 그 검증이 실전 투자 관점에서 신빙성이 있는지, 앞으로 어떤 검증을 넣어야 하는지 설계 조사와 문서화를 요청함
- Interpreted goal:
  - 구현 전에 `이 전략을 실전 전략 후보로 사용할 수 있나?`라는 질문에 답하기 위한 검증 domain, 데이터 요구사항, UI / JSON contract, 구현 우선순위를 정해야 함
- Analysis result:
  - 현재 Practical Validation은 source id, active component, weight total, Data Trust / Real-Money blocker, benchmark snapshot을 보는 최소 gate이며 깊은 실전 검증은 아니다
  - 실전 후보 검증으로는 replay reproducibility, same-period benchmark, rolling / walk-forward, drawdown / tail / recovery, regime stress, cost / turnover, ETF investability, parameter / weight sensitivity, overfit audit, paper monitoring plan이 필요하다
  - 각 domain은 `PASS / REVIEW / BLOCKED / NOT_RUN`으로 분리해야 하며, `NOT_RUN`은 통과가 아니라 아직 확인하지 못한 상태로 표시해야 한다
- Follow-up:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`에 조사 출처, domain 설계, v2 schema, UI 구조, 구현 slice를 문서화했다
  - 제품 코드는 아직 수정하지 않았다

### 2026-05-10 - Practical Validation V2는 앞 단계 검증을 반복하면 안 된다
- User request:
  - 사용자가 Practical Validation 이전에도 Data Trust, Real-Money, Compare, Mix 검증이 있으므로 V2 설계가 중복 검증을 만들지 않는지 확인이 필요하다고 지적함
- Interpreted goal:
  - 각 검증 domain의 stage ownership을 분리하고, Practical Validation이 무엇을 상속 / 통합 / 신규 계산해야 하는지 명확히 해야 함
- Analysis result:
  - Single Strategy runtime은 이미 거래비용, benchmark overlay, rolling / OOS review, ETF operability, liquidity, validation / guardrail policy, promotion / deployment readiness를 만든다
  - Compare 5단계 보드는 단일 후보 선택을 위한 Data Trust / Real-Money / 상대 순위 gate이고, Saved Mix 검증 보드는 replay 가능성과 V2 기록 연결성을 보는 gate다
  - Practical Validation V2는 이를 다시 점수화하는 단계가 아니라 upstream evidence를 상속하고, portfolio-level source contract / weight / mix alignment / missing domain / sensitivity / overfit / monitoring baseline을 추가하는 evidence pack이어야 한다
- Follow-up:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`에 앞 단계 검증과의 중복 위험, Stage Ownership Matrix, domain `origin` 설계, 중복 감점 방지 원칙을 보강했다

### 2026-05-10 - Practical Validation은 실전 투자 진단 엔진으로 설계해야 한다
- User request:
  - 사용자가 Practical Validation을 앞 단계 검증 요약판이 아니라, 실제 투자 후보로 검토할 때 필요한 asset allocation, concentration, macro / sentiment, stress, inverse / leveraged ETF, 대안 포트폴리오 비교 같은 실무적 검증 단계로 만들고 싶다고 설명함
- Interpreted goal:
  - 외부 자료와 실무 framework를 조사해 Practical Validation의 차별화된 진단 module, 중복 방지 경계, MVP 개발 순서를 문서화해야 함
- Analysis result:
  - Backtest Analysis는 성과 / Data Trust / Compare 선택 근거를 만드는 단계이고, Practical Validation은 그 evidence를 입력으로 받아 portfolio-level 실전 진단을 실행해야 한다
  - 주요 신규 module은 asset allocation fit, concentration / overlap, correlation / risk contribution, macro / regime, sentiment overlay, stress / scenario, alternative portfolio challenge, leveraged / inverse suitability, ETF operability, robustness / overfit audit이다
  - 단일 전략도 1개 component 100% 포트폴리오로 보고 같은 진단을 적용하며, mix는 component score 합산보다 exposure와 위험 구조를 우선 해석해야 한다
- Follow-up:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`를 새로 작성했다
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`를 evidence pack 중심에서 Practical Investment Diagnostics 중심으로 보강했다

### 2026-05-10 - Practical Validation은 Validation Profile로 판정 기준을 조정해야 한다
- User request:
  - 사용자가 Practical Validation에서 모든 진단을 보수적으로 적용하면 공격형 / 방어형 등 사용자 목적에 맞지 않게 다음 단계가 막힐 수 있다고 지적함
  - 3~5개 질문으로 사용자 성향과 목적을 파악해 threshold / weight / blocker 기준을 자동 조정하고, 사용자가 원한 방향과 후보 성격이 다르면 알려주는 기능을 제안함
- Interpreted goal:
  - 12개 진단 module은 유지하되, `Validation Profile`이 domain별 threshold, 중요도, blocker / review 기준, mismatch warning을 조정하는 구조를 문서화해야 함
- Analysis result:
  - 검증 domain을 줄이는 방식보다 가능한 domain은 모두 시도하고 profile에 따라 해석을 바꾸는 방식이 안전하다
  - Data Trust, weight 합계, 가격 부재, 거래 불가, execution boundary, 큰 leveraged / inverse exposure의 목적 부재 같은 invariant hard blocker는 profile로 무력화하면 안 된다
  - 공격형 목표인데 SPY / QQQ와 차이가 약하거나, 방어형 목표인데 equity / growth concentration이 높으면 intent mismatch warning으로 Final Review 전에 보여줘야 한다
- Follow-up:
  - Practical Validation research / design 문서에 Validation Profile 질문, profile별 threshold / weight / invariant blocker, intent mismatch warning, JSON / UI / 구현 slice 반영 사항을 보강했다

### 2026-05-10 - Sentiment Overlay는 후속 module로 두고 Asset Allocation Profile 용어를 명확히 한다
- User request:
  - 사용자가 Sentiment Overlay 데이터 연동은 1차 Practical Validation 이후에 추가해도 되는지 확인했고, 해당 내용을 문서에 짧게 남기길 요청함
  - `asset allocation profile`이 무엇을 뜻하는지도 질문함
- Interpreted goal:
  - 1차 Practical Validation core와 후속 market-context connector의 경계를 분리하고, asset allocation profile 용어를 문서상 명확히 해야 함
- Analysis result:
  - Sentiment Overlay는 반드시 넣고 싶은 future module이지만, 1차 구현에서는 `NOT_RUN` / future connector 상태로 남기고 core diagnostic flow를 먼저 안정화하는 것이 맞다
  - 후속 구현은 FRED 기반 VIX / Credit Spread / Yield Curve snapshot부터 시작하고, Fear & Greed는 optional connector로 둔다
  - asset allocation profile은 주식 / 채권 / 현금 / 금 / 원자재 / inverse / leveraged 노출을 사용자의 검증 목적에 맞춰 해석하는 자산 배분 성격 기준이다
- Follow-up:
  - Practical Validation research / design 문서와 glossary에 Sentiment Overlay 후속 구현 메모와 Asset Allocation Profile 정의를 추가했다

### 2026-05-10 - Validation Profile 질문과 한글 화면 표기 확정
- User request:
  - 사용자가 profile과 질문을 영어가 아니라 화면에서는 한글로 표기하고, 앞서 제안한 5개 질문으로 진행하길 원함
  - `profile로 무력화하면 안 되는 hard blocker`의 의미를 질문함
- Interpreted goal:
  - Practical Validation profile UI 질문, 선택지, 내부 저장 id, 한글 profile label, invariant hard blocker 설명을 문서에 명확히 해야 함
- Analysis result:
  - 사용자-facing profile 표기는 방어형 / 균형형 / 성장형 / 전술·헤지형 / 사용자 지정으로 둔다
  - 내부 id는 `conservative_defensive`, `balanced_core`, `growth_aggressive`, `hedged_tactical`, `custom`으로 저장한다
  - 5개 질문은 목적, 감내 손실, 운용 기간, 상품 / 운용 복잡도, 단순 대안 대비 기대를 묻는다
  - 무력화하면 안 되는 hard blocker는 사용자가 공격형 profile을 골라도 자동 통과 처리하면 안 되는 치명적 문제이며, risk tolerance와 validation failure를 구분해야 한다
- Follow-up:
  - Practical Validation research / design 문서와 glossary에 한글 label, 5개 질문, 내부 저장 id, invariant hard blocker 설명을 보강했다

### 2026-05-10 - Practical Validation 남은 설계 질문 정리
- User request:
  - 사용자가 남은 설계 질문 목록을 refresh해 달라고 요청함
- Interpreted goal:
  - 이미 결정된 질문과 실제 구현 시 확정할 질문이 섞여 있는 상태를 정리해야 함
- Analysis result:
  - sentiment hard blocker 여부, profile label / 질문 수 / domain 생략 여부 / invariant blocker / mismatch 처리 / NOT_RUN 허용 / sensitivity 기본 방침 등은 결정 완료로 이동했다
  - rolling window 세부값, cost assumption, baseline proxy, sensitivity perturbation grid, stress window 목록, sentiment connector 착수 시점은 구현 선택으로 남겼다
- Follow-up:
  - Practical Validation research / design 문서의 `남은 설계 질문` / `Open Questions`를 `결정 완료`와 `남은 구현 선택`으로 재정리했다

### 2026-05-10 - 설계 질문 표를 확인 여부 컬럼으로 통합
- User request:
  - 사용자가 설계 질문 상태를 `결정 완료`와 `남은 구현 선택` 두 섹션으로 나누지 말고 하나의 표로 합쳐 `확인 여부`를 `O / X`로 표시해 달라고 요청함
- Interpreted goal:
  - 설계 질문을 하나의 점검표처럼 읽을 수 있게 만들고, 결정된 항목과 구현 시 확정할 항목을 같은 표에서 구분해야 함
- Analysis result:
  - Practical Validation research / design 문서의 설계 질문 상태 표를 하나로 합치고 `확인 여부`, `질문`, `결정 / 기본 방향` 컬럼으로 바꾸는 것이 적절함
- Follow-up:
  - 두 문서의 설계 질문 상태를 단일 표로 통합하고 확인된 항목은 `O`, 구현 선택이 남은 항목은 `X`로 표시했다

### 2026-05-10 - Proxy classification과 holdings look-through 설명 보강
- User request:
  - 사용자가 `proxy classification으로 시작하고 missing coverage를 NOT_RUN으로 표시한다`는 문장의 의미를 이해했고, 그 내용을 간략히 문서에 보강해 달라고 요청함
- Interpreted goal:
  - ETF 내부 holdings 데이터가 없을 때 대략 분류와 정밀 look-through 검증의 차이를 문서에서 바로 이해할 수 있어야 함
- Analysis result:
  - Proxy classification은 ETF의 대표 성격으로 QQQ, XLK, SMH 등을 대략 분류하는 방식이다
  - Holdings look-through는 ETF 안의 실제 보유종목까지 확인해 Apple / Microsoft / Nvidia 같은 top holding overlap을 계산하는 정밀 방식이다
  - holdings 데이터가 없으면 정밀 중복률 검증은 통과가 아니라 `NOT_RUN`으로 표시해야 한다
- Follow-up:
  - Practical Validation research / design 문서에 proxy classification과 holdings look-through 차이, NOT_RUN 의미를 짧은 예시로 보강했다

### 2026-05-10 - Final Review route와 NOT_RUN 의미 보강
- User request:
  - 사용자가 `Final Review selected route에서 NOT_RUN을 허용할 것인가`의 의미를 이해했고, 해당 내용이 문서에 없다면 보강해 달라고 요청함
- Interpreted goal:
  - `NOT_RUN`이 통과가 아니라 미실행 상태이며, Final Review 이동은 가능하더라도 critical domain은 명시 확인이 필요하다는 경계를 문서화해야 함
- Analysis result:
  - `NOT_RUN`은 데이터나 기능 부족으로 아직 검증하지 못했다는 disclosure다
  - Sentiment connector 미구현이나 holdings look-through 데이터 부재는 Final Review 이동을 막지 않을 수 있지만, 핵심 가격 부재 같은 문제는 `BLOCKED` 후보로 봐야 한다
- Follow-up:
  - Practical Validation research / design 문서에 Final Review route와 `NOT_RUN` 처리 의미를 보강했다

### 2026-05-10 - Practical Validation rolling window와 cost assumption 기본값 확정
- User request:
  - 사용자가 rolling window 기본값과 cost assumption 의미를 확인했고, 확정된 항목의 확인 여부를 `O`로 바꿔 문서화하길 요청함
- Interpreted goal:
  - Practical Validation profile별 rolling 검증 기본 구간과 거래비용 기본 가정을 구현 전 설계 기준으로 고정해야 함
- Analysis result:
  - rolling window는 전략 lookback이나 리밸런싱 주기가 아니라 검증용 성과 측정 구간이다
  - 기본 rolling window는 방어형 24개월, 균형형 36개월, 성장형 60개월, 전술 / 헤지형 24개월, 사용자 지정 36개월로 둔다
  - cost assumption은 거래 수수료뿐 아니라 bid-ask spread, slippage, 세금성 비용을 포함한 거래비용 가정이다
  - MVP 기본 거래비용은 균형형 기준 one-way 10 bps로 시작하고, expense ratio / turnover / liquidity coverage가 붙으면 보정한다
- Follow-up:
  - Practical Validation research / design 문서에 rolling window와 cost assumption 설명을 보강하고 해당 설계 질문을 `O`로 변경했다

### 2026-05-10 - Stress window static calendar와 sentiment connector 의미 보강
- User request:
  - 사용자가 2000년 이후 미국 증시에 충격을 준 이벤트 구간을 static data로 정의하길 요청했고, sentiment connector의 의미와 FRED 기반 snapshot 추가 방향을 질문함
- Interpreted goal:
  - Practical Validation stress test가 AI 기억이나 임의 이벤트명이 아니라 버전 관리되는 deterministic stress calendar를 사용해야 함
  - Sentiment connector가 trade signal이 아니라 market-context data adapter임을 명확히 해야 함
- Analysis result:
  - `practical_validation_stress_windows_v1.json`을 static reference data로 추가해 Dot-com, 9/11, GFC, Lehman, 2010 Flash Crash, 2011 debt-ceiling/eurozone, 2015 China devaluation, 2018 volatility/Q4 selloff, COVID, 2022 rate shock, 2023 banking stress, 2024 carry unwind, 2025 tariff shock window를 정의했다
  - Stress window는 포트폴리오 수익률 curve와 benchmark curve를 해당 기간으로 잘라 return / MDD / spread를 계산하는 검증 preset이며, 기간이 겹치지 않으면 `NOT_RUN`으로 둔다
  - Sentiment connector는 FRED / DB / API에서 VIX, credit spread, yield curve 같은 시장 분위기 지표를 가져와 Practical Validation에 snapshot으로 붙이는 data adapter다
- Follow-up:
  - Practical Validation research / design 문서에 static stress calendar 링크와 sentiment connector 설명을 보강하고 stress window 설계 질문을 `O`로 변경했다

### 2026-05-10 - Alternative baseline / sensitivity grid / trial count 설계 완료 처리
- User request:
  - 사용자가 이미 협의한 단순 대안 baseline, sensitivity perturbation grid, run_history trial count 내용을 문서에 보강하고 완료 처리하길 요청함
- Interpreted goal:
  - Practical Validation의 복잡성 비교, 견고성 검증, 과최적화 audit 기본 방침을 구현 전 확정 상태로 정리해야 함
- Analysis result:
  - Alternative Portfolio Challenge는 SPY, QQQ, 60/40 proxy, cash-aware baseline을 1차 포함하고, All Weather-like proxy는 ETF / weight assumption을 별도 확정한 뒤 후속으로 둔다
  - Sensitivity MVP는 주요 window perturbation, mix weight +/- 5%p, drop-one, 기존 runtime이 지원하는 strategy-specific 작은 설정 변경부터 시작한다
  - run_history 원본은 저장하지 않고, Practical Validation에서 local run_history를 읽을 수 있을 때 `overfit_audit` 요약값만 validation row에 선택적으로 남긴다
- Follow-up:
  - Practical Validation research / design 문서에 세 항목의 의미와 MVP 처리 방식을 보강하고 설계 질문 상태를 `O`로 변경했다

### 2026-05-10 - Sentiment connector 후속 구현 범위 확정
- User request:
  - 사용자가 `sentiment connector는 언제 붙일 것인가?` 항목도 확인 완료로 문서 처리하길 요청함
- Interpreted goal:
  - Sentiment connector를 1차 Practical Validation core가 아니라 후속 module로 붙이는 방침을 확정 상태로 표시해야 함
- Analysis result:
  - 시작 범위는 FRED 기반 VIX / Credit Spread / Yield Curve snapshot이다
  - 이 데이터는 market-context evidence이며 trade signal이나 hard blocker로 쓰지 않는다
  - CNN Fear & Greed는 공식 안정 API / 재현성 문제 때문에 optional connector로 유지한다
- Follow-up:
  - Practical Validation research / design 문서의 sentiment connector 설계 질문 상태를 `O`로 변경했다

### 2026-05-10 - Practical Validation V2 core 구현 방향 확정
- User request:
  - 사용자가 새 전략 구현 없이 `DESIGN.md`과 투자 진단 research 문서를 기반으로 Practical Validation 개발을 진행하길 요청함
- Interpreted goal:
  - Backtest Analysis에서 넘어온 단일 전략 / Compare 후보 / weighted mix / saved mix를 같은 포트폴리오 검증 단위로 읽고, Final Review 전에 실전 후보로 올릴 수 있는지 profile-aware diagnostics로 보여줘야 함
- Analysis result:
  - 제품 전략 runtime은 건드리지 않고 Practical Validation result schema를 v2로 올렸다
  - 기존 source id / weight / Data Trust / Real-Money 확인은 `Input Evidence Layer`로 유지하고, 그 위에 12개 Practical Diagnostics domain을 `PASS / REVIEW / BLOCKED / NOT_RUN`으로 분리했다
  - `REVIEW / NOT_RUN`은 Final Review 이동을 자동 차단하지 않지만, 최종 판단 사유에서 확인해야 하는 evidence로 남긴다
  - `BLOCKED`는 Practical Validation 화면에서 Final Review 이동을 막는 source 보강 대상이다
- Follow-up:
  - 후속 개발은 return curve replay, benchmark parity, rolling/stress 구간 성과, correlation/risk contribution, ETF cost/liquidity connector, macro/sentiment connector 순서로 진행하는 것이 맞다

### 2026-05-10 - Practical Validation 남은 12개 개발 항목 진행
- User request:
  - 사용자가 profile-aware scoring부터 Selected Dashboard 연동까지 남은 12개 항목을 단계별로 개발하길 요청함
- Interpreted goal:
  - 기존 보드 구조가 아니라 실제 계산 가능한 domain은 바로 정량 계산하고, 데이터 connector가 아직 없는 항목은 proxy / NOT_RUN / REVIEW 경계를 명확히 해야 함
- Analysis result:
  - 새 Backtest Analysis handoff에는 compact monthly curve snapshot을 저장한다
  - 기존 source도 DB price proxy curve를 만들어 rolling, stress, baseline, correlation, sensitivity, operability 계산을 시도한다
  - profile category는 domain weight를 바꿔 score breakdown과 최종 score에 반영한다
  - holdings-level look-through, ETF expense / spread / AUM, FRED macro / sentiment는 아직 connector가 필요하므로 proxy 또는 후속으로 남긴다
- Follow-up:
  - 후속 고도화는 strategy runtime full replay 버튼, holdings provider, FRED connector, ETF expense / spread connector 순서로 진행한다

### 2026-05-10 - Practical Validation V2 남은 구현 계획 문서화
- User request:
  - 사용자가 `PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH`와 `DESIGN.md`에서 협의한 내용 중 아직 미완성인 항목과 구현 방식을 정리한 뒤, 문서 검토 후 개발을 진행하자고 요청함
- Interpreted goal:
  - 지금 코드가 완성된 범위와 남은 범위를 혼동하지 않도록, 실제 runtime replay / provider connector / Final Review 연동까지의 개발 계획을 검토 가능한 문서로 남겨야 함
- Analysis result:
  - 현재 Practical Validation V2는 profile, 12개 diagnostics board, profile-aware score, compact curve / DB price proxy 기반 rolling / stress / baseline / sensitivity / operability 1차 계산까지 구현됐다
  - 남은 핵심은 새 검증명을 추가하는 것이 아니라 proxy evidence를 actual runtime replay와 provider snapshot으로 승격하는 것이다
  - 첫 개발 단위는 helper split 후 actual runtime replay / curve provenance / benchmark parity hardening으로 잡는 것이 가장 안전하다
- Follow-up:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`를 추가하고, 사용자가 검토한 뒤 개발 범위를 확정하기로 했다

### 2026-05-10 - Practical Validation V2 P0 개발 진행
- User request:
  - 사용자가 향후 개발 우선순위 중 helper split, actual runtime replay, curve provenance, benchmark parity hardening 1~4번을 단계별로 진행하길 요청함
- Interpreted goal:
  - Practical Validation이 proxy 중심 diagnostics에서 실제 기존 runtime replay 근거를 우선 사용할 수 있게 하고, 상대 benchmark 비교의 기간 / coverage 신뢰도를 명시해야 함
- Analysis result:
  - helper 책임을 curve/parity와 replay로 분리했다
  - actual replay는 자동 실행이 아니라 사용자가 `실제 전략 replay 실행`을 누를 때만 기존 strategy runtime을 호출한다
  - replay 결과가 있으면 diagnostics는 actual replay curve를 우선 사용하고, 없거나 실패하면 기존 embedded snapshot / DB price proxy 진단을 유지한다
  - benchmark parity는 portfolio curve와 benchmark curve의 기간, 월별 coverage, frequency 차이를 계산해 review gap으로 남긴다
- Follow-up:
  - 다음 고도화는 Validation Inspector / profile comparison UX와 strategy-specific sensitivity runtime이 우선이다

### 2026-05-10 - Practical Validation runtime replay 필요성 재검토
- User request:
  - 사용자가 같은 날짜를 다시 재현하는 Actual Runtime Replay가 Practical Validation에서 실제로 필요한지 질문했고, 필요하다면 최신 데이터 기준 검증이어야 한다는 방향을 확인함
- Interpreted goal:
  - Practical Validation의 3번 구간이 단순 확인용 replay가 아니라 실전 후보 최신성 확인에 의미 있는 단계가 되어야 함
- Analysis result:
  - 동일 기간 replay는 contract / runtime 재현 확인에는 유용하지만, 실전 후보 검증의 핵심 근거로는 가치가 제한적이다
  - 따라서 기본 모드는 DB 최신 시장일까지 종료일을 확장하는 `최신 DB 데이터까지 확장 검증`으로 두고, `저장 기간 그대로 재현`은 보조 / 디버깅 모드로 낮추는 것이 맞다
  - 결과 row에는 재검증 mode, 저장 기간, 요청 기간, 실제 기간, 최신 시장일, 확장 일수, period coverage, curve provenance와 benchmark parity를 남겨 Final Review에서 어떤 데이터 기준의 evidence인지 구분하게 한다
  - 요청 종료일은 최신 DB 날짜까지 확장됐지만 실제 portfolio curve가 component cadence / intersection 때문에 따라오지 못하면 runtime 실행 성공과 별개로 `period_coverage=REVIEW`로 표시해야 한다
- Follow-up:
  - Practical Validation UI와 replay helper, validation result schema, code analysis 문서를 최신 runtime recheck 기준으로 수정했다

### 2026-05-11 - Practical Validation V2 P2 개발 문서가 필요하다
- User request:
  - 사용자가 P2 개발을 어떻게 진행할지 전용 개발 문서가 있는지 물었고, 없다면 정리하면서 `PROVIDER_CONNECTORS.md`도 만들길 요청함
- Interpreted goal:
  - P2 provider connector / macro connector / stress interpretation 작업이 기존 남은 구현 계획에 흩어져 있으므로, 구현 전에 실행 계획과 provider 세부 설계를 분리해 durable 문서로 남겨야 함
- Analysis result:
  - P2 전체 계획은 `CONNECTOR_AND_STRESS_PLAN.md`로 정리했다
  - Provider / DB / loader 상세 설계는 `PROVIDER_CONNECTORS.md`로 분리했다
  - 첫 구현 단위는 기존 `nyse_asset_profile`과 `nyse_price_history`를 bridge로 쓰는 Cost / Liquidity / ETF Operability connector가 가장 안전하다
  - holdings와 macro는 dedicated table / loader contract를 먼저 잡고, Practical Validation에서는 provider coverage summary와 compact evidence만 저장하는 방향이 맞다
- Follow-up:
  - 새 문서를 기존 Remaining Implementation Plan, Code Analysis README, Finance Doc Index에 연결했다

### 2026-05-11 - P2 provider 문서를 더 늘리지 않고 compact하게 관리한다
- User request:
  - 사용자가 ETF holdings, macro series, sentiment series 수집 계획 때문에 또 새 문서를 만들면 나중에 찾기 어려워질 수 있다고 지적함
- Interpreted goal:
  - P2 provider 개발 문서는 너무 세분화하지 말고, 이미 만든 provider connector plan 안에서 수집 / 저장 / 로딩 / Practical Validation 연결 계획을 함께 관리해야 함
- Analysis result:
  - 별도 `PROVIDER_DATA_COLLECTION_PLAN`은 만들지 않는다
  - `PROVIDER_CONNECTORS.md`가 ETF holdings, macro series, sentiment series의 collector 계획까지 소유한다
  - `CONNECTOR_AND_STRESS_PLAN.md`는 P2 전체 순서와 사용자-facing 진단 목표만 맡는다
- Follow-up:
  - provider connector plan에 `데이터 수집 구현 계획` section을 추가하고, Finance Doc Index / code analysis README의 설명을 보정했다

### 2026-05-11 - Practical Validation V2 P2-1 schema / ingestion field 계약
- User request:
  - 사용자가 P2-0 완료 후 P2-1 진행을 요청함
- Interpreted goal:
  - provider collector 구현 전에 12개 진단 정상화에 필요한 DB table, 필수 field, business key, fallback 기준을 먼저 확정해야 함
- Analysis result:
  - P2-1은 코드 구현이 아니라 schema / ingestion / loader 계약 확정 단계로 진행했다
  - 신규 table 후보는 `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`, `macro_series_observation` 4개다
  - 기존 `nyse_price_history`와 `nyse_asset_profile`은 actual provider data가 아니라 bridge / proxy source로만 읽는다
  - actual 판정은 진단별 최소 coverage 조건을 만족할 때만 가능하며, 부족하면 `REVIEW` 또는 `NOT_RUN` reason을 남긴다
- Follow-up:
  - 다음 작업은 P2-2로, `finance/data/db/schema.py`와 ETF operability 수집 / 저장 foundation을 실제 코드에 추가한다

### 2026-05-11 - Practical Validation V2 P2-2A ETF operability bridge/proxy 구현
- User request:
  - 사용자가 P2-2를 진행하되, 먼저 실제 provider actual 수집이 아니라 기존 데이터 기반 bridge/proxy 상태를 만드는 것으로 이해하면 되는지 확인하고 진행을 요청함
- Interpreted goal:
  - official ETF provider endpoint를 붙이기 전에 `etf_operability_snapshot` table, 기존 DB 기반 수집, UPSERT 저장, loader read path를 먼저 만들어야 함
- Analysis result:
  - `nyse_price_history`는 market price, 평균 거래량, 평균 거래대금 proxy를 제공할 수 있다
  - `nyse_asset_profile`은 일부 ETF의 total assets, bid, ask, fund family를 bridge evidence로 제공할 수 있다
  - 이 데이터는 actual provider data가 아니므로 `source=db_bridge`, `coverage_status=bridge|proxy|missing`으로 저장해야 한다
  - expense ratio, NAV, premium / discount, official leverage / inverse metadata는 아직 `missing_fields_json`에 남기고 P2-2B actual provider 수집에서 보강한다
- Follow-up:
  - 다음 구현은 official issuer source map을 endpoint 수준으로 검증하고 `source_type=official` row를 저장하는 P2-2B다

### 2026-05-12 - ETF provider source map을 DB로 관리하는 방향
- User request:
  - 사용자가 `nyse_etf`에 있는 ETF들을 기반으로 운용사 connector 정보를 일괄적으로 찾고, 테이블로 관리할 수 있는지 질문함
- Interpreted goal:
  - 새 ETF가 후보에 들어올 때마다 코드에 hardcoded source mapping을 직접 추가하는 흐름을 줄이고, Practical Validation이 "수집 가능 / 자동 탐색 필요 / 수동 connector 필요"를 구분해야 함
- Analysis result:
  - `nyse_etf`는 ticker / name / NYSE quote URL만 있으므로 provider endpoint 자체를 바로 제공하지 않는다
  - `nyse_asset_profile`의 fund family / long name과 issuer 공식 product list / endpoint 검증을 결합하면 source map 후보를 만들 수 있다
  - 검증된 endpoint는 `finance_meta.etf_provider_source_map`에 저장하고, ETF operability / holdings / exposure collector는 static map보다 이 verified source map을 먼저 사용하는 구조가 맞다
  - 금 현물 ETF는 일반 주식 holdings가 아니므로 `GLD`, `IAU`는 synthetic `commodity_gold` 100% gold exposure로 처리한다
- Follow-up:
  - source map discovery / Ingestion tab / Practical Validation gap 보강 버튼 연결을 구현했고, 현재 saved portfolio mix 기준 connector mapping gap이 해소되는 것을 확인했다

### 2026-05-12 - Operability REVIEW와 Sensitivity REVIEW의 의미 분리
- User request:
  - 사용자가 Provider Gap은 해소됐지만 `Operability / Cost / Liquidity`와 `Robustness / Sensitivity / Overfit`이 REVIEW로 남는 이유와 해결 범위를 질문함
- Interpreted goal:
  - 실제 데이터 부족, 판정 버그, 아직 별도 runtime이 필요한 sensitivity를 한 화면에서 구분할 수 있어야 함
- Analysis result:
  - `XLU`는 DB bridge row에 AUM / ADV / spread가 있었지만 `0.0` spread를 missing처럼 처리해 REVIEW가 났다
  - `QQQ`는 Invesco official row에 expense ratio만 있어 partial이었고, DB bridge의 AUM / ADV / spread를 병합하지 못해 REVIEW가 났다
  - Sensitivity는 drop-one / weight perturbation 일부는 계산됐지만 window perturbation이 실제 계산되지 않았고, strategy-specific parameter perturbation은 별도 runtime 작업으로 남겨야 했다
- Follow-up:
  - operability 병합 판정과 window perturbation 계산을 구현했고, strategy-specific sensitivity runtime은 후속 작업으로 유지했다

### 2026-05-12 - P2-6 stress / sensitivity 해석 보강 범위 확정
- User request:
  - 사용자가 P2-6에서 어떤 작업을 하는지 확인한 뒤 구현 진행을 요청함
- Interpreted goal:
  - stress / sensitivity 숫자표를 단순 PASS 표시로 끝내지 않고, Final Review에서 왜 REVIEW인지 또는 무엇을 더 확인해야 하는지 읽을 수 있게 해야 함
- Analysis result:
  - stress는 후보 기간과 겹치는 static event window 중 실제 curve로 계산된 구간과 compact monthly curve 때문에 계산되지 않은 구간을 분리해야 한다
  - sensitivity는 rolling, window, drop-one, weight tilt, strategy-specific runtime follow-up을 한 표에서 섞어 보이면 의미가 흐려지므로 해석 row로 구분해야 한다
  - strategy-specific perturbation은 아직 별도 runtime 후속이며, P2-6에서는 후속 필요 상태를 숨기지 않고 표시하는 것이 맞다
- Follow-up:
  - Stress / Sensitivity Interpretation row를 Practical Validation과 Final Review Robustness summary에 추가했다

### 2026-05-12 - backtest report의 candidate / validation 폴더는 현재 후보처럼 보이지 않게 내용 중심으로 재분류한다
- User request:
  - 사용자가 `candidates`와 `validation` 폴더의 문서들이 현재 프로그램 기준으로도 쓸모가 있는지, 삭제해야 하는지, 또는 나중에 쓰임이 있는지 검토를 요청함
  - archive 문서를 새로 늘리기보다 필요한 내용은 현재 구조에 맞게 마이그레이션하길 요청함
- Interpreted goal:
  - 과거 phase 번호를 기준으로 문서를 보존하지 않고, 실제로 나중에 참고할 수 있는 내용만 전략 log / validation smoke 문서로 흡수해야 함
- Analysis result:
  - Phase 21 계열 strategy rerun 문서는 독립 후보 문서로는 현재 source-of-truth가 아니지만, Value / Quality / Quality + Value 전략 log에 이미 핵심 근거가 남아 있으므로 standalone candidate report는 제거 가능하다
  - Phase 22 portfolio candidate 문서는 현재 후보가 아니라 weighted portfolio builder / saved replay 검증 fixture로 읽어야 하므로, portfolio candidate report가 아니라 runtime validation note로 재작성하는 것이 맞다
  - Quarterly contract와 Global Relative Strength smoke 문서는 현재 코드 이해와 회귀 검증에 가치가 있으므로 유지하되, phase 번호 파일명이 아니라 기능 중심 파일명으로 정리한다
- Follow-up:
  - `candidates/point_in_time/` 구조를 제거하고, weighted portfolio replay 검증과 validation smoke report를 내용 중심 이름으로 마이그레이션했다

### 2026-05-12 - data_architecture 문서는 삭제가 아니라 docs/data로 정식 승격한다
- User request:
  - 사용자가 backtest report 정리 이후 `data_architecture` 폴더도 현재 문서 체계에 맞춰 어떻게 마이그레이션할지 검토하고 진행해 달라고 요청함
- Interpreted goal:
  - archive를 늘리지 않고, 현재에도 유효한 데이터 / DB 의미 문서를 새 장기 지식 구조인 `.aiworkspace/note/finance/docs/data/`로 흡수해야 함
- Analysis result:
  - `DATA_FLOW_MAP`, `DB_SCHEMA_MAP`, `TABLE_SEMANTICS`, `DATA_QUALITY_AND_PIT_NOTES`는 모두 현재 Practical Validation P2 provider / DB / loader 구조와 맞는 핵심 문서라 삭제 대상이 아니다
  - 기존 `data_architecture/` 루트 폴더를 유지하면 `docs/data/`와 canonical 위치가 갈라지므로, 상세 문서 4개를 이름 그대로 `docs/data/`로 옮기는 것이 맞다
  - `docs/data/README.md`는 단순 table 목록이 아니라 읽는 순서, source-of-truth, 갱신 조건을 함께 가진 data 문서 index가 되어야 한다
- Follow-up:
  - 기존 `.aiworkspace/note/finance/data_architecture/` 폴더를 제거하고, data 문서 canonical 위치를 `.aiworkspace/note/finance/docs/data/`로 갱신했다

### 2026-05-13 - Reference / Guides와 Glossary의 문서 의존성 확인
- User request:
  - 사용자가 문서 삭제 전 `Reference > Guides` 화면이 운영 정책 md 파일을 읽는 구조인지 확인하고, 실제 의존 문서는 삭제하지 말아야 한다고 요청함
- Interpreted goal:
  - 앱에서 직접 읽는 문서와 화면에 참고 경로로만 노출되는 문서를 구분해, legacy 문서 삭제 전에 끊기는 reference를 없애야 함
- Analysis result:
  - `Reference > Guides`는 md 본문을 읽지 않고 `app/web/reference_guides.py` 안의 hardcoded guide text와 문서 경로 목록을 렌더링한다
  - `Reference > Glossary`는 `GLOSSARY_DOC_PATH.read_text()`로 glossary md를 실제 읽는다
  - 따라서 Guides 경로 목록은 새 docs 기준으로 바꾸고, Glossary는 새 `.aiworkspace/note/finance/docs/GLOSSARY.md`에 본문을 승격한 뒤 코드 읽기 경로를 바꾸는 것이 맞다
- Follow-up:
  - 1차 작업에서 Guides reference path와 Glossary read path를 새 docs 구조로 전환했다

### 2026-05-13 - 삭제 전 2차 legacy 문서 흡수 기준
- User request:
  - 사용자가 삭제 전 마지막 마이그레이션 권장 작업의 2차를 진행해 달라고 요청함
- Interpreted goal:
  - legacy root / operations / research / support 문서에서 새 구조에 남길 핵심만 흡수하고, 3차 삭제 때 안전하게 지울 수 있는 후보와 유지해야 할 런타임 의존성을 분리해야 함
- Analysis result:
  - root current-state 문서는 새 `docs/` 4개 축으로 대체 가능하다
  - operations registry guide는 여러 파일로 유지하기보다 `registries/README.md` 하나에 current Selection V2 / legacy compatibility를 모으는 것이 낫다
  - runtime artifact hygiene, external research, config externalization은 runbook 원칙으로 축약하면 충분하다
  - `practical_validation_stress_windows_v1.json`은 문서가 아니라 앱이 읽는 reference data라 삭제 대상이 아니며 새 `docs/data/` 위치로 이동해야 한다
  - support track의 plugin / skill / automation 문서는 현재 canonical이 아니며, 필요한 원칙은 `AGENTS.md`, `docs/runbooks/`, `agent/` 문서로 충분하다
- Follow-up:
  - 2차 작업에서 registry / runbook / data / task / agent 문서를 갱신하고 stress window code path를 새 위치로 바꿨다

### 2026-05-13 - 3차 legacy 문서 제거와 template 보존
- User request:
  - 사용자가 삭제 전 마이그레이션 1차 / 2차 이후 마지막 3차 작업 진행을 요청함
- Interpreted goal:
  - 새 docs 구조로 대체된 legacy 문서 tree를 실제로 제거하되, 런타임이나 helper가 읽는 파일은 깨지지 않게 유지해야 함
- Analysis result:
  - root current-state docs, `archive/`, `operations/`, 남은 `research/`, `support_tracks/`는 새 구조에 흡수 완료되어 삭제 가능하다
  - 기존 `phases/phase1`~`phase36` 상세 문서는 현재 구조와 맞지 않는 legacy history라 새 phase skeleton만 남기는 것이 맞다
  - `PHASE_PLAN_TEMPLATE.md`, `PHASE_TEST_CHECKLIST_TEMPLATE.md`는 phase helper가 읽는 source file이므로 삭제가 아니라 `docs/runbooks/templates/`로 이동하는 것이 맞다
  - `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`, `registries/`, `saved/`, active task docs는 유지해야 한다
- Follow-up:
  - 3차 작업에서 legacy tree와 legacy phase docs 제거, template 이동, helper path 갱신, 삭제 후 검증을 진행했다

### 2026-05-13 - README는 프로젝트 첫 관문 문서로 재작성한다
- User request:
  - 사용자가 프로젝트 초창기 README가 현재 finance 제품과 문서 체계에 맞지 않아 대규모 수정을 요청했고, 기존 내용을 억지로 살릴 필요 없이 처음부터 다시 써도 된다고 확인함
- Interpreted goal:
  - README를 상세 구현 로그가 아니라, 프로젝트 목적 / 사용 흐름 / 실행 방법 / 문서 위치 / 데이터 경계를 빠르게 이해하는 첫 관문으로 재정의해야 함
- Analysis result:
  - README에는 현재 핵심 workflow인 `Ingestion -> Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard`를 플로우차트로 보여주는 것이 가장 효과적이다
  - 전략별 세부 구현, legacy Candidate Review / Portfolio Proposal 세부 흐름, active task 진행 로그는 README에 길게 두지 않고 `.aiworkspace/note/finance/docs/`와 active task 문서로 연결해야 한다
  - README에는 live trading / broker order / auto rebalance가 현재 범위 밖이라는 non-goal을 명확히 두어 제품 경계를 오해하지 않게 해야 한다
- Follow-up:
  - README를 현재 제품 boundary, Finance Console navigation, quick start, repository map, documentation map, data persistence boundary, development principles 중심으로 재작성했다

### 2026-05-13 - root handoff log 비대화 방지 기준을 명시한다
- User request:
  - 사용자가 `WORK_PROGRESS.md`와 `QUESTION_AND_ANALYSIS_LOG.md`가 다시 너무 커질 수 있는지 우려하며, 그대로 둘지 지침을 추가할지 의견을 물음
- Interpreted goal:
  - root log를 유지하되 상세 작업 기록이 다시 누적되지 않도록 Codex가 따를 수 있는 기준을 명확히 해야 함
- Analysis result:
  - root log는 지도 역할로 두고, 상세 구현 과정 / 긴 분석 / 실행 로그는 active task 문서로 보내는 기준을 문서화하는 것이 좋다
- Follow-up:
  - `AGENTS.md`와 `docs/runbooks/README.md`에 root handoff log 기준을 추가했다

### 2026-05-13 - Skill System Rebuild 1차 범위 확정
- User request:
  - 사용자가 Notion의 skill / plugin 가이드를 기준으로 현재 finance skill을 검토하고, 1차 작업 진행을 요청함
- Interpreted goal:
  - 새 docs / tasks 구조에 맞지 않는 stale skill 경로를 먼저 제거하고, 더 이상 쓰지 않을 phase-management skill을 정리해야 함
- Analysis result:
  - 기존 skill들은 역할 자체는 유효하지만 legacy root 문서, `code_analysis`, `data_architecture`, `backtest_reports`, `phase<N>` 경로를 참조하고 있어 1차 보정이 필요했다
- Follow-up:
  - 1차에서 domain skill과 doc-sync skill의 문서 경로를 새 구조로 보정하고, `finance-phase-management`를 삭제했다

### 2026-05-13 - Skill System Rebuild 2차 workflow / domain 경계
- User request:
  - 사용자가 skill 개편 2차 작업 진행을 요청함
- Interpreted goal:
  - task 운영과 실제 코드 구현 skill을 분리해, Codex가 새 docs / tasks 구조에서 일관되게 작업을 시작하도록 해야 함
- Analysis result:
  - `finance-doc-sync`에 task lifecycle까지 맡기면 작업 시작/진행과 closeout alignment가 섞이므로 별도 workflow skill이 필요하다
  - 새 `finance-task-management`가 task 분류, active task 문서, root handoff log, domain skill routing을 맡고, Backtest UI / DB / factor / strategy skill은 구현 도메인만 맡는 구조가 적절하다
- Follow-up:
  - `finance-task-management`를 생성하고 기존 finance skill description / boundary와 `AGENTS.md` skill routing을 새 구조에 맞춰 보정했다

### 2026-05-13 - 프로젝트 전용 skill은 repo-local source로 관리한다
- User request:
  - 사용자가 현재 `~/.codex/skills`에 둔 프로젝트 skill을 repo 안에서 관리하는 것이 맞는지 확인했고, repo 안에서 관리하는 방향에 동의한 뒤 3차 진행을 요청함
- Interpreted goal:
  - skill 내용이 로컬 설정에만 남지 않고, 프로젝트 변경사항으로 리뷰 / 커밋 / 재현 가능해야 함
- Analysis result:
  - `~/.codex/skills`는 현재 Codex runtime용 설치본으로 적합하지만 프로젝트 source-of-truth로는 약하다
  - finance 전용 skill 원본은 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`에 두고, 필요 시 global skill 위치로 동기화하는 구조가 더 안정적이다
  - `SKILL.md`는 짧게 유지하고 domain 세부 규칙은 `references/`로 분리하는 것이 Notion skill 가이드와 맞다
- Follow-up:
  - 3차에서 6개 finance skill을 repo-local source로 추가하고 global 설치본을 동기화했다

### 2026-05-13 - AI workspace top-level 구조로 문서와 plugin을 통합한다
- User request:
  - 사용자가 `.aiworkspace/` 아래에 `note/finance`와 `plugins/quant-finance-workflow`를 두는 구조를 제안하고, 이 방향으로 마이그레이션을 요청함
- Interpreted goal:
  - AI / Codex 작업용 문서와 repo-local plugin source를 한 top-level workspace로 묶어 프로젝트 루트의 의미를 더 명확하게 해야 함
- Analysis result:
  - `.aiworkspace/note/finance`는 기존 finance 문서 / task / registry / saved / run_history의 새 canonical 위치로 적절하다
  - `.aiworkspace/plugins/quant-finance-workflow`는 프로젝트 전용 Codex skill / script source의 새 canonical 위치로 적절하다
  - 기존 path 참조가 많으므로 이동과 함께 코드 / 문서 / skill path 갱신, stale path grep, helper script / skill validation이 필요하다
- Follow-up:
  - AI Workspace Migration active task를 열고 폴더 이동과 주요 path 갱신을 진행했다

### 2026-05-13 - finance skill taxonomy는 4 workflow + 4 domain으로 고정한다
- User request:
  - 사용자가 처음 합의한 skill 구조와 실제 완료된 skill 목록이 다르다고 지적하고, `finance-backtest-candidate-refinement` 제거 여부를 질문함
- Interpreted goal:
  - phase worktree에서 쓰는 finance skill을 요청 접수 / 문서 동기화 / 통합 검토 / runbook 유지와 구현 domain skill로 명확히 분리해야 함
- Analysis result:
  - `finance-task-management`는 역할이 넓고 이름도 active task 운영에 치우치므로 `finance-task-intake`가 더 정확하다
  - `finance-integration-review`와 `finance-runbook-maintainer`는 `finance-doc-sync`나 intake에 섞지 않고 별도 workflow skill로 두는 것이 맞다
  - `finance-backtest-candidate-refinement`는 candidate-search worktree 성격과 겹치므로 phase worktree 공통 skill에서 제거하는 것이 맞다
- Follow-up:
  - repo-local plugin과 global mirror를 4 workflow + 4 domain skill 구조로 보정하기로 했다

### 2026-05-14 - Streamlit UI를 API + React/Next.js로 분리할지 조사한다
- User request:
  - 사용자가 현재 Streamlit UX/UI의 상용화 한계를 우려하며, Python quant engine은 유지하고 React/Next.js 등 별도 UI/API 구조를 쓰는 방향을 현재 기능/약점 분석, 유사 서비스 벤치마킹, 기능 후보/추천안까지 조사해 달라고 요청함
- Interpreted goal:
  - 당장 UI를 갈아엎는 결정이 아니라, product research 2단계 산출물로 현재 구조와 외부 패턴을 근거화해 다음 개발 우선순위를 정해야 함
- Analysis result:
  - Streamlit은 내부 research / ops console로 유지하는 것이 합리적이지만, 상용 UI 후보 화면은 API contract와 read-only Next.js pilot으로 점진 분리하는 방향이 가장 안전하다
  - full rewrite보다 `API/service contract extraction -> Selected Portfolio Dashboard read-only pilot -> job API` 순서가 리스크 대비 학습효과가 크다
- Follow-up:
  - 상세 산출물은 `.aiworkspace/note/finance/researches/active/2026-05-ui-platform-research/`에 작성했다

### 2026-05-14 - Product research 3단계는 실행 복기를 skill에 반영한다
- User request:
  - 사용자가 2단계 실제 research 운영 이후 3단계인 반복 후 스킬강화를 진행해 달라고 요청하고, 필요한 질문이 있으면 정리해서 물어보는 방식이 맞는지 확인함
- Interpreted goal:
  - 새 리서치를 하는 것이 아니라, 직전 research run에서 생긴 혼동과 개선점을 finance product research skill에 반영해야 함
- Analysis result:
  - 이번 run에서 특히 `RECOMMENDATION.md`의 1차 실행 범위와 장기 방향 구분, Streamlit 내부 콘솔 의미, research worktree stale 구조 처리, research 본문과 skill hardening task 위치 구분이 보강 포인트였다
- Follow-up:
  - `product-research-skill-stage3` task를 열고 product research 관련 4개 skill과 reference template을 보강했다

### 2026-05-14 - Backtest Result / Strategy Report 제품화를 조사한다
- User request:
  - 사용자가 4단계 반복 리서치 주제로 1번인 Backtest Result / Strategy Report 제품화 조사를 진행해 달라고 요청함
- Interpreted goal:
  - 현재 백테스트 결과와 report workspace를 audit하고, 외부 backtest/report 제품 패턴을 바탕으로 다음 기능 후보와 추천 구현 범위를 정리해야 함
- Analysis result:
  - 현 프로젝트는 evidence-first report 재료가 충분하지만, 아직 `BacktestReportPack` 같은 안정적인 report artifact contract가 없다
  - QuantConnect, QuantRocket, TradingView, QuantStats/pyfolio, NautilusTrader 패턴상 결과 화면, raw data, durable report를 분리하는 것이 적절하다
- Follow-up:
  - 다음 구현 후보는 `BacktestReportPack + Markdown report draft generator`이며, 상세 근거는 `.aiworkspace/note/finance/researches/active/2026-05-backtest-report-productization/RECOMMENDATION.md`에 정리했다

### 2026-05-14 - Product research 5단계는 plugin workflow로 고정한다
- User request:
  - 사용자가 지금까지의 리포트와 리서치가 플러그인을 만들기 위한 준비였다고 정리하고, 5단계 진행을 요청함
- Interpreted goal:
  - 새 리서치를 더 쓰는 것이 아니라, 검증된 product research 흐름을 기존 `quant-finance-workflow` plugin 안에서 반복 가능한 workflow로 만들어야 함
- Analysis result:
  - 별도 product research plugin 분리는 아직 이르며, 먼저 orchestration skill과 research bundle helper script를 기존 plugin에 넣는 것이 안전하다
  - actual research body는 계속 `researches/active/<research-id>/`, workflow/script/skill 변경 기록은 `tasks/active/product-research-plugin-stage5/`에 둔다
- Follow-up:
  - `finance-product-research-workflow`, `bootstrap_product_research_bundle.py`, `check_product_research_bundle.py`를 추가했고 다음 반복 run부터 이 경로를 사용한다

### 2026-05-14 - Product research는 별도 plugin으로 분리한다
- User request:
  - 사용자가 `finance-product-research-workflow`가 플러그인인지 확인한 뒤, 기존 workflow plugin에 함께 있으면 복잡해질 수 있으니 리서치용 별도 plugin으로 분리해 달라고 요청함
- Interpreted goal:
  - product research skill과 helper script의 source-of-truth를 `quant-finance-workflow`에서 분리해 독립 plugin으로 관리해야 함
- Analysis result:
  - `quant-finance-workflow`는 구현/통합/운영 workflow 중심으로 남기고, `quant-finance-product-research`는 research bundle 생성/검증, audit, benchmark, opportunity synthesis를 소유하는 경계가 더 명확하다
- Follow-up:
  - `.aiworkspace/plugins/quant-finance-product-research/`를 만들고 marketplace에 등록했으며, global mirror와 검증을 완료했다

### 2026-05-20 - Service contract 테스트를 추가한다
- User request:
  - 사용자가 UI와 engine 분리 후속 작업으로 다음 task 진행을 요청함
- Interpreted goal:
  - 분리된 service boundary가 UI-facing payload contract를 안정적으로 유지하는지 DB / Streamlit 화면 실행 없이 검증해야 함
- Analysis result:
  - 현재 `.venv`에는 `pytest`가 없으므로 표준 `unittest`가 가장 작은 검증 단위다
  - 우선 Practical Validation handoff와 Final Review evidence read model처럼 UI가 바로 소비하는 반환 형태를 contract test로 고정하는 것이 적절하다
- Follow-up:
  - `tests/test_service_contracts.py`를 추가하고 runbook / project map / script map에 focused test 위치와 명령을 기록했다

### 2026-05-20 - Provider gap collection을 UI에서 분리한다
- User request:
  - 사용자가 앞서 남겨둔 다음 작업인 Provider gap collection 분리를 진행해 달라고 요청함
- Interpreted goal:
  - Practical Validation 화면이 provider gap 수집 계획과 ingestion job 실행 책임까지 직접 들고 있지 않도록 service boundary로 옮겨야 함
- Analysis result:
  - UI에는 Provider Data Gaps 표시, 버튼, session state 반영만 남기고, source map lookup / collectable gap 판단 / job orchestration / run history metadata는 Practical Validation service가 맡는 구조가 적절하다
- Follow-up:
  - `app/services/backtest_practical_validation.py`로 provider gap row / plan / run orchestration을 이동하고, mocked service contract tests를 추가했다

### 2026-05-20 - Practical Validation replay helper를 service로 이동한다
- User request:
  - 사용자가 다음 작업 진행을 요청함
- Interpreted goal:
  - Provider gap 다음 slice로 남아 있던 replay plan / actual replay result 책임을 UI 파일 경계 밖으로 옮겨야 함
- Analysis result:
  - replay helper는 이미 Streamlit-free였으므로 얇은 wrapper보다 파일 자체를 `app/services`로 이동하는 것이 책임 위치를 더 명확히 한다
  - UI는 mode 선택, 실행 버튼, session state, 결과 표시만 유지하고 recheck period plan과 actual replay result construction은 service가 맡는 구조가 적절하다
- Follow-up:
  - `app/services/backtest_practical_validation_replay.py`로 이동하고 replay plan / blocked replay contract tests를 추가했다

### 2026-05-27 - Runtime wrapper cleanup은 result bundle helper부터 분리한다
- User request:
  - 사용자가 UI-engine boundary cleanup의 다음 단계 진행을 요청함
- Interpreted goal:
  - `app/runtime/backtest.py`를 바로 대규모로 쪼개지 않고 함수군과 public API를 확인한 뒤, 낮은 위험 split부터 적용해야 함
- Analysis result:
  - public runtime wrapper와 Real-Money / strict policy surface는 아직 `app.runtime.backtest` 호환성이 중요하므로 유지한다
  - 순수 result bundle 생성 helper는 DB / strategy 실행에 관여하지 않아 가장 안전한 첫 split 후보였다
- Follow-up:
  - `app/runtime/backtest_result_bundle.py`로 `build_backtest_result_bundle`을 이동하고 compatibility / shape contract tests를 추가했다

### 2026-05-27 - UI-engine boundary cleanup은 hard fail 기준으로 마감한다
- User request:
  - 사용자가 다음 단계 진행을 요청함
- Interpreted goal:
  - Task 6~8에서 정리한 service/runtime boundary가 다시 흐트러지지 않도록 lint, test, docs 기준을 강화해야 함
- Analysis result:
  - `app.services/app.runtime -> app.web` import는 더 이상 transitional advisory가 아니라 경계 위반으로 보는 것이 맞다
  - 이 task는 화면 변경이 아니라 helper script / contract test / runbook hardening이므로 browser QA보다 unit/lint 검증이 적절하다
- Follow-up:
  - `check_ui_engine_boundary.py`가 `app_web_import`를 hard violation으로 보고하고, phase는 closeout 상태가 됐다

### 2026-05-28 - Finance Console은 canonical `.aiworkspace/note/finance` 데이터를 읽어야 한다
- User request:
  - 사용자가 브라우저 실행 후 Overview와 여러 화면이 `registries`, `saved` 경로를 최신 위치에서 찾지 못한다고 수정 요청함
- Interpreted goal:
  - 예전 `.note/finance` 직접 참조를 제거하고, 현재 worktree의 `.aiworkspace/note/finance`를 app runtime / jobs / UI가 공통으로 읽게 해야 함
- Analysis result:
  - 여러 runtime / job / web helper가 `PROJECT_ROOT / ".note" / "finance"`를 직접 만들고 있었고, 특히 app/runtime 파일은 worktree parent 기준으로 잘못 계산될 위험이 있었다
  - `app/workspace_paths.py`를 canonical path helper로 두는 것이 registry / saved / run-history 참조를 가장 작게 통일하는 방법이다
- Follow-up:
  - 서비스 계약 테스트에 canonical path contract를 추가했고, Browser smoke에서 Overview가 실제 JSONL 카운트와 Top 3 후보를 표시하는 것을 확인했다

### 2026-05-28 - 실전 투자 판단 workflow의 약점과 개선 방향을 먼저 정리한다
- User request:
  - 사용자가 현재 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름이 실전 투자에는 부족하다고 보고, 상용 프로젝트와 비교해 약점 / 근거 / 개선 방향을 먼저 정리해 달라고 요청함
- Interpreted goal:
  - 바로 개발하지 않고 product direction research bundle을 열어 현재 약점, 외부 benchmark pattern, 기능 후보, 추천 가이드라인을 정리해야 함
- Analysis result:
  - 현재 흐름은 유지하되 `Investability Evidence Packet`, stricter validation gate, assumptions / limitations disclosure, source-of-truth breadcrumb를 먼저 만드는 것이 가장 높은 우선순위다
  - broker 연결, live approval, auto rebalance는 현재 경계 밖으로 유지한다
- Follow-up:
  - 산출물은 `.aiworkspace/note/finance/researches/active/2026-05-investable-workflow-gap-analysis/RECOMMENDATION.md`와 관련 bundle 문서에서 이어서 보면 된다

### 2026-05-28 - Final Review에서 investability evidence packet을 먼저 구현한다
- User request:
  - 사용자가 앞서 정리한 큰 개발 흐름을 실제 작업으로 진행해 달라고 요청함
- Interpreted goal:
  - 새 JSONL 저장소나 사용자 메모 저장 기능을 늘리지 않고, Final Review의 판단 근거와 selected-route gate를 먼저 강화해야 함
- Analysis result:
  - 기존 validation / robustness / paper observation evidence를 Streamlit-free packet read model로 묶고, critical gap이 있으면 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장을 차단하는 V1이 가장 작은 안전한 구현 단위다
- Follow-up:
  - 구현 기록과 검증 결과는 `.aiworkspace/note/finance/tasks/active/investability-evidence-packet-v1/`에서 확인한다

### 2026-05-29 - Selected Dashboard recheck 전 preflight를 하나로 묶는다
- User request:
  - 사용자가 Phase 12 다음 단계 진행을 요청함
- Interpreted goal:
  - Performance Recheck 실행 전 readiness와 symbol freshness가 따로 보이는 문제를 하나의 read-only operations preflight로 정리해야 함
- Analysis result:
  - Final Review embedded replay contract를 우선 사용하고 Current Candidate Registry를 fallback으로 쓰는 source priority가 필요하다
  - stale / missing price, missing replay contract, DB latest date error는 ready가 아니며 각각 review / needs data / blocked로 드러나야 한다
- Follow-up:
  - `selected_recheck_operations_preflight_v1`을 구현했고, 다음은 selected provider evidence staleness / coverage contract다

### 2026-05-29 - Selected provider evidence의 stale / partial 상태를 PASS에서 분리한다
- User request:
  - 사용자가 Phase 12 다음 단계 진행을 요청함
- Interpreted goal:
  - Selected Dashboard의 provider evidence가 오래되었거나 부분 coverage일 때도 충분한 근거처럼 보이는 문제를 차단해야 함
- Analysis result:
  - freshness date, source type, coverage mode, coverage weight, required evidence area를 하나의 staleness contract로 묶는 것이 가장 작은 read-only 강화 단위다
  - missing required provider area와 partial / stale evidence는 투자 가능 근거가 아니라 review 또는 needs input으로 표시되어야 한다
- Follow-up:
  - `selected_provider_evidence_staleness_contract_v1`을 구현했고, 다음은 recheck comparison review signal policy다

### 2026-05-29 - Review Signals의 성과 threshold owner를 Recheck Comparison으로 고정한다
- User request:
  - 사용자가 Phase 12 다음 단계 진행을 요청함
- Interpreted goal:
  - Review Signals와 Recheck Comparison이 CAGR / MDD / benchmark spread threshold를 중복 계산하지 않게 해야 함
- Analysis result:
  - Review Signals는 signal board이고, 성과 약화 판단의 policy owner는 Recheck Comparison으로 두는 것이 맞다
  - preflight / provider / comparison route를 하나의 read-only signal board로 묶으면 missing, stale, partial, failed recheck가 Clear로 숨지 않는다
- Follow-up:
  - `selected_review_signal_policy_v1`을 구현했고, 다음은 allocation drift evidence boundary다

### 2026-05-29 - Dossier / Continuity / Timeline source를 같은 Final Decision V2 row로 고정한다
- User request:
  - 사용자가 Phase 12 다음 단계 진행을 요청함
- Interpreted goal:
  - Decision Dossier, Continuity, Timeline, Review Signals가 서로 다른 source처럼 보이거나 session evidence를 durable monitoring history처럼 보이게 하는 gap을 줄여야 함
- Analysis result:
  - 새 저장소가 아니라 read model metadata로 `selected_decision_source_consistency_v1`을 붙이는 것이 가장 작은 안전한 구현 단위다
  - timeline source contract가 현재 selected decision row와 다르면 Continuity는 blocked issue로 표시해야 한다
- Follow-up:
  - 12-6 구현은 완료했고, 다음은 Phase 12 integrated QA / closeout이다

### 2026-05-29 - Phase 12는 통합 QA 후 완료 상태로 닫는다
- User request:
  - 사용자가 Phase 12 다음 단계 진행을 요청함
- Interpreted goal:
  - 12-1부터 12-6까지의 selected monitoring / recheck operations hardening이 전체 검증과 문서 closeout을 통과해야 함
- Analysis result:
  - compile, full service contracts, UI / engine boundary, finance hygiene, diff, storage boundary checks를 통과하면 Phase 12는 완료로 볼 수 있다
  - 다음 작업은 새 구현이 아니라 Phase 8-12 1차 hardening cycle 전체를 정리하는 Phase 13 closeout으로 넘기는 것이 맞다
- Follow-up:
  - Phase 12 closeout summary를 `phases/done/`에 남기고 roadmap / index를 Phase 13 next target으로 갱신했다

### 2026-05-29 - Phase 13은 1차 hardening cycle closeout board로 연다
- User request:
  - 사용자가 Phase 13 작업 진행을 요청함
- Interpreted goal:
  - Phase 8~12 약점 개선 결과를 하나의 1차 사이클로 검증 / 정리하는 마지막 phase를 시작해야 함
- Analysis result:
  - 바로 새 기능을 추가하기보다 improvement inventory, gate QA, storage audit, docs / runbook sync, residual risk triage, final closeout 순서로 진행하는 것이 맞다
  - broker/account/order/auto rebalance와 memo-like storage는 Phase 13 범위 밖으로 유지한다
- Follow-up:
  - Phase 13 board를 열었고 다음 작업은 `phase13-cycle-inventory-v1`이다

### 2026-05-30 - Backtest Analysis는 Stage와 검증 체크포인트를 분리해서 읽는다
- User request:
  - 사용자가 Backtest Analysis 결과 화면에서 Runtime Payload, Data Trust, Practical Validation handoff, Real-Money의 legacy 단계 표현이 혼란스럽다고 지적하고 1~6단계 개선을 요청함
- Interpreted goal:
  - 새 저장 기능을 늘리지 않고, Backtest Analysis를 후보 생성 화면답게 정리하며 검증 기준은 `검증 체크포인트` 언어로 분리해야 함
- Analysis result:
  - `Stage`는 Backtest Analysis / Practical Validation / Final Review / Selected Dashboard로 유지하고, Result Integrity / Candidate Readiness 같은 검증 기준은 별도 checkpoint로 표시하는 것이 맞다
  - Practical Validation handoff는 검증 metric이 아니라 Next Action으로 배치해야 한다
- Follow-up:
  - 구현 기록은 `.aiworkspace/note/finance/tasks/active/backtest-analysis-ux-checkpoint-v1/`에서 확인한다
### 2026-05-28 - Overview를 market intelligence entry point로 바꿀 수 있는지 조사한다
- User request:
  - 사용자가 Overview에 일/주/月 top movers, 월별 sector / industry Top N, FOMC/earnings calendar 탭을 넣을 수 있는지 개발 전 조사와 청사진을 요청함
- Interpreted goal:
  - 현재 후보 우선순위 Overview를 유지하면서, DB-backed 시장 스캔과 이벤트 캘린더를 어떤 순서로 구현할지 판단해야 함
- Analysis result:
  - Coverage 1000/2000 top movers와 sector / industry leadership은 기존 `nyse_asset_profile`과 `nyse_price_history`로 바로 구현 가능하다
  - 이벤트 캘린더는 FOMC는 공식 source로 가능하지만, earnings는 provider/API/persistence를 먼저 정해야 한다
- Follow-up:
  - 리서치 bundle은 `.aiworkspace/note/finance/researches/active/2026-05-overview-market-intelligence/`에 있고, 다음 구현은 사용자가 Overview 탭 구조를 승인하면 시작한다

### 2026-05-28 - Overview Market Intelligence 1차 slice를 구현한다
- User request:
  - 사용자가 scope lock 포함 전체 흐름을 확인한 뒤 실제 작업 진행을 요청함
- Interpreted goal:
  - 무료 API / 크롤링 원칙을 지키되, 첫 구현은 이미 적재된 local DB만 사용해 Overview를 시장 스캔 entry point로 바꿔야 함
- Analysis result:
  - `nyse_asset_profile`과 `nyse_price_history`만으로 Coverage 1000/2000 movers와 sector / industry leadership은 구현 가능하다
  - 화면에서 직접 원격 수집하지 않고, Events 탭은 ingestion 후속 slice를 받는 placeholder로 두는 것이 현재 구조와 가장 맞다
- Follow-up:
  - `app/services/overview_market_intelligence.py`와 Overview tabs를 추가했고, FOMC / earnings calendar ingestion은 다음 task 후보로 남겼다

### 2026-05-28 - S&P 500 daily movers는 전일 종가 대비 intraday snapshot으로 시작한다
- User request:
  - 사용자가 Coverage 500 대신 S&P 500, daily 기준은 전일 종가 대비, intraday 확장은 먼저 S&P 500만 진행하자고 확정함
- Interpreted goal:
  - Top1000 / Top2000 EOD ranking은 유지하되, S&P 500 daily는 무료 provider 기반 준실시간 snapshot을 저장 후 Overview에서 빠르게 읽어야 함
- Analysis result:
  - `nyse_asset_profile.market_cap` 기준 Top1000 / Top2000은 현재 profile snapshot 기준임을 UI metadata와 docs에 드러내야 한다
  - S&P 500 current constituents와 intraday return은 별도 table로 분리해 survivorship / provider delay 위험을 명시하는 것이 맞다
- Follow-up:
  - S&P 500 universe / intraday snapshot collector와 Overview controls를 구현했고, Top1000 / Top2000 intraday 확장은 실제 속도와 rate limit 확인 뒤 진행한다

### 2026-05-28 - Market Movers update click TypeError 수정
- User request:
  - 사용자가 Overview `Update Daily Snapshot` 클릭 시 `run_collect_sp500_intraday_snapshot` 호출 지점에서 에러가 난다고 제보함
- Interpreted goal:
  - 브라우저에서 재현 가능한 UI click path를 안정화하고, 5분 상태 갱신 UX는 유지해야 함
- Analysis result:
  - 실행 중인 Streamlit 프로세스가 이전 job-wrapper 함수 시그니처를 메모리에 잡고 있어 새 `quote_batch_size` 인자를 못 받는 것이 직접 원인이었다
  - 자동 새로고침 fragment 안에 수집 버튼과 `st.rerun()`이 같이 있던 구조도 불안정하므로 fragment는 DB 읽기 전용으로 분리하는 편이 맞다
- Follow-up:
  - Overview button action을 fragment 밖으로 옮기고, stale import 상황에서도 지원되는 인자만 넘기도록 호환 호출을 추가했다

### 2026-05-28 - Top1000 / Top2000 daily intraday refresh 확장
- User request:
  - 사용자가 S&P 500 refresh가 정상 작동하면 Top1000 / Top2000도 같은 방향으로 확장해 달라고 요청함
- Interpreted goal:
  - daily movers의 전일 종가 대비 quote snapshot을 S&P 500뿐 아니라 market-cap coverage에도 적용해야 함
- Analysis result:
  - 기존 `market_intraday_snapshot`은 `universe_code`가 unique key에 포함되어 있어 schema 변경 없이 `TOP1000`, `TOP2000` row를 저장할 수 있다
  - Top1000 / Top2000 universe는 current `nyse_asset_profile.market_cap` ranking 기준이며, quote-fast path는 충분히 빠르지만 yfinance OHLCV fallback은 넓은 coverage에서 오래 걸릴 수 있어 UI에서는 자동 fallback하지 않는 편이 맞다
- Follow-up:
  - generic market intraday collector / job wrapper를 추가하고 Overview daily view가 Top1000 / Top2000 intraday snapshot을 우선 읽도록 확장했다

### 2026-05-28 - Task 4 Market Event DB 구조를 먼저 만든다
- User request:
  - 사용자가 재정리된 Overview Market Intelligence phase 기준으로 Task 4 작업 진행을 요청함
- Interpreted goal:
  - FOMC와 earnings collector를 붙이기 전에 공통 event calendar table과 persistence contract를 먼저 만들어야 함
- Analysis result:
  - event calendar는 price fact가 아니라 Overview / ingestion metadata이므로 `finance_meta`에 두는 것이 맞다
  - 반복 수집 중복을 막으려면 요청된 공통 컬럼 외에 내부 business key인 `event_key`가 필요하다
- Follow-up:
  - `market_event_calendar` schema, normalized UPSERT, date-range read helper, service contract tests를 추가했다. 다음 구현 단위는 FOMC collector다

### 2026-05-28 - Overview Market Intelligence 2차 production baseline을 진행한다
- User request:
  - 사용자가 1차 구현 후 2차 작업부터 진행하자고 요청함
- Interpreted goal:
  - 새 source를 늘리기 전에 현재 Overview Market Movers와 Events가 최신성, 부분 실패, source 신뢰도, stale estimate를 명확하게 보여줘야 함
- Analysis result:
  - Market Movers refresh state는 기존 intraday snapshot metadata로 계산 가능하고, Events official / estimate 구분도 schema 변경 없이 `event_type`과 `source`에서 read model로 파생할 수 있다
- Follow-up:
  - 2차 baseline 구현과 acceptance checklist를 완료했다. 3차에서는 earnings provider estimate를 official/company 또는 대체 free source와 비교하는 source validation이 필요하다

### 2026-05-28 - Overview Market Intelligence 3차 earnings production baseline을 진행한다
- User request:
  - 사용자가 2차 완료 후 3차 작업도 진행해 달라고 요청함
- Interpreted goal:
  - earnings calendar를 단순 yfinance prototype에서 source validation, lifecycle cleanup, broader low-frequency collection이 가능한 운영 baseline으로 올려야 함
- Analysis result:
  - 범용 company IR official parser는 회사별 markup 편차 때문에 바로 넣기 어렵고, Nasdaq earnings calendar는 무료 alternate provider cross-check로 쓰는 것이 현실적이다
  - 같은 symbol/source의 이전 active earnings estimate는 DB에 남기되 `superseded`로 숨기고, 오래된 provider estimate는 `stale`로 구분하는 것이 auditability와 UX를 모두 지킨다
- Follow-up:
  - 3차 baseline을 구현했다. 다음은 4차에서 sector/mover visuals와 calendar-like Events UX를 다듬는 작업이다

### 2026-05-28 - Overview Market Intelligence 5차는 운영 상태판을 먼저 보강한다
- User request:
  - 사용자가 5차 작업 진행을 요청함
- Interpreted goal:
  - macro calendar나 official earnings source 같은 새 데이터 확장 전에, 이미 만든 Overview 수집 흐름이 매일 운영 가능한지 상태와 실패 원인을 한 화면에서 봐야 함
- Analysis result:
  - 현재 DB freshness metadata와 local `WEB_APP_RUN_HISTORY.jsonl`만으로 1차 Data Health read model을 만들 수 있다
  - 새 외부 source나 schema를 추가하지 않고도 stale snapshot, missing collection, partial / failed run을 구분할 수 있다
- Follow-up:
  - Overview `Data Health` 탭과 refresh-button run history 기록을 추가했다. 다음 고도화 후보는 scheduled refresh automation, macro calendar, official earnings source 중에서 선택한다

### 2026-05-28 - Overview Events에 공식 macro calendar를 추가한다
- User request:
  - 사용자가 자동 리프레시는 보류하고 다음 작업 진행을 요청함
- Interpreted goal:
  - FOMC와 earnings 외에 CPI, PPI, 고용지표, GDP 같은 미국 증시 주요 macro release 일정을 Overview Events에 추가해야 함
- Analysis result:
  - 기존 `market_event_calendar` table contract로 macro 일정도 저장 가능하다
  - BEA release schedule은 live parse와 저장이 가능하지만, BLS schedule page는 현재 환경에서 HTTP 403을 반환하므로 partial failure로 드러내는 것이 맞다
- Follow-up:
  - `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, `MACRO_GDP` event type과 Overview `Macro` filter를 추가했다. BLS 접근성 보강은 별도 후속 후보로 남긴다

### 2026-05-29 - Sector / Industry Leadership을 추세 중심으로 개편한다
- User request:
  - 사용자가 Sector / Industry Leadership에 S&P 500 coverage, Group dropdown, Daily / Weekly / Monthly trend graph, heatmap UX 개선을 요청함
- Interpreted goal:
  - 월간 단면 히트맵 대신 현재 강한 섹터/산업과 최근 흐름을 함께 읽을 수 있어야 함
- Analysis result:
  - 기존 DB의 universe/profile/price history만으로 Daily 1개월, Weekly 3개월, Monthly 6개월 non-overlap trend를 계산할 수 있음
- Follow-up:
  - 최신 Top N ranking과 해당 그룹들의 trend chart를 Overview UI에 추가했고, S&P 500 / Top1000 / Top2000 coverage를 지원한다

### 2026-05-29 - Sector / Industry trend를 더 길고 조작 가능하게 만든다
- User request:
  - 사용자가 Trend 기간을 Daily 3개월 / Weekly 6개월 / Monthly 1년으로 늘리고, 산업별 라인 on/off와 양수 그룹의 대표 티커 상세를 요청함
- Interpreted goal:
  - 현재 강한 섹터/산업뿐 아니라 최근 동향과 내부 주도 종목을 한 화면에서 조절해 봐야 함
- Analysis result:
  - DB price history 기반 non-overlap window 수를 늘리면 추가 source 없이 구현 가능하다
  - Streamlit chart click interaction보다 `Trend Groups` multiselect와 `Positive Group` selectbox가 더 안정적인 UX다
- Follow-up:
  - trend horizon 확장, line filter, ticker leader bar / return-share donut을 추가했다. Positive Return Share는 cap-weighted attribution이 아니라 양수 ticker return share로 정의했다

### 2026-05-29 - Sector / Industry Daily가 Market Movers refresh를 반영해야 한다
- User request:
  - 사용자가 Market Movers daily를 최신화했는데 Sector / Industry의 산업 Top N 티커가 2026-05-27 기준으로 보이는 이유를 묻고 개선 진행을 요청함
- Interpreted goal:
  - Daily leadership과 티커 리더는 Market Movers refresh 결과인 intraday snapshot을 공유해야 하며, Weekly / Monthly EOD 기준과 UI에서 구분되어야 함
- Analysis result:
  - 기존 Sector / Industry는 `nyse_price_history` EOD만 읽어서 `2026-05-28` sparse row를 버리고 `2026-05-27`을 effective date로 선택했다
  - `market_intraday_snapshot`에는 S&P 500 / Top1000 / Top2000 previous-close snapshot이 이미 있으므로 Daily에만 우선 적용하면 된다
- Follow-up:
  - Daily group leadership은 intraday snapshot을 우선 사용하고 fallback으로 EOD DB를 유지한다. UI에 Return Window / Price Mode를 표시했다

### 2026-05-29 - Events에 달력형 UI를 추가한다
- User request:
  - 사용자가 Events가 리스트로만 보이므로 달력 형태 UI도 함께 제공해 달라고 요청함
- Interpreted goal:
  - 기존 리스트의 세부 스캔 기능은 유지하면서, FOMC / earnings / macro 일정을 월간 달력으로 한눈에 봐야 함
- Analysis result:
  - 새 collector나 DB 변경 없이 `market_event_calendar` read model의 날짜 / 타입 / 중요도 필드만으로 월간 grid를 만들 수 있음
- Follow-up:
  - Events `Calendar` 탭에 월 선택형 달력 grid를 추가하고 기존 stacked chart와 날짜별 리스트는 아래에 유지했다

### 2026-05-29 - Market Movers missing quote row의 1차 원인 진단을 추가한다
- User request:
  - 사용자가 반복 refresh 후에도 남는 `missing quote row` 티커의 원인을 더 명확히 알 수 있는 기능을 요청함
- Interpreted goal:
  - 유료 API 없이 기존 Yahoo / yfinance / 내부 DB evidence를 조합해 사용자가 다음 조치를 판단할 수 있는 원인 후보와 confidence를 보여줘야 함
- Analysis result:
  - Yahoo quote batch 누락만으로 거래정지 / 상장폐지를 확정할 수 없으므로 `provider_quote_gap`, `batch_only_gap`, `history_gap_quote_available`, `missing_previous_close`, `possible_stale_universe` 같은 evidence-based diagnosis가 안전함
- Follow-up:
  - Overview `Coverage Diagnostics`에서 missing quote row만 대상으로 수동 진단을 실행하고, 결과를 job result table로 표시하도록 구현했다

### 2026-05-29 - Overview 자동 수집 운영을 시작한다
- User request:
  - 사용자가 브라우저를 켜지 않아도 자동으로 데이터를 수집하는 운영 레이어 개발을 요청함
- Interpreted goal:
  - 기존 Overview refresh button이 호출하던 ingestion job들을 cron / launchd / 외부 runner가 대신 호출할 수 있어야 하며, 중복 실행과 provider 과부하를 피해야 함
- Analysis result:
  - 1차 자동화는 long-running daemon보다 run-once CLI가 안전하다. CLI가 cadence, US market-hours, lock, scheduled run history metadata를 처리하면 로컬 scheduler와 Codex automation 양쪽에 붙이기 쉽다
- Follow-up:
  - `app.jobs.overview_automation`을 추가했고, Data Health auto/manual/failure-streak 표시와 quote gap issue persistence까지 보강했다. 다음 단계는 실제 macOS launchd / cron 등록 또는 Codex automation 연결 여부를 선택하는 것이다

### 2026-05-29 - 자동 수집을 브라우저가 열렸을 때만 작동하게 한다
- User request:
  - 사용자가 아직은 프로그램을 보고 있지 않을 때 수집할 필요가 없으므로, 브라우저가 열렸을 때만 스케줄러가 작동하는 방향을 제안하고 1차 작업 진행을 요청함
- Interpreted goal:
  - OS 상시 scheduler 대신 Overview 페이지가 열려 있는 세션에서만 S&P 500 daily snapshot을 주기적으로 확인해야 함
- Analysis result:
  - Streamlit `fragment(run_every=300)`이 브라우저 세션 기반 heartbeat에 적합하며, provider 호출은 직접 하지 않고 기존 `overview_automation --profile browser_safe` 경로를 재사용하는 것이 안전함
- Follow-up:
  - `browser_safe` profile과 Overview 상단 auto refresh toggle / status panel / heartbeat를 추가했다. 1차는 S&P 500 snapshot만 자동 check하며 Top1000 / Top2000 / Events는 후속 opt-in으로 남긴다

### 2026-05-30 - Market Movers refresh UI에서 수동/자동 갱신을 통합한다
- User request:
  - 사용자가 자동 갱신 패널이 중복되어 보이고, 수동 refresh UI와 자동 refresh UI가 같은 데이터 갱신인데 분리되어 있어 헷갈린다고 지적함
- Interpreted goal:
  - 사용자가 먼저 수동/자동을 선택하고, 같은 Market Movers refresh surface에서 상태, 카운트다운, 수동 버튼을 함께 봐야 함
- Analysis result:
  - 별도 top-level auto panel을 제거하고 Market Movers `데이터 갱신`에 통합하면 중복 렌더링과 개념 분리가 동시에 줄어든다
  - 초 단위 countdown / progress는 브라우저 JS로만 갱신하고, provider collection은 기존 5분 cadence guard를 유지해야 한다
- Follow-up:
  - Market Movers `데이터 갱신`에 `수동 갱신` / `자동 갱신` 모드를 추가하고, S&P 500 Daily 자동 모드에서 browser-side countdown과 기존 `browser_safe` heartbeat를 함께 사용하도록 정리했다

### 2026-05-30 - 기존 UI 패턴 보존과 제품 본질 보존을 구분한다
- User request:
  - 사용자가 기존 Streamlit 패턴 반복으로 화면 품질이 낮아지고, "기존 프로젝트 패턴 보존"이 UI 고정을 뜻한 것이 아니라고 지적함
- Interpreted goal:
  - 데이터 안정성과 투자 연구 workflow는 유지하되, `container / badge / card` 반복을 제품 UI 원칙으로 착각하지 않아야 함
- Analysis result:
  - 보존해야 할 것은 백테스트와 시장 데이터로 포트폴리오 판단을 돕는 본질, 데이터 수집 guardrail, 근거 흐름이다. 기존 helper 시각 패턴은 필요할 때 바꿀 수 있다
- Follow-up:
  - Market Movers `데이터 갱신` 영역부터 반복 badge/card layout을 줄이고, 상태/모드/액션이 한 번에 읽히는 명령 영역으로 재설계하는 1차 pass를 시작했다

### 2026-05-30 - Practical Validation은 후보별 module gate로 Final Review 이동을 판단한다
- User request:
  - 사용자가 Practical Validation의 선택 후보 표시, 검증 프로필 의미, 최신 데이터 재검증, 실전 진단 보드, 다음 단계 저장 / 이동 구조를 개편해 달라고 승인함
- Interpreted goal:
  - Backtest Analysis에서 넘어온 후보를 일괄 동일 검증으로 보는 대신 source traits와 validation profile에 따라 필요한 검증 module을 나누고, 필수 근거가 없으면 Final Review 이동을 막아야 함
- Analysis result:
  - 공격적 profile은 evidence를 생략하는 설정이 아니라 손실 허용선과 판단 threshold를 넓히는 설정이다. 최신 runtime replay, data coverage, validation efficacy, realism 같은 core evidence는 profile과 무관하게 필요하다
- Follow-up:
  - Practical Validation result에 source traits, validation modules, final review gate를 추가했다. 필수 module `BLOCKED` / `NEEDS_INPUT` / `NOT_RUN`은 save-and-move를 차단하고, 조건부 / 후속 참고 module은 source 성격에 맞게 적용 여부를 분리한다

### 2026-05-30 - Practical Validation 필수검증 8개는 유지하되 gate 설명을 정리한다
- User request:
  - 사용자가 필수검증 8개 리뷰 후 어떤 항목을 수정하면 되는지 확인했고, 해당 개편 진행을 승인함
- Interpreted goal:
  - 필수검증을 줄이지 않고, 사용자 화면에서 무엇이 Final Review 이동을 막고 무엇이 Final Review 판단 근거인지 더 명확하게 보여줘야 함
- Analysis result:
  - `Benchmark Parity`는 비교 기준을 benchmark에만 한정하지 않도록 `Benchmark / Comparator Parity`로 해석을 넓히는 것이 맞다
  - Source Integrity는 source 자격, Data Coverage는 최신 evidence coverage로 구분해야 한다
  - Stress / Robustness는 최소 실전 stress 근거를 필수로 두고 고급 parameter perturbation은 후속 / review 근거로 남기는 것이 적절하다
- Follow-up:
  - module row에 `Gate Effect`와 `Gate Reason`을 추가하고 필수검증 설명 / next action을 정리했다. 내부 `Benchmark parity` check key는 호환성을 위해 유지한다

### 2026-05-30 - Practical Validation 화면 보드와 검증 모듈을 분리한다
- User request:
  - 사용자가 GTAA 후보 검증 화면에서 보이는 `Final Review Gate`, audit board, provider board 등이 앞서 정의한 검증 module 목록과 섞여 보여 혼동된다고 지적하고 개선 진행을 승인함
- Interpreted goal:
  - 검증 module taxonomy는 유지하되, 사용자 화면의 board가 어떤 module evidence인지와 현재 후보에 적용되는지 명확히 보여줘야 함
- Analysis result:
  - module은 gate / 검증 의미 단위이고 board는 화면 근거 묶음이다. 두 개념을 분리하고 board registry를 두면 새 검증 추가 시 UI 설명과 적용 여부를 한 곳에서 관리할 수 있다
- Follow-up:
  - Practical Validation board registry, module evidence board mapping, Applied Validation Map, board badge, 단일 component 조건부 board의 Not applicable 표시를 추가했다

### 2026-05-30 - Practical Validation blocker 해결 위치를 표시한다
- User request:
  - 사용자가 Final Review Gate blocker 3개 중 `latest_replay`가 화면 어디에서 해결되는지 보이지 않는다고 지적하고 개선을 승인함
- Interpreted goal:
  - blocker table이 내부 module id가 아니라 사용자가 이동할 화면 위치와 실행할 액션을 바로 알려줘야 함
- Analysis result:
  - `latest_replay`는 별도 audit board가 아니라 `3. 최신 데이터 기준 전략 재검증`의 runtime recheck / period coverage evidence를 의미한다
- Follow-up:
  - module gate row에 `resolution_surface` / `resolution_action`을 추가하고 UI blocker / review table을 `Fix Location` / `Fix Action` 중심으로 표시했다

### 2026-05-30 - Practical Validation module / evidence / action 화면을 분리한다
- User request:
  - 사용자가 `Look-through Exposure Board`, `Provider Data Gaps`가 검증 모듈처럼 보여 혼동된다고 지적하고 화면 분리 개편을 승인함
- Interpreted goal:
  - 사용자는 먼저 검증 리스트와 통과 여부를 보고, 그 다음 검증 근거와 데이터 보강 액션을 별도 흐름으로 봐야 함
- Analysis result:
  - evidence board와 action board는 검증 결과를 판단하거나 보강하는 화면이지 검증 module 자체가 아니므로 같은 섹션 안에 섞으면 module처럼 오해된다
- Follow-up:
  - Practical Validation을 `4. Final Review Gate / 검증 모듈`, `5. 검증 근거 보드`, `6. 보강 액션`, `7. 저장 & Final Review 이동`으로 분리했다

### 2026-05-30 - Practical Validation을 상용 UX 형태로 다듬는다
- User request:
  - 사용자가 Practical Validation 개선 결과를 리뷰하고, 프로토타입 느낌이 강하면 CSS / 라이브러리 등을 활용해 상용화 가능한 UX/UI로 개선해 달라고 요청함
- Interpreted goal:
  - 검증 로직과 Final Review gate는 유지하되, 사용자가 후보 상태, blocker, evidence, 보강 액션을 raw table보다 먼저 이해할 수 있게 해야 함
- Analysis result:
  - 치명적 gate 결함은 발견하지 못했고, 주요 gap은 raw table 우선 노출, blocker action의 낮은 시각 우선순위, board map의 내부 구현 표식 느낌이었다
- Follow-up:
  - Control Center / Fix Queue / summary-first Evidence Workspace / Provider Action Center를 추가하고 raw table은 상세 영역으로 낮췄다

### 2026-05-31 - Practical Validation 저장 기록과 Final Review 후보 노출을 분리한다
- User request:
  - 사용자가 검증 결과 저장이 Final Review 이동과 별개로 보이고, Final Review에는 현재 단계에서 통과한 후보만 보여야 하며, 탭 최초 진입 시 과거 replay cache가 자동 노출되지 않아야 한다고 지적함
- Interpreted goal:
  - 저장-only는 audit trail로 유지하되 Gate 미통과 validation row는 Final Review 후보가 아니어야 하고, Practical Validation Step 3은 현재 세션에서 사용자가 실행한 replay evidence만 보여야 함
- Analysis result:
  - `final_review_gate.can_save_and_move=True`가 Final Review source picker eligibility 기준이다. 이전 session replay state가 자동 표시되면 `NOT_RUN`과 실제 재검증 실행의 의미가 흐려진다
- Follow-up:
  - Final Review source option을 Gate 통과 Practical Validation result로 제한하고, Practical Validation 신규 진입 / source 변경 / recheck mode 변경 시 replay display state를 초기화하도록 조정했다. Step 1~7 경계 surface도 복원했다

### 2026-05-31 - Portfolio Validation closeout 문서 최신화
- User request:
  - 사용자가 Portfolio Validation은 여기까지 마무리하고, 이번 세션에서 수정한 내용을 바탕으로 문서를 업데이트해 달라고 요청함
- Interpreted goal:
  - 새 기능 구현 없이 Practical Validation / Final Review 흐름, 저장 경계, closeout 상태를 장기 문서와 task 기록에 반영해야 함
- Analysis result:
  - 오래 남길 결정은 `저장-only는 audit trail`, `Final Review 후보는 Gate 통과 Practical Validation result만`, `Step 3 replay는 현재 세션 실행 결과만 표시`, `Portfolio Validation 구현 pass는 closeout complete` 네 가지다
- Follow-up:
  - `INDEX`, `ROADMAP`, `PROJECT_MAP`, flow docs, `STORAGE_GOVERNANCE`, `GLOSSARY`, task closeout docs를 최신화했다

### 2026-05-30 - Volume Rank의 기간별 거래량 정의를 명확히 한다
- User request:
  - 사용자가 Volume Rank가 비어 보이는 이유와 daily / weekly / monthly / yearly 거래량 표기 기준을 물었고, daily는 당일 거래량 / 거래대금, 나머지는 평균 또는 합계 기준으로 진행해 달라고 요청함
- Interpreted goal:
  - Volume Rank는 수익률 Top N 안의 재정렬이 아니라 선택 coverage의 returnable universe에서 별도 거래량 랭킹으로 계산해야 하며, 기간별 의미가 화면에서 드러나야 함
- Analysis result:
  - 현재 DB에는 daily volume이 존재한다. Daily는 latest snapshot / EOD day 기준, 비일별은 현재 return window의 average daily volume / average daily dollar volume과 total volume / total dollar volume이 가장 덜 모호하다
- Follow-up:
  - `volume_rows` read model을 추가하고 Volume chart / table이 이 전용 랭킹을 사용하도록 구현했다. Top2000 yearly는 여전히 약 20초로 날짜 윈도우 계산 최적화가 후속 후보로 남았다

### 2026-05-30 - Sector / Industry Trend와 Positive Detail을 더 읽기 쉽게 만든다
- User request:
  - 사용자가 Sector / Industry 안에서 Trend Groups가 컨트롤 변경 때마다 초기화되는 문제, line chart의 시각적 약함, Positive Group Detail의 색상 / 이전 수익률 marker 확장을 요청함
- Interpreted goal:
  - 탭 내부 컨트롤 변경은 사용자가 고른 group 의도를 보존하고, 섹터 상승/하락은 heatmap / delta / line을 함께 제공해 더 빠르게 읽히게 해야 함
- Analysis result:
  - Trend Groups state key를 coverage / period / top-N에서 분리하고 `sector` / `industry`별로 유지하면 내부 설정 변경과 탭 전환 의도를 구분할 수 있음
  - 이전 기간 수익률은 모멘텀 참고 지표로 쓸 수 있지만 예측 신호가 아니라 latest window와 previous window의 비교 맥락으로 표시하는 것이 안전함
- Follow-up:
  - Sector / Industry에 insight cards, Heatmap / Line / Latest Delta tabs, Positive ticker sector-colored bars, previous-period marker를 추가했고 Browser QA screenshot까지 확인했다

### 2026-05-30 - Daily Heatmap 과밀도를 줄인다
- User request:
  - 사용자가 Daily heatmap이 너무 촘촘해서 알아보기 어렵다고 지적하고 Daily 1개월, Weekly 3개월, Monthly 12개월 범위를 요청함
- Interpreted goal:
  - Trend horizon은 분석 의미보다 화면 판독성이 우선이며, 특히 Daily heatmap은 약 1개월 거래일만 보여야 함
- Analysis result:
  - 기존 Daily 3M / Weekly 6M / Monthly 1Y는 line chart에는 괜찮지만 heatmap에는 daily cell 수가 많아 과밀해진다
- Follow-up:
  - Trend window contract를 Daily 21 거래일 / Weekly 13주 / Monthly 12개월로 조정하고 서비스 계약 테스트와 Browser QA screenshot으로 확인했다

### 2026-05-30 - Heatmap 전체 섹터 선택 시 높이를 늘린다
- User request:
  - 사용자가 Trend Groups에 전체 섹터를 넣으면 Heatmap이 아래로 길어지지 않고 고정 영역 안에 압축되어 라벨이 작아진다고 지적함
- Interpreted goal:
  - 선택 group 수가 늘면 Heatmap chart height도 같이 늘어나야 하며, 섹터 라벨과 셀 값을 스크롤로 읽을 수 있어야 함
- Analysis result:
  - 기존 height 계산은 `min(680, 32 * group_count)`처럼 상한과 낮은 row height가 있어 선택 group이 많아질수록 행당 공간이 줄어들 수 있었다
- Follow-up:
  - Heatmap row height를 group당 54px로 고정하고 상한 cap을 제거했으며, 축 / 셀 label font size를 명시하고 contract test와 Browser QA screenshot으로 확인했다

### 2026-05-31 - Final Review 선정 저장 가능한 포트폴리오 후보를 찾는다
- User request:
  - 기존 DB, saved portfolio, registry를 활용해 Backtest Analysis -> Practical Validation -> Final Review를 실행하고, selected-route gate 통과 후보만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장해 Dashboard 노출을 확인해 달라고 요청함
- Interpreted goal:
  - Final Review selection-only save 정책을 지키면서 실제 운영 후보를 찾되, live approval / 주문 / 자동 리밸런싱 / broker 연동은 수행하지 않아야 함
- Analysis result:
  - 기존 Practical Validation row, saved portfolio 2개, legacy Final Review option 13개를 dry-run 평가했지만 `select_allowed=True` 후보가 없었다. 가장 가까운 후보는 `EW Growth/Commodity 30 + GTAA Clean-6 70`이나 Backtest Realism과 Component Role / Weight hard blocker가 남았다
- Follow-up:
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 append하지 않았고 Dashboard read model은 `dashboard_rows=0`, `HANDOFF_NO_FINAL_DECISION`으로 확인했다. 후보 보강은 evidence mapping / realism / provider / risk contribution 쪽에서 진행해야 한다

### 2026-05-31 - Practical Validation에서 후보 전략과 월별 선택 종목을 보여준다
- User request:
  - 사용자가 Practical Validation의 `검증할 후보 source` 선택 후 Step 1에서 어떤 전략 / mix 구성인지와 각 달 선택 종목이 보이지 않는다고 지적하고, 먼저 분석 방향을 확인한 뒤 개발 진행을 승인함
- Interpreted goal:
  - Backtest Analysis가 넘긴 단일 / mix 후보의 구성, component strategy, target weight, 월별 selection / holdings evidence를 Practical Validation Step 1에서 바로 읽을 수 있어야 함
- Analysis result:
  - 기존 source snapshot은 compact curve 중심이라 `Date`, `Total Balance`, `Total Return`만 보존했고, result frame의 `Next Ticker`, `Next Weight` 등 selection evidence가 Practical Validation handoff에서 사라졌다. 기존 registry row는 재작성하지 않고 fallback이 필요하다
- Follow-up:
  - source builder에 compact selection history helper를 추가하고 candidate / weighted mix / saved mix handoff와 runtime replay에 연결했다. Practical Validation Step 1은 strategy / construction brief, component strategy table, performance table, monthly selection / holdings table을 표시한다

### 2026-06-01 - Practical Validation이 Final Review selected-route 실패 사유를 먼저 잡아야 한다
- User request:
  - 사용자가 Practical Validation을 통과해 Final Review로 갔는데 Final Review에서 validation evidence 때문에 selected-route가 실패하는 흐름은 단계 의미가 맞지 않는다고 지적하고 수정 진행을 승인함
- Interpreted goal:
  - Final Review에서 deterministic하게 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장을 막을 evidence gap은 Practical Validation 단계에서 먼저 차단해야 함
- Analysis result:
  - 기존 Practical Validation module gate는 `REVIEW`를 이동 가능으로 처리했지만, Final Review selection policy는 gross-only / net-cost / 핵심 coverage 같은 selection-critical `REVIEW_REQUIRED`를 저장 차단으로 해석했다
- Follow-up:
  - Final Review selection policy를 Practical Validation `Selected-route Preflight`로 재사용하고, preflight 미통과 row는 Final Review source picker에서 숨기도록 구현했다. Existing registry row는 rewrite하지 않고 동적 preflight로 판정한다

### 2026-06-01 - Final Review 통과 후보를 Dashboard에 노출한다
- User request:
  - 사용자가 최종 통과한 후보들을 저장해서 Selected Portfolio Dashboard에 노출되도록 해 달라고 요청함
- Interpreted goal:
  - Final Review selected-route gate를 완화하지 않고, fresh 재검증에서 통과한 후보만 Final Decision V2와 Dashboard saved state에 남겨야 함
- Analysis result:
  - `GRS Liquid Macro Top2`, `GRS Macro Top1 MA200`, `GRS QQQ Gold Bonds Top2 MA150`, `GRS Macro Top3 MA200`는 replay PASS / Practical Validation READY / selected-route ready / investability packet ready였다. `GTAA Default Top3`는 fresh run에서 Practical Validation `BLOCKED`로 바뀌어 저장 대상에서 제외했다
- Follow-up:
  - Final Decision V2에 4개 row를 append하고 `Final Review 통과 후보 2026-06-01` dashboard portfolio에 4개 decision id를 배정했다. Dashboard는 read-only이며 live approval, order, broker/account linkage, auto rebalance는 모두 disabled다

### 2026-06-01 - Finance JSONL registry cleanup 전 read-only audit을 한다
- User request:
  - 사용자가 DB는 건드리지 않고 `.aiworkspace/note/finance/**/*.jsonl` 전체를 최신 프로그램 상태 기준으로 audit하고, 승인 전에는 삭제 / 재작성 없이 inventory와 정리안만 제시해 달라고 요청함
- Interpreted goal:
  - V1 / V2 / legacy compatibility / saved setup / local run history를 구분하고, GRS 4개 selected decision과 Selected Dashboard assignment를 유지하는 cleanup plan을 만들어야 함
- Analysis result:
  - 13개 JSONL, 109 row 모두 parse 성공. GRS 4개 Final Decision V2는 source/result registry counterpart는 없지만, 현재 Selected Dashboard read model은 Final Decision V2 self-contained record로 정상 작동하며 selected rows 4 / dashboard rows 4 / assigned 4 / missing 0이다
- Follow-up:
  - `.aiworkspace/note/finance/tasks/active/jsonl-registry-audit-20260601/DRY_RUN_REPORT.md`에 dry-run report를 작성했다. 승인 전 archive/delete/rewrite는 하지 않았고, source/result synthetic migration도 gate 재실행 없이는 하지 않는 방향을 권장했다

### 2026-06-01 - 초창기 prototype JSONL을 active에서 정리한다
- User request:
  - 사용자가 V1 / prototype 저장 데이터가 무엇인지 혼란스럽고, 실제 삭제가 필요한지 V2 승격이 필요한지 정리한 뒤 권장안대로 진행해 달라고 승인함
- Interpreted goal:
  - 초창기 candidate / proposal / pre-live / V1 final / generated run history를 active workflow에서 제거하되, 원본은 archive에 남기고 GRS 4개 Selected Dashboard 상태는 유지해야 함
- Analysis result:
  - legacy/prototype rows는 현재 selected-route gate를 통과한 V2 chain이 아니므로 V2 승격 대상이 아니며, GRS 4개는 이미 Final Decision V2 self-contained selected record로 Dashboard에서 정상 작동한다
- Follow-up:
  - 13개 JSONL을 archive에 백업하고 10개 active JSONL을 제거했다. active에는 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`, `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`, `SAVED_PORTFOLIOS.jsonl`만 남겼으며 selected rows 4 / dashboard rows 4 / assigned 4 / missing 0을 재검증했다

### 2026-06-02 - 선물장 OHLCV / 개장 전 급변 모니터링 방향을 조사한다
- User request:
  - 사용자가 선물장 지표나 OHLCV 캔들을 실시간에 가깝게 확인해, 미국장 또는 한국장 시작 전에 가파른 움직임을 파악하는 기능 방향을 조사해 달라고 요청함
- Interpreted goal:
  - 무료 또는 보편적 데이터 소스를 비교하고, 기존 Finance Overview / 운영툴 구조 안에서 수집 cadence, 저장 경계, UX/UI 방향을 먼저 정리해야 함
- Analysis result:
  - 무료 실시간 선물 API는 안정적이지 않다. 1차 MVP는 `yfinance` 1분봉을 DB-backed polling으로 저장하고, `Overview > Futures Monitor`에서 provider freshness / stale / failed 상태를 노출하는 방향이 가장 작고 현실적이다
- Follow-up:
  - `.aiworkspace/note/finance/researches/active/2026-06-futures-market-monitoring/`에 리서치 번들을 작성했다. 사용자 승인 후 구현은 futures collector / read model / Overview tab / Data Health 순서로 진행한다

### 2026-06-02 - 선물장 모니터링 MVP를 구현한다
- User request:
  - 사용자가 위에서 정의한 추천 방향대로 순서대로 구현하고, 도중 의사결정이 필요할 때만 멈춰 질문해 달라고 요청함
- Interpreted goal:
  - 리서치 결론을 실제 Finance 운영툴에 연결해, 무료 provider 기반 선물 1분봉 OHLCV 수집 / 저장 / Overview 표시 / Data Health 확인이 가능한 MVP를 만들어야 함
- Analysis result:
  - DB-backed `yfinance` collector와 service read model을 추가하면 Streamlit UI가 provider를 직접 호출하지 않고도 freshness, missing, stale, shock 상태를 표시할 수 있다. 무료 provider 특성상 `REVIEW` 상태와 최신 candle age를 강하게 노출해야 한다
- Follow-up:
  - `.aiworkspace/note/finance/tasks/active/futures-market-monitoring-mvp-v1/`에 실행 기록을 남겼다. `Overview > Futures Monitor`와 `Workspace > Ingestion` 수동 수집 진입점을 구현했고 Browser QA에서 `ES=F` candlestick chart와 stale / missing 경고를 확인했다

### 2026-06-02 - Futures Monitor 차트를 2x2 그리드로 확장한다
- User request:
  - 사용자가 한 화면에 몇 개 차트가 보이는지 확인한 뒤, 핵심 4개 선물을 2x2 미니 차트 그리드로 보여주는 개선을 진행해 달라고 승인함
- Interpreted goal:
  - 기존 선택 symbol 단일 상세 차트는 유지하되, Candles 탭에서 여러 선물의 움직임을 한 화면에서 비교할 수 있어야 함
- Analysis result:
  - read model은 이미 선택 symbol 전체의 candle row를 읽고 있었지만 반환값은 선택 symbol candle만 노출했다. `all_candles`를 함께 반환하면 provider 호출이나 DB schema 변경 없이 4개 미니 차트를 만들 수 있다
- Follow-up:
  - `Overview > Futures Monitor > Candles`에 선택 symbol을 포함한 최대 4개 미니 캔들 그리드를 추가했고, missing symbol의 15m / age metric은 `-`로 표시하도록 QA 중 수정했다

### 2026-06-02 - 나머지 선물 후보를 수집 검증하고 기본 watchlist를 확정한다
- User request:
  - 사용자가 지수 외 금리, 원자재, FX 후보도 같은 순서로 검증하고 기본 화면에 반영해 달라고 요청함
- Interpreted goal:
  - 후보 등록 상태를 넘어 실제 DB 수집 가능 여부를 확인하고, 개장 전 한 화면에서 볼 cross-asset 기본 2x2 구성을 정해야 함
- Analysis result:
  - non-optional core 16개(`ES=F`, `NQ=F`, `YM=F`, `RTY=F`, `ZN=F`, `ZB=F`, `CL=F`, `GC=F`, `SI=F`, `HG=F`, `NG=F`, `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F`) 모두 yfinance 1m rows를 저장했다. 무료 provider 특성상 latest candle은 wall-clock보다 약 10분 이상 늦어 `REVIEW` freshness로 표시된다
- Follow-up:
  - `Overview > Futures Monitor` 기본 Watch Group을 `Pre-open Core`로 바꾸고, 기본 2x2 심볼을 `NQ=F`, `ZN=F`, `CL=F`, `6E=F`로 확정했다

### 2026-06-02 - 선물 일봉으로 글로벌 매크로 온도계를 만든다
- User request:
  - 사용자가 수집 중인 지수 / 금리 / 원자재 / FX 선물 일봉으로 risk-on, 금리 부담, 달러 압력, 안전자산 선호 같은 시장 해석을 자동 요약하는 기능을 구현해 달라고 요청함
- Interpreted goal:
  - 기존 Futures Monitor 차트는 유지하면서 별도 점수 산출 / 문장 생성 로직을 만들고, Overview UI에서 점수 / 방향성 / 근거 티커 / 주의 문구를 한 화면에 보여줘야 함
- Analysis result:
  - 같은 `futures_ohlcv` table에 `interval_code=1d` row를 저장하면 신규 schema 없이 일봉 해석이 가능하다. 채권선물과 FX 선물은 raw 가격 방향을 경제적 해석 방향으로 반전해야 한다
- Follow-up:
  - `app/services/futures_macro_thermometer.py`와 `Overview > Futures Monitor > Macro Thermometer`를 추가했다. `1y / 1d` core futures backfill smoke는 16개 symbol / 4,032 rows 성공했고, 상세 실행 기록은 `.aiworkspace/note/finance/tasks/active/futures-macro-thermometer-v1/`에 남겼다

### 2026-06-02 - Macro Thermometer validation 리뷰 후속을 보정한다
- User request:
  - 사용자가 Macro Thermometer historical validation / confidence 보강이 충분한지 리뷰한 뒤, 지적사항을 개선해 달라고 요청함
- Interpreted goal:
  - 5y validation이 UI 렌더마다 과도하게 느려지지 않아야 하고, mixed scenario를 directional sample / hit-rate처럼 오해하게 만들면 안 되며, adverse / false-positive 지표도 요구사항대로 보여야 함
- Analysis result:
  - 기존 검증은 날짜별 target return 계산에서 같은 시리즈를 반복 정렬했고, mixed scenario의 occurrence count가 directional sample처럼 표시될 수 있었다. `Max Adverse`도 endpoint 기반이라 forward path adverse move 요구와 맞지 않았다
- Follow-up:
  - target return 선계산과 Overview TTL cache를 추가했고, mixed scenario는 hit-rate N/A / occurrence count로 분리했다. `Max Adverse`는 path 기준으로 바꾸고 false-positive rate를 UI summary와 threshold sensitivity에 노출했다. 상세 검증은 `.aiworkspace/note/finance/tasks/active/futures-macro-thermometer-validation-v1/RUNS.md`에 남겼다

### 2026-06-02 - Futures Monitor UI를 prototype tab 구조에서 workspace 구조로 바꾼다
- User request:
  - 사용자가 Futures Monitor가 테스트 더미처럼 보이고 Macro Thermometer와 Candles가 별도 탭이라 분석 흐름이 끊긴다고 지적하며, 개선 가이드 정리 후 순서대로 구현해 달라고 요청함
- Interpreted goal:
  - 기존 수집 / 검증 기능은 유지하면서 상단 데이터 상태를 항상 읽을 수 있게 하고, Macro Context와 live candles를 동시에 보여주는 분석 workspace로 재배치해야 함
- Analysis result:
  - TradingView / Koyfin식 watchlist + chart workspace 패턴을 참고하면, 수집 버튼 중심 UI보다 command center, 상태 badge, side-by-side chart/macro context, 하단 diagnostics 구조가 더 적합하다
- Follow-up:
  - `Overview > Futures Monitor`를 command center + Macro Context / Live Futures Charts 동시 노출 구조로 변경했다. Shock Board / Provider Run은 diagnostics로 이동했고, manual refresh는 snapshot in-place reload로 바꿨다. 상세 기록은 `.aiworkspace/note/finance/tasks/active/futures-monitor-ui-v2/`에 남겼다

### 2026-06-02 - Futures Monitor V2.1의 control / chart / macro 정보 위계를 보정한다
- User request:
  - 사용자가 스크린샷 기준으로 상단 symbol/control이 과하게 공간을 차지하고, mini chart 정보가 찌그러지며, Macro Context 정보 전달이 시각적으로 애매하다고 지적함
- Interpreted goal:
  - 기능이나 scoring을 바꾸지 않고 화면 밀도와 정보 위계를 개선해, chart evidence와 macro reliability를 더 빠르게 읽을 수 있어야 함
- Analysis result:
  - 문제 원인은 데이터 부족이 아니라 `st.metric` 과대 표시, full-width `Candle Symbol` control, generic KPI card grid가 만든 공간/시선 낭비다
- Follow-up:
  - 상단 controls를 한 줄로 압축하고 refresh는 `Data Actions`에 넣었다. Mini chart는 60m / 15m / Age chip + 큰 chart card로 바꿨고, Macro Context는 scenario / confidence / validation / history signal strip과 score chip으로 재구성했다

### 2026-06-02 - Futures Monitor를 Macro 상단 / Live 3x2 하단 구조로 재배치한다
- User request:
  - 사용자가 Selected Detail 차트가 2x2와 중복처럼 보이고, Macro와 Live를 좌우 column으로 나누기보다 Macro를 상단에, 선물 지표를 하단 3x2로 보여달라고 요청함
- Interpreted goal:
  - Macro 해석은 full-width 상단 context로 두고, 실시간 선물 차트는 하단 grid에서 비교하도록 화면 흐름을 단순화해야 함
- Analysis result:
  - 기존 Selected Detail은 선택 심볼의 첫 grid card와 같은 데이터를 크게 다시 보여줘 중복 인상을 만든다. 3x2 grid는 기본 Pre-open set도 6개로 확장해야 자연스럽다
- Follow-up:
  - Selected Detail을 제거하고 Macro Context -> Live Futures Charts 순서의 stacked layout으로 변경했다. Pre-open Core 기본은 `NQ=F`, `ZN=F`, `CL=F`, `6E=F`, `GC=F`, `6J=F` 6개로 확장했고, Macro detail은 `Macro Evidence & Data`로 통합했다

### 2026-06-02 - Futures Monitor 상단 control 의미를 정리한다
- User request:
  - 사용자가 `Focus`, `Window`, `Chart`가 무엇을 의미하는지 확인한 뒤, 필요하면 깔끔하게 정리해 달라고 요청함
- Interpreted goal:
  - Selected Detail 차트가 사라진 뒤 남은 단일 focus symbol control을 제거하고, 상단 control이 실제로 화면에 영향을 주는 선택만 남겨야 함
- Analysis result:
  - 현재 화면에서는 `Symbols`가 3x2 chart universe와 순서를 결정하고, `Window`는 보이는 기간, `Chart`는 candle aggregation만 담당하는 구조가 가장 명확하다. 단일 focus symbol은 남겨두면 중복된 개념처럼 보인다
- Follow-up:
  - `Focus` control을 제거했고 command/live header는 `6 selected futures · 5m candles · 6H window`처럼 선택 집합 기준으로 표시한다. Chart hourly option은 `60m`로 노출하고 기존 `1h` session state는 `60m`로 migrate한다

### 2026-06-02 - Futures Monitor Macro와 Live 갱신 범위를 분리한다
- User request:
  - 사용자가 60초 그래프 갱신 때 Macro Context도 같이 업데이트되는 것처럼 보이고, Macro daily refresh 버튼도 Futures Charts까지 흔드는 구조가 맞는지 지적함
- Interpreted goal:
  - `1d` Macro Context와 `1m` Live Futures Charts의 수집 / 렌더 갱신 경계를 분리하고, 각 영역이 자기 데이터만 갱신하도록 해야 함
- Analysis result:
  - 기존 auto fragment가 Macro와 Live를 함께 렌더했고, live snapshot의 latest provider run도 interval filter 없이 최신 run 전체를 읽어 daily macro run이 Data Feed에 표시될 수 있었다
- Follow-up:
  - Macro Context와 Live Futures Charts를 별도 Streamlit fragment로 분리했다. Macro 버튼은 fragment rerun만 호출하고, live auto refresh는 Live 영역만 실행한다. Live monitor latest run은 `interval_code='1m'`으로 필터링한다

### 2026-06-03 - Operations 탭을 단계별로 개편한다
- User request:
  - 사용자가 Operations 탭의 recommended restructuring을 단계별로 진행해 달라고 요청함
- Interpreted goal:
  - Selected Portfolio Dashboard는 post-selection monitoring으로 Operations에 유지하되, Operations 안에서 primary monitoring / system health와 legacy archive 도구를 구분해야 함
- Analysis result:
  - `Operations Overview` landing page를 추가하고, Selected Dashboard는 `Portfolio Monitoring`, Ops Review는 `System / Data Health`, Run History와 Candidate Library는 Archive recovery label로 낮추는 additive IA가 가장 안전함
- Follow-up:
  - `app/web/operations_overview.py`와 navigation label 정리를 구현했고, registry / saved schema / live order / auto rebalance는 변경하지 않았다. 상세 실행 기록은 `.aiworkspace/note/finance/tasks/active/operations-overview-ia-v1/`에 남겼다

### 2026-06-03 - Operations 2차~5차를 끝까지 진행한다
- User request:
  - 사용자가 2차부터 5차까지 단계별로 작업하고, 중간 의사결정이 필요하면 질문해 달라고 요청함
- Interpreted goal:
  - 1차 보강으로 끝내지 않고 Operations 기능 감사, 리밸런싱 의미 정정, archive 격하, 최종 Operations Console까지 이어서 완성해야 함
- Analysis result:
  - 삭제 여부는 아직 되돌리기 어려운 판단이므로 Backtest Run History / Candidate Library는 제거하지 않고 archive / recovery로 보존하는 것이 맞다. 리밸런싱 표는 주문처럼 보이는 컬럼명을 target snapshot / next review 언어로 바꿔야 한다
- Follow-up:
  - `Operations Console` action queue, 1차~5차 roadmap, surface audit decisions, target snapshot table semantics를 구현했다. live approval / order / account sync / auto rebalance / registry rewrite / report export는 추가하지 않았다

### 2026-06-07 - Operations archive 탭은 제거한다

- User request:
  - 사용자가 Portfolio Monitoring 외 archive 성격의 데이터 / 화면은 이제 별 의미가 없으므로 없애도 된다고 승인함.
- Interpreted goal:
  - Operations의 정체성을 `Portfolio Monitoring + System / Data Health`로 좁히고, Backtest Run History / Candidate Library를 상단 Operations 탭에서 제거한다.
- Analysis result:
  - UI 탭 제거와 데이터 삭제는 분리한다. 현재 차수에서는 top navigation / Overview lane에서 archive를 제거하되, run history / candidate registry / helper code 삭제는 별도 audit 전까지 하지 않는 것이 안전하다.
- Follow-up:
  - `app/web/streamlit_app.py`, `app/web/operations_overview.py`, 관련 docs / tests를 갱신했다. 상세 기록은 `.aiworkspace/note/finance/tasks/active/operations-archive-tabs-removal-20260607/`에 남겼다.

### 2026-06-03 - Risk-On Momentum 5D V2는 Backtest Analysis 연구 lane으로 구현한다

- User request: V1 이후 Risk-On Momentum 5D V2 고도화 계획을 구현하되 Practical Validation / Final Review / Selected Dashboard governance는 바로 연결하지 말라고 요청함.
- Interpreted goal: ATR exit, macro ranking penalty, comparison / sensitivity / stability / trade-cause / quality warning analysis를 Backtest Analysis Daily Swing research surface에 추가한다.
- Analysis result: Strategy core는 `finance/swing.py`, indicator / macro / repeated analysis helper는 별도 finance module로 분리하고 UI / history / artifact는 기존 Backtest Analysis 경계 안에 연결하는 것이 안전하다.
- Follow-up: Daily Swing Practical Validation module, Final Review route, Daily Signal / Paper Strategy Monitor lane은 별도 설계 승인 후 구현한다.

### 2026-06-03 - Risk-On Momentum 5D universe에 S&P 500을 추가한다

- User request: Risk-On Momentum 5D의 universe mode가 Top1000 / Top2000 / Manual뿐이므로 S&P 500도 추가해 달라고 요청함.
- Interpreted goal: Backtest Analysis 안에서 S&P 500 constituent 기반 daily swing research run을 선택할 수 있어야 하며, Top1000과 혼동되는 market-cap Top500 fallback은 피해야 함.
- Analysis result: 기존 `load_market_cap_universe_members("SP500")` 경로가 S&P 500 membership row를 읽고 있으므로 새 수집기 없이 runtime resolver와 Single Strategy form에 `sp500` mode를 추가하면 된다.
- Follow-up: `snp500` 입력 alias도 `SP500`으로 해석한다. 멤버십 row가 없으면 S&P 500 universe refresh 필요 오류를 낸다.

### 2026-06-03 - Futures Monitor chart가 sparse하게 보이는 원인을 보정한다

- User request: `Overview > Futures Monitor > Live Futures Charts`에서 금리(`ZN=F`), 원유(`CL=F`), 금(`GC=F`) 선물 차트가 잘못 나오는 이유를 물었고, 원인 설명 후 수정을 승인함.
- Interpreted goal: 차트 렌더 문제가 아니라 provider / DB coverage 문제인지 검증하고, 1d / 1m 응답이 너무 적어 6H chart가 왜곡되는 경우도 collector에서 복구해야 함.
- Analysis result: yfinance `period=1d`, `interval=1m`은 해당 symbols에 대해 13-33개 row만 반환했지만 `period=2d`, `interval=1m`은 같은 시간대의 dense rows를 반환했다.
- Follow-up: collector가 empty뿐 아니라 sparse 1d / 1m symbols도 한 번 `2d / 1m`으로 보강 수집하고 recovered sparse rows를 대체하도록 수정했다. 상세 검증은 `.aiworkspace/note/finance/tasks/active/futures-market-monitoring-mvp-v1/RUNS.md`에 남겼다.

### 2026-06-04 - Why It Moved SEC 공시 preview를 V1.7로 개선한다

- User request: `Overview > Market Movers > Why It Moved`의 SEC 공시 섹션을 filing reader benchmark 기반으로 개선하되 automatic catalyst classifier나 durable storage로 확장하지 말라고 요청함.
- Interpreted goal: 기존 SEC metadata table과 official Open link를 유지하면서, 사용자가 선택한 filing 1건을 버튼으로만 앱 안에서 bounded preview할 수 있어야 함.
- Analysis result: SEC EDGAR / BamSEC / Quartr / AlphaSense UX는 compact filing metadata, source status, search snippets, official source traceability를 보여준다. 현재 범위에서는 selected-filing reader preview와 explicit failure boundary만 채택하는 것이 맞다.
- Follow-up: V1.7은 session-only SEC preview, 8-K Item / 10-Q·10-K section locator, nested iXBRL sanitizer regression, Browser QA screenshot까지 완료했다. DB schema, registry / saved JSONL, filing body 저장, AI summary, sentiment, automatic cause judgement는 추가하지 않았다.

### 2026-06-05 - Why It Moved SEC 공시 preview를 V1.8 Digest로 확장한다

- User request: main-dev에서 Why It Moved 개선을 이어가되 SEC 공시는 링크 이동보다 앱 안에서 공시 내용을 텍스트/표 단서로 볼 수 있게 하고, 한국 뉴스는 별도 조사/정책 문제로 분리해 달라고 요청함.
- Interpreted goal: V1.7 selected-filing preview를 유지하면서 공시 원문 전체 덤프가 아닌 manual investigation용 digest를 추가해야 함.
- Analysis result: SEC / filing-reader UX의 핵심은 metadata list, selected document reader, section / snippet / exhibit jump다. 현재 범위에서는 8-K Item / Exhibit, 10-Q·10-K TOC / MD&A / Risk Factors / Financial Statements / bounded table clues만 채택한다.
- Follow-up: V1.8 digest를 구현했다. 한국 뉴스 metadata는 credentialed provider policy 후속으로 남겼고, DB schema / registry / saved JSONL / filing body / AI summary / sentiment / automatic cause judgement는 추가하지 않았다.

### 2026-06-06 - Why It Moved SEC preview / Digest를 table-only로 되돌린다

- User request: SEC 공시 섹션에서 기존 제목과 `Form / Filing Date / Title / Open` 표는 남기고, 그 아래 추가했던 원문 미리보기 / Digest를 rollback해 다시 제대로 파악하고 싶다고 요청함.
- Interpreted goal: V1.7 / V1.8 selected-filing preview 기능을 현재 제품 surface에서 제거하고, SEC lane을 compact metadata table + official SEC link 상태로 되돌려야 함.
- Analysis result: 이전 Digest는 8-K / 10-Q / 10-K의 의미를 다시 정리하기 전 product UX로는 너무 앞서 나간 형태다. 재무제표 표 preview는 별도 10-Q / 10-K 또는 SEC XBRL/companyfacts feature로 재설계하는 것이 맞다.
- Follow-up: 서비스 / UI preview fetch·parse·digest helper와 contract tests를 제거하고 table-only rollback contract로 대체했다. 상세 실행과 검증은 `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/`를 본다.

### 2026-06-02 - Risk-On Momentum 5D V1 구현을 시작한다
- User request:
  - 사용자가 사전 계획된 `Risk-On Momentum 5D V1`을 구현해 달라고 요청함
- Interpreted goal:
  - 기존 Backtest Analysis / Single Strategy 경로 안에 Top1000 기본 short-term stock swing strategy를 추가하되, UI가 provider를 직접 fetch하지 않고 DB price / annual statement shadow / futures macro Mean-Z loader를 통해 실행해야 함
- Analysis result:
  - V1 범위는 `close_based + fixed_pct + Equal Slot`로 제한하고, full trade / scanner detail은 registry가 아니라 generated backtest artifact에 둔다. Macro filter는 futures thermometer의 continuous Mean-Z를 hard filter로 사용한다
- Follow-up:
  - Core strategy, DB runtime, Single Strategy form, result `Swing Detail`, History replay fields, Compare default runner, focused tests를 구현했다. Browser QA에서 Manual universe input과 `Swing Detail` 결과 탭을 확인했고, full service contract 237 tests도 통과했다. 상세 검증과 남은 risk는 `.aiworkspace/note/finance/tasks/active/risk-on-momentum-5d-v1/`를 확인한다

### 2026-06-06 - Overview Market Sentiment V1 2차를 Practical Validation에 연결한다
- User request:
  - CNN Fear & Greed / AAII sentiment를 Practical Validation 화면에 시장 심리 context overlay로 연결하되, trade signal / PASS-BLOCKER / live approval / order / auto rebalance로 쓰지 말라고 요청함
- Interpreted goal:
  - 후보 검증자가 현재 시장 심리가 risk-on / neutral / risk-off 중 어디에 가까운지 참고하되, 기존 validation gate와 저장 경계는 유지해야 함
- Analysis result:
  - Overlay는 저장된 `macro_series_observation`을 Overview sentiment snapshot으로 읽고 Practical Validation 전용 read model로 변환하는 것이 가장 안전하다. 결과 JSONL에 섞지 않고 `context_only`, `gate_effect=none`, `registry_write=false`를 명시한다
- Follow-up:
  - `Backtest > Practical Validation`에 context overlay band를 추가했다. Final Review Gate, selected-route preflight, registry, saved setup, live trading boundary는 변경하지 않았다

### 2026-06-07 - Futures Monitor가 갱신 후에도 그래프 / 데이터가 비어 보이는 원인을 고친다

- User request: `Workspace > Overview > Futures Monitor`에서 업데이트를 실행해도 선물 그래프와 데이터가 간헐적으로 갱신되지 않는 문제의 원인 파악과 해결을 요청함.
- Interpreted goal: provider가 늦거나 선물장이 닫힌 상황에서도 저장된 최신 futures OHLCV를 화면에서 확인할 수 있어야 하며, stale 데이터는 fresh처럼 보이면 안 됨.
- Analysis result: 수집기는 empty/sparse `1d / 1m` 응답 fallback을 이미 갖고 있었지만, Overview service read path가 `UTC_TIMESTAMP() - lookback`으로만 조회해 최신 저장 candle이 현재 시각 기준 window 밖이면 DB row가 있어도 `MISSING`처럼 보였다.
- Follow-up: `app/services/futures_market_monitoring.py`가 각 symbol의 latest stored candle 기준으로 chart window를 읽도록 수정했다. 상태 계산은 현재 시각 대비 `Stale`로 유지한다.

### 2026-06-07 - Reference 탭을 현재 제품 흐름에 맞게 1차 개편한다

- User request: 오래전에 중단된 `Reference` 탭을 현재 프로그램 방향과 구조에 맞게 전체적으로 개선하고, 벤치마킹 기반으로 단계별 가이드를 잡은 뒤 진행해 달라고 요청함.
- Interpreted goal: `Reference > Guides`를 포트폴리오 후보 선정 전용 guide에서 Overview / Ingestion / Backtest / Validation / Operations까지 안내하는 task-first Reference Center로 바꿔야 함.
- Analysis result: 기존 Guide의 route selector / timeline / Go-Review-Stop 구조는 유지 가치가 있지만 첫 화면이 product-wide help center 역할을 못한다. Reference는 read-only guide여야 하며 job 실행, provider fetch, registry write, live approval / order / auto rebalance를 추가하면 안 된다.
- Follow-up: 1차로 catalog service와 Reference Center shell을 구현하고, 기존 guide는 `Portfolio Selection Journey`로 보존했다. 후속 차수는 Glossary 통합, contextual links, Browser QA 기반 polish다.

### 2026-06-07 - Reference 2차로 journey / playbook 상세를 확장한다

- User request: 사용자가 Reference 개편 2차 작업 진행을 요청함.
- Interpreted goal: 1차 Reference Center의 task card / 요약 표만으로는 부족하므로, 사용자가 실제로 막힌 상황에서 확인 순서, failure state, evidence location을 따라갈 수 있어야 함.
- Analysis result: 상세 내용은 Streamlit-free catalog에 두고 UI는 선택한 journey / playbook을 렌더링만 하는 구조가 drift와 boundary risk를 줄인다.
- Follow-up: journey steps / failure states, provider snapshot / ingestion success UI stale / archive recovery playbooks, check steps / evidence locations를 추가했다. Reference는 read-only guide이며 job 실행 / provider fetch / registry write / live trading action은 추가하지 않았다.

### 2026-06-08 - Reference 5차로 drift guard와 QA polish를 추가한다

- User request: 사용자가 Reference 개편 5차 작업 진행을 요청함.
- Interpreted goal: 4차 contextual links가 붙은 뒤 Glossary term / Reference route boundary와 어긋나지 않도록 자동 점검하고, 화면 guide path 표시를 정리해야 함.
- Analysis result: guard는 `app/services/reference_contextual_help.py`에 Streamlit-free report로 두고, renderer는 catalog text 표시만 담당하는 것이 UI-engine boundary에 맞다.
- Follow-up: `build_reference_contextual_help_drift_report()`를 추가하고 raw `>` guide focus copy를 slash path로 정리했다. Reference query deep-linking과 신규 surface 확장은 후속 선택 사항으로 남긴다.

### 2026-06-08 - sub-dev는 Overview / Ingestion / Operations 분석·시각화 베이스로 활용한다

- User request: 사용자가 이 세션 / worktree를 핵심 백테스트·검증과 별개로 Overview, Ingestion, Operations 및 macro / 시장 자료 분석·시각화 개발 방향을 잡는 베이스로 쓰고 싶다고 설명하고, 현재 Overview 정보의 장점 / 약점 / 개선 후보를 정리해 달라고 요청함.
- Interpreted goal: AGENTS.md를 지금 변경하지 않고, product direction research bundle로 sub-dev 역할과 다음 개발 후보를 정리한다.
- Analysis result: 현재 Overview는 DB-backed market context coverage가 넓지만 futures / sentiment / events / movers / data health가 분산되어 있어 summary-first macro cockpit이 먼저 필요하다. 두 번째 후보는 Data Health와 Ingestion 실행 콘솔의 action handoff 강화다.
- Follow-up: 상세 산출물은 `.aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/`를 본다. 구현은 사용자 승인 후 별도 세션에서 시작한다.

### 2026-06-08 - Overview Macro Context Cockpit V1을 1차로 구현한다

- User request: 사용자가 sub-dev worktree에서 승인된 1차 범위로 `Overview Macro Context Cockpit V1` 설계/구현, Browser QA, 문서 정리, commit까지 요청함.
- Interpreted goal: 새 수집 / 스키마 / 저장 없이 기존 DB-backed Overview read model을 합성해 첫 화면에서 market movement, breadth, futures, sentiment, events, data freshness, next deep tab을 읽게 한다.
- Analysis result: Cockpit 합성은 `app/services/overview_market_intelligence.py`에 두고, helper cache와 `overview_ui_components.py` 렌더러를 통해 `render_overview_dashboard` 탭 위에 표시하는 구조가 UI-engine boundary에 맞다.
- Follow-up: 2차는 Data Health -> Ingestion handoff, 3차는 breadth / heatmap and macro week view다. Candidate Ops IA 변경은 별도 승인 후보로 남긴다.

### 2026-06-08 - Overview Data Health -> Ingestion Handoff를 2차로 구현한다

- User request: 사용자가 1차 Cockpit 다음 2차 작업 진행을 요청함.
- Interpreted goal: Data Health가 보여주는 stale / missing / failed / partial / due 상태를 사용자가 실제로 확인할 collection surface로 넘기되, Overview가 Ingestion 실행 큐나 job owner가 되면 안 됨.
- Analysis result: 기존 `build_collection_ops_snapshot` row를 재사용해 Streamlit-free handoff model을 만들고, Data Health 탭 상단에 우선순위 / owner / target / freshness / read-only boundary를 표시하는 것이 가장 작은 변경이다.
- Follow-up: 3차 후보는 breadth / heatmap and macro week view이며, persistent Ingestion Action Queue나 Candidate Ops IA 변경은 별도 승인 후 진행한다.

### 2026-06-08 - Overview breadth / macro week first pass를 3차로 구현한다

- User request: 사용자가 2차 다음 3차 작업 진행을 요청함.
- Interpreted goal: 첫 화면과 deep tab 진입 전에 움직임이 broad한지 집중됐는지, 가까운 FOMC / CPI / PPI / Employment / GDP / earnings 이벤트가 무엇인지 기존 DB-backed snapshot으로 보여줘야 함.
- Analysis result: group leadership snapshot은 participation / concentration summary와 existing latest heatmap으로 접고, event calendar snapshot은 14일 macro week lane과 cluster로 접는 것이 가장 작은 변경이다.
- Follow-up: full breadth heatmap, events quality workflow, source/provider hardening, Overview IA closeout은 후속 4~5차 후보로 남긴다.

### 2026-06-08 - Overview source confidence catalog를 4차로 구현한다

- User request: 사용자가 3차 다음 4차 작업 진행을 요청함.
- Interpreted goal: 1~3차 Overview context가 어떤 source / provider / collector 상태에 기대는지 cockpit 안에서 숨기지 않고 보여줘야 함.
- Analysis result: 새 provider hardening이 아니라 기존 cockpit snapshots를 재사용해 source, owner, freshness, caveat, next check를 표시하는 read-only catalog가 가장 안전한 4차다.
- Follow-up: 5차는 Overview IA closeout 후보이며, Reference companion이나 provider 교체 / paid source decision은 별도 승인 후보로 남긴다.

### 2026-06-08 - Overview IA closeout을 5차로 구현한다

- User request: 사용자가 다음 단계 진행을 요청함.
- Interpreted goal: 1~4차로 만든 Overview cockpit 흐름을 deep tab IA와 연결하고 Candidate Ops 경계를 닫되, Backtest workflow나 navigation removal까지 확장하면 안 됨.
- Analysis result: cockpit 아래 static `Overview Map / Deep Tab Reading Order`를 두고 Market Context / Data Repair / transitional Candidate Ops를 나누는 것이 가장 작은 closeout 변경이다.
- Follow-up: 실제 Candidate Ops relocation / removal, Reference companion, provider hardening은 별도 승인 후보로 남긴다.

### 2026-06-09 - Futures Monitor 전체 선택 시 chart가 6개만 보이는 원인을 고친다

- User request: 사용자가 `Futures Monitor`에서 symbol을 전체로 해도 선물 그래프가 6개만 나오는 것 같다고 확인과 진행 방향을 요청함.
- Interpreted goal: 전체 선택 상태에서 숨은 6개 cap 때문에 chart coverage가 오해되지 않도록 하되, 기본 렌더 성능은 유지해야 함.
- Analysis result: DB read model은 23개 선택과 16개 OHLCV row coverage를 이미 전달했고, UI helper `_futures_chart_symbols()`가 chart grid를 첫 6개로 제한하고 있었다.
- Follow-up: `Charts` control을 추가해 기본 `Compact 6`과 `All with data`를 분리했다. Provider / DB schema / persistence / validation / monitoring / trading boundary는 변경하지 않았다.

### 2026-06-10 - Overview market context 안내를 한글화하고 일괄 갱신入口를 추가한다

- User request: 사용자가 `Market context needs review`, `Overview Map` 등 영어-first 문구를 이해하기 쉽게 한글화하고, Overview 상단에서 보이는 데이터를 일괄 업데이트하는 기능을 먼저 요청함.
- Interpreted goal: product term은 유지하되 설명 copy를 한국어 중심으로 바꾸고, 기존 개별 refresh job들을 한 버튼에서 실행하는 수동 bundle을 추가해야 함.
- Analysis result: 새 provider / schema가 아니라 `app/jobs/overview_actions.py` facade 안에서 SP500 movers, futures 1m/daily, sentiment, FOMC, earnings, macro calendar 기존 action을 순차 실행하는 것이 경계에 맞다.
- Follow-up: `Workspace > Overview` 상단에 `Market Context 일괄 갱신` 버튼을 추가했다. Scheduler hardening, source별 retry UX, action queue persistence는 후속 차수로 남겼다.

### 2026-06-10 - Overview Macro Context를 별도 첫 탭으로 분리한다

- User request: 사용자가 Overview Macro Context를 Market Movers 앞의 별도 탭으로 만들고, Deep Tab 안내도 cockpit과 같이 움직이는 것이 맞는지 질문 후 진행을 승인함.
- Interpreted goal: Overview 진입 시 종합 context를 먼저 보게 하고, deep tab 안내 / Overview Map을 해당 summary surface 안에 묶어야 함.
- Analysis result: `Market Context`를 첫 deep tab으로 두고 refresh / cockpit / Deep Tab guide / Overview Map을 함께 렌더링하는 것이 IA상 가장 명확하다.
- Follow-up: `Workspace > Overview > Market Context` 첫 탭을 추가했다. 자동 갱신 정책과 refresh result UX 세분화는 후속 차수로 남겼다.

### 2026-06-10 - Market Context cockpit을 card-first에서 summary-first로 개선한다

- User request: 사용자가 card-heavy UX가 최선인지, `시장 context 확인이 필요합니다` copy가 오해를 줄 수 있는지 물은 뒤 전체 개선을 요청함.
- Interpreted goal: 시장 상태 경고처럼 읽히는 headline을 source/data review 의미로 정정하고, 첫 화면에서 결론과 다음 확인 순서가 먼저 보이게 해야 함.
- Analysis result: 기존 카드 분리는 source/freshness 노출에는 좋지만 읽는 순서가 약하므로, summary rail을 카드 위에 두고 analytical cards와 supporting cards의 밀도를 나누는 것이 적절하다.
- Follow-up: `Market Context 일부 source 확인 필요` headline, 상태 / 다음 확인 / 자료 기준 rail, primary/secondary card styling을 추가했다. Source Confidence / Overview Map 접힘 UX는 후속 후보로 남긴다.

### 2026-06-10 - Market Context 보조 섹션을 접힘 형태로 낮춘다

- User request: 사용자가 2차 진행을 요청함.
- Interpreted goal: Source Confidence와 Overview Map은 중요하지만 첫 화면의 분석 결론보다 보조 근거이므로 기본 노출 밀도를 낮춰야 함.
- Analysis result: 두 섹션을 별도 탭으로 빼기보다 같은 Market Context 안에서 native disclosure로 접어 두는 것이 경계와 흐름을 보존한다.
- Follow-up: `Source Confidence / 출처 신뢰도`와 `Overview Map / 화면 지도`를 기본 접힘 섹션으로 렌더링했다. refresh result UX 세분화는 3차로 남긴다.

### 2026-06-12 - Market Context를 가이드 UI에서 시장 브리프 UI로 바꾼다

- User request: 사용자가 `Overview > Market Context` 후속 개선 1차를 승인하면서, Events/Data Health 보강이나 과거 유사국면 기능은 구현하지 말고 후속 리스크로만 정리하라고 요청함.
- Interpreted goal: 기존 `현재 맥락:` 핵심요약은 유지하되, 별도 `다음 확인 순서`, Deep Tab guide, `해석 전 확인` 카드 묶음이 시장 브리프 흐름을 끊지 않게 재배치해야 함.
- Analysis result: cockpit read model에 `brief_rows`와 `interpretation_cues`를 추가하고, renderer는 시장 움직임 / 확산 / futures-macro 배경 / 이벤트·심리·자료 주의점을 row 흐름으로 보여주는 것이 가장 작은 변경이다.
- Follow-up: 2차는 갱신 후 상단 context 반영과 Data Health 노출 범위 재검토, 별도 데이터 작업은 CPI/Event coverage 보강, 별도 제품 검토는 과거 유사국면 기능이다.

### 2026-06-12 - Market Context 갱신 후 상단 브리프가 새 snapshot을 다시 읽게 한다

- User request: 사용자가 후속 개선 2차로 `보조 갱신` 실행 후 상단 Market Context가 실제 새 snapshot을 반영하는지 고치라고 요청함.
- Interpreted goal: job result table을 키우지 않고, cache/rerun 문제를 해결해 사용자가 상단 브리프의 반영 여부를 작게 확인할 수 있어야 함.
- Analysis result: cockpit이 refresh button보다 먼저 렌더되므로 cache clear만으로는 같은 Streamlit pass의 상단 brief를 갱신할 수 없다. result 저장 -> reflection state 저장 -> cache clear -> `st.rerun()` 순서가 필요하다.
- Follow-up: CPI/Event coverage 보강, Macro Calendar 수집/ICS fallback 검증, Data Health 노출 범위 재검토는 3차 이후 별도 작업으로 남긴다.
