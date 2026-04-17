# Phase 22 Portfolio-Level Candidate Construction Plan

## 이 문서는 무엇인가

- 이 문서는 `Phase 22`에서 무엇을 만들고 검증할지 정리하는 kickoff plan이다.
- 핵심은 단일 전략 하나가 아니라,
  여러 전략을 섞은 weighted portfolio를 **하나의 후보**로 볼 수 있는지 판단하는 기준을 세우는 것이다.

## 목적

1. `portfolio-level candidate`가 무엇인지 먼저 정의한다.
2. `Phase 21`에서 확인한 annual strict current anchors를 기반으로 대표 portfolio 후보 묶음을 만든다.
3. weighted portfolio와 saved portfolio replay 결과를 durable report로 남겨,
   단순 UI 결과가 아니라 다시 검토 가능한 후보 기록으로 만든다.

## 쉽게 말하면

- 지금까지는 "좋은 전략 하나"를 찾고 다듬는 작업이 중심이었다.
- 이제는 "좋은 전략 여러 개를 섞으면 더 실전적인 포트폴리오 후보가 되는가"를 보는 단계다.
- 단, 아무 조합이나 좋은 포트폴리오라고 부르지 않기 위해
  먼저 "어떤 조건을 만족해야 portfolio 후보라고 부를 수 있는가"부터 정리한다.

## 왜 필요한가

- `Phase 21`에서 `Value / Quality / Quality + Value` current anchor를
  `33 / 33 / 34`로 섞은 representative weighted portfolio가 재현 가능하다는 점을 확인했다.
- 하지만 그 결과는 아직 최종 portfolio winner가 아니다.
- 지금 기준이 없으면 다음 문제가 생긴다.
  - weighted portfolio 결과가 좋아 보여도 후보로 승격해도 되는지 애매하다.
  - saved portfolio가 많아질수록 어떤 조합이 의미 있는 후보인지 헷갈린다.
  - 단일 전략 후보의 `promotion / shortlist / deployment` 해석과 portfolio 후보 해석이 섞인다.
  - `Phase 23` quarterly productionization이나 `Phase 24` new strategy expansion으로 넘어갈 때 비교 기준이 흔들린다.

## 이 phase가 끝나면 좋은 점

- 단일 전략 후보와 portfolio 후보를 구분해서 읽을 수 있다.
- weighted portfolio 결과를 단순 화면 결과가 아니라 재검토 가능한 후보 기록으로 남길 수 있다.
- 어떤 portfolio 조합을 유지, 교체, 보류할지 판단하는 기준이 생긴다.
- 다음 phase에서 quarterly나 new strategy를 붙이더라도,
  기존 annual strict portfolio baseline과 비교하기 쉬워진다.

## 이 phase에서 다루는 대상

- 직접 다루는 대상:
  - `Value Strict Annual` current anchor
  - `Quality Strict Annual` current anchor
  - `Quality + Value Strict Annual` current anchor
  - `Compare & Portfolio Builder`
  - `Weighted Portfolio Builder`
  - `Saved Portfolio Replay`
  - portfolio-level report / index / checklist 문서
- 이번 phase에서 일부러 뒤로 미루는 대상:
  - quarterly prototype productionization
  - 완전히 새로운 strategy family 구현
  - 실제 live deployment 운영 체계
  - 광범위한 brute-force portfolio search

## 현재 구현 우선순위

1. Portfolio-Level Candidate Semantics 정의
   - 쉽게 말하면:
     - 어떤 weighted portfolio를 "후보"라고 부를 수 있는지 기준을 먼저 정한다.
   - 왜 먼저 하는가:
     - 기준 없이 백테스트를 더 돌리면 숫자는 늘어나지만 해석이 흐려진다.
   - 기대 효과:
     - 이후 report와 UI 검증에서 같은 언어로 유지 / 교체 / 보류 판단을 할 수 있다.

2. Representative Portfolio Candidate Pack 구성
   - 쉽게 말하면:
     - `Phase 21`에서 확인한 3개 annual strict anchor를 출발점으로,
       실제 후보로 다시 볼 조합을 정한다.
   - 왜 필요한가:
     - `33 / 33 / 34` bridge는 workflow 검증이었으므로,
       후보 판단용 pack으로 다시 정리해야 한다.
   - 기대 효과:
     - baseline portfolio candidate와 대안 조합을 같은 frame에서 비교할 수 있다.

3. Portfolio-Level Validation Report 작성
   - 쉽게 말하면:
     - portfolio 조합 결과를 표와 해석으로 남겨,
       나중에 다시 봐도 왜 이 조합을 봤는지 알 수 있게 만든다.
   - 왜 필요한가:
     - weighted portfolio 결과는 UI에서 사라지기 쉽고,
       source / weight / date alignment / replay 여부가 같이 남아야 재현 가능하다.
   - 기대 효과:
     - portfolio 후보도 strategy backtest log처럼 durable하게 관리된다.

