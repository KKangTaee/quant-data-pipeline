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
  - [PHASE23_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase23/PHASE23_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md)

## Entries

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
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`와 `manage_current_candidate_registry.py`를 추가해 current candidate를 machine-readable하게 남기고 다시 읽을 수 있게 했다
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
    `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`의 active row를 읽는다고 명시했다
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
