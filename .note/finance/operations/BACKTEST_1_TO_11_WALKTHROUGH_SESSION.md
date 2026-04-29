# Backtest Walkthrough Session

## 목적

이 문서는 Phase 30 QA 문서가 아니다.

사용자가 실제 후보 포트폴리오 하나를 들고,
`1단계 데이터 최신화`부터 `Portfolio Proposal / Live Readiness 경계`까지
프로그램을 어떻게 읽고 넘어가는지 익히는 별도 실습 기록이다.

## 관리 기준

- 이 문서는 `.note/finance/phase30/*` 문서를 갱신하지 않기 위한 별도 기록장이다.
- 실습 중 나온 질문, 해석, UI 보조 기능, 다음 확인 항목은 이 문서에 모은다.
- Phase 문서는 특정 phase의 구현 / QA 범위가 바뀔 때만 수정한다.
- 일반 Guide나 Real-Money UI가 바뀐 경우에는 앱 코드와 code analysis 문서에 기록하고,
  실습 맥락은 이 문서에 따로 남긴다.

## 현재 실습 후보

| 항목 | 값 |
|---|---|
| 후보 이름 | `GTAA Balanced Top-2` |
| Registry ID | `gtaa_real_money_balanced_top2_ief_20260418` |
| Strategy family | `GTAA` |
| Tickers | `SPY, QQQ, GLD, IEF` |
| Top Assets | `2` |
| Rebalance Interval | `4` |
| Score Horizons | `1M / 3M` |
| Trend Filter Window | `200` |
| Fallback Mode | `defensive_bond_preference` |
| Defensive Tickers | `TLT, IEF, LQD, BIL` |
| 실습상 4단계 상태 | `Promotion != hold`, `Deployment != blocked`, 핵심 blocker 없음 |

이 후보는 4단계 `Hold면 먼저 막히는 항목 해결`을 통과한 예시로 사용한다.
이는 투자 승인이나 주문 지시가 아니라,
5단계 Compare에서 다른 후보와 비교해 볼 수 있다는 뜻이다.

### Interval / Rebalance Interval 읽는 법

현재 walkthrough의 공통 실행 option은 `month_end`다.
이 경우 `Interval` 또는 `Rebalance Interval`은 주 단위가 아니라
월말 데이터 row를 몇 개마다 사용할지 정하는 값이다.

| 입력값 | `month_end` 기준 의미 | 실습에서 주의할 점 |
|---|---|---|
| `1` | 매월 리밸런싱 / 매월 신호 갱신 | 대략 4주 cadence로 보려면 이 값을 쓴다 |
| `4` | 4번째 월말 row마다 리밸런싱 / 신호 갱신 | 4주가 아니라 대략 4개월 cadence다 |
| `12` | 12번째 월말 row마다 리밸런싱 | 연 1회 cadence다 |

따라서 `Equal Weight Same Universe`를 말 그대로 4주 / 월간 리밸런싱 benchmark로 쓰려면
`Rebalance Interval = 1`이 맞다.
다만 현재 실습 후보인 `GTAA Balanced Top-2` registry 계약은 `Interval = 4`이므로,
후보의 cadence를 그대로 맞춘 Compare smoke에서는 Equal Weight도 `Rebalance Interval = 4`로 실행했다.

### Compare에서 interval을 꼭 맞춰야 하나

원칙은 "무엇을 비교하려는가"에 따라 다르다.

| 비교 목적 | interval 처리 | 해석 |
|---|---|---|
| 같은 cadence에서 전략 로직 차이를 비교 | 가능하면 같은 interval로 맞춘다 | 이번 GTAA 실습 smoke처럼 GTAA, Equal Weight, GRS, Risk Parity를 모두 `4`로 둔 경우 |
| 후보의 실제 운용 계약끼리 비교 | 각 후보의 원래 interval을 유지할 수 있다 | 단, 결과 차이에 strategy logic뿐 아니라 cadence 차이도 섞였다고 표시해야 한다 |
| 월간 benchmark와 비교 | benchmark는 `1`을 쓸 수 있다 | `option=month_end`에서 `1`은 매월 / 대략 4주 cadence다 |

5단계에서 처음 후보를 확인할 때는 보통
기간, timeframe, option, universe, Real-Money / guardrail 해석 기준을 먼저 맞춘다.
그 다음 interval은 아래 둘 중 하나로 선택한다.

