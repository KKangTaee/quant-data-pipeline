# Finance Question And Analysis Log

## Purpose
This file stores the current, concise set of durable `finance` design decisions and analysis outcomes.

Use it for:
- active architecture interpretations
- current strategy-refinement direction
- decisions that should influence the next turns

Detailed historical analysis was archived on `2026-04-13`.

## Active Pointers

- latest phase board:
  - [PHASE34_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase34/PHASE34_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md)

## Entries

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
  - Phase 34 문서 bundle을 `.note/finance/phases/phase34/` 아래에 생성했다
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
  - Phase 33 문서 bundle을 `.note/finance/phases/phase33/` 아래에 생성했다
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
    `plugins/quant-finance-workflow`
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
  - `.note/finance/PHASE_PLAN_TEMPLATE.md`를 새로 만들어,
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
    - `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md`를 기본 템플릿으로 사용할 것
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
  - `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`와 `manage_current_candidate_registry.py`를 추가해 current candidate를 machine-readable하게 남기고 다시 읽을 수 있게 했다
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
    `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`의 active row를 읽는다고 명시했다
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
  - 확인 시작점은 `.note/finance/backtest_reports/phase21/README.md`로 정리했다
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
  - durable report는 `.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md`에 저장했다
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
  - `.note/finance/docs/architecture/`를 새 canonical code flow 위치로 만들었다
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
  - `.note/finance/data_architecture/`를 새 canonical data / DB architecture 위치로 만들었다
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
  - 기존 `3-3. 상세 구현 메모` 원문을 `.note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`로 이동했다
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

### 2026-04-21 - `.note/finance/` root Markdown은 상위 문서 중심으로 유지한다
- Request topic:
  - 사용자가 `.note/finance/` 루트에 정리되지 않은 Markdown 파일들이 있으니, 폴더로 관리할 수 있는 파일은 폴더를 만들어 관리해 달라고 요청함
- Interpreted goal:
  - root에는 큰 지도 / 활성 로그 / 템플릿만 남기고, 운영성 문서, research 참고 자료, support-track 문서, developer flow 문서를 목적별 폴더로 이동해야 함
