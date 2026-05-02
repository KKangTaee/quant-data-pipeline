# Phase 25 Pre-Live Operating System And Deployment Readiness Plan

## 이 문서는 무엇인가

이 문서는 `Phase 25`에서 무엇을 만들고, 왜 만드는지 설명하는 kickoff 문서다.

Phase 25는 live trading을 시작하는 단계가 아니다.
백테스트 결과와 Real-Money 검증 신호를 본 뒤,
실제 돈을 넣기 전에 무엇을 관찰하고 기록해야 하는지 정리하는 운영 준비 단계다.

## 목적

Phase 25의 목적은 세 가지다.

1. `Real-Money 검증 신호`와 `Pre-Live 운영 점검`을 화면과 문서에서 분리한다.
2. paper tracking, watchlist, hold, re-review 같은 운영 상태와 그 상태에 붙는 다음 행동 기록 기준을 만든다.
3. 사용자가 후보를 다시 볼 때 "왜 이 후보를 관찰 중인지", "무엇을 언제 다시 확인해야 하는지", "무엇이 아직 blocker인지"를 빠르게 이해하게 만든다.

## 쉽게 말하면

지금까지는 백테스트 결과를 만들고,
그 결과에 Real-Money 관련 위험 신호를 붙이는 데 집중했다.

Phase 25는 그 다음 단계다.
좋아 보이는 결과가 나왔을 때 바로 실전 투입으로 넘어가지 않고,
"일단 종이에 적어두고 한동안 관찰하자",
"이 조건이 해결되기 전까지는 보류하자",
"다음 재검토일에 다시 보자"를 기록하는 운영판을 만든다.

## 왜 필요한가

백테스트 결과가 좋다고 해서 실전 준비가 끝난 것은 아니다.

예를 들어 어떤 전략이 높은 CAGR과 낮은 MDD를 보여도,
데이터 품질, 거래비용, 최근 성과 붕괴, ETF 유동성, benchmark 대비 약점,
운영자가 감당할 수 있는 리밸런싱 주기 같은 문제가 남을 수 있다.

Real-Money 검증 신호는 이런 문제를 알려주는 진단표다.
하지만 진단표만 있으면 사용자는 다음 행동을 직접 기억해야 한다.
Phase 25는 그 다음 행동을 기록하고 반복할 수 있게 만든다.

여기서 말하는 다음 행동은 단순히 `watchlist` 같은 상태값 하나가 아니다.
`operator_reason`, `next_action`, `review_date`, `tracking_plan`까지 포함한 운영 기록이다.
이 정보가 있어야 Pre-Live가 Real-Money promotion 단계와 구분된다.

## 이 phase가 끝나면 좋은 점

- 사용자가 Real-Money 결과를 보고 다음 행동을 더 쉽게 정한다.
- 후보가 `watchlist`, `paper tracking`, `hold`, `re-review` 중 어디에 있는지 남길 수 있다.
- 각 후보에 대해 무엇을 언제 다시 확인할지, 어떤 조건이면 중단하거나 다음 단계로 갈지 남길 수 있다.
- 나중에 같은 후보를 다시 볼 때 판단 근거를 잃어버리지 않는다.
- 실전 투입 전 점검과 투자 추천을 혼동하지 않게 된다.
- Phase 26 이후 실제 deployment readiness나 더 강한 investability review로 넘어갈 준비가 된다.

## 이 phase에서 다루는 대상

직접 다루는 대상:

- `Backtest` 결과에 이미 존재하는 Real-Money 검증 신호
- strategy / compare / saved portfolio에서 나온 후보를 pre-live 관찰 대상으로 넘기는 기준
- paper tracking / watchlist / hold / re-review 기록 포맷
- operator-facing guidance와 manual checklist

이번 phase에서 일부러 하지 않는 것:

- 자동 매매
- 실전 주문 실행
- 특정 후보의 투자 승인
- portfolio weight optimization
- 사용자가 요청하지 않은 broad investment analysis

## 현재 구현 우선순위

1. Pre-Live 경계와 운영 상태 정의
   - 쉽게 말하면: Real-Money 신호와 Pre-Live 운영 점검이 무엇이 다른지 고정한다.
   - 왜 먼저 하는가: 이 경계가 흐리면 Phase 25가 기존 Real-Money 탭의 중복 기능처럼 보인다.
   - 기대 효과: 이후 UI, 문서, checklist가 같은 언어로 정리된다.