- **cadence-matched compare**:
  후보가 `Interval = 4`라면 비교 전략도 `4`로 맞춰 전략 로직 차이를 본다.
- **benchmark compare**:
  Equal Weight를 "월간 시장 기준"으로 두고 싶다면 `Rebalance Interval = 1`을 쓴다.
  이때는 후보와 benchmark의 cadence가 다르다고 Review Note에 남긴다.

## 이 세션에서 정리한 질문과 답

### Risk-Off 후보군 해석

`Risk-Off=defensive_bond_preference`는 `Risk-Off Contract`의 fallback 방식이다.
공격 후보가 trend filter에 막히거나 risk-off 상태가 되면,
방어 후보 중 사용할 수 있는 ticker로 해당 슬롯을 채우려는 규칙이다.

중요한 점은 `Defensive Tickers`에 적었다고 해서 자동으로 GTAA universe가 넓어지지는 않는다는 것이다.
현재 설정은 다음처럼 읽는다.

| 입력 | 값 |
|---|---|
| GTAA Tickers | `SPY, QQQ, GLD, IEF` |
| Defensive Tickers | `TLT, IEF, LQD, BIL` |
| 실제 usable defensive 후보 | `IEF` |

즉 현재 run에서는 두 목록의 교집합인 `IEF`만 실제 방어 fallback 후보로 쓸 수 있다.
`TLT`, `LQD`, `BIL`도 실제 fallback 후보로 쓰려면 GTAA Tickers에도 함께 포함해야 한다.

### 후보가 2개면 비중은 어떻게 되나

`Top Assets = 2`이면 최종 통과 슬롯은 2개다.
두 후보가 모두 통과하면 기본적으로 각각 50%씩 구성된다.
한 후보만 통과하고 다른 슬롯이 trend filter에 막히면,
막힌 슬롯은 usable defensive fallback 후보로 대체되거나 현금으로 남는다.

예를 들어 최종 후보가 `IEF`, `QQQ` 두 개로 살아남으면 50% / 50%로 읽는다.
반대로 `IEF`는 살아남고 `QQQ`만 막혔는데 usable fallback도 `IEF`뿐이면,
이미 보유 후보에 들어간 `IEF`를 한 번 더 중복해서 채우지는 않는다.
그때 남는 슬롯은 현금으로 남는다.

### 4단계에서 5단계로 넘어가는 최소 기준

4단계 통과는 live trading approval이 아니다.
`Hold 해결`을 마치고 5단계 Compare로 넘겨도 되는지를 보는 기준이다.

최소 기준:

- `Promotion Decision != hold`
- `Deployment Readiness / Deployment Status != blocked`
- 핵심 blocker 없음

Real-Money의 `5단계 Compare 진입 평가`는 이 판단을 10점 척도로 보조한다.
`8.0 / 10` 이상이면 깔끔한 Compare 진입으로 읽고,
8점 미만이어도 위 세 조건이 만족되면 조건부로 Compare에는 넘길 수 있다.
위 세 조건 중 하나라도 깨지면 점수와 무관하게 4단계에서 먼저 멈춘다.

### 5단계 Compare는 무엇을 확인하나

5단계는 좋은 백테스트 하나를 바로 후보 registry에 넣는 단계가 아니다.
같은 기간 / 같은 Real-Money 해석 기준에서 다른 후보와 비교해도 계속 볼 만한지 확인하는 단계다.

#### 비교할 만한 대상은 어떻게 고르나

5단계 Compare가 의미 있으려면 비교 대상은 "아무 전략"이면 안 된다.
현재 확인 중인 후보와 같은 투자 문제를 풀거나,
후보의 약점 / 대체 가능성 / 단순 기준 대비 우위를 확인할 수 있어야 한다.

| 비교 대상 역할 | 왜 필요한가 | 예시 |
|---|---|---|
| Naive baseline | 복잡한 전략을 쓸 이유가 있는지 확인 | 같은 universe Equal Weight |
| Market benchmark | 시장 노출만 들고 가는 것보다 나은지 확인 | SPY, 60/40, AGG / BIL 조합 |
| 가까운 대안 전략 | 비슷한 목적을 다른 방식으로 푼 전략보다 나은지 확인 | GTAA vs Global Relative Strength |
| 위험 기준 대안 | 수익이 좋아도 낙폭 / 변동성 대비 납득되는지 확인 | Risk Parity Trend, 방어형 allocation |
| 기존 강한 후보 | 이미 남아 있는 후보보다 새 후보를 추가할 이유가 있는지 확인 | Current Candidate Registry의 active 후보 |

