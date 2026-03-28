# Phase 5 Strategy Library And Risk Overlay Plan

## 목적

- Phase 4에서 정리된 strict annual family를 바탕으로,
  다음 단계의 연구/전략 확장 방향을 고정한다.
- 특히 현재 `Quality`, `Value`, `Quality + Value` strict 전략에 없는
  risk-management overlay를 별도 설계/구현 축으로 정리한다.
- 동시에 이 프로젝트를
  **직접 투자 판단에 참고 가능한 실전형 research environment**
  으로 끌어올리기 위한 운영 원칙도 같이 고정한다.

## Phase 4에서 넘겨받는 현재 상태

Phase 4 종료 시점 기준으로:
- unified Backtest UI가 존재한다
- price-only public 전략 4종이 동작한다
- factor/fundamental public 전략 4종이 동작한다
  - `Quality Snapshot`
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- strict annual family는
  - fast runtime
  - staged managed universe
  - selection history / selection frequency
  - stale-price preflight
  - quality / value / multi-factor candidate
  까지 갖춘 상태다

## 현재 strict factor 전략의 한계

현재 strict factor 전략군은 모두 다음 구조에 가깝다.

1. month-end snapshot factor 읽기
2. top-N 종목 선택
3. equal-weight 할당
4. 다음 rebalance일까지 그대로 보유

즉 현재는 아래 기능이 없다.

- intramonth risk-off
- 시장 급락 시 현금 전환
- `MA200` 하향 이탈 시 방어
- drawdown-triggered stop
- volatility targeting overlay
- defensive asset rotation

따라서 다음 phase에서는
**factor-selection layer와 risk-overlay layer를 분리해서 다루는 것**
이 핵심이다.

## Phase 5의 정식 방향

Phase 5는 다음 두 축을 같이 다룬다.

1. `Strategy Library And Comparative Research`
2. `Risk Overlay For Strict Factor Strategies`

즉 Phase 5는
strict annual family를 단순 후보 전략 모음에서
**연구 가능한 전략 라이브러리 + 확장 가능한 overlay 실험장**
으로 키우는 단계다.

추가로 Phase 5의 운영 원칙은
**“실전 투자 판단에 참고 가능한 수준의 투명성과 해석 가능성 확보”**
를 명시적 목표로 둔다.

관련 정책 문서:
- `.note/finance/phase5/PHASE5_PRACTICAL_INVESTMENT_READINESS_POLICY.md`

## 실전형 목표의 뜻

Phase 5에서 말하는 “실전형”은 아래를 뜻한다.

- stale price / factor coverage 이슈가 숨겨지지 않는다
- managed preset이 실제 usable universe에 가깝게 유지된다
- selection / overlay / cash fallback을 사용자가 읽을 수 있다
- 결과를 보고 실제 투자 판단에 참고할 수 있을 정도로
  데이터 상태와 전략 동작이 설명 가능하다

이는 자동매매 시스템을 바로 만든다는 뜻은 아니며,
우선순위는 아래에 더 가깝다.

- decision-support quality
- data freshness transparency
- interpretation quality
- managed universe reliability

## 핵심 작업 축

### A. strict family comparative research

- `Quality` / `Value` / `Quality + Value` 비교 기준 정리
- canonical preset / benchmark 정리
- compare 결과 읽기 강화
- strategy notes / interpretation 문서 보강

### B. risk overlay requirements

- 어떤 위험 신호를 허용할지 결정
- overlay가 month-end only인지 intramonth인지 결정
- cash / defensive asset / partial de-risk 중 어느 방식으로 갈지 결정
- point-in-time / look-ahead 위험을 다시 확인

### C. first overlay implementation set

현실적인 first set 후보:
- `Trend Filter Overlay`
  - 예: `Close < MA200`이면 현금 또는 defensive asset
- `Market Regime Overlay`
  - 예: benchmark regime 악화 시 exposure 축소
- `Drawdown / Volatility Guard`
  - 예: 최근 drawdown / realized vol 기준으로 risk budget 축소

### D. runtime / UI exposure

- overlay-enabled strict strategy wrapper 추가
- UI에서 overlay on/off와 핵심 파라미터 노출
- result table / meta에 overlay event 기록
- compare에서 overlay 유무 비교 가능하게 정리

### E. historical managed-universe policy

- strict managed preset은 **run-level static universe**를 유지한다
- stale symbol을 이유로
  selected end date 기준 run 전체에서 미리 교체하지 않는다
- 대신 각 rebalance date마다
  - 가격이 있는 종목
  - factor snapshot이 usable한 종목
  만 자연스럽게 후보로 남긴다
