# Backtest 1 To 11 Walkthrough Session

## 목적

이 문서는 Phase 30 QA 문서가 아니다.

사용자가 실제 후보 포트폴리오 하나를 들고,
`1단계 데이터 최신화`부터 `11단계 Portfolio Proposal / Live Readiness 경계`까지
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

신규 전략을 처음 분석하는 경우의 기본 경로는 `Candidate Review > Send To Compare`가 아니다.
`Candidate Review > Send To Compare`와 `Load Recommended Candidates`는 이미
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
- 다음 단계에서 어떤 후보 역할로 Candidate Draft에 넘길지 말할 수 있다.

화면에서는 Compare 결과 상단의 `6단계 Candidate Draft 진입 평가`를 먼저 본다.
이 박스는 10점 만점으로 다음 네 가지를 합산한다.

| 기준 | 배점 | 의미 |
|---|---:|---|
| Compare Run | 2점 | 2개 이상 전략이 정상 비교됐는지 |
| Data Trust | 2점 | 선택 후보의 기간 / 가격 최신성 / 제외 ticker가 해석 가능한지 |
| Real-Money Gate | 3점 | 4단계 blocker가 Compare 이후에도 다시 나타나지 않았는지 |
| Relative Evidence | 3점 | CAGR, End Balance, MDD, Sharpe 중 설명 가능한 상대 근거가 있는지 |

점수 해석:

- `8.0 / 10` 이상: 6단계 Candidate Draft 진행 가능
- `6.5 / 10` 이상: 조건부 진행 가능. Review Note에 약점과 확인 항목을 남긴다
- 그 아래: 5단계 Compare에서 비교 기준, 설정, Data Trust, Real-Money blocker를 다시 확인한다

통과 또는 조건부 통과 상태라면 `Send Selected Strategy To Candidate Draft`로 6단계에 보낼 수 있다.
이 버튼은 registry 저장이나 Pre-Live 승인이 아니라 `Candidate Review > Candidate Intake Draft`로 보내는 버튼이다.

현재 실습에서는 `GTAA Balanced Top-2`를 신규 후보처럼 Compare form에 직접 재현하고,
benchmark 성격의 Equal Weight, momentum 대안인 Global Relative Strength,
선택적으로 risk-balanced 대안인 Risk Parity Trend와 비교한 뒤 Candidate Draft로 넘길지 판단한다.

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
| benchmark 성격 | `Equal Weight` | Manual tickers `SPY, QQQ, GLD, IEF`, Rebalance Interval `4` |
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

## 이 세션에서 추가된 일반 UI / Guide 보조 기능

아래 항목은 Phase 30 QA 항목이 아니라,
사용자가 1~11단계 walkthrough를 따라가며 판단하기 쉽게 만든 일반 보조 기능이다.

| 위치 | 추가 내용 | 목적 |
|---|---|---|
| `Reference > Guides > GTAA Risk-Off 후보군 보는 법` | defensive ticker와 GTAA universe의 교집합 설명 | fallback 후보를 잘못 읽지 않게 함 |
| `Reference > Guides > 단계 통과 기준` | 4단계에서 5단계로 넘어가는 최소 기준 | 단계형 흐름과 stop/go 기준을 분리 |
| `Backtest 결과 > Real-Money > 현재 판단 > 5단계 Compare 진입 평가` | 10점 만점 readiness box | Checklist 상세를 보기 전에 Compare 진입 가능성을 빠르게 확인 |

## 다음 실습 시작점

현재 후보는 4단계 pass 예시로 둔다.
다음 실습은 5단계 Compare에서 시작한다.

확인할 것:

- `GTAA Balanced Top-2`의 single run 설정을 Compare form에 직접 재현한다.
- 비교 기준으로 Equal Weight, 다른 ETF 전략, 또는 이미 registry에 있는 대표 후보 중 목적에 맞는 것을 고른다.
- 각 후보의 CAGR / MDD뿐 아니라 Data Trust, Promotion, Deployment, blocker를 함께 본다.
- `6단계 Candidate Draft 진입 평가`에서 선택 후보의 점수와 막는 항목을 확인한다.
- 후보가 살아남으면 `Send Selected Strategy To Candidate Draft`로 6단계에 넘긴다.