좋은 비교군의 조건:

- 같은 투자 문제를 풀어야 한다.
- 기간, timeframe, option은 먼저 맞춘다.
- universe, cadence, 거래비용, risk-off 조건이 다르면 그 차이를 Review Note에 남긴다.
- 일부러 약한 strawman만 두지 않는다.
- 최소 하나는 단순하고 강한 기준이어야 한다.

GTAA 실습에서는 아래 비교가 의미 있다.

- `Equal Weight Same Universe`: 같은 ETF를 그냥 균등 보유했을 때보다 GTAA가 나은지 확인
- `Global Relative Strength`: 비슷한 momentum 계열 ETF 전략보다 GTAA가 나은지 확인
- `Risk Parity Trend`: 더 위험 균형적인 접근보다 GTAA의 수익 / 낙폭 조합이 납득되는지 확인
- 필요하면 `SPY` 또는 `60/40`: 아주 단순한 시장 기준보다 이 전략을 쓸 이유가 있는지 확인

상황 예시:

현재 확인 중인 전략이 `GTAA Balanced Top-2`라고 하자.
이 전략은 ETF tactical allocation 후보이므로,
비교군은 같은 ETF를 더 단순하게 보유하는 방법,
비슷한 momentum 방식,
더 위험 균형적인 접근,
그리고 단순 시장 benchmark를 함께 두면 좋다.

| 비교 대상 | 설정 예 | 왜 비교하나 | 통과 해석 |
|---|---|---|---|
| `Equal Weight Same Universe` | `SPY, QQQ, GLD, IEF`, 후보와 같은 cadence | 같은 ETF를 그냥 균등 보유하는 것보다 GTAA를 쓸 이유가 있는지 확인 | 수익 / End Balance가 우위이고 MDD도 과도하게 나빠지지 않으면 기본 근거가 생김 |
| `Global Relative Strength` | `SPY, QQQ, GLD, IEF`, Top 2, 같은 score horizon | 비슷한 momentum ETF 전략보다 GTAA 구조가 나은지 확인 | 성과가 더 좋거나, 성과가 비슷해도 낙폭 / 안정성이 더 납득되면 근거가 생김 |
| `Risk Parity Trend` | 기본 Risk Parity universe, 후보와 같은 cadence | 위험 균형형 접근보다 GTAA의 수익 / 낙폭 교환이 납득되는지 확인 | MDD가 더 크더라도 수익 보상이 충분하거나, MDD도 함께 우위면 강한 근거 |
| `SPY` 또는 `60/40` | 단순 market benchmark 또는 주식/채권 혼합 benchmark | 아주 단순한 시장 노출보다 전략을 운영할 이유가 있는지 확인 | 복잡한 tactical 전략을 쓸 만큼 risk-adjusted 근거가 설명되어야 함 |

이 예시에서 비교 대상 하나만 이기는 것이 목표는 아니다.
각 비교 대상 앞에서 후보의 역할을 말할 수 있어야
6단계 Candidate Packaging으로 넘길 근거가 생긴다.

비교 대상이 형편없는 전략뿐이면 5단계는 통과 의식이 된다.
따라서 5단계의 핵심은 Compare 버튼을 누르는 것이 아니라,
`비교할 만한 대상`을 고르고 그 앞에서도 후보를 남길 이유가 있는지 설명하는 것이다.

#### 4단계에서 바로 6단계로 가도 되나

기술적으로는 가능하다.
`Latest Backtest Run`이나 `History`에서 single run을 바로 `Candidate Packaging` 초안으로 보낼 수 있기 때문이다.
다만 이 경우는 `single-run draft`로 보고,
Review Note에 `Compare 미실행 / 상대 근거 pending`을 남겨야 한다.

각 기준이 어디에서 확인되는지 나누면 다음과 같다.

| 6단계 진입 기준 | Single run만으로 확인 가능한가 | Compare가 필요한 이유 |
|---|---|---|
| Data Trust | 가능 | compare에서는 다른 전략과 같은 기간 / 같은 데이터 조건인지 한 번 더 확인 |
| Real-Money Gate | 가능 | compare 이후에도 blocker가 다시 나타나지 않는지 확인 |
| Compare Run | 불가능 | 여러 후보를 같은 설정 묶음으로 실제 실행했는지 확인하는 기준 |
| Relative Evidence | 제한적 | 후보가 benchmark / 대안 대비 왜 남아야 하는지 설명하려면 비교군이 필요 |

