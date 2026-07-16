# Finance Roadmap

Status: Active
Last Verified: 2026-07-16

## Current State After Master Merge

현재 active phase는 없다.

현재 active task는 없다.

Latest completed task는 `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-context-v1-20260716/`다.

- 목적: 경제사이클 결과 아래의 정적인 네 문장을 실제 evidence 기반 자산별 확인 흐름으로 바꾼다.
- 완료: 1차 자산별 orientation/read model, 2차 2×2 React 카드·actual read model·regression/docs를 닫았다.
- 판정 계약: 네 canonical factor 중 비중립 근거가 두 개 미만이면 `자료 부족`, 우호/부담 개수 차이가 두 개 이상이면 우세 상태, 나머지는 `혼재`다. 국면은 설명 맥락으로만 사용한다.
- actual 상태: 2026-06-30 기준 `채권·금리 혼재 / 주식 부담 / 금·달러 우호 / 원자재 혼재`이며 카드마다 두 근거와 바뀌는 조건을 표시한다.
- 품질 경계: 수익률·목표가격·매수/매도 예측이 아니며 별도 가격/provider 수집과 경제사이클 validation gate는 변경하지 않았다.
- 상세 계획: `docs/superpowers/plans/2026-07-16-economic-cycle-asset-context.md`.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/`다.

- 목적: 계산 가능한 `LIMITED` 결과를 전부 숨기던 V1을 `잠정 모델 추정 / 검증된 모델 추정 / 판단 불가`로 분리하고, 원형 clock을 승인된 2×2 혼합형으로 교체한다.
- 완료: 1차 contract 확인, 2차 provisional persistence/read model, 3차 2×2 확률 경로·ribbon, 4차 122 snapshot 재물질화·desktop/420px Browser QA, 5차 docs/regression을 닫았다.
- actual 상태: publication gate는 h0/h1/h2 모두 `LIMITED`지만 세 horizon의 유효 계산값은 `PROVISIONAL`이다. 2026-06-30 우세 결과는 현재 회복 `46.7%`, +1M 회복 `40.5%`, +2M 회복 `47.4%`다. DB의 121개월 replay는 보존하고 화면 read model은 최근 60개월만 제공한다.
- 품질 경계: rolling-origin threshold와 PIT 원칙은 변경하지 않았다. parameter/입력이 불완전한 horizon만 `UNAVAILABLE`로 남기고 유효 LIMITED 확률은 검증 사유와 함께 공개한다.
- UI: 현재/+1M/+2M 확률 카드, 2×2 회복·확장·둔화·침체 좌표, 최근 12개월 과거 실선, 미래 점선, hover/focus 지점 정보, 최근 60개월+2개월 ribbon을 표시한다. Ribbon 열 수는 실제 history 개수를 사용해 전체 너비를 채운다.
- 상세 계획: `docs/superpowers/plans/2026-07-16-us-economic-cycle-provisional-hybrid.md`.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-us-economic-cycle-v1-20260716/`다.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-derived-quarter-provenance-v1-20260716/`다.

- 목적: taxonomy concept rename 때문에 끊긴 전환분석 Q4/TTM을 동등한 확정 공시 concept family로 복구하고, 직접 공시와 산출값을 화면에서 구분한다.
- 완료: 1차 mixed-concept Q4 resolver, 2차 per-metric/TTM provenance, 3차 neutral marker/inspector disclosure, 4차 actual/Browser QA와 docs.
- 계산 계약: exact concept와 direct Q4가 우선이다. missing Q4만 explicit family의 같은 symbol/fiscal year/unit 및 primary-period/PIT 조건을 만족한 FY/Q1/Q2/Q3로 계산한다.
- 사용자 계약: `FILING_DERIVED`는 forecast가 아닌 `공시 기반 산출`이며 source-quarter marker, active formula, TTM input notice로 표시한다. guard 실패는 계속 결측이고 선을 보간하지 않는다.
- actual QA: MRNA 2023-Q4 revenue `2.811B`, GP `1.882B`, operating income `0.006B`; desktop/420px overflow 0과 신규 console error 0을 확인했다.
- 제외: taxonomy 문자열 유사도 매칭, schema/provider/collector 변경, 자동 backfill, universe-wide concept audit.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/`다.

- 목적: AAPL의 stored diluted EPS가 전환분석 unit filter에서 누락되는 버그를 수정하고, 6개 rail에서 transition과 already-positive state를 구분했다.
- 완료: 1차 EPS reader/operating evidence, 2차 rail semantics/copy, 3차 actual/Browser QA와 docs.
- 의미: `USD per share`를 canonical diluted-EPS unit으로 읽고, backend milestone threshold는 유지한다. React의 `ESTABLISHED`만 이미 흑자인 영업/EPS 상태를 전환 `MET`과 구분한다.
- actual QA: AAPL PER/turnaround TTM EPS `7.90`, headline `PER_READY`; RIVN TTM EPS `-3.07`, `PER_READY=NOT_MET`. desktop/420px overflow 0과 신규 console error 0을 확인했다.
- 제외: schema/provider/자동수집/진단 panel/universe screener.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/`다.

- 목적: PER와 전환 분석 공통 상단에 `최신 데이터로 다시 계산` action 하나를 두고, 실제 repairable freshness gap만 selected-symbol 범위로 수집한다.
- 현재 단계: 1차 공용 calendar/freshness/CIK-independent collection, 2차 unified event/UI, 3차 actual/Browser QA와 문서 정렬을 완료했다.
- 최신성 계약: 가격은 마지막 완료 NYSE session, 시장가치는 profile snapshot과 가격 기준일 7일 정렬, 재무는 기존 raw coverage gap만 사용한다.
- 수집 계약: 검색·선택·분석 전환은 DB-only다. explicit click에서 profile/price는 CIK 없이 실행하고 SEC statement만 CIK identity를 요구한다.
- UI 계약: PER/전환 selector 바깥의 CTA 하나가 두 분석을 함께 다시 읽으며, generic 기준일을 가격·재무·공개일로 구분한다.
- actual QA: NET는 explicit action 뒤 price `2026-07-14`, profile `2026-07-15`, statement period `2026-03-31` / available `2026-05-08`로 READY가 됐다. AAPL stale 화면은 CTA 1개와 desktop/420px overflow 0을 확인했다.
- 범위 제외: 자동 수집, 전체 종목 갱신, 새 진단 패널, 새 table/schema, 발표되지 않은 filing calendar 추정.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-turnaround-analysis-v1-20260715/`다.

- 목적: 미국 개별주식 내부에 `PER 상대가치 | 전환 분석`을 추가해 P/E가 성립하지 않는 selected company를 quarterly filing evidence로 분석한다.
- 현재 단계: 1차 분기 계산 정확도, 2차 분석 엔진, 3차 loader/service/collection, 4차 UI, 5차 actual/Browser QA와 문서 정렬을 완료했다.
- 계산 계약: cumulative H1/9M/FY를 discrete Q2/Q3/Q4로 filing-aware 복원하고, TTM 매출·margin·OCF·FCF·EPS를 quarterly available_at 기준으로 만든다.
- 판단 계약: operating milestone과 cash runway/debt/dilution risk를 분리하고 negative/zero denominator를 valid multiple로 바꾸지 않는다.
- UI 계약: selected stock 안에서 PER/전환 selector를 제공하며 negative EPS는 전환 분석을 기본으로 연다. Graph는 monthly PER 복제가 아니라 8/12/20-quarter 영업·현금 전환이다.
- 가치평가 계약: current input freshness와 numerator/denominator consistency가 검증될 때만 stage-appropriate multiple/yield를 표시하며 target price/매매 신호를 만들지 않는다.
- 운영 경계: 검색·선택·분석 전환은 DB read-only다. raw 보강은 SEC CIK를 확인한 selected symbol의 명시 action만 허용하고, missing CIK는 분석을 보존한 채 collection만 BLOCKED로 둔다.
- actual QA: RIVN/LCID/PLTR는 전환 분석, AMD/AAPL은 기존 PER를 추천했다. 420px overflow와 browser console error는 0이었다.
- 범위: V1은 selected-company analysis다. all-U.S.-stock discovery/ranking과 peer-relative valuation은 후속이다.

Previous completed U.S. stock valuation task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-valuation-v1-20260714/`다.

- 목적: Market Context의 Nasdaq-100 user-facing selector를 searchable 미국 개별주식 상대가치 화면으로 교체한다.
- 현재 단계: 1차 계산 정확도, 2차 엔진, 3차 검색·수집, 4차 UI 교체, 5차 actual/Browser QA와 문서 정렬을 완료했다.
- 계산 계약: 월말 가격과 filing-aware quarterly TTM diluted EPS carry-forward로 monthly P/E를 만들며 EPS를 월별 보간하지 않는다.
- Graph 2 계약: FOMC real GDP + PCE를 macro proxy로 두고, 기업의 historical TTM EPS excess growth P25/P50/P75를 결합한다.
- 운영 경계: 검색/화면 진입은 DB read-only이고 selected-symbol price/SEC 수집은 명시 action에서만 실행한다.
- 결과: AAPL/NVDA/META/TSLA actual DB는 READY이며 loss/short-listing/SEC-gap/split/foreign issuer 경계도 distinct state로 검증했다. S&P 화면은 유지하고 기존 Nasdaq backend는 보존했다.
- 정확성 후속: comparative Q/FY는 primary filing period만 사용하고 split-year Q/FY를 같은 share basis로 맞춘 뒤 Q4를 계산한다. AMD actual은 TTM EPS `3.05`, P/E `169.22x`, 성장 관측 `10/8`로 READY이며 Graph 1/Graph 2 상태를 독립 판정한다.
- 부분 이력 후속: 개별주 1/3/5년은 요청한 전체 달력 월을 유지하면서 `READY/PARTIAL/INSUFFICIENT_HISTORY`를 구분한다. 계산 가능한 월만 원래 위치에 그리며, missing price/EPS, non-positive EPS, rolling warmup, PIT evidence gap을 연결·보간하지 않는다. Actual AAPL은 3년 `36/36`, 5년 `42/60`; AMD는 `33/36`, `39/60`이다.
- 다음 단계: 현재 PER/전환 분석의 필수 후속은 없다. historical SEP/PIT coverage backfill, all-stock turnaround discovery, peer-relative valuation은 각각 독립 승인 범위다.

Previous completed Nasdaq history task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-scenario-history-warmup-v1-20260713/`다.

- 목적: Nasdaq valuation이 READY여도 60개월 rolling PER warmup 부족으로 비어 있던 1/3/5년 적정구간을, 사용자가 최대 119개월 실제 자료 보강으로 복구하거나 정확한 잔여 부족량을 확인하게 한다.
- 현재 단계: 1차 warmup 진단, 2차 119개월 resumable repair, 3차 history action/EPS 출처, 4차 React/Python UX, 5차 actual DB/Browser QA와 문서 정렬을 완료했다.
- actual QA: canonical repair는 172,240 rows를 저장했고 READY 월을 62에서 66으로 늘렸다. 현재 1/3/5년은 각각 71/95/119개월 중 66개월이 준비돼 7개 계산점만 있으며, 전체 선택 기간이 준비될 때까지 `INSUFFICIENT_HISTORY`로 유지한다.
- 품질 경계: 60개월 rolling log(PER), 월별 actual diluted EPS/price weighted coverage 95%, filing availability를 유지한다. blocked 월을 보간하거나 공식 Nasdaq index-level P/E/EPS로 표시하지 않는다.
- 운영 경계: 화면 진입만으로 provider를 호출하지 않는다. valuation blocker의 60개월 action과 READY-state history의 119개월 action을 분리하고, 명시 클릭에서만 동기 수집한다.
- 다음 data step: acquired/delisted historical constituents와 foreign issuer의 무료·안정적 EPS/EOD source contract가 승인되기 전에는 gate를 낮추거나 blocked 월을 합성하지 않는다.

Previous completed Nasdaq coverage task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713/`다.

- 목적: SEC QQQ holdings와 SEC company actual을 결합한 QQQ proxy의 최근 60개월 valuation coverage blocker를 사용자 action으로 보강한다.
- 결과: planner, canonical EPS/EOD 수집, strict rematerialization, synchronous blocker CTA를 완료했고 당시 local 60개월 gate를 복구했다.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/`다.

### Recent Completed Institutional Portfolios Track

Recent completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-security-detail-chart-layout-v1-20260712/`다.

- 목적: `Workspace > Institutional Portfolios > 종목 분석 > 종목 상세`에서 차트와 보유 기관 리스트가 2-column으로 나뉘고 기본 range slider가 어색했던 종목 상세 UX를 줄였다.
- 주요 변경: selected-security detail을 선택 종목 / 포트폴리오 내 위치 overview card, full-width stored-OHLCV chart row, 하단 scrollable holder-list row로 재배치했다. 차트는 OHLC / volume strip, volume bars, price scale, mini navigator, line/candle toggle, hover crosshair를 유지한다.
- 이번 차수에서 하지 않은 일: DB schema 변경, ingestion 변경, provider 변경, full chart library 도입, true holding-duration metric, 추천 / trading semantics 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-watchlist-mapping-v1-20260712/`다.

- 목적: `Workspace > Institutional Portfolios`에서 유명 투자자 alias 검색과 CUSIP-symbol mapping 상태가 부족해 드러켄밀러 같은 대가 포트폴리오를 찾기 어렵고, 가격 차트 empty 원인을 구분하기 어려웠던 문제를 줄였다.
- 주요 변경: manager watchlist / alias seed를 Duquesne, Bridgewater, Third Point, Icahn, Tiger Global, Lone Pine, Soros, Akre 등으로 확장하고 DB watchlist loader 경계를 열었다. manager search는 alias 매칭 CIK를 우선 보여주고 검색 중 rail / selection도 검색 결과 순서를 따른다. ambiguous CUSIP-symbol mapping은 차트용 ticker로 쓰지 않는다. selected-security price action은 `symbol_missing`, `mapping_ambiguous`, `price_missing`, `ready` 상태로 분리된다.
- 이번 차수에서 하지 않은 일: Dataroma / Fintel scraping, WhaleWisdom / OpenFIGI adapter 구현, 새 가격 provider, DB schema 변경, 추천 / trading semantics 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-two-tier-tabs-v1-20260712/`다.

- 목적: `Workspace > Institutional Portfolios`에서 `포트폴리오 / 종목 분석` 구분이 한 줄 안의 그룹 라벨처럼 보여 어색했던 탭 UX를 줄였다.
- 주요 변경: React workbench tab bar를 상위 탭(`포트폴리오`, `종목 분석`)과 현재 상위 영역에 따른 하위 탭(`요약 / 전체 보유` 또는 `종목 상세 / 기관 보유 랭킹`)으로 분리했다.
- 이번 차수에서 하지 않은 일: DB schema 변경, ingestion 변경, provider 변경, true holding-duration metric, 추천 / trading semantics 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-portfolio-security-ia-v1-20260712/`다.

- 목적: `Workspace > Institutional Portfolios`에서 기관 포트폴리오 탭과 티커 / 기업 분석 탭이 같은 1차 레벨에 섞여 보이는 IA 혼선을 줄였다.
- 주요 변경: React workbench tab bar를 `포트폴리오` 그룹(`요약`, `전체 보유`)과 `종목 분석` 그룹(`종목 상세`, `기관 보유 랭킹`)으로 분리했다. 기존 `보유 기관 조회` 기능은 `종목 상세` 안의 보유 기관 리스트로 유지한다.
- 이번 차수에서 하지 않은 일: true multi-quarter holding duration metric, DB schema 변경, ingestion 변경, external provider, 추천 / trading semantics 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-interactive-security-chart-v1-20260712/`다.

- 목적: `Workspace > Institutional Portfolios` 보유기관조회의 선택 종목 차트를 단순 mini line chart에서 hover / dotted guide / range 이동 / 라인-캔들 toggle이 있는 저장 OHLCV 기반 interactive chart로 개선했다.
- 주요 변경: selected-security chart payload에 `open/high/low/close/volume`을 포함하고, React `InteractiveSecurityChart`가 tooltip, crosshair, high-low guide, range slider, pan controls, line/candle mode를 렌더링한다.
- 이번 차수에서 하지 않은 일: 새 가격 provider, UI external fetch, DB schema 변경, live trading / 추천 / broker / auto rebalance 연결.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-holding-chart-refresh-v1-20260712/`다.

- 목적: `Workspace > Institutional Portfolios` 보유기관조회에서 선택 종목 차트가 비어 보이는 원인을 실제 DB 기준으로 분리하고, DB에 이미 있는 가격 row는 차트로 연결하며, 가격 row가 없을 때는 버튼으로 기존 OHLCV 수집 job을 실행하게 한다.
- 주요 변경: service-level safe CUSIP-symbol resolver, curated symbol -> CUSIP 우선 reverse lookup, selected-security price action payload, React 가격 데이터 수집 버튼, Streamlit event -> `run_collect_ohlcv` boundary를 추가했다.
- 이번 차수에서 하지 않은 일: DB schema 변경, external site scraping, full security master 구축, 추천 / 매매 신호 / live trading / auto rebalance 연결.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-ux-detail-performance-v1-20260711/`다.

- 목적: Institutional Portfolios의 selected-security detail, report-period performance, institution-count ranking, scroll / pending fallback을 보강했다.
- 주요 변경: CUSIP-level aggregation, selected-security chart payload, report-period performance panel, institution-count ranking tab을 추가했다.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-live-sec13f-v1-20260709/`다.