4. Saved Portfolio Replay와 문서 동기화
   - 쉽게 말하면:
     - 저장된 portfolio를 다시 실행했을 때 같은 결과가 나오는지 확인하고,
       roadmap / index / checklist에 남긴다.
   - 왜 필요한가:
     - portfolio 후보는 재현성이 깨지면 후보가 아니라 일회성 실험이 된다.
   - 기대 효과:
     - Phase 22 closeout 때 사용자가 직접 QA할 수 있는 근거가 생긴다.

## 이 문서에서 자주 쓰는 용어

- `Portfolio-Level Candidate`
  - 전략 하나가 아니라 여러 전략을 정해진 weight로 섞은 포트폴리오 후보다.
- `Portfolio Bridge`
  - compare 결과를 weighted portfolio와 saved portfolio replay까지 이어보는 연결 검증이다.
- `Component Strategy`
  - portfolio 후보 안에 들어가는 각각의 단일 전략이다.
- `Date Alignment`
  - 여러 전략 결과의 날짜를 어떻게 맞춰 portfolio 결과를 계산할지 정하는 방식이다.
- `Saved Portfolio Replay`
  - 저장된 portfolio 구성을 다시 불러와 같은 결과가 나오는지 확인하는 재현성 검증이다.
- `Promotion Semantics`
  - 어떤 결과를 후보, watchlist, comparison-only, blocked처럼 해석할지 정하는 규칙이다.

반복적으로 쓰이는 용어는 `.note/finance/FINANCE_TERM_GLOSSARY.md`에도 함께 정리한다.

## 이번 phase의 운영 원칙

- 기준 먼저, broad rerun은 나중에 한다.
- `Phase 21` portfolio bridge 결과를 최종 후보로 바로 승격하지 않는다.
- portfolio 후보는 component strategy의 약점을 숨기는 용도로 쓰지 않는다.
- saved replay가 재현되지 않으면 portfolio candidate로 보지 않는다.
- raw `CAGR / MDD`만으로 승격하지 않고,
  component status, date alignment, benchmark / guardrail 해석, replay 여부를 함께 본다.
- 사용자가 Phase 22 checklist를 확인하기 전에는 다음 major phase로 넘어가지 않는다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: Portfolio-Level Candidate Semantics 정의

- 무엇을 바꾸는가:
  - portfolio 후보의 정의, 최소 기록 항목, 유지 / 교체 / 보류 기준을 문서로 고정한다.
- 왜 필요한가:
  - 후보 기준이 없는 상태에서 조합 테스트를 늘리면 결과가 쌓여도 의사결정이 어려워진다.
- 끝나면 좋은 점:
  - 다음 작업에서 어떤 portfolio 조합을 후보로 볼지 판단할 수 있다.

### 두 번째 작업: Representative Portfolio Candidate Pack 구성

- 무엇을 바꾸는가:
  - `Value / Quality / Quality + Value` annual strict anchors를 기준으로
    baseline portfolio candidate pack을 만든다.
- 왜 필요한가:
  - `Phase 21`의 `33 / 33 / 34` 결과를 workflow 검증이 아니라 candidate construction 관점으로 다시 읽기 위해서다.
- 끝나면 좋은 점:
  - baseline 조합과 대안 weight 조합을 같은 기준으로 비교할 수 있다.

### 세 번째 작업: Portfolio-Level Report와 Saved Replay 검증

- 무엇을 바꾸는가:
  - portfolio 결과를 report로 남기고,
    저장 후 replay가 같은 결과를 내는지 확인한다.
- 왜 필요한가:
  - portfolio 후보는 source, weight, date alignment, replay 결과가 함께 남아야 재현 가능하다.
- 끝나면 좋은 점:
  - 나중에 같은 portfolio 후보를 다시 열어도 결과와 해석을 추적할 수 있다.

### 네 번째 작업: Closeout Checklist와 Index Sync

- 무엇을 바꾸는가:
  - Phase 22 checklist, roadmap, finance doc index, backtest report index를 현재 상태에 맞춘다.
- 왜 필요한가:
  - 사용자가 QA할 때 "무엇을 어디서 확인해야 하는지"가 바로 보여야 한다.
- 끝나면 좋은 점:
  - Phase 22를 닫고 Phase 23으로 넘어갈지 판단할 수 있다.

## 다음에 확인할 것

- portfolio 후보를 후보라고 부를 최소 조건은 first work unit에서 확정했다.
- `Phase 21`의 `33 / 33 / 34` bridge는 저장 definition 기준
  `[33.33, 33.33, 33.33]` equal-third baseline pack으로 다시 정리했다.
- 다음에는 portfolio-level benchmark / guardrail interpretation을 정리하고,
  equal-third baseline과 비교할 weight alternative 범위를 결정한다.

## 한 줄 정리

- `Phase 22`는 단일 전략 후보를 넘어, 여러 전략을 섞은 portfolio를 하나의 재현 가능한 후보로 다루기 위한 기준과 첫 후보 pack을 만드는 phase다.