따라서 5단계는 "Candidate Packaging 초안 생성의 기술적 필수 조건"은 아니지만,
`Current Candidate Registry`, `Pre-Live Review`, `Portfolio Proposal`로 이어질 후보라면
거치는 것을 기본 원칙으로 둔다.

예외적으로 아래 상황에서는 4단계에서 바로 6단계로 넘어갈 수 있다.

- 좋은 single run을 잊지 않기 위해 후보 초안만 먼저 남기는 경우
- 이미 과거에 같은 후보군 / 같은 benchmark로 비교한 근거가 있고, 이번 run은 갱신 확인인 경우
- operator가 `compare_pending` 상태로 Review Note를 남기고 나중에 5단계를 보완하기로 한 경우

반대로 신규 전략을 실제 후보로 남기거나, registry append / Pre-Live / Portfolio Proposal로 이어가려면
5단계 Compare에서 최소한 benchmark 성격 후보 하나와 비교하는 것이 안전하다.

신규 전략을 처음 분석하는 경우의 기본 경로는 `Candidate Review > 보조 도구: Send Candidates To Compare`가 아니다.
`Candidate Review > 보조 도구: Send Candidates To Compare`와 `Load Recommended Candidates`는 이미
`CURRENT_CANDIDATE_REGISTRY`에 저장된 대표 후보를 다시 불러오는 quick re-entry 도구다.
아직 registry에 없는 신규 전략이라면 이 경로로 시작하면 안 된다.

신규 전략의 5단계 기본 경로:

1. 4단계까지 통과한 `Single Strategy` 결과의 설정을 기준 후보 계약으로 본다.
2. `Backtest > Compare & Portfolio Builder`로 직접 이동한다.
3. `Strategies`에서 신규 전략의 strategy family와 비교 기준 1~3개를 고른다.
4. `Compare Period & Shared Inputs`를 4단계 single run과 같은 기간 / timeframe / option으로 맞춘다.
5. 신규 전략의 strategy-specific box에서 universe, top, interval, score horizon, trend filter,
   risk-off, Real-Money Contract, guardrail 같은 세부 설정을 single run과 동일하게 복사한다.
6. 비교 기준은 목적에 맞게 고른다. 예를 들어 benchmark 성격의 Equal Weight,
   더 방어적인 대안, 더 공격적인 대안, 또는 기존 대표 후보를 둔다.
7. `Run Strategy Comparison`을 실행하고 Summary Compare, Compare Data Trust Snapshot,
   Real-Money / Guardrail Scope, Focused Strategy를 확인한다.

주의:

- `Load Recommended Candidates`는 신규 전략을 자동으로 포함하지 않는다.
- 이 버튼은 이미 registry에 active 상태로 기록된 대표 후보 묶음을 불러오는 기능이다.
- 현재 compare form은 같은 strategy family 후보를 여러 개 동시에 넣는 데 제한이 있다.
  같은 family의 파라미터 변형끼리 비교하려면 각각 single run / history 결과를 따로 보고,
  한 후보를 기준으로 다른 family 또는 benchmark 성격 후보와 먼저 비교한다.

통과 기준:

- Compare run이 2개 이상 전략으로 정상 실행된다.
- 기준 후보의 Data Trust가 해석 가능한 상태다.
- 기준 후보의 Real-Money gate가 `Promotion != hold`, `Deployment != blocked`, 핵심 blocker 없음 상태다.
- 후보가 목적에 맞는 상대 우위를 설명할 수 있다.
- 다음 단계에서 어떤 후보 역할로 Candidate Packaging에 넘길지 말할 수 있다.

화면에서는 Compare 결과 상단의 `6단계 Candidate Packaging 진입 평가`를 먼저 본다.
이 박스는 10점 만점으로 다음 네 가지를 합산한다.

