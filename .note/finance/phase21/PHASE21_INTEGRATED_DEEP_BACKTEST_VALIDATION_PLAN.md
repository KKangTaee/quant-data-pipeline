# Phase 21 Integrated Deep Backtest Validation Plan

## 이 문서는 무엇인가
- `Phase 21`에서 무엇을 깊게 다시 검증할지,
  왜 지금 이 phase가 필요한지,
  어떤 순서로 검증을 열어야 하는지 정리한 kickoff 문서다.

## 목적
- `Value`, `Quality`, `Quality + Value` current candidate를 같은 검증 기준에서 다시 확인한다.
- lower-MDD 대안과 saved / weighted portfolio bridge까지 포함해
  **지금 실제로 들고 갈 후보가 무엇인지**를 더 분명하게 만든다.
- 이후 `portfolio-level candidate construction`과 `new strategy expansion`이
  더 흔들리지 않도록 validation 기준을 고정한다.

## 쉽게 말하면
- 이제는 기능을 더 많이 붙이는 단계보다,
  **지금까지 만든 후보가 정말 유지할 만한지 다시 크게 검증하는 단계**
  가 더 중요해졌다.
- 문서와 UI는 어느 정도 정리됐으니,
  이제는 후보를 한 프레임에서 다시 돌려보며
  "유지 / 교체 / 보류"를 더 분명하게 판단하려는 phase다.

## 왜 필요한가
- `Phase 15 ~ 20` 동안:
  - strongest candidate
  - lower-MDD near miss
  - structural contract
  - compare / weighted / saved workflow
  까지는 충분히 쌓였다.
- 하지만 지금까지의 결과는
  phase별 bounded validation과 operator workflow 정리에 더 가까웠다.
- 이 상태로 바로 portfolio-level candidate나 새 전략으로 넘어가면,
  **현재 annual strict family의 기준점이 정말 유지되는지**
  다시 큰 프레임에서 확인하지 못한 채 다음 단계로 가게 된다.

## 이 phase가 끝나면 좋은 점
- `Value / Quality / Quality + Value`의 current anchor를 더 자신 있게 유지하거나 교체할 수 있다.
- lower-MDD alternative가 실제 rescue candidate인지 더 분명해진다.
- saved / weighted portfolio bridge가 portfolio-level candidate로 넘어갈 준비가 되었는지 판단하기 쉬워진다.
- 다음 phase가 "또 검증"이 아니라,
  **검증된 후보 위에서 확장하는 단계**가 된다.

## 이 phase에서 다루는 대상
- `Value Snapshot (Strict Annual)` current anchor / near-miss
- `Quality Snapshot (Strict Annual)` current anchor / alternative
- `Quality + Value Snapshot (Strict Annual)` strongest practical point / lower-MDD alternative
- `Compare & Portfolio Builder`
- `Saved Portfolios`
- strategy hub / backtest log / current candidate summary / phase reports

## 현재 구현 우선순위
1. validation frame definition
   - 쉽게 말하면:
     - 어떤 후보를 어떤 기간 / 기준 / report 형식으로 다시 볼지 먼저 고정한다.
   - 왜 먼저 하는가:
     - deep validation은 결과보다 frame이 흔들리면 해석이 다시 흐려지기 때문이다.
   - 기대 효과:
     - 이후 rerun이 늘어나도 비교 기준이 유지된다.
2. annual strict family integrated rerun
   - 쉽게 말하면:
     - `Value`, `Quality`, `Quality + Value` current candidate와 주요 대안을 같은 판에서 다시 돌린다.
   - 왜 필요한가:
     - current anchor 유지 / 교체 / rescue 여부를 지금 단계에서 정리해야 한다.
   - 기대 효과:
     - strongest candidate와 lower-MDD alternative의 현재 위치가 다시 명확해진다.