- 목적: React workbench가 preview sample에 머무르지 않고 SEC official 13F DB snapshot을 실제로 읽는 제품 화면이 되게 한다.
- 주요 변경: refresh status / watchlist schema, official SEC 13F ingestion status row, secondary refresh panel, workbench freshness payload, conservative CUSIP-symbol enrichment, docs / QA를 정렬했다.
- 이번 차수에서 하지 않은 일: Dataroma / WhaleWisdom / Fintel scraping, paid API adapter, broker / live trading / auto rebalance, 완전한 security master 구축.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-react-workbench-v1-20260709/`다.

- 목적: 기존 `Workspace > Institutional Portfolios` V1이 SEC 13F ingestion / DB 조회 중심으로 보여 실제 투자 대가 / 기관 포트폴리오를 시각적으로 탐색하는 제품 경험이 약했던 문제를 해결했다.
- 주요 변경: `app/web/streamlit_components/institutional_portfolios_workbench/` React workbench를 추가하고, Python service에 visual payload / preview payload contract를 만들었다. 첫 화면은 manager rail, allocation donut, top holdings, reported quarter change board, sector exposure, holdings tab, institutional interest drill-down을 보여준다. DB empty 상태는 clearly labeled preview로 표시하고 raw DB error는 setup expander에만 둔다.
- 이번 차수에서 하지 않은 일: 새 provider / paid API integration, Dataroma / WhaleWisdom scraping, broker / live trading / auto rebalance 연동, 완전한 security master 수준 CUSIP-symbol mapping.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/institutional-portfolios-workspace-v1-20260708/`다.

- 목적: Market Movers의 선택 종목 조사단서와 분리해, 투자 대가 / 기관별 전체 SEC Form 13F portfolio와 reported holdings change를 Workspace에서 탐색하는 read-only surface를 만들었다.
- 주요 변경: `Workspace > Institutional Portfolios` navigation, SEC 13F official data set ingestion action, `finance_meta.institutional_13f_*` schema, parser / loader / service read model, holdings / reported changes / sector exposure / reverse lookup UI, source caveat / runbook / flow docs를 추가했다.
- 이번 차수에서 하지 않은 일: Dataroma / WhaleWisdom scraping, paid API integration, broker / live trading / auto rebalance 연동, Backtest / Practical Validation / Final Review gate 연결, 완전한 security master 수준의 CUSIP-symbol mapping.

Recent completed Final Review task는 `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/`다.

- 목적: 해결 가능한 근거는 Practical Validation에서 닫고, 핵심 미구현은 block/defer하며, Final Review에는 수용 또는 Monitoring 이관으로 종결할 비핵심 한계만 전달한다.
- 주요 변경: root issue dedup, Level2 actionability Gate, GRS 기간과 survivorship applicability 계약, Final Review terminal-state snapshot, measured-only score impact를 완료했다.
- QA: focused service/source contract tests, 실제 DB 확인, React build, py_compile, diff check, Browser QA를 완료했다. Dynamic historical universe용 PIT membership/delisting provider는 후속 승인 전까지 blocker로 남긴다.

Previous completed Overview / Market Context task는 `.aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712/`다.

- 목적: 기존 Market Context brief/cockpit/sector/event visible composition을 제거하고, 현재 S&P 500의 상대 멀티플 위치와 FOMC 기반 예상 EPS/지수 시나리오를 숫자로 비교한다.
- 주요 변경: Shiller 월별 가격·EPS, optional S&P Index Earnings actual As-Reported quarter, Federal Reserve SEP vintage, SPX/SPY EOD를 `Ingestion -> DB -> Loader -> Service -> React`로 연결했다. 그래프 1은 완결 Shiller 최근 60개월의 `-2σ/-1σ/중심/+1σ/+2σ` log(PER) anchor와 36개월 민감도를 유지하면서, EPS 미발표 최신 가격월과 current SPX EOD를 March EPS 기준 잠정 PER 점선으로 2026-07까지 연장한다. 그래프 2는 공식 actual 4분기를 우선하고 없으면 최신 Robert Shiller TTM EPS를 사용하며, 공식 SEP 21개 vintage와 120개월 Shiller warmup으로 최근 1년·3년·5년 실제 SPX/rolling 적정 SPX band를 선택해 표시한다.
- 경계: 월별 과거 지점은 월중 SEP를 다음 달부터 적용하고 calendar-year target을 선택한다. 이 흐름은 Shiller EPS가 strict release-vintage PIT 원본이 아니므로 `과거 시점 재구성 시나리오`이며, SEP median `real GDP + PCE`와 trailing PER band는 공식 적정가·투자 신호·애널리스트 컨센서스가 아니다.
- QA: valuation 37 tests, Market Context 35 contracts, TypeScript, Vite build, 실제 21개 SEP vintage/1,867 Shiller rows 기반 read model, desktop/420px Browser QA를 통과했다. Graph 2 history는 12/36/60 points를 반환했고 5년 화면의 SEP marker 19개/label 7개와 current-app console error/horizontal overflow 0건을 확인했다. generated V1.4 QA screenshot은 커밋하지 않는다.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-movers-top-actions-monthly-history-v1-20260711/`다.

- 목적: Market Movers 비-Daily 상단의 긴 설명형 버튼을 간결하게 만들고, Monthly full-window 갱신 성공 뒤에도 provider 가용 이력이 짧은 종목이 같은 갱신 대상으로 반복되는 문제를 해결했다.
- 주요 변경: action button에는 행동명만 남기고 대상/기간/제외 설명은 버튼 아래 한 줄로 분리했다. Full-window 수집 후에도 period row threshold가 부족한 symbol은 `market_data_issue(issue_type=limited_price_history)`로 기록하며, 이후 preflight에서는 현재 랭킹 제외 상태로 설명하고 같은 수집 action을 다시 제안하지 않는다.
- 이번 차수에서 하지 않은 일: S&P 500 membership 변경, Monthly 수익률 계산식 변경, 과거 가격 합성, 새 provider/table/schema, 자동 매매/검증/모니터링 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-movers-visual-grouping-v1-20260711/`다.

- 목적: Sector Breadth의 색상 범위가 카드 테두리/막대에서 끊기고, 선택 종목 조사 workflow가 여러 독립 박스로 분리돼 보이는 문제를 줄였다.
- 주요 변경: React/fallback Sector Breadth는 3% outer surface와 4% lane direction tint를 사용한다. Ranking Board는 모드별 전체 상세 표 expander를 같은 keyed 부모에 둔다. 선택 종목 조사는 selector, React 조사 패널, 조사 단서 tabs, Research Snapshot, 기본 지표 그래프를 keyed Streamlit 부모 container 하나로 묶는다.
- 이번 차수에서 하지 않은 일: 섹터 계산/payload 의미, 선택 종목 조회 action, provider/DB/schema/registry/saved 변경.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/overview-market-movers-section-title-unification-v1-20260711/`다.

- 목적: Market Movers의 `섹터 / 시장 확산 맥락`이 외부 divider와 내부 결과 title을 중복 사용해 큰 섹션 계층이 고정되지 않는 문제를 줄였다.
- 주요 변경: React/fallback 섹터 영역은 `SECTOR BREADTH / 섹터 / 시장 확산 맥락 / 설명 / 상태` 헤더를 사용하고, 데이터 기반 breadth headline은 그 아래 결과 요약으로 분리한다.
- 이번 차수에서 하지 않은 일: Market Movers 상단/Ranking Board/선택 종목 조사 재설계, 섹터 계산/payload 의미 변경, provider/DB/schema/registry/saved 변경.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/post-merge-docs-flow-refresh-20260708/`다.

Previous completed Practical Validation recheck handoff task는 `.aiworkspace/note/finance/tasks/active/practical-validation-recheck-handoff-loop-fix-v1-20260712/`다.

- 목적: Final Review에서 Level2 보강으로 돌아간 뒤 자료만 수집하고 구형 검토서를 다시 여는 반복을 차단한다.
- 주요 변경: 두 provider collection 완료 경로가 replay state를 공통으로 초기화하고, Level2가 `자료 보강 -> Flow 2 재검증 -> 새 결과 저장 -> Final Review 확인` 순서를 표시한다. current-session replay가 없으면 save-and-move를 거부한다.
- Final Review: append-only history는 보존하되 source별 최신 validation을 eligibility보다 먼저 선택한다. 최신 row가 blocked면 과거 eligible row로 fallback하지 않으며, 명시적인 save-and-move만 새 stable key를 선택·확정한다.
- QA: focused service / contract tests 188개, React production build, target py_compile, `git diff --check`, Final Review 재검증 상태 / 판단 비활성 / 760px no-overflow Browser QA를 통과했다. 실제 provider 수집과 registry append는 실행하지 않았다. in-app Browser의 custom component rerun은 자동화에서 관측하지 못해 Python intent consumer와 recovery contract test로 보완했다.

Latest completed Practical Validation pre-Final enrichment gate task는 `.aiworkspace/note/finance/tasks/active/practical-validation-pre-final-enrichment-gate-v1-20260712/`다.

- 목적: 현재 Python collector로 해결 가능한 필수 외부 데이터 gap을 Final Review 숙제로 넘기지 않고 Practical Validation에서 보강·재검증한 뒤에만 승격한다.
- 주요 변경: executable operability / holdings·exposure / required macro plan을 synthetic `pre_final_data_enrichment` blocker로 합성하고, Flow 4 수집 뒤 Flow 2 replay를 초기화해 재검증과 새 validation 저장을 강제한다.
- Final Review: current blocking validation은 후보에서 제외한다. legacy / later-stale 검토서는 복구 안내와 과거 근거만 읽을 수 있고, Decision Desk / recommendation / Final Decision Action은 `2단계 재검증 필요` 상태로 잠긴다.
- QA: focused service / contract tests, React build, py_compile, `git diff --check`, Practical Validation ↔ Final Review Browser QA, 760px no-overflow 검증을 통과했다. provider 수집과 판단 저장은 실행하지 않았고 registry / saved / run history / screenshot을 커밋하지 않았다.

Previous completed Final Review readable review evidence task는 `.aiworkspace/note/finance/tasks/active/final-review-readable-review-evidence-v1-20260711/`다.

- 목적: `남은 판단 근거`의 raw audit 이름과 코드형 관측·판단 근거를 사용자 언어로 바꾸고, 각 항목이 무엇이며 어떻게 개선할지를 같은 카드에서 끝내게 한다.
- 주요 변경: stored audit 값을 새로 판정하지 않고 한국어 title / 검증 설명 / 현재 확인 내용 / 판단 이유로 번역했다. 각 trace는 데이터 최신화, source 탐색, 재검증, 기간 확장, 검증 기능 보강, 사용자 판단, 인수 제한 중 하나의 행동으로 분류한다.
- 사용자 흐름: 실제 provider plan이 있는 항목만 `2단계 데이터 보강으로 이동`을 제공한다. Final Review React는 navigation intent만 내고, Practical Validation Python boundary가 같은 후보의 수집 실행과 이후 Flow 2 재검증을 소유한다.
- QA: focused contract test 59개, React build, py_compile, `git diff --check`, 760px Browser QA와 Final Review → Practical Validation handoff를 통과했다. 실제 수집 / 판단 저장은 실행하지 않았고 registry / saved / run history를 변경하지 않았다.

Previous completed Final Review decision flow simplification task는 `.aiworkspace/note/finance/tasks/active/final-review-decision-flow-simplification-v1-20260711/`다.

- 목적: 실제 완료 행동인 최종 판단을 긴 report 뒤에서 총평 / 4행 해석 직후로 올리고, 중복 Appendix와 과거 ledger가 완료 지점을 흐리지 않게 한다.
- 주요 변경: React report 안에 네 route와 사용자가 직접 작성하는 판단 사유, gate 기반 CTA를 배치했다. React는 intent만 전달하고 Python이 save evaluation, 자동 Decision ID, route template, row append를 소유한다.
- 화면 정리: Evidence Appendix와 Saved Decisions / Dossier / Evidence Packet / Raw JSON을 Final Review에서 제거했다. selected row 운영 확인은 Operations > Portfolio Monitoring이 소유하며 기존 decision JSONL은 보존한다.
- QA: BacktestRuntime / FinalReviewEvidence 계약 137개, React build, py_compile, `git diff --check`, Browser QA의 확인 전후 / 화면 순서 / 사유 입력 전후 CTA / Appendix·Saved 미노출을 확인했다. 실제 저장 CTA는 누르지 않아 registry를 변경하지 않았다.

Previous completed Final Review responsive evidence task는 `.aiworkspace/note/finance/tasks/active/final-review-responsive-evidence-v1-20260711/`다.

- 목적: 축소 화면에서 REVIEW trace list가 공통 2열 selector에 잡혀 첫 카드가 좁아지고 긴 audit 문자열이 옆 카드를 밀어내던 문제를 해결한다.
- 주요 변경: review impact header selector를 first child로 한정하고 trace list를 독립 1열로 고정했다. 긴 lifecycle / provider 문자열은 카드 내부에서 줄바꿈하며, compact / mobile에서는 header badge와 trace label을 세로로 정리한다.
- 판단 경계: Python evidence / score / gate / 저장 계약은 변경하지 않았다. React CSS와 presentation contract만 보정했다.
- QA: React build, focused contract test, py_compile, `git diff --check`, Browser QA 900px / 680px를 통과했고 두 폭 모두 document / trace 가로 overflow 0을 확인했다.

Previous completed Final Review decision surface consolidation task는 `.aiworkspace/note/finance/tasks/active/final-review-decision-surface-consolidation-v1-20260711/`다.

- 목적: 하단 근거 탭의 시각적 단절, REVIEW trace 빈칸, 목적이 불명확한 대안 실험, 투자 검토서와 중복되는 Decision Cockpit / Final Decision Action을 하나의 판단 흐름으로 정리한다.
- 주요 변경: 하단을 연결된 `점수 근거 / 남은 판단 근거 / 다음 실험 아이디어` shell로 바꾸고 세부 점수명을 한국어로 정리했다. Level2 summary는 module별 stored audit row와 연결해 measured / derived / qualitative / missing contract로 구분한다. 다음 실험은 적용 가능한 상위 3개만 `바꿀 것 / 같게 둘 것 / 확인할 것`으로 표시한다.
- 판단 흐름: standalone Decision Cockpit과 반복 Save Readiness / disabled order action은 visible flow에서 제거했다. Python selection-readiness model은 유지하고 `판단 기록`이 상태 / 차단 수 / 권장 판단 / route / 사유 / 저장 CTA를 한 번에 보여준다.
- QA: Final Review evidence service 53개, page contract 8개, React build, py_compile, `git diff --check`, Browser QA를 통과했다. registry / saved / run history / QA screenshot은 변경 또는 stage하지 않았다.

Previous completed Final Review guidance actionability task는 `.aiworkspace/note/finance/tasks/active/final-review-guidance-actionability-v1-20260711/`다.

- 목적: 모든 패턴이 비슷한 `참고` 문장으로 보이고 Level2 보강 지시가 Final Review 행동처럼 노출되던 문제를 해결해, 사용자가 현재 판단과 다음 행동을 바로 읽게 한다.
- 주요 변경: 10개 패턴을 named evidence adapter 기반 `판단 가능 / 조건부 추적 / 추가 검증 필요 / 적용 제외`로 판정하고 first-read를 최대 6개로 제한했다. 각 카드는 `현재 진단 / 의미 / 변화 조건 / 다음 행동`을 표시하고 source / 기준일 / technical path는 접힌 상세로 이동했다. 총평 아래에는 성과 / 위험 / 근거 신뢰도 / Monitoring 적합성 4행을 배치했다.
- stage ownership: Final Review는 `최종 판단에서 결정할 것 / 2단계에서 인수한 제한사항 / Monitoring으로 넘길 조건 / 선정 전 해소할 차단 항목`만 구분한다. 2단계 Flow4 보강 문구는 Final Review 사용자 행동으로 반복하지 않는다.
- QA: focused service / contract tests 53개, React build, py_compile, `git diff --check`, Browser QA의 확인 전후 / 후보 변경 stale 차단 / Review Queue 제거 / 기술 trace disclosure / 4행 해석 / REVIEW 소유권을 확인했다.

Latest completed portfolio workflow reset task는 `.aiworkspace/note/finance/tasks/active/portfolio-workflow-legacy-reset-rebuild-20260711/`다.

- 목적: 구형 저장 계약으로 인해 Level2 REVIEW가 Final Review에서 한 역할로 몰리던 기존 6개 후보를 현재 1차 → 2차 → 3차 계약으로 다시 생성한다.
- 주요 변경: 단일 GRS 4개와 weighted mix 2개를 stored-period runtime으로 재실행하고, source 6개 / workspace·review role 포함 validation 6개 / schema-v3 monitoring decision 6개를 새 ID로 저장했다. Portfolio Monitoring setup 3개도 새 decision ID로 다시 연결했다.
- 저장 경계: 이번 작업은 사용자가 명시한 reset migration으로 active registry chain을 교체했다. legacy reusable `SAVED_PORTFOLIOS.jsonl`은 제거했고, live approval / broker order / auto rebalance는 만들지 않았다.
- QA: data-chain invariant, focused unittest 5개, py_compile, `git diff --check` 통과. Browser QA는 localhost URL 보안 정책으로 미실행이다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-investment-report-redesign-v1-20260711/`다.

- 목적: 투자 검토서의 중복 상태 / 기술 용어 / 불명확한 REVIEW 감점과 반복 본문을 정리하고, 저장 evidence 범위 안에서 조건부 Monitoring 방향을 제시한다.
- 주요 변경: 외부 Investment Report card를 제거하고 헤더를 단일 상태 / 투자 매력도 / 확인 필요 수로 줄였다. 투자 매력도, 근거 신뢰도, Monitoring 준비도를 분리하고 open REVIEW 개수 자동 감점 / cap을 제거했다. 총평, 강점 / 약점, 저장 전 질문과 10개 조건부 패턴 가이드를 first-read로 만들고 하단은 `점수 근거 / REVIEW 근거 / 대안 실험 후보` 세 탭으로 정리했다.
- 판단 경계: Python service가 score 의미, REVIEW trace, 패턴 support state와 조건부 문구를 만들고 React는 표시만 한다. 패턴은 `supported / indicative / insufficient`만 사용하며 대안 배분은 counterfactual backtest 전에는 점수 개선으로 예측하지 않는다.
- QA: focused tests 53개, React build, py_compile, `git diff --check`, Browser QA 확인 전후 / stale 차단 / Review Queue 제거 / 점수 축 / 패턴 가이드 / REVIEW와 대안 실험 탭을 확인했다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-confirmed-review-flow-v1-20260711/`다.