- Result:
  - 운영성 문서는 `.note/finance/operations/`, daily market update 문서는 `.note/finance/operations/daily_market_update/`, research 문서는 `.note/finance/research/`, support 논의 문서는 `.note/finance/support_tracks/`, 기존 backtest refinement flow guide는 `.note/finance/docs/architecture/`로 이동했다
  - `FINANCE_DOC_INDEX.md`와 관련 링크를 새 위치로 갱신했다
  - 앞으로 root `.note/finance/`는 `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, glossary, active logs, phase templates 중심으로 유지한다

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
  - `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 Pre-Live 운영 상태 전용 append-only registry로 정했다
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
  - 기본값은 출력만 하며, 실제 `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 저장은 `--append`가 있을 때만 수행한다
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
  - `Candidate Review Note`를 `CURRENT_CANDIDATE_REGISTRY.jsonl`과 별도인 `.note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl`에 저장하는 구조로 정했다
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
  - `Append To Current Candidate Registry`를 눌러야만 `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`에 append된다
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
  - 사용자는 `.note/finance/phases/phase29/PHASE29_TEST_CHECKLIST.md` 기준으로 QA를 진행하고, 완료되면 Phase 29 closeout 후 Phase 30으로 넘어간다

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
  - 향후 저장소 후보는 `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이지만, 이번 작업에서는 파일 생성 / append helper / UI 구현을 하지 않는다
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
  - 저장소는 `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이며 첫 proposal 저장 시 생성되는 append-only registry다
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
  - 사용자는 `.note/finance/phases/phase30/PHASE30_TEST_CHECKLIST.md` 기준으로 final manual QA를 진행한다

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
  - `.note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md`를 만들고 GTAA 실습 후보, Risk-Off 해석, 4->5 기준, 5단계 Compare 기준, 이번 세션에서 추가된 UI 보조 기능을 모았다
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
  - `.note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`를 새로 만들어 app/web, runtime, finance core, loaders, data/DB, repo-local automation의 script별 책임을 요약했다
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
  - `.note/finance` root에 `phase1`~`phase30` 폴더가 직접 흩어져 있어 문서가 파편화되어 보이므로, phase 문서를 상위 폴더로 묶고 기존 링크도 정리해 달라고 요청함
- Interpreted goal:
  - root에는 top-level map, glossary, template, registry, operations entry만 남기고 phase 실행 문서는 한 곳에서 찾을 수 있게 만든다
- Analysis result:
  - canonical phase path를 `.note/finance/phases/phase<N>/`로 정했다
  - 새 phase 생성 helper도 이 위치로 생성하도록 바꿔야 이후 문서 구조가 다시 흩어지지 않는다
  - `FINANCE_DOC_INDEX.md`에는 folder map을 추가해 phase / operations / backtest_reports / architecture / flows docs / data_architecture / research / support_tracks / archive의 역할을 바로 구분하게 했다
- Follow-up:
  - old `.note/finance/phaseN` 링크는 `.note/finance/phases/phaseN`으로 갱신했다
  - `.note/finance/phases/README.md`를 새 phase 문서 landing page로 추가했다

### 2026-05-02 - finance JSONL 저장 파일 폴더화
- User request:
  - `.jsonl` 파일도 별도 폴더를 만들어 관리하는 것이 좋지 않겠냐고 질문했고, 제안한 구조대로 진행을 승인함
- Interpreted goal:
  - `.note/finance` root에 실행 이력, registry, saved portfolio 파일이 섞이지 않게 하고, 앱 / helper / 문서가 같은 저장 위치를 바라보게 만든다
- Analysis result:
  - app-readable durable registry는 `.note/finance/registries/`에 둔다
  - 로컬 실행 이력은 `.note/finance/run_history/`에 둔다
  - 사용자가 명시적으로 저장한 weighted portfolio 설정은 `.note/finance/saved/`에 둔다
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
  - Phase31을 열 때는 `.note/finance/registries/LIVE_READINESS_REVIEW_REGISTRY.jsonl` 같은 별도 decision registry와 `Backtest > Live Readiness` 또는 Portfolio Proposal handoff UI를 우선 정의한다

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
  - Phase31 문서 bundle을 `.note/finance/phases/phase31/` 아래에 생성했다
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
  - 사용자 QA는 `.note/finance/phases/phase31/PHASE31_TEST_CHECKLIST.md` 기준으로 진행한다
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
  - proposal row는 `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append되고 있었다
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
  - 사용자는 `.note/finance/phases/phase32/PHASE32_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다
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
  - Final Decision은 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 별도로 저장하며 current candidate, Pre-Live, Portfolio Proposal, Paper Ledger registry를 덮어쓰지 않는다
  - `SELECT_FOR_PRACTICAL_PORTFOLIO`도 live approval이나 broker order가 아니라 Phase35 운영 가이드 입력이다
- Follow-up:
  - Phase34는 `implementation_complete / manual_qa_pending` 상태가 됐다
  - 사용자는 `.note/finance/phases/phase34/PHASE34_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다
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
  - Phase35 문서 bundle을 `.note/finance/phases/phase35/` 아래에 만들었다
  - Phase35는 `active / not_ready_for_qa` 상태이며, 첫 작업은 operating policy contract 정리다

### 2026-05-04 - Phase35 Post-Selection Operating Guide 구현 완료
- User request:
  - Phase35의 첫 번째 작업부터 마지막 작업까지 순서대로 진행하고, checklist 확인 단계가 되면 알려 달라고 요청함
- Interpreted goal:
  - 최종 선정 후보를 바로 주문이나 승인으로 연결하지 않고, 사용자가 따라갈 리밸런싱 / 축소 / 중단 / 재검토 운영 기준을 UI와 append-only 기록으로 만들어야 함
- Analysis result:
  - Phase35 입력은 `SELECT_FOR_PRACTICAL_PORTFOLIO`와 `READY_FOR_POST_SELECTION_OPERATING_GUIDE`를 만족하는 final review record로 제한한다
  - 운영 가이드는 final decision 원본을 덮어쓰지 않고 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`에 별도 append-only row로 남긴다
  - `Backtest > Post-Selection Guide`에서 selected final decision, target components, operating readiness, operating policy, saved guide review를 확인한다
  - `운영 가이드 기록`도 live approval, broker order, 자동매매가 아니다
- Follow-up:
  - Phase35는 `implementation_complete / manual_qa_pending` 상태가 됐다
  - 사용자는 `.note/finance/phases/phase35/PHASE35_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다

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
  - 최종 판단 원본은 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다
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
  - 사용자가 나중에 다시 확인할 수 있도록 `.note/finance/operations/FINAL_SELECTED_PORTFOLIO_OPERATIONS_DASHBOARD_GAP_20260504.md`에 요약 문서를 생성했다
  - 사용자 판단상 1순위 기능은 `최종 선정 포트폴리오 운영 대시보드`로 기록했다

