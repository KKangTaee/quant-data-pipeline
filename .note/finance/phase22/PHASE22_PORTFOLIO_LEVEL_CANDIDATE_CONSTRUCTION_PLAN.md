# Phase 22 Portfolio-Level Candidate Construction Plan

## 현재 상태

- `Phase 22`는 `manual_validation_ready` 상태다.
- 기준 정의, baseline portfolio report, benchmark / guardrail policy,
  weight alternative first-pass rerun까지 끝났다.
- 이제 사용자는 `PHASE22_TEST_CHECKLIST.md`를 보며
  문서가 이해되는지, 판단 근거가 충분한지 확인하면 된다.

## 중요한 경계

`Phase 22`는 **실전 투자 포트폴리오를 고르는 phase가 아니다.**

이번 phase의 목적은 퀀트 프로그램 안에서 아래 기능이 제대로 작동하는지 확인하는 것이다.

- 여러 전략 결과를 하나의 weighted portfolio로 묶을 수 있는가
- 그 포트폴리오의 source, weight, date alignment를 기록할 수 있는가
- 저장한 portfolio를 다시 replay했을 때 결과를 재현할 수 있는가
- 결과를 보고 사용자가 유지 / 교체 / 보류 같은 해석을 남길 수 있는가

따라서 여기서 말하는 `baseline`은 투자 기준점이 아니라
**개발 검증용 기준 포트폴리오**다.

`Value / Quality / Quality + Value` 3개를 쓴 이유도
"이 3개가 최종 투자 조합이라서"가 아니다.

이미 Phase 21에서 같은 기간, 같은 universe, 같은 strict annual runtime으로 검증된 대표 전략들이라
포트폴리오 기능을 테스트하기 좋은 fixture였기 때문이다.

즉 이번 phase의 진짜 질문은:

- "이 포트폴리오가 실전 투자할 만큼 좋은가?"

가 아니라:

- "이 프로그램이 여러 전략을 섞고, 저장하고, 다시 검증하는 workflow를 신뢰할 수 있게 제공하는가?"

이다.

## 목적: 쉽게 말하면

`Phase 22`의 목적은 **전략 여러 개를 섞은 포트폴리오 결과를 프로그램 안에서 안전하게 기록하고 다시 검증할 수 있는 구조를 만드는 것**이다.

지금까지는 주로 아래 질문을 봤다.

- `Value` 전략 하나가 좋은가
- `Quality` 전략 하나가 좋은가
- `Quality + Value` 전략 하나가 좋은가

`Phase 22`에서는 개발 관점의 질문으로 바뀐다.

- 전략 3개를 섞은 결과가 프로그램 안에서 일관되게 계산되는가
- 그 포트폴리오 구성을 나중에 다시 재현할 수 있는가
- 비중을 바꿔도 같은 frame에서 비교할 수 있는가
- 숫자가 좋아 보여도 개발 검증 단계와 투자 판단 단계를 구분할 수 있는가

즉, 단순히 화면에서 만든 weighted portfolio 결과를 보고
"좋다"라고 끝내는 phase가 아니다.

source, component, weight, date alignment, replay, 해석이 남아야
프로그램 안에서 다시 다룰 수 있는 `Portfolio-Level Candidate` 기록으로 볼 수 있다.

## 왜 필요한가

`Phase 21`에서 아래 흐름은 이미 확인했다.

1. current candidate 3개를 compare로 불러온다.
2. weighted portfolio로 묶는다.
3. saved portfolio로 저장한다.
4. 다시 replay했을 때 결과가 재현된다.

하지만 이것은 **workflow가 작동한다는 검증**이었다.

아직 다음 질문은 남아 있었다.

- 이 묶음을 portfolio 후보라고 불러도 되는가
- 후보라면 어떤 status를 줄 것인가
- `33 / 33 / 34`와 saved equal-third definition을 어떻게 구분할 것인가
- `25 / 25 / 50`, `40 / 40 / 20` 같은 weight 대안은 baseline을 교체할 만큼 좋은가
- portfolio-level benchmark와 guardrail은 단일 전략 기준과 어떻게 달라야 하는가

기준 없이 포트폴리오 백테스트를 더 돌리면 숫자는 늘어나지만,
나중에 어떤 결과가 같은 조건에서 나온 것인지,
어떤 결과가 단순 화면 실험인지,
어떤 결과가 다시 재현 가능한지 판단하기 어려워진다.

## 이 phase가 끝나면 좋은 점

- 단일 전략 후보와 포트폴리오 후보를 구분해서 읽을 수 있다.
- weighted portfolio 결과가 단순 화면 결과인지, 재현 가능한 후보 기록인지 구분할 수 있다.
- 개발 검증용 baseline portfolio와 weight alternative를 같은 기준으로 비교할 수 있다.
- Phase 23에서 quarterly / alternate cadence를 볼 때,
  annual strict portfolio fixture와 비교하기 쉬워진다.
- 사용자가 checklist를 보며 "무엇을 어디서 확인해야 하는지" 따라갈 수 있다.

## 이번 phase에서 확인한 질문