3. portfolio bridge validation
   - 쉽게 말하면:
     - compare / weighted / saved portfolio 흐름으로 만든 candidate가 실제로 의미 있는지 본다.
   - 왜 필요한가:
     - 이후 `portfolio-level candidate construction`으로 가려면 bridge가 연구 artifact인지, 실제 candidate lane인지 판단해야 한다.
   - 기대 효과:
     - phase 22의 대상이 single-strategy인지 portfolio-level인지 더 선명해진다.
4. closeout and interpretation sync
   - 쉽게 말하면:
     - rerun 결과를 strategy hub, backtest log, current candidate summary에 같은 언어로 정리한다.
   - 왜 필요한가:
     - deep validation 결과가 chat에만 남으면 다음 phase에서 다시 흔들린다.
   - 기대 효과:
     - 이후 phase가 validation 결과를 확정된 기준처럼 다시 사용할 수 있다.

## 이 문서에서 자주 쓰는 용어
- `Integrated Deep Validation`
  - strongest / alternative / portfolio bridge를 같은 validation frame에서 다시 검증하는 것
- `Current Anchor`
  - 현재 practical 기준에서 대표 후보로 쓰고 있는 설정
- `Lower-MDD Alternative`
  - 낙폭은 더 낮지만 현재 gate나 해석 면에서 anchor를 바로 대체하진 못한 후보
- `Portfolio Bridge`
  - compare -> weighted portfolio -> saved portfolio 흐름으로 이어지는 후보 재사용 동선

## 이번 phase의 운영 원칙
- validation first
  - 이번 phase는 새 기능 확장보다 검증과 해석 정리에 우선순위를 둔다.
- same-frame comparison
  - family별 strongest / alternative / bridge 결과를 가능한 한 같은 frame에서 비교한다.
- durable reporting
  - 의미 있는 결과는 strategy hub / backtest log / candidate summary에 남긴다.
- support tooling is secondary
  - plugin / skill / agent automation은 필요하면 쓰되,
    main phase의 산출물로 세지 않는다.

## 이번 phase의 주요 작업 단위
- 첫 번째 작업:
  - integrated validation frame을 정의한다.
  - 무엇을 바꾸는가:
    - candidate set, 기간, 비교 기준, 결과 기록 방식을 먼저 고정한다.
  - 왜 필요한가:
    - deep rerun 결과가 많아질수록 먼저 frame이 고정되어 있어야 한다.
  - 끝나면 좋은 점:
    - 이후 rerun이 phase 전체에서 같은 기준으로 읽힌다.
- 두 번째 작업:
  - annual strict family rerun pack을 실행한다.
  - 무엇을 바꾸는가:
    - current anchor / lower-MDD alternative / near-miss를 실제로 다시 검증한다.
  - 왜 필요한가:
    - current candidate 유지 / 교체 판단을 더 미루기 어렵기 때문이다.
  - 끝나면 좋은 점:
    - 현재 strongest family가 더 선명하게 정리된다.
- 세 번째 작업:
  - portfolio bridge validation을 수행한다.
  - 무엇을 바꾸는가:
    - weighted / saved portfolio candidate가 다음 phase 대상이 될 수 있는지 검토한다.
  - 왜 필요한가:
    - portfolio-level phase를 열기 전에 bridge의 의미를 먼저 확인해야 한다.
  - 끝나면 좋은 점:
    - 다음 phase를 single-strategy 중심으로 갈지, portfolio-level로 갈지 판단하기 쉬워진다.

## 다음에 확인할 것
- current anchor를 그대로 유지하는 family가 무엇인지
- lower-MDD alternative 중 실제 rescue candidate가 생기는지
- saved / weighted portfolio가 `Phase 22`의 메인 대상이 될 만큼 의미 있는지
- quarterly prototype productionization을 언제 여는 것이 타당한지

## 한 줄 정리
- `Phase 21`은 **지금까지 만든 annual strict 후보와 portfolio bridge를 한 기준에서 다시 검증해, 다음 확장 phase의 기준점을 확정하는 deep validation phase**다.