- `Price Freshness Preflight`는 계속 유지하되
  - 운영 경고 / 데이터 점검 용도
  - run-level exclusion / replacement 용도는 아님
- 필요하면 향후 별도 `investable now` 정책을 검토할 수 있지만,
  현재 Phase 5 기본값은 historical backtest 타당성이다

### F. carry-over expansion and polish from Phase 4

Phase 4 closeout 이후 사용자가 미리 요청한 다음 항목도
Phase 5에서 함께 다루는 편이 자연스럽다.

1. `Quarterly strict factor family`
   - 현재 strict factor public family는 annual snapshot 기준이다
   - 이후 quarterly statement shadow path를 별도 후보로 열 수 있다
   - 다만 annual보다 coverage / timing / freshness / runtime 부담이 커질 수 있으므로
     first overlay보다 한 단계 뒤에 두는 편이 안전하다

2. `Compare advanced-input parity for strict factor strategies`
   - 현재 compare 화면에서 price-only 전략 일부는 advanced override가 잘 열려 있지만,
     `Quality` / `Value` / `Quality + Value` strict 전략은
     strategy-specific advanced input 조절성이 아직 부족하다
   - 이 항목은 새로운 전략 연구라기보다
     compare UX consistency 보강에 가깝기 때문에
     Phase 5 초반 carry-over polish로 처리하는 것이 적절하다

## 추천 구현 순서

1. baseline comparative research 정리
2. compare advanced-input parity 보강
3. overlay requirements 문서 고정
4. first overlay 한 가지 선정
5. overlay runtime first pass 구현
6. strict family compare / interpretation 확장
7. historical managed-universe policy 고정
8. historical preset semantics + UI clarification
9. 이후 quarterly strict family 검토
10. second overlay 후보 검토

## first overlay 추천

현재 기준으로 가장 자연스러운 first overlay는:

- `Trend Filter Overlay`

이유:
- 이미 price-only 전략군에 `MA200` 기반 defensive logic 예시가 있다
- 사용자도 직관적으로 이해하기 쉽다
- factor-selection 전략 위에 얹기 좋은 구조다
- intramonth risk-off와 month-end-only overlay 중 두 방향으로 확장하기 쉽다

## 예상 public candidate 예시

- `Quality + Trend Filter (Strict Annual)`
- `Value + Trend Filter (Strict Annual)`
- `Quality + Value + Trend Filter (Strict Annual)`

이 단계에서는 기존 factor ranking을 버리는 것이 아니라,
기존 top-N selection 위에 risk overlay를 덧씌우는 방향으로 본다.

## 운영 / 연구 관점 체크포인트

- overlay가 snapshot factor timing과 충돌하지 않는지
- intramonth signal일 경우 price freshness 요구가 더 커지는지
- managed universe `300/1000`에서 runtime cost가 감당 가능한지
- stale symbol warning이 historical backtest 해석을 방해하지 않는지
- preset static universe와 rebalance-date filtering을 사용해도
  연구/실전 판단 목적에 충분한지
- compare/history에 overlay event를 어떻게 남길지
- quarterly strict path를 열 경우
  annual 대비 coverage depth와 freshness 요구가 얼마나 악화되는지
- compare advanced-input parity를 열 때
  공통 입력(`timeframe`, `option`)과 strategy-specific 입력을 어떻게 분리할지

## 완료 기준

Phase 5는 최소한 아래가 충족되면 첫 챕터 완료로 본다.

- strict factor baseline 비교 기준이 문서화되어 있음
- first risk overlay rule이 고정되어 있음
- overlay-enabled strict 전략 1종 이상이 구현되어 있음
- UI / compare / history에서 overlay 상태를 읽을 수 있음

## 현재 상태

- phase direction:
  - `confirmed`
- phase formal opening:
  - `opened`
- current implementation:
  - `first_chapter_completed`

## 현재 첫 챕터 진척

현재까지 완료된 것:

- strict family baseline comparative research 정리
- compare strict factor advanced-input parity first pass
- first overlay requirement 고정
- first overlay 선정
  - `month-end MA200 trend filter`
- overlay runtime / UI / history / interpretation first pass
- historical managed-universe policy 고정
- preflight + tooltip 기반 historical universe semantics 정리
- quarterly strict family review
- second overlay candidate review

현재 남은 핵심:

- next chapter에서 second overlay 착수 여부 확정
- quarterly strict family를 실제로 열 시점 확정
- project operating-model refresh를 먼저 수행할지 여부 확정