| 질문 | 확인 위치 | 현재 판단 |
|---|---|---|
| portfolio 후보란 무엇인가 | `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md` | source / weight / replay / 해석이 남아야 후보 |
| baseline portfolio는 무엇인가 | `PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md` | 개발 검증용 equal-third baseline 유지 |
| benchmark는 무엇으로 둘 것인가 | `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md` | `SPY`가 아니라 equal-third baseline |
| guardrail은 어떻게 읽을 것인가 | `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md` | actual trading rule이 아니라 report-level warning |
| weight 대안은 baseline을 교체했는가 | `PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md` | 교체 없음, 두 대안은 보류 |

## Portfolio-Level Candidate로 인정하는 최소 조건

portfolio 후보는 "전략을 섞은 결과표"만으로는 부족하다.

최소한 아래가 남아야 한다.

| 필요한 정보 | 왜 필요한가 |
|---|---|
| component strategy 목록 | 어떤 전략을 섞었는지 알아야 한다 |
| component source | 각 전략이 어떤 후보 문서에서 왔는지 추적해야 한다 |
| validation period | 어느 기간에서 검증했는지 고정해야 한다 |
| universe frame | 서로 다른 universe 결과를 섞지 않기 위해 필요하다 |
| weight | portfolio 결과의 핵심 입력이다 |
| date alignment | 여러 전략 결과의 날짜를 어떻게 맞췄는지 알아야 한다 |
| benchmark / guardrail 해석 | 단일 전략 기준과 portfolio 기준을 구분해야 한다 |
| key metrics | CAGR, MDD, Sharpe, End Balance를 비교해야 한다 |
| saved replay 또는 재현 근거 | 다시 실행했을 때 같은 결과가 나와야 후보로 볼 수 있다 |
| interpretation / next action | 유지, 교체, 보류 판단이 남아야 한다 |

이 기준은 checklist 1번에서 확인하면 된다.

## 이번 phase의 실제 진행 순서

### 1. 후보 기준 정의

- 문서:
  - `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md`
- 확인한 것:
  - `Portfolio-Level Candidate`의 뜻
  - 최소 기록 항목
  - 유지 / 교체 / 보류 판단 기준

### 2. baseline portfolio candidate pack 작성

- 문서:
  - `PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
- 확인한 것:
  - `Value / Quality / Quality + Value` current anchor 3개를 개발 검증용 baseline pack으로 정리
  - `33 / 33 / 34`는 Phase 21의 near-equal 입력이고,
    Phase 22 공식 baseline은 `[33.33, 33.33, 33.33]`임을 분리
  - 현재 status는 `baseline_candidate / portfolio_watchlist / not_deployment_ready`

### 3. benchmark / guardrail / weight scope 정리

- 문서:
  - `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md`
- 확인한 것:
  - 같은 fixture 조합의 weight alternative를 비교할 때 primary benchmark는 `SPY`가 아니라 equal-third baseline
  - `SPY`는 market context로만 유지
  - portfolio-level guardrail은 actual trading rule이 아니라 report-level warning
  - weight 대안은 `25 / 25 / 50`, `40 / 40 / 20` 두 개만 먼저 보기로 결정

### 4. weight alternative rerun

- 문서:
  - `PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md`
- 확인한 것:
  - `25 / 25 / 50`은 CAGR은 좋아지지만 `Quality + Value` 편중이 커짐
  - `40 / 40 / 20`은 MDD는 조금 낮아지지만 CAGR을 포기함
  - 따라서 baseline 교체 없이 equal-third baseline 유지

## 이번 phase에서 하지 않는 일

아래는 중요하지만 이번 phase에서는 일부러 열지 않는다.

- quarterly prototype productionization
- new strategy family 구현
- broad brute-force weight search
- risk parity / volatility targeting
- live deployment 운영 체계
- portfolio-level registry schema 확정

이것들을 지금 다 열면 Phase 22의 질문이 흐려진다.

이번 phase의 핵심은 **annual strict current anchors로 만든 첫 개발 검증용 portfolio baseline을 재현 가능한 후보 기록으로 정리하는 것**이다.

다시 말해, 실전 투자를 승인하는 것이 아니라
프로그램이 포트폴리오 구성 workflow를 제대로 다룰 수 있는지 확인하는 단계다.

## checklist에서 확인하는 방법

`PHASE22_TEST_CHECKLIST.md`의 1번은 아래처럼 읽으면 된다.

1. 이 plan 문서의 `목적: 쉽게 말하면`, `왜 필요한가`, `Portfolio-Level Candidate로 인정하는 최소 조건`을 읽는다.
2. `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md`의 `기본 정의`, `Portfolio-Level Candidate 최소 기록 항목`, `후보 판단 규칙 초안`을 읽는다.
3. 아래 세 가지가 이해되면 checklist 1번을 체크할 수 있다.
   - weighted result와 portfolio candidate는 다르다.
   - source / weight / date alignment / replay / 해석이 남아야 후보가 된다.
   - 유지 / 교체 / 보류 판단은 숫자만이 아니라 재현성과 해석까지 같이 본다.

## 한 줄 정리

`Phase 22`는 좋은 전략 3개를 섞은 결과를 바로 최종 포트폴리오라고 부르지 않고,
**포트폴리오 구성 기능을 개발 검증용 baseline과 재현 가능한 기록으로 관리할 수 있게 만든 phase**다.