| 기준 | 배점 | 의미 |
|---|---:|---|
| Compare Run | 2점 | 2개 이상 전략이 정상 비교됐는지 |
| Data Trust | 2점 | 선택 후보의 기간 / 가격 최신성 / 제외 ticker가 해석 가능한지 |
| Real-Money Gate | 3점 | 4단계 blocker가 Compare 이후에도 다시 나타나지 않았는지 |
| Relative Evidence | 3점 | CAGR, End Balance, MDD, Sharpe 중 설명 가능한 상대 근거가 있는지 |

Data Trust는 점수를 `6.4` 같은 값으로 강제로 cap하지 않고,
`OK / WARNING / BLOCKED` gate로 따로 표시한다.
요청 종료일과 실제 결과 종료일이 1-2일 정도 어긋나는 경우는 보통 warning으로 두고,
Candidate Packaging으로 넘길 때 Review Note에 남긴다.
가격 최신성 error나 결과 기간이 크게 비는 경우는 blocked로 보고 Compare에서 먼저 재확인한다.

점수 해석:

- `8.0 / 10` 이상: 6단계 Candidate Packaging 진행 가능
- `6.5 / 10` 이상: 조건부 진행 가능. Review Note에 약점과 확인 항목을 남긴다
- 그 아래: 5단계 Compare에서 비교 기준, 설정, Data Trust, Real-Money blocker를 다시 확인한다

통과 또는 조건부 통과 상태라면 `Send Selected Strategy To Candidate Packaging`으로 6단계에 보낼 수 있다.
이 버튼은 registry 저장이나 Pre-Live 승인이 아니라 `Candidate Review > 1. Draft 확인 / Review Note 저장`으로 보내는 버튼이다.

현재 실습에서는 `GTAA Balanced Top-2`를 신규 후보처럼 Compare form에 직접 재현하고,
benchmark 성격의 Equal Weight, momentum 대안인 Global Relative Strength,
선택적으로 risk-balanced 대안인 Risk Parity Trend와 비교한 뒤 Candidate Packaging으로 넘길지 판단한다.

### 현재 실습용 Compare 구성

`GTAA Balanced Top-2`를 신규 후보처럼 직접 Compare form에 재현해서 테스트한다.

공통 설정:

| 항목 | 값 |
|---|---|
| Start Date | `2016-01-29` |
| End Date | `2026-04-27` |
| Timeframe | `1d` |
| Option | `month_end` |

선택 전략:

| 역할 | Strategy | 설정 |
|---|---|---|
| 기준 후보 | `GTAA` | Manual tickers `SPY, QQQ, GLD, IEF`, Top `2`, Interval `4`, Score Horizons `1M / 3M`, Trend Filter `200`, Risk-Off `Defensive Bond Preference`, Defensive Tickers `TLT, IEF, LQD, BIL` |
| benchmark 성격 | `Equal Weight` | Manual tickers `SPY, QQQ, GLD, IEF`, Rebalance Interval `4`로 후보 cadence를 맞춤. 월간 / 4주 benchmark가 목적이면 `1` |
| momentum 대안 | `Global Relative Strength` | Manual tickers `SPY, QQQ, GLD, IEF`, Cash / Defensive Ticker `IEF`, Top `2`, Interval `4`, Score Horizons `1M / 3M`, Trend Filter `200` |
| risk-balanced 대안 | `Risk Parity Trend` | 기본 `Risk Parity Universe`, Rebalance Interval `4`, Vol Window `6` |

처음 실습이 너무 느리면 `Risk Parity Trend`를 제외하고,
`GTAA`, `Equal Weight`, `Global Relative Strength` 세 개만 먼저 비교한다.

### 2026-04-29 실습용 Compare smoke 결과

아래 결과는 위 구성을 `.venv` runtime에서 직접 실행해 확인한 값이다.
UI에서 다시 실행할 때 DB 상태나 end date가 달라지면 숫자는 달라질 수 있다.

| 역할 | Strategy | CAGR | MDD | End Balance | Promotion | Deployment |
|---|---|---:|---:|---:|---|---|
| 기준 후보 | `GTAA Balanced Top-2` | `17.88%` | `-8.39%` | `53,876.9` | `real_money_candidate` | `paper_only` |
| benchmark 성격 | `Equal Weight Same Universe` | `11.85%` | `-21.26%` | `31,491.0` | `-` | `-` |
| momentum 대안 | `Global Relative Strength Same Universe` | `1.05%` | `-22.45%` | `11,133.4` | `hold` | `blocked` |
| risk-balanced 대안 | `Risk Parity Trend Default Universe` | `1.43%` | `-33.07%` | `11,537.3` | `hold` | `blocked` |