- 목적: label identity와 즉시 report 렌더 때문에 생기는 후보 오선택 / stale 혼동을 막고, Level2 REVIEW를 실제 확인 행동으로 읽게 했다.
- 주요 변경: Final Review 후보 selector는 stable key를 사용하고 visible Review Queue를 제거했다. `최종 검토서 확인` 전에는 후보별 report / cockpit / decision action을 열지 않으며, 선택 변경 시 stale 경고와 함께 downstream surface를 숨긴다. 투자 검토서는 다섯 REVIEW role을 `Final Review 확인 필요`에서 `점수에 반영됨 / 저장 전 확인 / Monitoring 조건으로 넘김 / blocker`로 표시한다.
- 판단 경계: 확인 버튼은 저장된 Practical Validation evidence를 읽을 후보만 확정한다. 재검증, provider fetch, DB 수집, registry / saved rewrite, live approval, broker order, auto rebalance를 수행하지 않는다.
- QA: focused tests 53개, React build, py_compile, `git diff --check`, Browser QA 후보 연속 전환 / 확인 전후 / stale 차단 / Level2 행동 섹션 / Review Queue 제거를 확인했다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-investment-report-detail-tabs-v1-20260711/`다.

- 목적: Final Review `투자 검토서` 하단 상세 근거가 expander 5개로 세로 반복되어 다시 긴 목록처럼 보이는 문제를 줄였다.
- 주요 변경: React investment report lower detail 영역을 `근거 상세`, `저장 경계`, `개선 후보`, `Review 처리`, `Monitoring` 탭으로 바꿨고, 선택한 탭 하나의 내용만 하단 panel에 표시한다.
- 판단 경계: 탭 상태는 React local UI state일 뿐이며 Python score, gate, route decision, save guidance, Monitoring handoff, provider / persistence boundary는 변경하지 않았다.
- QA: RED/GREEN source contract, focused Final Review / evidence service tests 51개, py_compile, npm build, `git diff --check`, Browser QA tab click과 screenshot을 확인했다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-investment-report-flat-ui-v1-20260710/`다.

- 목적: Final Review `투자 검토서`가 박스 안에 박스가 반복되는 dashboard처럼 보여 Monitoring 후보 여부, 추천 이유, 확인 지점을 빠르게 읽기 어려운 문제를 줄였다.
- 주요 변경: React investment report first-read를 meta strip, `왜 후보인가` / `무엇을 확인해야 하나` decision brief, capped strength / watch rows, interpretation rows로 평면화했다. 상세 scorecard, Level2 REVIEW 처리, 저장 / Monitoring handoff, 약점 개선안, Monitoring 조건은 lower disclosure로 낮췄다.
- 판단 경계: Python read model이 score, gate, route decision, save guidance, Monitoring handoff, provider / persistence boundary를 계속 소유한다. React는 기존 payload 표시 우선순위와 layout만 바꾼다.
- QA: TDD RED/GREEN source contract, focused Final Review / evidence service tests 51개, py_compile, npm build, `git diff --check`, Browser QA iframe DOM check와 screenshot을 확인했다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-investment-report-ia-v1-20260710/`다.

- 목적: Final Review `투자 검토서`가 최종 선택 사유, 저장 전 메모, 저장 / Monitoring handoff copy를 반복하고 일부 하단 카드가 guide처럼 보이는 문제를 줄였다.
- 주요 변경: Python investment report payload가 `decision_summary`, high-score dimension 기반 강점, compact `watch_items`, 실제 해석용 `interpretation_cards`를 만들고 React는 `선택 판단 요약`, `강점`, `확인 지점`, `해석`으로 표시한다. first-read의 old `다음 행동` / `판단 저장 전 메모` block은 제거했다.
- 판단 경계: score, gate, route decision, save, Monitoring handoff, provider fetch, registry / saved JSONL persistence는 변경하지 않았다. React는 Python read model 표시만 맡는다.
- QA: TDD RED/GREEN, focused Final Review / evidence service tests 51개, py_compile, npm build, `git diff --check`, Browser QA를 확인했다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-candidate-selection-integration-v1-20260710/`다.

- 목적: Final Review의 독립 `Step 1 / Candidate Board`가 상단 `후보 현황과 다음 판단`과 같은 후보 상태를 반복해 보이는 문제를 줄였다.
- 주요 변경: `Backtest > Final Review`는 Decision Desk 아래에 Review Queue, `검토 대상` selector, 접힌 후보 비교 상세를 바로 붙이고, 중복 select-ready / hold / blocked lane cards와 numbered Step eyebrow를 제거했다. 이후 흐름은 `Final Review 투자 검토서`, `Decision Cockpit`, `Final Decision Action`, `Evidence Appendix`, saved decision review로 의미형 섹션을 따라 읽는다.
- 판단 경계: Candidate Board read model은 계속 기존 evidence를 읽어 queue / detail을 만들지만, UI는 별도 단계처럼 보이지 않는다. score, gate, 저장, provider fetch, registry / saved JSONL write, Portfolio Monitoring handoff 계산은 변경하지 않았다.
- QA: TDD RED/GREEN source contract, focused Final Review / evidence tests 52개, py_compile, `git diff --check`, Browser QA를 확인했다.

Previous completed Final Review UX follow-up task는 `.aiworkspace/note/finance/tasks/active/final-review-sentiment-scope-cleanup-v1-20260710/`다.

- 목적: Final Review에서 판단 근거가 아닌 CNN / AAII 시장심리 패널과 raw detail table이 first-read decision surface를 차지하지 않게 했다.
- 주요 변경: `Backtest > Final Review`는 Decision Desk 다음에 후보 선택 패널과 투자 검토서를 이어서 보여주며, 시장심리 패널 / `CNN / AAII detail` expander를 렌더링하지 않는다. 자세한 심리 해석은 `Workspace > Overview > Sentiment`가 소유하고, Operations > Portfolio Monitoring의 read-only context overlay는 유지한다.
- 판단 경계: 시장심리는 Final Review gate, score, 저장 가능 여부, Candidate Board priority, Portfolio Monitoring signal, broker order, auto rebalance를 바꾸지 않는다. 시장심리 timing / rebalance 활용은 별도 제품 리서치와 look-ahead-safe 검증 전까지 구현하지 않는다.
- QA: focused Final Review source contract와 timing / rebalance documentation contract를 RED/GREEN으로 확인했다.

Previous completed Final Review UX task는 `.aiworkspace/note/finance/tasks/active/final-review-top-ux-cleanup-v1-v4-20260709/`다.

- 목적: Backtest `Final Review / Level3` 상단을 안내 / 가이드 반복이 아니라 후보 현황, 선택 가능성, 다음 판단 중심으로 정리했다.
- 주요 변경: top summary를 짧은 목적 / destination copy로 줄이고, shared Backtest selector의 오래된 run-history caption과 Final Review top Reference help, 1~5 flow card를 first-read surface에서 제거했다. Decision Desk는 올라온 후보, 선택 가능, 보류 / 재검토, 숨김, 저장된 판단, Monitoring 연결을 먼저 보여준다. 후속 `final-review-sentiment-scope-cleanup-v1-20260710`에서 CNN / AAII sentiment 패널도 Final Review first-read에서 제거했다.
- 판단 경계: Final Review는 gate / score / 저장 / Monitoring handoff 계산을 Python service / page boundary에 유지한다. 시장심리는 context-only이며 selected-route gate, Candidate Board priority, Final Decision save readiness, Portfolio Monitoring signal을 바꾸지 않는다.
- QA: 1차~4차를 development -> QA -> commit 순서로 진행했고, focused service/source contract tests 55개, py_compile, `git diff --check`, Browser QA로 Final Review 상단 렌더링과 `Operations > Portfolio Monitoring` route wording을 확인했다.
- 후속 후보: `sentiment timing / rebalance research`는 별도 제품 리서치와 look-ahead-safe 검증 후에만 논의한다. 현재 task에서는 시장심리를 gate나 monitoring signal로 만들지 않았다.

Previous completed Final Review task는 `.aiworkspace/note/finance/tasks/active/final-review-detailed-scorecard-v1-v6-20260709/`다.

- 목적: Backtest `Final Review / Level3`의 단순 종합 점수를 실전 포트폴리오 선별에 쓸 수 있는 세부 점수 / 점수 상한 / 선택 사유 read model로 강화했다.
- 주요 변경: Python `backtest_evidence_read_model`이 5개 weighted dimension(`Investment`, `Risk`, `Readiness`, `Evidence Quality`, `Monitoring Suitability`), Level2 REVIEW role별 점수 영향, hard blocker / selected-route not-ready / gate review-required / 과도한 open review score cap, selection rationale, 판단 저장 전 required note를 만든다. React `Final Review 투자 검토서`는 이를 `세부 점수`, `Level2 REVIEW 점수 영향`, `최종 선택 사유`, `판단 저장 전 메모`로 표시만 한다.
- 판단 경계: Level2 REVIEW는 Final Review에서 재검증하지 않고 최종 판단 부담 / 근거 품질 / Monitoring 추적 조건으로 점수와 사유에 반영한다. blocker와 selected-route not-ready는 높은 원점수라도 추천권 점수로 올라가지 않게 cap을 적용한다.
- QA: service contract 47개 focused test, React build, py_compile, Browser QA에서 Final Review React iframe의 `세부 점수`, `Level2 REVIEW 점수 영향`, `최종 선택 사유`, `판단 저장 전 메모` 렌더링을 확인했다.
- 후속 후보: 실제 portfolio variant 생성, 자동 약점 최적화, 개선 포트폴리오 신규 backtest / 비교 저장은 구현하지 않았다. 필요하면 별도 task에서 Python engine/service boundary로 설계한다.

Previous completed Final Review task는 `.aiworkspace/note/finance/tasks/active/final-review-level3-react-v2-v6-20260709/`다.

Previous completed Final Review analysis task는 `.aiworkspace/note/finance/tasks/active/final-review-level3-redesign-analysis-v1-20260709/`다.

Latest completed Practical Validation task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow5-cta-integration-v1-20260709/`다.

- 목적: Practical Validation Flow5가 별도 검증 단계처럼 보이면서 Flow3 결론과 저장 / Final Review 이동 action이 분리되어 보이는 문제를 줄였다.
- 주요 변경: Flow3 `검증 결론` React component가 `next_stage_action` read model을 받아 `검증 결과 저장(기록용)`과 `저장하고 Final Review로 이동` CTA를 렌더링한다. React는 click intent만 보내고, Python page/service가 save-only audit append, Final Review handoff, session state, rerun을 처리한다. 별도 visible Flow5 container는 제거했고 Selection Source JSON / Practical Validation Result JSON은 Flow4 `상세 근거 / 원자료` Raw Evidence로 낮췄다.
- 이번 차수에서 하지 않은 일: validation gate threshold 변경, Final Review selected-route policy 변경, provider/FRED/API/DB fetch path 생성, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/`다.

- 목적: Practical Validation의 `REVIEW`가 모두 Final Review 숙제처럼 보이고 REVIEW-only 카테고리가 숨겨져 검증 항목이 갑자기 줄어든 것처럼 보이는 문제를 바로잡았다.
- 주요 변경: `review_role` / `review_role_label` read-model contract를 추가해 REVIEW를 `데이터 주의`, `2단계 실용성 주의`, `최종 판단 참고`, `Monitoring 추적`, `저장 전 보강`으로 분리했다. Flow 4는 적용된 REVIEW-only Practical Validation category를 숨기지 않고 카테고리별 검증 결과에서 보여주며, provider-facing copy는 `ETF 운용사 / 공식 외부 데이터` 중심으로 낮췄다. Final Review는 수익성 / benchmark / 후보 비교 / 최종 모니터링 후보 판단 중심으로 설명한다.
- 이번 차수에서 하지 않은 일: 새 수집 엔진, DB schema, provider fetch path, validation gate threshold 전면 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-center-v1-20260709/`다.

- 목적: Practical Validation Flow 4에서 `데이터 보강 대상`과 `Provider 보강 액션`이 별도 영역처럼 보이며, 사용자가 수집 버튼이 무엇을 수집하는지 알기 어려운 문제를 줄인다.
- 주요 변경: Flow 4를 `카테고리별 검증 결과 -> 데이터 보강 / 수집 실행 -> 상세 근거 / 원자료`로 읽게 했다. React board는 표시 전용 `데이터 보강 대상`을 맡고, 기존 Python 수집 버튼은 같은 action center의 `수집 실행` 하위 블록으로 남긴다. 버튼 주변에는 `수집하는 것 / 하지 않는 것 / 실행 후 다음 단계`를 배치했고, provider 작업 상세 table은 `상세 근거 / 원자료` raw detail로 낮췄다.
- 이번 차수에서 하지 않은 일: 새 수집 엔진, DB schema, provider fetch path, validation gate threshold, Final Review 화면 재구성, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-data-action-board-v1-20260709/`다.

- 목적: Practical Validation Flow 4에서 지금 해결할 데이터 보강 항목과 Final Review / Monitoring에서 판단할 참고 항목이 섞여 보이는 문제를 줄였다.
- 주요 변경: Flow 4 visible order를 `카테고리별 검증 결과 -> 데이터 보강 대상 / 액션 -> 상세 근거 / 원자료`로 정리했다. 후속 action center task에서 이 영역의 user-facing 이름을 `데이터 보강 / 수집 실행`으로 확정했다. `단계별 검증 소유권` expander와 별도 `수집 대상 근거` expander는 visible UI에서 제거하고, Python workspace read model의 display-only `data_action_board`를 React card board로 렌더링한다. React는 props 표시만 맡고 provider/FRED/API/DB fetch, validation calculation, collection execution, gate, registry / saved write는 기존 Python service / runtime 경계에 남겼다.
- 이번 차수에서 하지 않은 일: 새 수집 엔진, DB schema, provider fetch path, Final Review 화면 재구성, gate threshold 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow-gating-evidence-ia-v1-20260708/`다.

- 목적: Practical Validation에서 Flow 2 재검증 실행 전 Flow 3 / Flow 4가 자동으로 보이는 문제를 막고, Flow 4 하단의 근거 / Provider 부족근거 덩어리를 실제 보강 흐름 중심으로 정리했다.
- 주요 변경: Flow 2 current-session replay가 없으면 Flow 1 / Flow 2만 렌더링한다. Data Coverage / Construction Risk / Provider Investability 중 수집으로 해결 가능한 provider / holdings / exposure / macro gap만 `수집하기` CTA를 노출한다. Flow 4는 `카테고리별 검증 결과 -> 단계별 검증 소유권 -> Provider / Data 보강 액션 -> 접힌 근거 부록` 순서로 읽는다.
- 이번 차수에서 하지 않은 일: Final Review 화면 재구성, gate threshold 변경, registry / saved JSONL rewrite, provider ingestion 신규 경로, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-category-empty-state-v1-20260708/`다.

- 목적: Practical Validation Flow 4 `카테고리별 검증 결과`에서 `보강 항목 없음`이 통과 / 비적용 / Final Review 판단 항목처럼 애매하게 보이는 문제를 줄였다.
- 주요 변경: workspace read model에 `visible_criteria_detail_groups`와 `visible_in_practical_validation`을 추가했다. Flow 3 React / fallback과 Flow 4 board는 visible groups만 읽고, REVIEW-only / empty group은 내부 read model에는 남기되 PV visible category result에서 숨긴다. React fallback copy도 `보강 항목 없음`을 통과처럼 해석하지 않게 정리했다.
- 이번 차수에서 하지 않은 일: Final Review 화면 재구성, Final Review gate threshold 변경, validation module planner 정책 변경, registry / saved JSONL rewrite, provider ingestion, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/post-merge-docs-flow-refresh-20260708/`다.

- 목적: `sub-dev` / `backtest-dev` 병합 이후 공용 문서의 current pointer, 코드 흐름, Overview surface 이름이 현재 master와 어긋나지 않게 정리했다.
- 주요 변경: Product Direction, Roadmap, architecture / data / flow docs, Overview runbook을 현재 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events` primary tab 구조와 Backtest / Practical Validation / Operations 경계에 맞췄다. `Futures Monitor` / `Sector / Industry`는 current primary surface가 아니라 retained data / helper context 또는 과거 이력으로 낮췄고, Overview Data Health handoff / Market Context cockpit의 user-facing service label도 `Futures Macro` / `Market Movers` 기준으로 보정했다.
- 이번 차수에서 하지 않은 일: product UX 구조 변경, provider ingestion, DB schema / strategy runtime 변경, registry / saved JSONL rewrite, generated QA screenshot 정리, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-boundary-cleanup-v1-20260708/`다.

- 목적: Practical Validation Flow 3 / Flow 4가 Final Review에서 판단할 `REVIEW` 항목을 현재 보강해야 할 검증 이슈처럼 보여주는 혼선을 줄였다.
- 주요 변경: Flow 3은 Practical Validation outcome summary를 읽어 `보강 후 재검증`, 실패 카테고리, 검증 카테고리만 보여주며 `Final Review 이동 가능 / 보류`, `확인 필요` review count, `보류 항목` copy를 제거했다. Flow 4는 `Final Review 참고`, `Final Review 이동 요약`, legacy gate technical expander를 렌더링하지 않고, Practical Validation에서 보강해야 할 기준과 원인만 보여준다.
- 이번 차수에서 하지 않은 일: Final Review 화면 재구성, Final Review gate threshold 변경, registry / saved JSONL rewrite, provider ingestion, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-final-review-handoff-v1-20260708/`다.