2. Pre-Live 후보 기록 포맷 설계
   - 쉽게 말하면: 후보를 관찰 대상으로 올릴 때 무엇을 저장해야 하는지 정한다.
   - 왜 필요한가: 결과 수치만 저장하면 나중에 왜 관찰 중인지 알 수 없다.
   - 기대 효과: paper tracking과 재검토 흐름을 재현할 수 있다.
   - 현재 결정: `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 별도 운영 기록소로 두고, current candidate registry와는 pointer로 연결한다.

3. Operator review workflow 설계
   - 쉽게 말하면: 후보를 보고 `watchlist`, `paper tracking`, `hold`, `reject`, `re-review` 중 어디로 보낼지 정한다.
   - 왜 필요한가: 좋은 결과와 실제 운영 준비 상태는 다르기 때문이다.
   - 기대 효과: 사용자가 다음 행동을 화면이나 문서에서 놓치지 않는다.
   - 현재 결정: `draft-from-current` helper로 current candidate에서 Pre-Live 기록 초안을 만들고,
     운영자가 확인한 뒤 `--append`로 저장하는 report/helper 기반 흐름을 먼저 사용한다.

4. Pre-Live dashboard / report draft
   - 쉽게 말하면: 관찰 중인 후보들을 한곳에서 볼 수 있는 초안을 만든다.
   - 왜 필요한가: 후보가 늘어나면 chat이나 개별 report만으로는 관리가 어렵다.
   - 기대 효과: Phase 26 이후 deployment readiness 판단의 기반이 생긴다.
   - 현재 구현: `Backtest > Pre-Live Review` 패널에서 current candidate를 선택하고
     Pre-Live 기록 초안을 확인한 뒤 저장할 수 있다.

## 이 문서에서 자주 쓰는 용어

- `Real-Money 검증 신호`
  - 백테스트 결과에 붙는 진단표다.
  - 거래비용, benchmark, drawdown, 유동성, promotion 상태 같은 위험 신호를 보여준다.

- `Pre-Live 운영 점검`
  - Real-Money 검증 신호를 본 뒤 사람이 무엇을 할지 정하는 운영 절차다.
  - paper tracking, watchlist, hold, re-review 같은 상태와 함께
    `operator_reason`, `next_action`, `review_date`, `tracking_plan`을 기록한다.
  - 상태값만 있으면 Real-Money promotion 단계와 비슷해 보이므로,
    다음 행동 기록이 Pre-Live의 핵심이다.

- `Paper Tracking`
  - 실제 돈을 넣지 않고, 정해진 기간 동안 전략 결과와 위험 신호를 관찰하는 상태다.

- `Watchlist`
  - 당장 paper tracking까지는 아니지만, 다시 볼 가치가 있어 목록에 남겨두는 상태다.

- `Hold`
  - 데이터 품질, 구조적 위험, 검증 부족 같은 이유로 보류하는 상태다.

- `Re-Review`
  - 특정 조건이나 날짜가 지나면 다시 확인하기로 남기는 상태다.

## 이번 phase의 운영 원칙

- 개발 기본 방향은 `데이터 수집 + 백테스트 제품 개발`이다.
- Real-Money 신호는 투자 승인 장치가 아니라 검증 신호로 읽는다.
- Pre-Live 운영 점검은 live trading이 아니라 paper / watchlist / review를 위한 준비 절차다.
- 사용자가 명시적으로 분석을 요청하면 분석과 백테스트는 수행할 수 있다.
- 다만 그 경우에도 phase roadmap이 투자 분석 중심으로 drift하지 않도록 별도 분석으로 기록한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: Pre-Live 경계와 운영 상태 정의

- 무엇을 바꾸는가:
  - Phase 25 문서와 glossary / guide에서 Real-Money와 Pre-Live의 역할을 분리해 읽게 만든다.
- 왜 필요한가:
  - 둘 다 "실전 전에 확인하는 것"처럼 보이지만, 하나는 진단표이고 하나는 운영 절차다.
- 끝나면 좋아지는 점:
  - 이후 UI나 checklist를 만들 때 같은 설명을 반복하지 않아도 된다.

### 두 번째 작업: 후보 기록 포맷 설계

- 무엇을 바꾸는가:
  - pre-live 후보 기록에 필요한 필드를 정한다.
  - 예: source run, strategy, settings, Real-Money signal, blocker, next action, review date.
  - 저장 위치는 `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`로 고정한다.
  - helper는 `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`를 사용한다.
- 왜 필요한가:
  - 나중에 후보를 다시 봤을 때 단순 수치가 아니라 판단 맥락까지 복원해야 한다.
- 끝나면 좋아지는 점:
  - paper tracking과 watchlist가 일회성 메모가 아니라 재현 가능한 기록이 된다.

### 세 번째 작업: Review workflow와 UI 초안

- 무엇을 바꾸는가:
  - operator가 후보를 어떤 상태로 보낼지 선택하고 확인하는 흐름을 만든다.
  - 먼저 `manage_pre_live_candidate_registry.py draft-from-current <registry_id>`로
    current candidate에서 Pre-Live 기록 초안을 만드는 entry point를 추가했다.
- 왜 필요한가:
  - 현재는 Real-Money 결과를 본 뒤 다음 행동이 사람 머릿속에 남기 쉽다.
- 끝나면 좋아지는 점:
  - 후보 관리가 `좋음 / 나쁨`이 아니라 `관찰 / 보류 / 재검토`로 정리된다.

### 네 번째 작업: Manual QA와 handoff

- 무엇을 바꾸는가:
  - 사용자가 실제로 Phase 25 흐름을 검수할 수 있는 checklist를 만든다.
  - `Backtest > Pre-Live Review` 화면에서 확인해야 할 항목을 checklist에 반영한다.
- 왜 필요한가:
  - Pre-Live는 특히 용어가 헷갈리기 쉬워서 UI 위치와 확인 행동이 명확해야 한다.
- 끝나면 좋아지는 점:
  - Phase 26으로 넘어가기 전에 운영 준비 체계가 사용자 관점에서 이해 가능한지 확인할 수 있다.

## 다음에 확인할 것

- Pre-Live 후보 기록은 파일 기반 registry로 먼저 둔다.
- 기존 `CURRENT_CANDIDATE_REGISTRY.jsonl`과 새 Pre-Live 기록은 분리하고, 필요할 때 `source_candidate_registry_id`로 연결한다.
- report/helper workflow는 먼저 추가했다.
- `Backtest > Pre-Live Review` panel도 추가했다.
- 다음에는 사용자가 checklist 기준으로 UI / registry / 문서 흐름을 QA한다.

## 한 줄 정리

Phase 25는 좋은 백테스트 결과를 바로 투자로 넘기지 않고,
paper / watchlist / hold / re-review로 관리하는 실전 전 운영판을 만드는 단계다.