`GTAA`를 6단계 후보로 선택했을 때 smoke 기준 Draft Score는 `9.0 / 10`,
판정은 `6단계 Candidate Draft 조건부 진행 가능`이었다.
조건부가 된 이유는 Review Note에 같이 남길 warning이 1개 있었기 때문이다.

## 6단계 Candidate Packaging 흐름 재정의

사용자 질문에 따라 기존 6 / 7 / 8단계는 하나의 사용자-facing 단계로 다시 묶는다.

이 구간은 전략을 다시 검증하는 단계가 아니다.
4단계와 5단계에서 확인한 후보를 Pre-Live Review가 읽을 수 있는 형태로 포장하는 단계다.
즉, 좋은 백테스트 결과를 `Review Note`, `Current Candidate Registry row`, `Pre-Live route`까지 이어지는 하나의 후보 패키지로 만드는 과정이다.

| 단계 | 이름 | 하는 일 | 통과 기준 |
|---|---|---|---|
| 6단계 | `Candidate Packaging` | Draft 확인, Review Note 저장, registry 저장, Pre-Live route 확인을 한 화면에서 순서대로 처리 | `Candidate Packaging 종합 판단`의 Route가 `PRE_LIVE_READY`면 7단계 Pre-Live로 진행 |
| 7단계 | `Pre-Live 운영 점검` | paper tracking / watchlist / hold / re-review 같은 운영 상태를 저장 | `Save Pre-Live Record`로 운영 기록 저장 |
| 8단계 | `Portfolio Proposal` | 후보 묶음을 목적, 비중, 운영 상태와 함께 제안 초안으로 묶음 | proposal이 후보 조합을 설명하고 live approval과 분리되어 있음 |

Candidate Packaging 안에서 확인하는 데이터는 아래처럼 나뉜다.

| 구성요소 | 확인하는 데이터 | 왜 필요한가 |
|---|---|---|
| Draft 확인 | 후보 이름, source, result snapshot, Data Trust, Real-Money signal, settings snapshot | 이 후보가 어떤 실행에서 왔고 재현 가능한지 확인 |
| Review Note | Review Decision, Operator Reason, Next Action, Review Date | 사람이 왜 이 후보를 남기는지 나중에 읽을 수 있게 함 |
| Registry 저장 | Current / Near Miss / Scenario / Stop 범위, Record Type, registry id, 중복 저장 여부 | 후보를 machine-readable JSON row로 남기되 역할을 잘못 부여하지 않게 함 |
| Pre-Live route | Registry identity, result, contract, review context, Real-Money signal, route | Pre-Live로 보낼 후보인지, Compare로 돌아갈 후보인지 결정 |

이 단계의 시각 장치는 세 군데에 있다.

| 위치 | 시각 장치 | 의미 |
|---|---|---|
| `1. Draft 확인 / Review Note 저장` | `Candidate Packaging 저장 준비` | Review Note로 저장 가능한 초안인지 확인 |
| `2. Registry 저장` | `Registry 후보 범위 판단` | Current / Near Miss / Scenario / Stop 중 어디까지 남길지 확인 |
| `3. Pre-Live 진입 평가` | `Candidate Packaging 종합 판단` | `PRE_LIVE_READY`, `COMPARE_REVIEW_READY`, `BOARD_HOLD` route 확인 |

### Candidate Packaging에서 다음 단계로 가는 조건

7단계 Pre-Live로 넘어가려면 최종 route가 `PRE_LIVE_READY`여야 한다.

| Route | 의미 | 다음 행동 |
|---|---|---|
| `PRE_LIVE_READY` | `current_candidate`이고 Real-Money gate가 `hold/blocked`가 아니며, result / contract / review context가 남아 있음 | 7단계 `Pre-Live Review`에서 paper tracking, watchlist, hold 같은 운영 상태를 저장 |
| `COMPARE_REVIEW_READY` | `near_miss` 또는 `scenario`로 읽히며, 비교에 다시 넣을 만큼 result / contract / review context가 있음 | Compare Picker에서 비교할 다른 후보를 추가한 뒤 다시 비교 |
| `BOARD_HOLD` | 후보 row의 역할, 성과 snapshot, 설정 snapshot, Real-Money signal, 판단 메모 중 일부가 부족함 | Candidate Packaging 안에서 registry row 또는 Review Note를 보강 |