- 목적: Practical Validation Flow 4가 Final Review에서 해석할 REVIEW 항목을 카테고리별 상세 문제처럼 보여 사용자가 현재 보강해야 할 항목과 최종 판단 항목을 혼동하는 문제를 줄였다.
- 주요 변경: 당시 Flow 4 main board는 `통과`, `보강 후 재검증 필요`, `실전 사용 어려움`을 먼저 보여주며, REVIEW 항목을 `Final Review 참고` handoff count로 낮췄다. 후속 Boundary Cleanup V1에서 이 visible count도 Flow 3 / Flow 4에서 제거했다.
- 이번 차수에서 하지 않은 일: Final Review evidence 화면 재구성, gate threshold 변경, registry / saved JSONL rewrite, provider ingestion, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-outcome-taxonomy-v1-20260708/`다.

- 목적: Practical Validation Flow 4가 raw status 중심으로 보여 `REVIEW`, `NEEDS_INPUT`, `BLOCKED`의 실제 행동 의미를 구분하기 어려운 문제를 줄였다.
- 주요 변경: Flow 4 criteria summary는 `통과`, `보강 후 재검증 필요`, `Final Review 판단 필요`, `실전 사용 어려움` outcome layer를 먼저 보여준다. `READY`는 통과로 읽고, `Current=REVIEW`인 input check는 `NEEDS_INPUT`으로 강등하지 않아 최신 replay / coverage review가 Final Review 판단 항목으로 남는다.
- 이번 차수에서 하지 않은 일: registry / saved JSONL rewrite, provider ingestion, 새 DB schema, Final Review selected-route threshold 전면 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-refactor-v1-20260708/`다.

- 목적: Practical Validation의 1차 필수 검증에서 같은 검증이 여러 module 안에 반복되는 문제를 줄이고, `validation_efficacy`를 방법론 검증 전용으로 축소했다.
- 주요 변경: `app/services/backtest_validation_efficacy.py`는 walk-forward / OOS / regime split row만 생성한다. module planner / board registry / workspace는 `Validation Method Strength`와 `Stress / Robustness`를 분리해 보여주며, Flow 4 copy는 `검증 방법론`, `강건성`, `실전성 진단`처럼 사용자-facing 업무명으로 정리했다. Final Review gate와 evidence read model도 `Validation Method Strength` label과 method-only blocker 문구를 사용한다.
- 이번 차수에서 하지 않은 일: gate threshold 강화, registry / saved JSONL rewrite, provider ingestion, 새 DB schema, 새 live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-audit-v1-20260708/`다.

- 목적: Practical Validation의 1차 필수 검증이 여러 module 안에서 같은 검증을 반복 소유하는 문제를 막기 위해 현재 audit row inventory와 `check_id -> owner_module` taxonomy를 정리했다.
- 주요 결론: `validation_efficacy`는 source / replay / benchmark / provider / PIT / survivorship / robustness를 다시 보는 umbrella audit이 아니라 walk-forward / OOS / regime split 중심의 `validation_method_strength`로 축소해야 한다. replay, benchmark, PIT, survivorship, provider freshness, stress/robustness는 각각 owner module이 단독 소유해야 한다.
- 이번 차수에서 하지 않은 일: Python service refactor, gate threshold 변경, Flow 4 UI 변경, registry / saved JSONL rewrite, provider ingestion, Final Review selected-route policy 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-symbol-resolver-v1-20260708/`다.

- 목적: Backtest Quality / Value Factor Readiness에서 stale/missing price ticker가 단순 가격 지연인지 ticker-change symbol identity 문제인지 구분하고, 사용자가 검토 후 repair를 실행할 수 있게 한다.
- 주요 변경: `nyse_symbol_lifecycle(event_type=ticker_change)` 기반 resolver / active repair 저장 path를 추가했다. 후보는 same CIK, lifecycle coverage, source reference, resolved ticker price freshness를 `evidence_factors`로 설명하고 LOW confidence는 자동 반영하지 않는다. Active repair는 source ticker를 rewrite하지 않고 collection ticker만 resolved symbol로 바꾸며, price refresh plan/details에 `source_range` / `resolved_range` / `split_status` metadata-only PIT split contract를 남긴다. Factor Readiness는 후보쌍 / 신뢰도 / 기간 경계 / 다음 행동을 보여주고 repair 후 readiness 재확인과 백테스트 재실행을 안내한다.
- 이번 차수에서 하지 않은 일: official corporate-action feed 신규 수집, 실제 old/new ticker price series stitching, universe 선정 정책 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-factor-readiness-action-ui-v1-20260707/`다.

- 목적: Quality / Value strict form의 Factor Readiness가 내부 진단값 중심으로 보여 사용자가 `무엇이 문제인지 / 어떤 티커인지 / 어떻게 해결할지`를 바로 알기 어려운 문제를 줄인다.
- 주요 변경: strict preset 안내는 후보군 선택 정보만 짧게 남기고, Factor Readiness React panel은 문제 / 영향받는 티커 / 해결 방법 / action button 중심 contract로 바꿨다. 가격 문제는 Backtest OHLCV refresh service, statement gap은 targeted Extended Statement Refresh로 연결하고, provider/source gap은 반복 업데이트가 아니라 수동 확인 문제로 표시한다.
- 이번 차수에서 하지 않은 일: OHLCV provider 교체, DB schema 변경, universe 선정 정책 변경, factor/runtime 계산 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-coverage-provider-gap-refresh-v1-20260707/`다.

- 목적: Backtest Data Trust의 Coverage 최신화가 provider no-data / persistent source gap 심볼을 계속 해결 가능한 버튼으로 보여주는 문제를 막는다.
- 주요 변경: price refresh plan이 명백한 provider/source gap 심볼을 refresh 대상에서 제외하고, 실행 후 rows_written=0 + unresolved 심볼이 남으면 같은 화면에서 retry action card를 다시 렌더링하지 않는다.
- 이번 차수에서 하지 않은 일: OHLCV provider 교체, DB schema 변경, universe 선정 정책 변경, factor/runtime 결과 계산 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-steps-v3-20260707/`다.

- 목적: Practical Validation Flow 4의 `해결 방법`이 여러 Next Action을 한 줄에 이어 붙인 설명처럼 보이지 않게 하고, 사용자가 처리 순서를 바로 읽을 수 있게 했다.
- 주요 변경: `resolution_guide`에 UI용 `action_steps` list를 추가하고, Flow 4 criteria card가 이를 번호형 목록으로 렌더링한다. non-PASS audit row의 `Next Action`은 구체 단계로 우선 노출하고, 기준별 기본 action guide는 보강 / 재검증 같은 후속 단계로 붙인다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, module severity 변경, replay 실행 로직 변경, provider ingestion orchestration 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-guide-v2-20260707/`다.

- 목적: Practical Validation Flow 4의 상세 카드가 위치 안내에 머물지 않고, 사용자가 실제로 무엇을 보강하면 통과되는지 판단할 수 있게 했다.
- 주요 변경: `resolution_guide`에 `통과 기준`을 추가하고, criteria card를 `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치` 구조로 재구성했다. Audit row의 non-PASS `Criteria`와 `Next Action`은 계속 우선 사용하며, 위치는 실행 위치 보조 정보로 낮췄다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, replay 실행 로직 변경, provider ingestion orchestration 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Recent Backtest completed task는 `.aiworkspace/note/finance/tasks/active/backtest-quarterly-productionization-v1-20260708/`다.

- 목적: Strict quarterly Quality / Value / Quality+Value를 prototype 표시가 아닌 formal `Strict Quarterly` 후보로 정식화하되, quarterly filing lag와 statement shadow coverage 민감성은 post-run Factor Readiness에서 확인하게 한다.
- 주요 변경: strict quarterly runtime wrappers가 annual-like investability / benchmark / promotion / guardrail inputs를 받도록 확장했고, result bundle에 statement shadow coverage metadata를 남긴다. post-run Factor Readiness는 실제 실행 결과 기준으로 가격 / statement 문제 티커와 해결 버튼을 보여준다. Strategy catalog / runner catalog / evidence inventory / forms / compare / history helper는 user-facing `Strict Quarterly` label을 사용하고 legacy `_prototype` key는 replay 호환용으로 유지한다.
- 이번 차수에서 하지 않은 일: official historical index membership ingestion, provider no-data 대체 소스 구축, live approval / broker order / auto rebalance, 기존 saved/run history JSONL 재작성.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-resolution-guide-v1-20260707/`다.

- 목적: Practical Validation Flow 4의 `보강 위치`가 단순 위치 문자열이라 사용자가 실제 부족 항목과 해야 할 일을 파악하기 어려운 문제를 해결했다.
- 주요 변경: workspace read model에 `resolution_guide`를 추가하고, Flow 4 criteria card를 `검증한 것 / 부족한 것 또는 확인할 것 / 해야 할 일 / 확인 위치` 구조로 렌더링한다. Data Coverage / Validation Method Strength 등 audit row가 있는 기준은 non-PASS `Criteria`와 `Next Action`을 우선 사용한다. 위치명은 `Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세`, `Flow4 > Provider / Data 보강 액션`처럼 실제 화면 경로로 세분화했다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, replay 실행 로직 변경, provider ingestion orchestration 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/backtest-pit-universe-v1-20260707/`다.

- 목적: Quality / Value strict coverage가 현재 market-cap Top-N을 과거 전체 기간에 고정해 쓰는 look-ahead / survivorship 위험을 줄이고, 사용자가 2016년부터 실행할 때 당시 월말 기준 근사 universe를 선택할 수 있게 한다.
- 주요 변경: `finance_meta.equity_universe_snapshot` / `equity_universe_member` schema와 builder / upsert / loader를 추가했다. Strict Quality / Value / Quality+Value annual and quarterly strict runners는 `PIT Monthly Snapshot Universe`를 선택하면 사전 저장 monthly membership을 읽고, 각 리밸런싱일에는 가장 가까운 이전 snapshot을 적용한다. Backtest Single Strategy와 Portfolio Mix Builder strict form은 `PIT Monthly Snapshot Universe`만 visible option으로 노출한다. Static Managed Research와 Historical Dynamic PIT는 기존 saved payload / old run 호환용 legacy internal path로만 유지한다.
- 이번 차수에서 하지 않은 일: paid official historical Russell / S&P membership ingestion, float-adjusted market cap feed, broker execution, live approval / order / auto rebalance, 기존 Strategy selector의 React 이관.
- 중요한 한계: V1 PIT monthly universe는 DB 가격과 latest-known statement shares 기반 근사 large-cap membership이다. 공식 지수 편입 이력이나 완전한 historical float-adjusted market cap이 필요하면 별도 provider / collector phase가 필요하다.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-strategy-form-cleanup-v1-20260707/`다.

- 목적: 사용자가 요청한 맥락대로 기존 Strategy dropdown과 strategy-specific Streamlit form switching은 유지하고, 과하게 추가된 Strategy Detail panel을 제거한 뒤 각 전략 form 내부의 preset / preflight / advanced input 설명만 정리했다.
- 주요 변경: active Strategy Detail service / React component / render path를 제거했다. strict preset 설명은 `현재 기준 / 주의 / 업데이트 방법` compact model로 바꿨고, Quality / Value strict form은 `데이터 준비 기준`, compact preset basis, Price Freshness Preflight 순서로 읽히게 했다. Equal Weight / ETF-like form은 기존 layout을 유지하고 혼란스러운 `runtime wrapper` copy만 줄였으며, Portfolio Mix Builder는 Streamlit-owned strict settings와 같은 preset helper를 계속 사용한다.
- 이번 차수에서 하지 않은 일: Strategy selector / actual form controls의 React 이관, strategy runtime / result bundle / registry / saved JSONL / Practical Validation gate policy 변경, provider 수집 로직 변경, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task record는 `.aiworkspace/note/finance/tasks/active/backtest-strategy-detail-react-v1-20260707/`다. 이 작업의 Price Freshness Preflight asset fix는 유지하지만, Strategy Detail panel은 latest cleanup task에서 제거되어 active product flow가 아니다.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-labels-v1-20260706/`다.

- 목적: Practical Validation Flow 4가 내부 `Workbench` / audit taxonomy가 아니라 사용자가 찾을 수 있는 `검증 기준 상세` 화면으로 읽히게 했다.
- 주요 변경: Flow 4 title을 `검증 기준 상세`으로 바꾸고, category title emphasis를 강화했으며, `보강 위치`를 `검증 기준 상세 · 데이터 품질 / Provider 보강`, `검증 기준 상세 · 검증 강도 / 강건성`, `Flow 2 · 실전 재검증 실행` 같은 화면 기준 위치명으로 통일했다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, replay 실행 로직 변경, provider 수집 로직 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow3-conclusion-summary-v1-20260706/`다.

- 목적: Practical Validation Flow 3을 Fix Queue / 보강 가이드가 아니라 `검증 결론` compact summary로 읽히게 했다.
- 주요 변경: Flow 3은 Final Review 이동 가능 / 보류와 카테고리별 통과 / 실패 / 확인 필요만 요약한다. `현재 문제 / 완료 기준 / 보강 위치` 같은 상세 설명과 검증 모듈 기술 상세는 Flow 4로 이동했다. 반복 안전 문구도 Flow 3 React surface에서 제거했다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, selected-route policy 변경, provider 수집 실행, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-category-results-v1-20260706/`다.

- 목적: Practical Validation Flow 4가 Final Review 이동 기준판이 아니라 카테고리별 검증 결과로 읽히게 하고, 후보 특성과 무관한 검증이 universal blocker처럼 보이는 문제를 줄였다.
- 주요 변경: workspace read model이 `Source & Replay`, `Data Quality / Bias Control`, `Comparison Validity`, `Realism / Tradability`, `Validation Method Strength`, `Stress / Robustness`, `Portfolio Construction`, `Conditional Evidence` category를 만든다. `selected_route_preflight`는 `Final Review 이동 요약`으로 분리했다. stress / robustness missing evidence는 기본 REVIEW, construction risk는 ETF-like 또는 weighted mix에만 적용, sentiment risk-on/off overlay는 macro gate status에서 제외했다.
- 이번 차수에서 하지 않은 일: provider 수집 실행, registry / saved JSONL rewrite, Final Review selected-route 저장 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-issue-summary-v1-20260706/`다.

- 목적: Practical Validation Flow 3 / Flow 4의 blocker 설명이 가이드 문단처럼 보이지 않게 하고, 사용자가 실제로 무엇을 보강해야 하는지 바로 읽게 했다.
- 주요 변경: workspace read model이 module별 `현재 문제 / 완료 기준 / 보강 위치 / 영향` field와 criteria group별 `통과한 기준 / 남은 문제 / 판정` summary를 만들었다. 이때 Flow 3 React surface는 이슈 큐로 표시했으나, 최신 `practical-validation-flow3-conclusion-summary-v1-20260706`에서 visible UI는 `검증 결론` 요약으로 축소했고 상세 보강 field는 Flow 4로 내렸다. `NEEDS_INPUT`, `NOT_RUN`, `REVIEW` 같은 raw status는 first-read label이 아니라 기술 tag로 낮춘다.
- 변경하지 않은 경계: validation threshold / gate policy 의미, registry / saved JSONL rewrite, provider 수집, replay 실행 로직, Final Review handoff persistence, live approval / broker order / auto rebalance.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-readable-fix-queue-v1-20260706/`다.

Recent Backtest handoff task는 `.aiworkspace/note/finance/tasks/active/backtest-second-stage-visibility-v1-20260705/`다.

- 목적: Backtest Analysis의 Data Trust / Handoff가 2차 Practical Validation review focus를 1차 상세 검토처럼 보여주는 혼선을 줄였다.
- 주요 변경: Data Trust는 excluded ticker / malformed price row 같은 직접 데이터 이슈만 상세 표시하고, `meta["warnings"]` 기반 review focus는 2차 전달 count / 위치 안내로 낮췄다. Handoff / Policy Signals도 2차 상세 판단 문구를 반복하지 않는다.
- 이번 차수에서 하지 않은 일: source registration write, Practical Validation review queue 저장, registry / saved JSONL / strategy runtime / gate threshold 변경.

Recent Overview / Market Movers task는 `.aiworkspace/note/finance/tasks/active/overview-market-movers-fundamental-charts-20260708/`다.

- 목적: `Workspace > Overview > Market Movers` selected-symbol 조사단서의 PER / EPS / 당기순이익 / 유동비율 / FCF chart payload와 UI를 보강해 연간 / 분기 추세를 함께 읽게 한다.
- 주요 변경: 분기 chart 이력을 연간보다 짧게 잘라 보이던 제한을 늘리고, 금액 문자열 formatter가 comma 단위 숫자와 억 / 천 달러 단위를 안정적으로 표시하도록 보강했다.

Recent Overview Futures Macro task는 `.aiworkspace/note/finance/tasks/active/overview-futures-macro-evidence-original-data-ux-20260706/`다.

- 목적: `Workspace > Overview > Futures Macro`의 React 현재 근거와 하단 `원본 데이터 / 계산 추적`을 분리하고, historical validation / raw table 문구를 사용자가 판단 재료로 연결해 읽을 수 있게 정리한다.
- 현재 상태: 1차~5차와 후속 카드 정리 완료. React workbench는 하나의 custom component / iframe 안에서 `MacroContextSection`, `RecentFlowSection`, `HistoricalValidationPanel`로 내부 분리되어, 화면상 `매크로 컨텍스트`, `최근 흐름`, `과거 점검`을 별도 카드처럼 읽게 한다. `CurrentEvidencePanel`은 `MacroContextSection` 안에서 현재 score evidence를 맡으므로 현재 근거가 과거 점검과 분리되어 읽힌다. Historical validation은 현재 16개 선물 일봉 상태를 과거 동일 계산식으로 다시 찾아보는 보조 검산이며, `오늘과 비슷한 과거 흐름 확인` action은 `과거 점검` 섹션 안에 있다. 결과는 먼저 `비슷한 상태`, `상태 빈도`, `방향성 판정`, `판정 이유` 결론 타일로 읽고, 상세 타일은 `판정`, `5거래일 표본`, `20거래일 표본`, `자산군 해석`으로 확인한다. 하단 `원본 데이터 / 계산 추적`은 `매크로 컨텍스트`, `최근 흐름`, `과거 점검`을 검산하는 raw table 부록이다.

