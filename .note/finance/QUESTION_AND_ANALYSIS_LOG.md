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
  - [PHASE17_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md)

## Entries

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
      `defensive sleeve risk-off`
      쪽이 더 자연스럽다