같은 Review Note를 이미 append했다면, 두 번째부터는 기본적으로 저장 버튼을 막는다.
`CURRENT_CANDIDATE_REGISTRY.jsonl`은 append-only라서 반복 클릭하면 새 revision이 추가될 수 있지만,
Saved Candidate Board는 같은 `registry_id`의 latest row만 보여주므로 화면 변화가 작게 보일 수 있다.
의도적으로 같은 Review Note를 새 revision으로 남겨야 할 때만
`같은 Review Note를 새 registry revision으로 다시 저장` 체크박스를 켠다.

## 이 세션에서 추가된 일반 UI / Guide 보조 기능

아래 항목은 Phase 30 QA 항목이 아니라,
사용자가 walkthrough를 따라가며 판단하기 쉽게 만든 일반 보조 기능이다.

| 위치 | 추가 내용 | 목적 |
|---|---|---|
| `Reference > Guides` | `핵심 개념 가이드`, 단계 실행 흐름, `단계 통과 기준`, `문서와 파일` 묶음으로 재정리 | 실습 중 필요한 설명과 stop/go 기준을 한 화면에서 더 쉽게 찾게 함 |
| `Reference > Guides > GTAA Risk-Off 후보군 보는 법` | defensive ticker와 GTAA universe의 교집합 설명 | fallback 후보를 잘못 읽지 않게 함 |
| `Reference > Guides > 단계 통과 기준` | 4->5, 5->6, 6->7 기준과 Candidate Packaging 통합 기준 | 단계형 흐름과 stop/go 기준을 분리 |
| `Backtest 결과 > Real-Money > 현재 판단 > 5단계 Compare 진입 평가` | 10점 만점 readiness box | Checklist 상세를 보기 전에 Compare 진입 가능성을 빠르게 확인 |
| `Backtest > Compare & Portfolio Builder > Strategy Comparison` | 6단계 Candidate Packaging 진입 평가 | Compare 이후 Candidate Packaging으로 넘길 수 있는지 점수로 확인 |
| `Backtest > Candidate Review > 1. Draft 확인 / Review Note 저장` | Candidate Packaging 저장 준비 box와 disabled save button | Draft가 저장 가능한 상태일 때만 Review Note를 저장하도록 함 |
| `Backtest > Candidate Review > 2. Registry 저장` | Registry 후보 범위 판단 box와 record type gate | Review Note를 Current / Near Miss / Scenario / Stop 중 어디까지 남길지 정하고 통과 시 같은 Candidate Packaging 안에서 append |
| `Backtest > Candidate Review > 2. Registry 저장` | 같은 Review Note의 중복 registry append 기본 차단 | Saved Candidate Board에는 latest row만 보여 반복 클릭이 무의미하게 보이는 문제를 방지 |
| `Backtest > Candidate Review > 3. Pre-Live 진입 평가` | Candidate Packaging 종합 판단 box | 저장된 후보가 Pre-Live로 갈지, Compare로 돌아갈지, Board에 보류될지 확인 |

## 다음 실습 시작점

현재 후보가 5단계 Compare를 통과했다면 다음 실습은 6단계 Candidate Packaging에서 시작한다.

확인할 것:

- `Send Selected Strategy To Candidate Packaging`을 누른 뒤 `Candidate Review > 1. Draft 확인 / Review Note 저장`으로 이동한다.
- 후보 이름 / source / result snapshot / Data Trust / Real-Money signal / settings snapshot이 들어왔는지 본다.
- `Review Decision`, `Operator Reason`, `Next Action`을 작성한다.
- `Candidate Packaging 저장 준비`가 저장 가능 상태인지 확인한다.
- `Save Candidate Review Note`를 눌러 Review Note를 저장한다.
- 저장 뒤 `2. Registry 저장`에서 Current / Near Miss / Scenario / Stop 범위를 확인한다.
- 범위 판단과 Record Type이 맞으면 같은 Candidate Packaging 안에서 `Append To Current Candidate Registry`를 누른다.
- `3. Pre-Live 진입 평가`에서 방금 저장한 후보의 Route를 확인한다.
- Route가 `PRE_LIVE_READY`면 `Open Selected Candidate In Pre-Live Review`로 7단계를 연다.
- Route가 `COMPARE_REVIEW_READY`면 Compare에서 비교할 후보를 추가해 다시 검토한다.
