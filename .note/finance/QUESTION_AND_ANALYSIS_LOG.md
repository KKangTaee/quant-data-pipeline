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
  - [PHASE18_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md)
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