### 2026-05-05 - Compare & Portfolio Builder 저장 Mix UX 재구성
- User request:
  - GTAA 70 + Equal Weight 30 mix를 확인하고 저장하려는데, Weighted Portfolio Builder / Result / Save 영역과 저장된 파일 관리 위치가 한 화면에서 잘 드러나지 않는다고 지적함
- Interpreted goal:
  - 새 전략 비교와 저장된 mix 다시 열기를 분리해, 사용자가 `비교 -> 비중 조합 -> 결과 확인 -> 저장` 흐름과 `저장된 mix load / replay` 흐름을 혼동하지 않게 해야 함
- Analysis result:
  - saved portfolio row는 후보 registry가 아니라 재사용 가능한 weighted portfolio setup이다
  - 따라서 저장 위치는 `.note/finance/saved/SAVED_PORTFOLIOS.jsonl` 유지가 적절하며, UI에서 `Portfolio Mix`와 저장 위치를 명확히 보여주는 편이 registry semantics를 흐리지 않는다
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
  - `.note/finance/registries/` 폴더가 없어졌다가 복구되었으므로, 복구된 registry 내용을 기준으로 현재 후보와 포트폴리오 해석을 다시 검토해 달라고 요청함
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
  - `.note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`에 route / session key / registry dependency / source contract / 단계별 구현 순서를 정리했다
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
  - `.note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`에 Clean V2 저장소 설계, legacy archive 정책, 새 JSONL 파일 역할, 사후관리 flow를 보강했다

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
  - `.note/finance/tasks/active/practical-validation-v2/DESIGN.md`에 조사 출처, domain 설계, v2 schema, UI 구조, 구현 slice를 문서화했다
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
  - `.note/finance/tasks/active/practical-validation-v2/DESIGN.md`에 앞 단계 검증과의 중복 위험, Stage Ownership Matrix, domain `origin` 설계, 중복 감점 방지 원칙을 보강했다

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
  - `.note/finance/research/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`를 새로 작성했다
  - `.note/finance/tasks/active/practical-validation-v2/DESIGN.md`를 evidence pack 중심에서 Practical Investment Diagnostics 중심으로 보강했다

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
  - `.note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`를 추가하고, 사용자가 검토한 뒤 개발 범위를 확정하기로 했다

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
  - archive를 늘리지 않고, 현재에도 유효한 데이터 / DB 의미 문서를 새 장기 지식 구조인 `.note/finance/docs/data/`로 흡수해야 함
- Analysis result:
  - `DATA_FLOW_MAP`, `DB_SCHEMA_MAP`, `TABLE_SEMANTICS`, `DATA_QUALITY_AND_PIT_NOTES`는 모두 현재 Practical Validation P2 provider / DB / loader 구조와 맞는 핵심 문서라 삭제 대상이 아니다
  - 기존 `data_architecture/` 루트 폴더를 유지하면 `docs/data/`와 canonical 위치가 갈라지므로, 상세 문서 4개를 이름 그대로 `docs/data/`로 옮기는 것이 맞다
  - `docs/data/README.md`는 단순 table 목록이 아니라 읽는 순서, source-of-truth, 갱신 조건을 함께 가진 data 문서 index가 되어야 한다
- Follow-up:
  - 기존 `.note/finance/data_architecture/` 폴더를 제거하고, data 문서 canonical 위치를 `.note/finance/docs/data/`로 갱신했다

### 2026-05-13 - Reference / Guides와 Glossary의 문서 의존성 확인
- User request:
  - 사용자가 문서 삭제 전 `Reference > Guides` 화면이 운영 정책 md 파일을 읽는 구조인지 확인하고, 실제 의존 문서는 삭제하지 말아야 한다고 요청함
- Interpreted goal:
  - 앱에서 직접 읽는 문서와 화면에 참고 경로로만 노출되는 문서를 구분해, legacy 문서 삭제 전에 끊기는 reference를 없애야 함
- Analysis result:
  - `Reference > Guides`는 md 본문을 읽지 않고 `app/web/reference_guides.py` 안의 hardcoded guide text와 문서 경로 목록을 렌더링한다
  - `Reference > Glossary`는 `GLOSSARY_DOC_PATH.read_text()`로 glossary md를 실제 읽는다
  - 따라서 Guides 경로 목록은 새 docs 기준으로 바꾸고, Glossary는 새 `.note/finance/docs/GLOSSARY.md`에 본문을 승격한 뒤 코드 읽기 경로를 바꾸는 것이 맞다
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
  - 전략별 세부 구현, legacy Candidate Review / Portfolio Proposal 세부 흐름, active task 진행 로그는 README에 길게 두지 않고 `.note/finance/docs/`와 active task 문서로 연결해야 한다
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