Recent data-source migration task는 `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p8-final-docs-runbook-alignment/`다.

- 목적: 재무제표 source migration 1~9차를 닫고, durable docs와 runbook에서 EDGAR statement shadow를 canonical financial statement path로, broad yfinance fundamentals / factors를 saved/history replay용 legacy compatibility로 고정한다.
- 주요 변경: Market Movers annual financial snapshot, strict annual factor backtest family, Ingestion financial statement refresh, statement coverage QA, and docs now use EDGAR detailed statements / statement shadow as the primary source contract. Quarterly consumers remain gated to `10-Q` / `10-Q/A`; `10-K` / FY full-year flow values are not treated as quarterly values.

2026-06-07 master 병합 후 제품은 다음 네 흐름이 함께 연결된 상태다.

```text
Workspace > Ingestion
  -> Workspace > Overview market context
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

현재 5차~10차 code structure / refactor baseline round는 closeout됐다.

- 5차: UI / service / runtime / jobs / finance layer boundary and refactor baseline audit.
- 6차: Overview / Ingestion collection-read action boundary cleanup.
- 7차 / 7B: Ingestion Console physical split and read-only diagnostic facade extraction.
- 8차: Backtest runtime Risk-On Momentum, real-money / readiness, strict quality / value family split.
- 9차: Backtest Compare Portfolio Mix Builder visual component extraction.
- 10차: final structure audit, residual split decision, and handoff closeout.

- Recent GTAA cadence task: `.aiworkspace/note/finance/tasks/active/gtaa-result-cadence-monthly-valuation-20260629/`
- 목적: GTAA `interval`을 결과 row thinning이 아니라 strategy-owned rebalance cadence로 해석하고, 비리밸런싱월에도 최신 후보 신호 / valuation row를 볼 수 있게 한다.
- 주요 변경: GTAA sample / runtime path는 strategy 실행 전에 `.interval(...)`로 입력 row를 줄이지 않는다. `GTAA3Strategy(rebalance_interval=...)`가 실제 holdings 변경 cadence를 소유하고, month-end row 뒤에는 요청 종료일 이하 최신 공통 거래일 row를 보강한다.
- 이번 차수에서 하지 않은 일: 가격 데이터 coverage refresh, provider / DB schema / registry / saved JSONL 변경, Practical Validation / Final Review / Monitoring behavior 변경, live trading / broker order / auto rebalance semantics 추가.
- Recent Overview Market Movers UX redesign task: `.aiworkspace/note/finance/tasks/active/overview-market-movers-redesign-v2-01-20260629/`
- 목적: Overview > Market Movers가 metric-card / prototype pattern처럼 보이는 문제를 Toss Securities / Upbit / StockAnalysis / TradingView / Finviz benchmark 기반의 market-board UX로 1~6차 재설계한다.
- 1차 범위: user-facing language / IA reset. `변동 종목`, `랭킹 기준`, `상승 / 하락 / 거래량 / 이상 거래량 / 섹터`로 정리하고 새 provider / schema / UI external fetch / trade signal은 추가하지 않는다.
- 후속: 2차 compact mover tape / list, 3차 chart workspace, 4차 sector breadth visual, 5차 selected-symbol investigation pane, 6차 data trust / empty state hardening.
- Recent completed Overview task: `.aiworkspace/note/finance/tasks/active/overview-final-cleanup-v33-v36-20260629/`
- 목적: Overview refactor의 남은 1순위~4순위 cleanup을 닫고, UI component body / dashboard wrapper / old service facade / Data Health scope ambiguity를 정리한다.
- 주요 변경: renderer body를 `app/web/overview/components/*`로 옮기고 `overview_ui_components.py`를 thin facade로 축소했다. `overview_dashboard.py`는 `render_overview_dashboard`만 re-export한다. `app/services/overview_market_intelligence.py`는 삭제했고 internal imports는 `app/services/overview/*` domain modules로 이동했다. `data_health.py`는 unused import를 제거하고 direct Market Context vs reference context `Scope` / coverage counts를 제공한다.
- 이번 차수에서 하지 않은 일: Overview 화면 레이아웃 / UX 재설계, 새 provider / DB schema / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed Overview task: `.aiworkspace/note/finance/tasks/active/overview-service-split-v25-v32-20260629/`
- 목적: Overview read-model service monolith를 domain-owned service modules로 나눠 향후 tab / 기능 추가 시 계산 위치를 명확히 한다.
- 주요 변경: Sentiment, Events, Data Health, Market Movers, Market Context, Why It Moved 구현 본문을 `app/services/overview/*`로 분리했다. Market Context는 split domain services를 조립하고, old aggregate path는 final cleanup 전까지 compatibility facade로 축소했다.
- 이번 차수에서 하지 않은 일: Overview 화면 레이아웃 / UX 재설계, 새 provider / DB schema / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed Overview task: `.aiworkspace/note/finance/tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/`
- 목적: `Workspace > Overview`의 남은 `legacy_dashboard.py` dependency를 helper cluster 단위로 제거하고, active page / tab / helper ownership을 명시적 모듈 구조로 닫는다.
- 주요 변경: Market Context / Events / Sentiment / Market Movers / Futures Macro helper ownership을 `app/web/overview/*_helpers.py`로 옮기고, `app/web/overview/legacy_dashboard.py`를 삭제했다. `app/web/overview_dashboard.py`는 필요한 compatibility export만 명시적으로 제공한다.
- 이번 차수에서 하지 않은 일: Overview product flow 재설계, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed structure task: `.aiworkspace/note/finance/tasks/active/overview-tab-helper-extraction-v11-v16-20260625/`
- 목적: Overview primary tab entrypoint가 직접 legacy helper를 호출하지 않도록, Market Context / Events / Futures Macro / Market Movers / Sentiment 각각의 tab-local helper bridge를 만든다.
- 주요 변경: `app/web/overview/{market_context,events,futures_macro,market_movers,sentiment}_helpers.py`를 추가하고 active tab entry modules가 semantic helper functions를 호출하게 했다.
- 이번 차수에서 하지 않은 일: low-level helper body 전체 물리 이동, `legacy_dashboard.py` 삭제, provider / schema / registry / saved JSONL 변경, validation / monitoring / trading semantics 추가.
- Recent completed task: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-refresh-state-v1-20260624/`
- 목적: `Workspace > Overview > Futures Macro` 탭이 저장된 선물 일봉 최신일을 stale하게 보여주지 않도록 DB 최신 marker와 화면 snapshot cache 경계를 정리한다.
- 주요 변경: `load_overview_futures_macro_snapshot` cache key에 latest stored 1D futures candle marker를 포함했다. `Futures Macro` 탭 상단에는 `일봉 매크로 갱신`과 `최신 데이터 다시 읽기` controls를 추가해 daily collection과 cache reload를 탭 안에서 직접 실행할 수 있게 했다.
- 이번 차수에서 하지 않은 일: futures daily collector provider 교체, OS scheduler / automation cadence 변경, DB schema / registry / saved JSONL 변경, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-mixed-substates-v1-20260624/`
- 목적: `Workspace > Overview > Futures Macro`에서 자주 보이는 `혼재된 매크로 흐름`을 억지 directional signal로 바꾸지 않고, 현재 선물 일봉 점수만으로 어떤 혼재인지 더 읽히게 한다.
- 주요 변경: `generate_market_interpretation`은 기존 directional scenario rule이 모두 빗나간 fallback에서만 mixed subtype을 계산한다. 상위 scenario는 `혼재된 매크로 흐름`으로 유지해 historical validation compatibility를 보존하고, summary에는 `sub_scenario`, `regime_hint`, `mixed_reason`을 추가한다. Overview brief hero는 하위 맥락을 보조 라벨로 보여준다.
- 이번 차수에서 하지 않은 일: FRED `T10Y3M` / `VIXCLS` / `BAA10Y`, real yield, breakeven inflation 같은 macro source score 추가, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-tab-split-v1-20260624/`
- 목적: `Workspace > Overview`의 기본 진입 화면인 `Market Context`에서 무거운 futures macro historical validation을 분리하고, 별도 `Futures Macro` primary tab에서 선물 매크로 진단을 관리한다.
- 주요 변경: Overview primary tabs는 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events` 순서다. `Market Context` helper는 기본 `include_futures_macro=False`, `include_historical_analog=False`로 cockpit을 만들며 movement / breadth / sentiment / events / data 중심의 light brief만 즉시 로드한다. `Market Context` renderer에서는 historical analog controls / reading flow / repair action을 제외했다. `Futures Macro` tab은 저장된 선물 일봉 snapshot과 historical validation이 필요한 상세 진단을 소유한다. `nyse_price_history` 최신 raw date 조회는 `MAX(date)` 대신 `ORDER BY date DESC LIMIT 1` read path로 바꿨다.
- 이번 차수에서 하지 않은 일: futures validation 결과 DB 저장 테이블 추가, provider / schema / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-load-gate-removal-v1-20260624/`
- 목적: `Workspace > Overview > Market Context`의 `시장 맥락 불러오기` gate를 제거하고, 전처럼 기본 시장 맥락 본문이 즉시 렌더링되게 되돌린다.
- 주요 변경: explicit load button / loaded-tab session state / lazy body gate를 제거했다. Internal `st.pills` text-tab underline selector와 no-anchor switching은 유지한다. Cold timing 기준 느린 구간은 `load_overview_macro_context_cockpit`의 snapshot fan-out, 특히 futures macro validation으로 확인했다.
- 이번 차수에서 하지 않은 일: futures macro validation 최적화, loader 구조 분리, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-nav-internal-lazy-load-v1-20260623/`
- 목적: `Workspace > Overview` primary tab 전환을 anchor/link navigation이 아니라 같은 브라우저 안의 내부 탭 전환으로 고치고, 첫 진입 때 무거운 `Market Context` 본문 로드를 늦춘다.
- 주요 변경: primary selector는 `st.pills` 내부 widget을 사용하되, user-provided reference처럼 plain text tabs + active red underline으로 보이게 scoped CSS를 적용한다. Query-param slug는 직접 진입 호환 입력으로만 읽고 `<a href>` navigation은 렌더링하지 않는다. 이 작업의 explicit load gate는 `overview-market-context-load-gate-removal-v1-20260624`에서 제거됐다.
- 이번 차수에서 하지 않은 일: Market Context 내부 old source label 흡수, futures / sector service 또는 renderer helper 물리 삭제, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-primary-nav-pill-v1-20260623/`
- 목적: `Workspace > Overview`의 네 개 primary tab을 기본 Streamlit segmented/radio 위젯 느낌이 아니라 제품형 compact navigation으로 보이게 했다.
- 주요 변경: primary selector를 Korean-first compact pill nav로 바꾸고, English secondary label과 `?overview_tab=market-movers` 같은 query-param slug selection을 추가했다. 이 anchor 기반 visual polish는 이후 `overview-nav-internal-lazy-load-v1-20260623`에서 내부 widget selector로 대체됐다.
- 이번 차수에서 하지 않은 일: Market Context 내부 old source label 흡수, futures / sector service 또는 renderer helper 물리 삭제, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Earlier completed task: `.aiworkspace/note/finance/tasks/active/overview-primary-tab-soft-remove-v1-20260623/`
- 목적: `Workspace > Overview`에서 사용 가치가 선명하지 않은 `Futures Monitor`와 `Sector / Industry` standalone tab을 primary navigation에서 제거하고, Overview를 더 작고 확실한 market context entry로 좁혔다.
- 주요 변경: 당시 primary selector / lazy dispatch는 `Market Context`, `Market Movers`, `Sentiment`, `Events`만 노출하고 기존 session 또는 deep-link 값이 `Futures Monitor` / `Sector / Industry`를 가리키면 `Market Context`로 fallback했다. 이후 `Futures Macro`가 current primary tab으로 분리되었고, `Futures Monitor` / `Sector / Industry` standalone tab은 여전히 current primary surface가 아니다.
- 이번 차수에서 하지 않은 일: futures / sector service 또는 renderer helper 물리 삭제, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Earlier completed task: `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-v1_1-20260623/`
- 목적: `Workspace > Overview > Futures Monitor`의 Workbench V1 후속으로, prototype-like lower evidence / validation / refresh 영역을 제품형 read-only market context 흐름으로 정리했다.
- 주요 변경: context bar는 상태만 요약하고, `자료 갱신` module이 1분봉 / 일봉 매크로 / 화면 reload / 확인 방식을 소유한다. 이후 Futures Macro React 후속에서는 React `현재 근거`와 하단 `원본 데이터 / 계산 추적`으로 역할을 분리했고, 원본표는 `매크로 컨텍스트`, `최근 흐름`, `과거 점검`을 검산하는 `현재 점수 -> 구성 기여 -> 선물 일봉 변화 -> 과거 표본` 순서로 읽는다.
- 이번 차수에서 하지 않은 일: provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-v1_1-20260623/`
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-layout-v1-20260623/`
- 목적: `Workspace > Overview > Futures Monitor`를 form/card 느낌에서 compact workbench 기본 화면으로 재구성했다.
- 주요 변경: Workbench context bar, compact watch strip, market brief hero, weekly flow lane, chart workspace question을 도입하고 symbol edit / refresh setting / raw evidence / provider diagnostics를 낮췄다.
- 이번 차수에서 하지 않은 일: provider/schema/registry/saved write, live trading/order/recommendation/monitoring signal semantics.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-refresh-ux-v21-20260622/`
- 목적: `Workspace > Overview > Market Context`의 V19 Macro meaning / gradient 보정으로, 핵심 자산 비교와 Macro 조건 결과 비교 matrix의 양수 / 음수 색상 구분을 더 분명히 하고, 조건에는 쓰지 않은 Macro 배경 값이 어떤 상태를 뜻하는지 바로 읽히게 했다.
- 주요 변경: Historical analog / Macro conditioned comparison matrix cells는 median return 또는 delta 방향과 크기를 green / red gradient로 표시한다. Reference-only Macro backdrop cards는 T10Y3M / VIXCLS / BAA10Y 현재 값 옆에 `양의 금리곡선`, `변동성 주의`, `신용위험 안정권` 같은 상태와 해당 값의 의미 문장을 보여준다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-intersection-v18-20260622/`
- 목적: `Workspace > Overview > Market Context`의 V18 Macro intersection 보정으로, Macro 조건 표본이 GLD 조건을 먼저 적용한 뒤 금리선물을 적용하는 순서 의존 결과처럼 보이는 문제를 정리했다.
- 주요 변경: Macro conditioned analog 모델은 broad count, GLD 같은 상태 count, 금리선물 같은 상태 count, futures 계산 가능 count, 두 조건 교집합 count를 별도로 제공한다. Macro basis bar는 `기본 유사 맥락 기준` / `GLD 같은 상태` / `금리선물 같은 상태` / `두 조건 모두`로 표시하고, 최종 조건 후 결과는 두 조건 모두 현재와 같았던 교집합 표본으로 계산한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-polish-v17-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V17 Macro polish 보정으로, Macro 조건 축소 bar의 `37회`, `6회`가 정확히 어떤 GLD / 금리선물 상태를 뜻하는지 바로 읽히지 않고 `현재 Macro 배경 참고`가 긴 텍스트 덩어리처럼 보이는 문제를 정리했다.
- 주요 변경: Macro basis bar는 `XLY가 SPY 대비 5D 기준 비슷하게 강했던 구간` -> `GLD가 현재처럼 중립권이었던 과거 구간` -> `ZN=F/ZB=F가 현재처럼 금리 압력이 엇갈렸던 구간`처럼 각 단계의 조건 뜻을 먼저 보여준다. `조건에는 쓰지 않은 Macro 배경`은 T10Y3M / VIXCLS / BAA10Y를 한글 상태 badge, 현재 값, broad 표본 내 같은 상태 비율 bar, compact source 설명 순서로 보여준다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-matrix-v16-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V16 Macro matrix 보정으로, V15 Macro 조건 비교가 여전히 wide table / verbose source text 중심의 prototype-like UI로 보이는 문제를 정리했다.
- 주요 변경: Macro sample flow는 historical analog와 같은 basis bar로 표시하고, 결과 변화는 자산 x `기본 / 조건 후 / 변화` matrix로 렌더링한다. 긴 조건 source 원문은 접힌 상세로 낮추고, 현재 Macro 배경은 `금리곡선` / `변동성` / `신용스프레드` 한글 라벨을 우선 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-labels-v15-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V15 Macro labels 보정으로, `Macro 조건 후 결과 변화`에서 `37회`, `6회`, `같은 상태`가 무엇을 뜻하는지 기본 사용자가 바로 이해하기 어려운 문제를 정리했다.
- 주요 변경: Macro sample flow를 `기본 유사 맥락` -> `GLD 조건 적용` -> `금리선물 조건 적용` 단계로 명명하고, 각 단계가 broad anchor pool에서 어떤 표본을 남겼는지 문장으로 설명한다. `현재 Macro 배경 참고`는 T10Y3M / VIXCLS / BAA10Y의 한글 지표 설명과 broad sample 중 같은 상태 횟수를 함께 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-clarity-v14-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V14 Macro clarity 보정으로, `Macro 조건 비교`가 기본 유사 맥락 조건과 Macro 추가 조건을 섞어 보여주고, `Macro 조건 포함 핵심 자산` 표가 더 나은 예측표처럼 오해될 수 있던 문제를 정리했다.
- 주요 변경: `Sector ETF vs SPY relative strength`는 broad sample을 만드는 기본 유사 맥락 기준으로 분리하고, GLD / Rate Pressure futures는 Macro 추가 조건으로 표시한다. Macro 섹션은 sample narrowing, broad vs conditioned 결과 변화, 현재 Macro 배경(T10Y3M / VIXCLS / BAA10Y), 접힌 상세 / 원본 통계 순서로 읽는다. Historical analog matrix는 median return 방향과 크기에 따라 색상 농도를 조절하고, sector pressure map 수익률은 소수점 둘째 자리까지 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-flow-alignment-v13-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V13 흐름 보정으로, 상단 섹터 압력 지도와 `참고: 과거 유사 맥락`이 서로 다른 섹터를 기준으로 보이고 섹터 지도 / analog / macro 비교가 여전히 prototype-like guide UI처럼 읽히는 문제를 정리했다.
- 주요 변경: latest historical analog는 상단 Market Context의 visible daily sector leadership snapshot을 재사용한다. Selected as-of는 선택일 daily sector snapshot을 쓰고, pattern window는 sector source가 아니라 similarity window만 바꾼다. Sector pressure map은 provider sector alias를 canonical 11개 섹터로 normalize하고 전체를 균일 tile로 표시한다. Historical analog는 `먼저 볼 점` / `주의할 점` / `시장 배경 요약` guide block을 기본 화면에서 제거하고, sector ETF / SPY / QQQ / TLT / GLD를 하나의 핵심 비교 matrix로 보여준다. Broad analog rows가 없으면 Macro 조건 비교는 숨겨 dashed prototype UI를 만들지 않는다. V14에서 Macro 조건 비교는 broad-vs-conditioned 결과 변화와 현재 Macro 배경 중심으로 다시 정리됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-usability-v12-20260621/`
- 목적: `Workspace > Overview > Market Context`의 historical analog V12 보정으로, 실제 계산 기준일이 선택일보다 오래된 경우에도 보강 경로가 없고 기준 / 조건 / 표본 / 자산 통계가 반복 table-first로 보이는 문제를 정리했다.
- 주요 변경: selected as-of common daily price basis mismatch를 limiting symbols 대상 bounded OHLCV refresh action으로 연결했다. 기준 영역은 compact basis summary와 접힌 계산 경계 상세로 줄였고, 핵심 자산은 5D / 20D / 60D matrix로 먼저 읽으며 보조 자산은 시장 배경 요약, 원본 표는 `상세 통계` disclosure로 낮췄다. V13에서 latest historical analog 기준 섹터는 상단 visible sector leadership snapshot과 정렬되고, 시장 배경 요약은 sector ETF / SPY / QQQ / TLT / GLD 핵심 matrix로 흡수됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-macro-ux-v11-20260621/`
- 목적: `Workspace > Overview > Market Context`의 historical analog / Macro 조건 비교 UX 보정으로, 과거 유사 맥락과 Macro 조건 포함 비교가 카드 안 카드 / prototype-like payload dump처럼 보이는 문제를 정리했다.
- 주요 변경: historical analog 기준 영역을 wide basis bar로 바꾸고, 설명을 `현재 기준` / `유사 사례 조건` / `표본 품질`로 나눴다. 결과 해석은 `먼저 볼 점` / `주의할 점`으로 분리했고, Macro 조건 포함 비교는 broad analog의 sibling section으로 분리해 funnel, broad-vs-conditioned lanes, 조건 역할 그룹, dimension audit을 보여준다. V12에서 historical analog broad 영역은 다시 compact basis summary와 matrix-first outcome으로 보정됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-basis-clarity-v10-20260620/`
- 목적: `Workspace > Overview > Market Context`의 historical analog 기준일 UX 보정으로, 선택 기준일과 실제 계산 기준일이 다를 때 날짜가 무시된 것처럼 보이는 문제를 정리했다.
- 주요 변경: historical analog service model에 requested / effective as-of alignment, limiting symbols, basis warning을 추가했다. UI는 `요청 기준일`과 `실제 계산 기준일`을 나눠 보여주고, Macro 조건 포함 비교는 broad sample -> GLD 배경 -> 금리선물 압력 funnel로 읽게 했다. V11에서 이 표시 구조는 card stack에서 basis bar / separate Macro comparison section으로 재정리됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-session-basis-v9-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V8 후속으로, 미국장 휴장 / 주말 / 장외 시간에도 `오늘의 시장 브리프`처럼 보이고 장중 snapshot age 때문에 보강 이슈가 과하게 보이는 문제를 정리했다.
- 주요 변경: 기존 NYSE session helper를 Market Context cockpit에 전달해 `market_session` basis payload를 만들었다. 장중에는 `오늘의 시장 브리프`, 휴장에는 `마지막 거래일 시장 브리프`, 장 시작 전 / 장 종료 후에는 현재 세션 기준 브리프로 표시한다. 휴장 중에는 마지막 trading session date를 기준일로 고정하고, stale / due intraday elapsed age만으로 `현재 이슈만 보강` action을 만들지 않는다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-actionability-v8-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V7 후속으로, `현재 이슈만 보강`에서 제외되는 Events와 관리 메타인 Data Health가 계속 `자료 확인 필요`처럼 남아 사용자를 헷갈리게 하는 문제를 정리했다.
- 주요 변경: source confidence에 `source_role` / `actionability` / `counts_for_status`를 추가해 direct brief source, reference context, management meta를 분리했다. Top `자료 상태`, source confidence summary, source ledger는 보강 가능한 자료만 unresolved로 세며, Events estimate caveat는 `참고 제한`, Data Health는 `관리 메타`로 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-smart-refresh-v7-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V6 후속으로, Events caveat가 상단 시장 브리프 결론처럼 보이고 `필요 자료 일괄 보강`이 현재 이슈와 무관한 전체 job 실행처럼 보인다는 사용자 피드백을 정리했다.
- 주요 변경: `brief_rows`는 움직임, 확산, Futures/Macro 배경 3행으로 고정하고 Events는 event timeline / source evidence / `refresh_plan.excluded_items`로 낮췄다. 새 `refresh_plan`은 보강 가능 / 일부 보강 / 보강 제외를 분리하며, 기본 버튼은 `현재 이슈만 보강`으로 현재 action ids만 실행한다. 기존 전체 7개 job 실행은 `전체 Market Context 자료 보강` fallback으로 유지하고, refresh 결과는 raw job rows 전에 브리프 반영 요약을 먼저 보여준다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-context-absorption-v6-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V5 `브리프 신뢰도`가 여전히 가이드/주의사항처럼 보이고 시장맥락 자체의 필요 정보로 읽히지 않는다는 사용자 피드백에 따라, 별도 신뢰도 섹션을 제거하고 의미 있는 부분만 시장 브리프 결론으로 흡수했다. V7에서 Events caveat는 상단 brief conclusion에서 다시 내려갔다.
- 주요 변경: `brief_caveats` / `브리프 신뢰도`를 제거했다. V6의 optional `이벤트 배경`은 V7부터 default brief row가 아니며, Futures / OHLCV data-health 항목이 있을 때만 `Futures/Macro 배경`을 `장중 macro 해석 보류`로 낮춘다. 상세 source / freshness는 하단 `근거: 자료 기준 / 출처 상태`가 소유한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-confidence-v5-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V4 보정 후 Events / 자료 신뢰도 caveat가 `오늘의 시장 브리프` 결론처럼 보인다는 사용자 피드백에 따라, 시장 브리프와 브리프 읽기 강도 근거를 분리했다. V6에서 이 별도 섹션은 제거되고 필요한 정보만 브리프 결론에 흡수됐다.
- 주요 변경: V5에서는 `brief_rows`를 움직임, 확산, Futures/Macro 배경의 3행 market story로 유지하고, Events / 자료 기준을 별도 `brief_caveats` / `브리프 신뢰도` 영역에서 보여줬다. V6부터 `brief_caveats`는 제거됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-findings-integration-v4-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V3 `맥락 검토 결과`가 가격 움직임 / Futures-Macro를 상단 브리프와 중복해서 보여준다는 사용자 피드백에 따라, 중복 findings rail을 없애고 Events / 자료 신뢰도 caveat만 `오늘의 시장 브리프` 안으로 통합했다. V5에서 이 caveat는 `브리프 신뢰도`로 다시 분리됐다.
- 주요 변경: V4에서는 `brief_rows`가 움직임, 확산, Futures/Macro 배경, 이벤트 caveat, 자료 신뢰도 caveat의 5행 흐름이 됐다. V5부터 `brief_rows`는 3행 market story, `brief_caveats`는 별도 confidence row로 읽는다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-context-findings-v3-20260620/`
- 목적: `Workspace > Overview > Market Context`의 `다음 맥락 체크`가 여전히 사용자가 직접 다른 탭을 확인하라는 checklist처럼 보인다는 사용자 피드백에 따라, Market Context가 이미 읽은 보조 맥락의 결론을 보여주도록 바꿨다.
- 주요 변경: user-facing `다음 맥락 체크`를 `맥락 검토 결과`로 전환하고, 가격 움직임 / Futures-Macro / Events / 자료 신뢰도 caveat를 `결론`, `해석 영향`, `자료 기준` 행으로 표시한다. V4에서 이 rail은 기본 화면에서 제거되고 Events / 자료 신뢰도 caveat만 브리프에 흡수됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-flow-redesign-v2-20260620/`
- 목적: `Workspace > Overview > Market Context` V1 UX 보정이 여전히 카드 재배치처럼 보인다는 사용자 피드백에 따라, Market Context를 wide brief lane / next-check rail / transparent reading sections로 다시 정리했다.
- 주요 변경: `시장 브리프` rows를 cockpit 안의 `오늘의 시장 브리프`로 흡수하고, `다음 맥락 체크`를 card grid 대신 priority / observation / reason / action rail로 표시하며, `Macro 조건 포함 pilot`은 UI상 `Macro 조건 포함 비교`로 broad vs conditioned sample 차이를 먼저 읽게 했다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-futures-conditioned-analog-v3b-20260618/`
- 목적: `Workspace > Overview > Market Context`의 3차-B historical analog 개선으로 3차-A `Macro 조건 포함 pilot`에 stored futures daily OHLCV 기반 Rate Pressure proxy 조건 1개를 추가했다.
- 실제 사용 조건: 필수 sector ETF vs SPY relative strength, GLD price proxy safe-haven / gold context, `ZN=F` / `ZB=F` Rate Pressure futures proxy.
- 이번 차수에서 하지 않은 일: FRED 2Y/10Y 수집 또는 조건화, events / sentiment historical conditioning, 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, full PIT sector universe storage, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- sample quality: 20D Browser QA 기준 broad sample 69회 중 GLD + futures 조건 포함 sample 1회로 줄어 `REVIEW` 상태였다. UI는 broad sample, Macro 조건 sample, sample quality, sample reduction reason, used / insufficient / excluded conditions를 함께 표시한다.
- Recent completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-conditioned-analog-pilot-v1-20260618/`
- 목적: `Workspace > Overview > Market Context`의 3차-A historical analog 개선으로 기존 broad analog와 별도인 `Macro 조건 포함 pilot` 영역과 GLD price proxy condition을 추가했다.
- Recent completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-asof-window-v2-20260618/`
- 목적: `Workspace > Overview > Market Context`의 2차 historical analog 개선으로 `참고: 과거 유사 맥락`에 latest / 과거 기준 시점 replay와 5D / 20D / monthly pattern window controls를 추가했다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, macro-conditioned analog, full PIT sector universe storage, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- as-of replay 판정: 기존 DB만으로는 current universe / sector metadata와 selected-as-of DB prices 기반 bounded replay가 가능하다. 과거 당시 universe / sector classification / market-cap snapshot을 보장하는 full PIT replay는 후속 storage/read path 승인이 필요하다.
- Recent completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-action-flow-v1-20260618/`
- 목적: `Workspace > Overview > Market Context`의 1차 source-action flow 개선으로 `다음 맥락 체크`를 실제 `next_checks` checklist로 렌더링하고, Data Health / Events source action, source confidence footer, historical analog 기준 시점 / 계산식 표시를 명확히 했다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema, UI render 중 external fetch, macro-conditioned analog 계산, historical analog replay 저장소, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- 2차 / 3차 후속: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-action-flow-v1-20260618/DESIGN.md`에 historical analog 기준 시점 / 기간 확장 설계와 macro-conditioned analog pilot 설계 메모를 남겼다.
- Recent previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-movers-coverage-refresh-v1-20260617/`
- 목적: `Workspace > Overview > Market Movers`에 Nasdaq-listed current snapshot coverage를 추가하고, Nasdaq Symbol Directory / intraday 반복 갱신 경로와 Coverage Diagnostics evidence를 보강했다.
- 이번 차수에서 하지 않은 일: Nasdaq Composite / Nasdaq-100 표현, trade signal / 추천, 새 provider / DB schema, registry / saved JSONL write, OS scheduler 등록, 대량 provider collection 실행.
- Recent previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-movers-period-refresh-v1-20260616/`
- 목적: `Workspace > Overview > Market Movers`에서 Weekly / Monthly / Yearly period도 EOD 가격 이력 기준과 `가격 이력 갱신` 수동 action을 같은 화면에서 확인하게 했다.
- 이번 차수에서 하지 않은 일: Daily 자동 갱신 복제, Market Context / Futures / Events / Backtest / Operations / historical analog 변경, 새 provider, DB schema, registry / saved JSONL write, 대량 provider collection 실행.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-readability-v5-20260616/`
- 목적: `Workspace > Overview > Market Context`에서 `참고: 과거 유사 맥락`이 표부터 보이는 구조를 정의 문장, 핵심 요약 strip, `먼저 읽을 결론`, 핵심 / 보조 자산 table 흐름으로 재구성해 사용자가 과거 유사맥락의 기준과 해석을 먼저 읽게 했다.
- 이번 차수에서 하지 않은 일: historical analog 계산식 변경, macro / futures / event / sentiment conditioned analog expansion, anchor date drill-down, 새 provider, DB schema, loader, CSV upload, registry / saved JSONL write, Overview render 중 external fetch, 예측 / 추천 / trading signal, validation / monitoring gate.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-repair-v4-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 `참고: 과거 유사 맥락`의 `자료 부족` 상태를 부족 ticker / row 기준 / `보조 갱신` repair action으로 연결하고, `근거: 자료 기준 / 출처 상태`는 접힌 summary에서도 정상 / 확인 / 부족 count와 핵심 source를 읽게 했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, loader, CSV upload, registry / saved JSONL write, Overview render 중 external fetch, 예측 / 추천 / trading signal, validation / monitoring gate, macro / futures / event conditioned analog expansion.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-supporting-flow-v3-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 하단 보조 흐름을 `다음 맥락 체크`, `참고: 과거 유사 맥락`, `근거: 자료 기준 / 출처 상태`로 재정의하고 Data Health를 main cue row에서 evidence context로 낮췄다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-copy-density-v2-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 `오늘의 시장 맥락`을 `현재 맥락:` 한 줄 요약 대신 2~3문장형 brief로 풀고, reading-flow 단락의 typography / color density를 조정했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-section-flow-v1-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 상단 cockpit은 headline / tape / 섹터 압력 지도 / 이벤트 타임라인만 담고, `시장 브리프`, `해석할 때 같이 볼 변수`, `과거 유사 맥락 참고`, `자료 기준 / 출처 상태`를 별도 reading-flow section으로 분리했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-hybrid-visual-v1-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 card-first 구조를 줄이고, 5칸 시장 테이프 / 섹터 압력 지도 / 이벤트 타임라인 / 근거 row 흐름으로 현재 맥락을 더 시각적으로 읽게 한다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, full dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-historical-analog-v1-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 current sector leadership을 sector ETF proxy로 연결하고, coverage가 충분한 경우에만 과거 유사 맥락 이후 5D / 20D / 60D 주요 자산 흐름을 context-only로 보여준다.
- 이번 차수에서 하지 않은 일: 예측 모델, 투자 추천 / 매수·매도 신호, Backtest strategy 연결, Practical Validation / Final Review / Operations gate 연결, DB schema, 새 provider, registry / saved JSONL write, full historical PIT sector universe reconstruction.
- Current local coverage note: live leadership sector changes with the latest stored market snapshot. If its sector ETF proxy has insufficient local daily price rows, Market Context now shows the missing ticker and an explicit `보조 갱신` OHLCV repair action instead of a generic `자료 부족` dead end.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-events-data-trust-v1-20260612/`
- 목적: `Workspace > Overview > Market Context / Events`에서 FOMC / CPI / PPI / Employment / GDP 같은 주요 macro event를 recent + upcoming 관점으로 읽고, Market Context에서는 compact event cue와 자료 주의점만 보여준다.
- 이번 차수에서 하지 않은 일: 과거 유사국면 / 향후 예측 기능, 새 provider, DB schema, registry / saved JSONL write, Backtest / Practical Validation / Final Review / Operations 변경, Data Health 진단 패널 전면화.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-ia-closeout-v1-20260608/`
- 목적: `Workspace > Overview` cockpit 아래에 `Overview Map / Deep Tab Reading Order`를 추가해 market context, data repair, transitional Candidate Ops 경계를 명확히 닫았다.
- 이번 차수에서 하지 않은 일: Candidate Ops 제거 / 이동, Backtest workflow 변경, 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-source-confidence-catalog-v1-20260608/`
- 목적: `Workspace > Overview` cockpit 하단에 기존 DB-backed snapshots의 source, owner, freshness, caveat, next check를 보여주는 read-only Source Confidence lane을 추가했다.
- 이번 차수에서 하지 않은 일: 새 provider, provider 교체, DB schema, registry / saved JSONL write, Overview render 중 external fetch, Reference companion 본격 연결, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-breadth-macro-week-v1-20260608/`
- 목적: `Workspace > Overview > Sector / Industry`와 `Events` 상단에 breadth / concentration, latest heatmap, 14일 macro week lane을 추가했다.
- 이번 차수에서 하지 않은 일: full breadth heatmap, Events Quality workflow 본격 구현, 새 provider, schema, persistence, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-data-health-ingestion-handoff-v1-20260608/`
- 목적: `Workspace > Overview > Data Health` 상단에 stale / missing / failed / partial / due targets를 우선순위화하고 owning collection surface로 넘기는 read-only handoff lane을 추가했다.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-macro-context-cockpit-v1-20260608/`
- 목적: `Workspace > Overview` 상단에 기존 DB-backed movers / breadth / futures / sentiment / events / data-health snapshot을 합성한 summary-first market context cockpit을 추가했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, Data Health -> Ingestion Action Queue, heatmap / macro week view, Candidate Ops IA 변경, live approval / broker order / auto rebalance.
- Recent completed Reference merge-review task: `.aiworkspace/note/finance/tasks/active/merge-review-fixes-20260608/`
- 목적: sub-dev / main-dev master merge review에서 확인된 Reference contextual help internal link, Reference V4 task status, Reference Guides catalog test assertion 문제를 바로잡았다.
- 이번 차수에서 하지 않은 일: Reference 전체 UX 재설계, URL query deep-linking, Ingestion / Overview 전체 surface 연결, DB / registry / saved JSONL rewrite, provider fetch, live approval / broker order / auto rebalance.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/reference-drift-guard-qa-polish-v5-20260608/`
- 목적: Reference contextual help가 shared Glossary concept dictionary와 Reference route boundary에서 drift되지 않도록 Streamlit-free guard를 추가하고, guide path copy 표시를 정리한다.
- Recent previous sub-dev task: `.aiworkspace/note/finance/tasks/active/operations-v2-closeout-20260608/`
- 목적: Operations Overview V2 5차로 1차~4차 개편을 최종 QA / runbook / durable docs 기준으로 닫고, 정상 top-navigation QA path와 direct `/operations` local routing diagnostic을 분리한다.

Recent Backtest strategy contract work retained from `backtest-dev`:

- `risk-parity-dual-momentum-5b-20260610`: Backtest 5B로 Risk Parity Trend와 Dual Momentum의 strategy runtime / result bundle 계약을 고도화했다. Risk Parity는 volatility window / eligible universe / inverse-vol weight / cash-only state / guardrail effect / low-vol overweight를, Dual Momentum은 top-N concentration / trend rejected ticker / selected count / cash proxy retention / turnover-whipsaw 해석을 result row/meta와 기존 Selection History에서 확인할 수 있게 됐다. 새 Backtest Analysis evidence / log / workbench panel, registry / saved JSONL / run history / generated artifact write, provider / FRED direct fetch, Practical Validation / Final Review / Monitoring behavior, live trading / broker order / auto rebalance는 열지 않았다.
- `global-relative-strength-5a-20260609`: Backtest 5A로 Global Relative Strength의 strategy runtime / result bundle 계약을 고도화했다. GRS는 strategy가 rebalance interval을 직접 소유하고, cash proxy / benchmark contract / excluded ticker / stale price / top-N concentration / momentum score window 정보를 result bundle meta와 기존 Selection History에서 해석할 수 있게 됐다. 새 evidence/log/workbench panel과 durable writes는 열지 않았다.
- `backtest-analysis-direction-reset-20260609`: Backtest 4차 4C로 3A~4B evidence / governance / workbench 패널을 기본 화면에서 내리고, Backtest Analysis를 전략 실행 / 비교 / 후보 생성 중심으로 되돌렸다. 2026-06-30 cleanup 이후 해당 보조 패널은 기본 Backtest Analysis render path에서 제외된 historical / auxiliary surface로 남는다.
- `etf-rerun-matrix-workbench-20260608`, `etf-current-anchor-workbench-20260608`, `etf-evidence-expansion-20260608`, `risk-on-momentum-governance-20260608`, `strict-annual-etf-bridge-20260608`, `strategy-evidence-inventory-direction-panel-20260608`: Backtest 3A~4B read-only strategy evidence / bridge / governance / ETF readiness / rerun matrix workbench records. 이 흐름은 current candidate promotion, Practical Validation result creation, provider snapshot collection, live trading / broker order / auto rebalance를 열지 않는 retained work record다.

## Product Tracks

| Track | Current State | Main Surfaces | Boundary |
|---|---|---|---|
| Data Collection / Data Trust | DB-backed ingestion baseline complete | `Workspace > Ingestion`, MySQL, loaders | UI에서 provider / FRED / external source를 직접 fetch하지 않는다. Overview bounded refresh는 `app/jobs/overview_actions.py` facade만 통과한다 |
| Overview / Market Context | Production baseline plus recent sentiment / Why It Moved work complete | `Workspace > Overview` | Market context and investigation only; bounded refresh action allowed through facade; no trade signal, approval, order, registry rewrite |
| Backtest Analysis | Candidate creation plus compact Korean-first stage navigation cleanup complete | `Backtest > Backtest Analysis` | 후보 source 생성 단계; final decision / monitoring governance는 후속 단계 |
| Practical Validation / Final Review | Investability evidence workflow complete through P2 / P3 and first hardening cycle | `Backtest > Practical Validation`, `Backtest > Final Review` | PASS / BLOCKER / selected-route gate는 validation evidence가 소유; sentiment overlay is context-only |
| Operations / Portfolio Monitoring | Operations Console now opens with portfolio-first status summary, evidence health strip, and priority/evidence ordered review queue, while Portfolio Monitoring remains daily-monitoring-first | `Operations > Operations Console`, `Operations > Portfolio Monitoring`, `System / Data Health` | Read-only monitoring and explicit scenario update; no live approval, broker order, account sync, auto rebalance |
| UI / Engine Boundary | Service/runtime boundary and lint baseline complete | `app/services`, `app/runtime`, `app/web` | UI handles render/session state; runtime / service owns engine dispatch, JSONL helpers, read models |

## Recently Merged Work

| Workstream | Status | Durable Notes |
|---|---|---|
| Overview Legacy Dashboard Removal V17-V24 | Complete | `app/web/overview/legacy_dashboard.py` was physically removed after remaining helper ownership moved into tab-local helper modules. `app/web/overview_dashboard.py` now keeps explicit compatibility exports only, while active page / tab / helper ownership lives under `app/web/overview/`. |
| Overview Tab Helper Extraction V11-V16 | Complete | Market Context, Events, Futures Macro, Market Movers, and Sentiment primary tab entry modules now call tab-local helper bridges instead of importing `legacy_dashboard.py` directly. |
| Overview Legacy Cleanup V6-V10 | Complete | Overview navigation moved to `app/web/overview/navigation.py`, IA read-model ownership moved to `app/services/overview/ia.py`, confirmed unused standalone wrappers / Candidate Ops helpers were removed, and guard tests prevent reintroduction. |
| Overview Structure Split V2-V5 | Complete | Overview primary tab modules own tab-level orchestration, `app/web/overview/components/` component surfaces and `app/services/overview/` service surfaces were introduced, and boundary guard contracts protect active page / tab / component / service ownership. |
| Overview Tab Module Split V1 | Complete | `app/web/overview_dashboard.py` became a compatibility wrapper, active Overview shell moved to `app/web/overview/page.py`, and primary tab entry modules were added for Market Context, Market Movers, Futures Macro, Sentiment, and Events. |
| Overview Market Context Load Gate Removal V1 | Complete | Current Overview keeps the internal text-tab underline selector but removes the explicit `시장 맥락 불러오기` gate. Market Context renders immediately when selected. Cold timing shows the slow path is the cockpit snapshot fan-out, especially futures macro validation. |
| Overview Nav Internal Lazy Load V1 | Superseded | This replaced anchor navigation with internal `st.pills` text tabs and added a first-load Market Context gate. The internal no-anchor navigation remains, but the explicit load gate was removed by Overview Market Context Load Gate Removal V1. |
| Overview Primary Nav Pill V1 | Superseded | This first visual polish rendered a compact custom anchor nav with Korean primary labels, English secondary labels, and query-param tab slugs. It was replaced by Overview Nav Internal Lazy Load V1 because tab switching must stay inside the current browser session rather than behave as link navigation. |
| Overview Primary Tab Soft Remove V1 | Complete | Futures Monitor and Sector / Industry standalone tabs are soft-removed from primary navigation, with stale selected values falling back to Market Context. Current Overview primary tabs later settled as Market Context, Market Movers, Futures Macro, Sentiment, and Events. Futures / sector services and helper renderers are retained as context data paths or repurpose candidates. |
| Overview IA Cleanup V22 | Complete | Superseded by Overview Primary Tab Soft Remove V1 for current primary tab membership. V22 demoted Data Health to Market Context source / refresh evidence plus Operations / Ingestion ownership and removed Candidate Ops from the Overview render path, while still retaining Futures Monitor and Sector / Industry at that time. Registry / saved data and Backtest / Operations core workflows are unchanged. |
| Overview Market Context Source Refresh UX V21 | Complete | Market Context source evidence now reads as `자료 상태 요약 -> 시장 브리프 직접 자료 -> 참고 / 관리 자료 -> 보강 판단`, and no-action refresh states use a compact no-action panel plus secondary full refresh instead of a prototype-like disabled action. Refresh action ids and data boundaries are unchanged. |
| Overview Market Context Macro Meaning Gradient V19 | Complete | Historical analog and Macro conditioned comparison matrix cells now use clearer green/red gradients based on median return or delta direction and magnitude. Reference-only T10Y3M / VIXCLS / BAA10Y backdrop cards now pair the current numeric value with Korean state meaning such as positive yield curve, volatility watch, and contained credit spread, without changing hard conditioning or data boundaries. |
| Overview Market Context Macro Intersection V18 | Complete | Macro conditioned comparison now reports broad sample, GLD same-state sample, Rate Pressure futures same-state sample, futures-computable sample, and the final GLD ∩ futures intersection separately. The visible basis bar reads as `기본 / GLD 같은 상태 / 금리선물 같은 상태 / 두 조건 모두`, avoiding an order-dependent funnel interpretation. |
| Overview Market Context Macro Polish V17 | Complete | Macro conditioned comparison now shows the meaning of each narrowing step inside the basis bar: broad sector ETF vs SPY analog pool, current-like GLD bucket, then current-like ZN=F / ZB=F rate-pressure bucket. Reference-only T10Y3M / VIXCLS / BAA10Y backdrop now renders as Korean state badges, current value, same-state ratio bars, and compact source labels. |
| Overview Market Context Macro Matrix V16 | Complete | Macro conditioned comparison now uses the same visual language as historical analog: a basis bar for broad -> GLD -> futures narrowing, a compact asset x `기본 / 조건 후 / 변화` matrix, collapsed verbose condition source details, and Korean-first labels for current Macro backdrop. |
| Overview Market Context Macro Labels V15 | Complete | Macro conditioned comparison now names the visible narrowing stages as broad basis, GLD condition, and rate-pressure futures condition. It explains `81회 -> 37회 -> 6회` as broad anchors narrowed by current-like GLD and futures states, and current Macro backdrop cards include Korean descriptions plus broad-sample same-state counts. |
| Overview Sentiment React UX V1 | Complete | Sentiment now renders a React workbench when the component build is available: service-owned phase/headline/summary first, freshness-tied refresh/reload actions, CNN / AAII cross-read, recent range percentile / min-max cards, CNN headline / component / AAII divergence panel, analysis steps, driver lanes, CNN component explanations, component latest-vs-previous changes, hover-readable history line chart, component bar chart, and stored-row evidence tables. Python services still own DB reads, refresh actions, and all interpretation text; React does not create trade signals, validation gates, monitoring signals, or recommendations. |
| Overview Market Sentiment V1 | 1차~3차 complete | CNN Fear & Greed / AAII collect into `finance_meta.macro_series_observation`. Overview Sentiment, Practical Validation, Final Review, and Portfolio Monitoring read it as context-only market backdrop. |
| Operations Overview IA / Operations Console V2-V5 | V2 closeout complete | Operations now has a console entry, Portfolio Monitoring and System / Data Health as the only top-level Operations tabs, and disabled live trading boundary copy. Operations Overview no longer exposes archive / development-history decision tables in the operator path and now starts with Portfolio Monitoring Status plus Evidence Health before a priority/evidence ordered review queue. Closeout QA and routing diagnostic are documented in `docs/runbooks/OPERATIONS_OVERVIEW_QA.md`; Backtest Runs / Candidate Library data deletion is deferred. |
| Risk Parity / Dual Momentum 5B | Complete | Risk Parity Trend now exposes volatility window, eligible universe, inverse-vol weights, cash-only reasons, guardrail cash-only state, and low-vol overweight diagnostics. Dual Momentum now retains trend-rejected top-N slots as cash proxy and exposes selected / rejected / unfilled counts, cash proxy return, concentration, and selection-change / whipsaw diagnostics. Both reuse existing Selection History and result bundle meta without adding a new panel. |
| Global Relative Strength 5A | Complete | GRS strategy cadence now lives in strategy runtime, not duplicated period-row slicing. Cash proxy, benchmark, excluded ticker, stale price, top-N concentration, rebalance interval, and momentum window metadata flow to the result bundle and Selection History without new evidence/log/workbench panels or durable writes. |
| Backtest Entry Cleanup Tabs V1 | Complete | Backtest entry removes the top guide expander, strategy capability helper expander, and bottom research reference board from the default render path. The 3-stage workflow selector now uses Korean-first `st.pills` text tabs with red active underline. |
| Backtest Analysis Direction Reset 4C | Complete | Backtest Analysis returned to execution-first strategy run / comparison / candidate creation. Reference help and 3A-4B evidence / governance / ETF workbench panels are now historical / auxiliary surfaces outside the default Backtest Analysis render path. |
| Risk-On Momentum 5D V1/V2 | Implementation / QA complete | Daily Swing research lane added under Backtest Analysis. V2 adds ATR exit, macro ranking penalty, comparison / sensitivity / stability / trade-cause / quality-warning analysis, S&P 500 universe option. Governance connection to Practical Validation / Final Review / Portfolio Monitoring is deferred. |
| Selected Dashboard Monitoring First UX V1 | Complete | Portfolio Monitoring opens with Active Portfolio Monitoring Scenario first, while portfolio setup and strategy board sit below. Scenario results stay explicit/session-based and do not auto-write monitoring logs. |
| Overview Market Movers Workbench V1-V5 | Complete | Market Movers now renders as a context-only workbench with command strip, Top Gainers / Top Losers / Volume Leaders / Unusual Volume / Sector Leaders modes, selected-symbol investigation, sector breadth/heatmap context, and coverage trust UX. Coverage trust uses Good / Stale / Partial / Needs Refresh / No Universe / Missing Quotes language, grouped missing diagnostics first, raw diagnostics collapsed, and existing Overview action facade refreshes only. |
| Overview Market Movers Second Pass / Why It Moved | Current V1 complete; period refresh V1 complete; Market Interest V2 complete | Return / Volume rank, previous-period context, manual investigation board, keyless Google News KR RSS metadata/snippet, compact SEC metadata table, and selected-symbol `시장 관심` evidence panel. Weekly / Monthly / Yearly expose a manual EOD price-history refresh action through the existing Overview action facade / OHLCV job boundary. Market Interest V2 fetches existing selected-symbol news / Korean news / SEC metadata into one `시장 관심` evidence panel, keeps analyst actions as structured-source-not-connected until API-key/terms approval, separates `기관 보유 배경 · 13F 지연 자료` from issuer SEC filings, and lowers source links to disclosure. It still adds no article body, filing body, analyst report body, AI summary, catalyst classifier, recommendation, score, DB schema, registry, saved setup write, or live trading semantics. |
| Overview Macro Context Cockpit V1 | Complete | Overview opens with a summary-first cockpit that synthesizes existing DB-backed movers, sector breadth, futures macro thermometer, CNN / AAII sentiment, event calendar, and data-health evidence. It remains context-only and adds no provider, schema, registry, saved setup, validation gate, monitoring signal, or trading action. |
| Overview Data Health Ingestion Handoff V1 | Superseded as primary Overview tab | The read model remains a historical / helper artifact, but V22 removes `Data Health` from Overview top-level navigation. Market Context source / refresh evidence and Operations / Ingestion now own the user-facing data-health path. |
| Overview Breadth / Macro Week V1 | Complete | This introduced breadth / concentration summary and latest heatmap for the then-active Sector / Industry surface, plus a 14-day Events macro week lane. Current UI reads sector breadth through Market Context / Market Movers instead of a standalone primary tab. It reuses existing DB-backed snapshots only and remains context-only, with no provider, schema, registry, saved setup, validation gate, monitoring signal, or trading action. |
| Overview Source Confidence Catalog V1 | Complete | The Overview cockpit now includes a compact Source Confidence lane for prices, breadth, futures, sentiment, events, and data health source state. It reuses the same snapshots already loaded by the cockpit, exposes owner / freshness / caveat / next check, and does not add provider fetch, schema, persistence, validation, monitoring, or trading semantics. |
| Overview IA Closeout V1 | Superseded by V22 | V1 made Market Context / Data Repair / transitional Candidate Ops boundaries visible. V22 completes the approved IA cleanup by removing Candidate Ops from Overview and demoting Data Health out of primary Overview tabs. |
| Overview Market Context Brief Flow Redesign V2 | Complete | Market Context now absorbs `시장 브리프` rows into the top `오늘의 시장 브리프` lane, renders `다음 맥락 체크` as a priority / observation / reason / action rail instead of a card grid, and shows `Macro 조건 포함 비교` as broad vs conditioned sample context. It remains DB-backed and context-only with no provider fetch, schema, registry / saved write, validation, monitoring, or trading semantics. |
| Overview Market Context Macro Clarity V14 | Complete | Macro conditioned comparison now separates the broad basis from additional Macro conditions, shows broad-vs-conditioned result deltas before raw tables, surfaces T10Y3M / VIXCLS / BAA10Y as current Macro backdrop rather than hidden preview labels, and keeps Events / sentiment deferred. Matrix cells use median-return strength coloring and sector pressure returns display two decimal places. |
| Overview Market Context Flow Alignment V13 | Complete | Latest historical analog now follows the same visible daily sector leadership snapshot as the top Market Context view, while selected as-of uses the selected daily sector basis. Sector pressure renders the canonical 11-sector map with equal tiles, and historical analog removes default guide blocks in favor of one sector ETF / SPY / QQQ / TLT / GLD core comparison matrix. Macro comparison stays compact and is hidden when broad analog rows are unavailable. |
| Overview Market Context Analog Usability V12 | Complete | Historical analog now connects stale selected-as-of common daily price basis to a bounded OHLCV refresh action for limiting ETF symbols. The broad analog section reads as compact basis summary, collapsed calculation details, method line, summary strip, core 5D / 20D / 60D outcome matrix, support asset summary, and collapsed detailed tables. It remains DB-backed and context-only. |
| Overview Market Context Analog / Macro UX V11 | Complete | Historical analog now renders as an analysis flow: controls directly precede the analog section, requested/effective basis values sit in a wide basis bar, the similarity method is split into `현재 기준` / `유사 사례 조건` / `표본 품질`, and Macro conditioned comparison is a separate sibling section with funnel, broad-vs-conditioned lanes, condition-role groups, and dimension audit. It remains DB-backed and context-only. |
| Overview Market Context Analog Basis Clarity V10 | Complete | Historical analog now separates requested basis date from actual calculation date when common DB daily price coverage is older. Selected dates such as 2026-06-18 show the effective 2026-05-29 calculation date, limiting symbols, and no-post-basis-price boundary; Macro comparison reads as broad sample -> GLD backdrop -> rate-pressure futures backdrop. |
| Overview Market Context Session Basis V9 | Complete | Market Context now reads the existing US market session state before naming the brief. During open trading it can show `오늘의 시장 브리프`; during weekends / holidays it shows `마지막 거래일 시장 브리프` with the previous trading date as basis and does not create current refresh actions only because intraday snapshot age elapsed while the market was closed. |
| Overview Market Context Source Actionability V8 | Complete | Market Context now separates source confidence into actionable brief sources, reference limitations, and management meta. `현재 이슈만 보강` exclusions such as Events estimate caveats no longer remain as unresolved `자료 확인 필요`, and Data Health is shown as `관리 메타` rather than a market-context source issue. |
| Overview Market Context Smart Refresh V7 | Complete | Market Context keeps the default brief to movement, breadth, and Futures/Macro only. Events caveats are excluded from the brief and shown as non-actionable refresh exclusions unless future cause-analysis logic is approved. `refresh_plan` now separates resolvable, partial, and non-actionable items; `현재 이슈만 보강` runs only current action ids and `전체 Market Context 자료 보강` remains a fallback. |
| Overview Market Context Brief Context Absorption V6 | Complete | Market Context removed the separate `브리프 신뢰도` guide section and no longer returns `brief_caveats`. Events / data-source limits are absorbed only when they change the market brief: optional `이벤트 배경` shows whether events are weak direct-cause evidence, and Futures / OHLCV freshness can lower `Futures/Macro 배경` to `장중 macro 해석 보류`. Source details remain in the evidence disclosure. |
| Overview Market Context Brief Confidence V5 | Complete | Market Context keeps `오늘의 시장 브리프` to movement, breadth, and Futures/Macro background, while Events / data caveats now render as a separate `브리프 신뢰도` section that adjusts reading strength rather than acting as market conclusions. `context_findings` / `next_checks` remain compatibility payloads only. |
| Overview Market Context Brief Findings Integration V4 | Complete | Market Context removed the default V3 `맥락 검토 결과` rail and temporarily absorbed Events / 자료 신뢰도 caveat into `오늘의 시장 브리프`; V5 later split those caveats into `브리프 신뢰도`. Price movement and Futures / Macro remain in the main brief/headline, avoiding duplicate P1/P2 reading. `context_findings` / `next_checks` remain compatibility payloads only. |
| Overview Market Context Context Findings V3 | Complete | Market Context converted `다음 맥락 체크` from an action checklist into `context_findings` conclusions for price movement, Futures / Macro, Events, and data-health caveat. V4 removed the default findings rail; V5 briefly rendered Events / data-source notes as brief confidence; V6 removed that guide section and absorbs only interpretation-changing limits into the market brief. |
| Overview Market Context UX V3 | Complete | Market Context now opens as a summary-first cockpit: current context headline, separate data-state rail, core/supporting card hierarchy, action-oriented next check order, and secondary refresh placement. It keeps existing DB-backed read models and Overview action facade boundaries, with no provider fetch, schema, registry / saved write, validation, monitoring, or trading semantics. Direct `/overview` local first-load still has a Streamlit Page not found modal and remains a routing follow-up. |
| Overview Market Context Events Data Trust V1 | Complete | Events now reads recent 7D plus upcoming horizon rows, prioritizes FOMC / CPI / PPI / Employment / GDP over earnings in context surfaces, splits Macro Week Lane into recent major and upcoming events, and keeps Market Context event/Data Health cues compact. Local DB still lacks CPI rows for 2026-06-10 and 2026-07-14, so Macro Calendar collection or BLS `.ics` import remains a data coverage follow-up. |
| Overview Market Context Historical Analog V1 | Complete | Market Context now has a compact `과거 유사 맥락 참고` section that maps current sector leadership to a sector ETF proxy and, when price coverage is sufficient, summarizes 5D / 20D / 60D forward returns for major assets from simple SPY-relative historical anchors. It is context-only and does not create prediction, recommendation, trade signal, validation gate, Final Review, Operations monitoring, schema, provider, registry, or saved JSONL behavior. Coverage can be uneven by sector ETF; V4 turns those gaps into an explicit repair action. |
| Overview Market Context Hybrid Visual V1 | Complete | Market Context now renders as a card-light hybrid cockpit: 5-cell tape, sector pressure map, event timeline, existing evidence rows, historical analog disclosure, and source confidence disclosure. It reuses stored Overview snapshots only and does not add provider fetch, schema, persistence, registry / saved write, validation gate, monitoring signal, or trading action. |
| Overview Market Context Section Flow V1 | Complete | Market Context now keeps the top cockpit focused on headline, tape, sector pressure map, and event timeline, then renders market brief, interpretation variables, historical analog, source confidence, and boundary copy as sibling reading-flow sections. It remains DB-backed and context-only. |
| Overview Market Context Copy Density V2 | Complete | Market Context now renders `오늘의 시장 맥락` as a short 2-3 sentence narrative and tightens reading-flow typography / color density so the brief, variables, historical analog, and source confidence sections read as a sequence instead of one dense surface. It remains DB-backed and context-only. |
| Overview Market Context Analog Readability V5 | Complete | Market Context historical analog now explains the similarity rule before the table, surfaces sample / proxy median / positive-rate / worst-path summary metrics, and splits detailed rows into core assets and supporting assets. The calculation remains the existing sector ETF relative-strength analog and stays context-only. |
| Overview Market Context Analog Repair V4 | Complete | Market Context now turns historical analog `자료 부족` into an actionable gap panel with missing ETF ticker / row evidence and a `보조 갱신` OHLCV repair action through the existing Overview action facade. Source confidence also shows normal / review / missing counts and key source pills before expansion. It remains DB-backed and context-only; no new provider, schema, registry / saved write, validation, monitoring, or trading action was added. |
| Overview Market Context Supporting Flow V3 | Complete | Market Context now reframes the lower supporting flow as `다음 맥락 체크`, `참고: 과거 유사 맥락`, and `근거: 자료 기준 / 출처 상태`. Data Health is no longer a primary market-variable row; it stays available as evidence/source context. It remains DB-backed and context-only. |
| Overview Market Context Source Action Flow V1 | Complete | Market Context now renders `다음 맥락 체크` from `next_checks` instead of legacy `interpretation_cues`, with target tab, source area, reason, action, freshness, and priority visible. Source Confidence exposes review source/action hints while collapsed, historical analog shows current as-of / data window / calculation basis, and refresh assist remains a secondary collapsed action. |
| Overview Market Context Analog As-Of Window V2 | Complete | Market Context historical analog now has 기준 시점 and 패턴 기간 controls. It can replay latest or a selected as-of date using existing DB prices plus current universe / sector metadata, and supports 5D / 20D / monthly pattern windows while keeping the existing distribution table. Full PIT sector membership / metadata replay remains a storage/read-path approval item. |
| Overview Market Context Macro Dimension Audit V3C | Complete | Market Context `Macro 조건 포함 pilot` now includes `맥락 차원 상태`, showing actual hard conditions, stored FRED `T10Y3M` / `VIXCLS` / `BAA10Y` availability and bucket preview counts, plus event / sentiment annotation or deferred reasons. It remains context-only and does not add FRED / event / sentiment hard filtering. |
| Overview Market Context Futures-Conditioned Analog V3B | Complete | Market Context `Macro 조건 포함 pilot` now keeps GLD context and adds one stored futures daily OHLCV Rate Pressure proxy condition using `ZN=F` / `ZB=F`. The condition is bounded by selected as-of / anchor date, shows used or insufficient state, and remains context-only. |
| Overview Market Context Macro-Conditioned Analog Pilot V1 | Complete | Market Context historical analog separates the original broad analog from a `Macro 조건 포함 pilot`. 3차-A introduced GLD price proxy context and sample quality display; 3차-B extended it with the stored futures Rate Pressure proxy; 3차-C adds dimension availability / preview audit without applying FRED / events / sentiment as hard filters. |
| Futures Market Monitoring / Futures Macro | Complete | yfinance futures 1m / daily OHLCV feeds stored-candle diagnostics and the Futures Macro current score / lazy historical validation flow. Historical validation is point-in-time read-only context, not a prediction guarantee. |

## Completed Foundations

| Foundation | Status | Closeout |
|---|---|---|
| UI Engine Boundary Foundation / Cleanup | Complete | Service/runtime boundary and `app.services/app.runtime -> app.web` import hard-fail lint baseline are in place. |
| Investability Decision Foundation | Complete | Validation gate, storage governance, data provenance, look-through, robustness, selected monitoring, decision dossier baseline complete. |
| Phase 8 Data Evidence Expansion | Complete | Provider / macro / provenance / lifecycle evidence added for investability workflow. |
| Phase 9 Cost / Slippage / Liquidity Realism | Complete | Cost model, turnover, net-cost curve, liquidity / capacity, cost / slippage sensitivity evidence added. |
| Phase 10 Walk-forward / OOS / Regime Validation | Complete | Temporal validation, holdout, macro regime evidence added and connected to selection evidence. |
| Phase 11 Portfolio Construction Risk Controls | Complete | Concentration / overlap / exposure, risk contribution, component role / weight evidence added. |
| Phase 12 Selected Monitoring / Recheck Operations | Complete | Recheck readiness, provider evidence staleness, review signals, allocation boundary, decision dossier continuity complete. |
| Phase 13 First-Cycle Hardening Closeout | Complete | Integrated QA, gate matrix, storage audit, docs/runbook alignment, residual risk carry-forward complete. |
| Practical Validation V2 P2 / P3 | Closeout complete | Provider / macro / look-through / robustness normalization and selected monitoring handoff QA complete. |
| Documentation / AI Workspace Rebuild | Practical closeout | `.aiworkspace/note/finance` and repo-local skill/plugin source are canonical. |

## Current Documentation State

`tasks/active/` and `phases/active/` still contain retained completed boards from prior worktrees.
For now, read them as detailed work records unless the current roadmap or root handoff explicitly names them as active.

Current active phase:

- none

Current active task:

- none

Latest completed task:

- `overview-market-context-turnaround-derived-quarter-provenance-v1-20260716` — 1차~4차 complete

Previous completed task:

- `overview-market-context-turnaround-stage-semantics-fix-v1-20260716` — 1차~3차 complete

Recent completed docs cleanup tasks:

- `post-merge-docs-flow-refresh-20260708`
- `post-merge-verification-handoff-20260607`
- `post-merge-active-state-cleanup-20260607`
- `post-merge-boundary-docs-alignment-20260607`
- `post-merge-docs-alignment-20260607`

Recent completed structure audit tasks:

- `refactor-round-closeout-20260607`
- `backtest-compare-components-split-20260607`
- `ingestion-diagnostic-facade-20260607`
- `runtime-backtest-strict-family-split-20260607`
- `runtime-backtest-real-money-split-20260607`
- `runtime-backtest-risk-on-momentum-split-20260607`
- `streamlit-ingestion-console-split-20260607`
- `overview-ingestion-action-boundary-20260607`
- `code-boundary-refactor-audit-20260607`

Retained completed boards in `phases/active/` should not be treated as newly open phase work.
Their closeout summaries live under `.aiworkspace/note/finance/phases/done/` when available.

State manifest pointers:

- task state manifest: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- phase state manifest: `.aiworkspace/note/finance/phases/active/STATUS_MANIFEST.md`
- Post-merge docs / code flow refresh: `.aiworkspace/note/finance/tasks/active/post-merge-docs-flow-refresh-20260708/STATUS.md`
- post-merge handoff: `.aiworkspace/note/finance/tasks/active/post-merge-verification-handoff-20260607/HANDOFF.md`
- Refactor Round Closeout: `.aiworkspace/note/finance/tasks/active/refactor-round-closeout-20260607/AUDIT.md`
- Backtest Compare Components Split: `.aiworkspace/note/finance/tasks/active/backtest-compare-components-split-20260607/DESIGN.md`
- Ingestion Diagnostic Facade: `.aiworkspace/note/finance/tasks/active/ingestion-diagnostic-facade-20260607/DESIGN.md`
- Runtime Backtest Strict Family split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-strict-family-split-20260607/DESIGN.md`
- Runtime Backtest Real-Money split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-real-money-split-20260607/DESIGN.md`
- Runtime Backtest Risk-On Momentum split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-risk-on-momentum-split-20260607/DESIGN.md`
- Streamlit Ingestion Console split: `.aiworkspace/note/finance/tasks/active/streamlit-ingestion-console-split-20260607/DESIGN.md`
- Overview / Ingestion action boundary: `.aiworkspace/note/finance/tasks/active/overview-ingestion-action-boundary-20260607/DESIGN.md`
- code refactor audit: `.aiworkspace/note/finance/tasks/active/code-boundary-refactor-audit-20260607/AUDIT.md`

Legacy `.note/` was removed after user approval and is no longer part of the current local state.

## Next Decisions

| Candidate | Why It Matters | Requires Approval Before |
|---|---|---|
| Backtest package refactor follow-up | V2-V8 moved Backtest runtime, stores/read models, Single Strategy forms, Portfolio Mix Builder, Practical Validation, and Final Review into packages. Remaining follow-up is smaller cleanup of transitional shared helpers such as `backtest_common.py`, not another broad same-name module split | Moving remaining shared helper ownership or public call paths |
| Large-surface second refactor round | 10차 closeout confirmed large files remain in Backtest Compare, Overview, Operations / Portfolio Monitoring runtime, and Overview services | Opening a new focused refactor round that changes module ownership or public call paths |
| Physical task / phase archive migration | `tasks/active` and `phases/active` still contain retained completed folders even though current active state is now manifest-clean | Moving folders, deleting retained boards, changing archive layout, or repairing historical links |
| Overview Why It Moved V2 | Current V1 is manual/session-only; durable metadata retention or SEC financial-statement preview needs a storage/source policy | DB schema, article/filing body handling, AI summary, catalyst classification |
| Risk-On Momentum 5D governance | Strategy is implemented as research lane but not connected to validation / monitoring daily signal policy | Practical Validation module, Final Review gate, Portfolio Monitoring signal integration |
| Overview scheduler hardening | Browser-session refresh exists; OS scheduler / launchd production operation is a separate decision | Enabling unattended scheduled collection |
| Overview historical analog expansion | 2차 supports latest / selected as-of bounded replay and 5D / 20D / monthly pattern windows using current universe metadata plus DB prices. 3차-A adds GLD context; 3차-B adds one stored futures daily OHLCV Rate Pressure proxy condition; 3차-C shows macro dimension availability / preview status for FRED, events, and sentiment without hard filtering | Adding upload/import flow, full PIT sector universe / metadata storage, expanding sector ETF coverage, CPI/FOMC event-window analogs, events/sentiment conditioning, FRED rates collection, safe-haven futures variants beyond the current Rate Pressure proxy, or strengthening PIT/survivorship/sample-quality treatment |
| UI platform split | Streamlit is workable but complex UX may eventually benefit from API + React/Next.js | Any large frontend migration or service API expansion |
| Second-cycle investability hardening | Phase 13 carry-forward material can seed another phase | Opening a new phase from carry-forward matrix |

## Work Model

| Layer | Location | Meaning |
|---|---|---|
| Phase | `.aiworkspace/note/finance/phases/active/<phase>/` | User-approved multi-task direction, design, integration owner |
| Task | `.aiworkspace/note/finance/tasks/active/<task>/` | Actual implementation, docs, QA, investigation unit |
| Research | `.aiworkspace/note/finance/researches/active/<research-id>/` | Product direction / benchmark / feature opportunity body |
| Durable Docs | `.aiworkspace/note/finance/docs/` | Stable project knowledge after implementation or approved direction |
| Root Handoff Logs | `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 3~5 line milestone / decision pointers only |

## Update Rules

- Add detailed implementation history to task docs, not this roadmap.
- Keep this roadmap focused on active state, completed foundations, and next decisions.
- Update `PRODUCT_DIRECTION.md` when the product purpose or user-facing workflow changes.
- Update `PROJECT_MAP.md` when ownership boundaries or entry points change.
- Update architecture / flow / data docs when runtime, storage, or user workflow boundaries change.
- Use `docs/architecture/SYSTEM_BOUNDARIES.md` as the first checkpoint for layer / storage / product surface boundary changes.

## 2026-07-12 Completed Foundation: Final Review Evidence Closure V1

- 1차~4차 완료: root issue dedup, Level2 action handler Gate, GRS signal/valuation 기간 계약, static/dynamic survivorship policy, Final Review terminal-state snapshot, measured-only score impact.
- current Final Review 후보 계약은 `unresolved_actionable=0`, `critical_engineering=0`, `missing_contract=0`을 요구한다.
- 다음 승인 후보는 dynamic historical universe용 PIT membership / delisting provider이며, 도입 전에는 해당 후보를 defer/block한다.
