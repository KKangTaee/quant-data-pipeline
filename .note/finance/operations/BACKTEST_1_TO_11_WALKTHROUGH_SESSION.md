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

통과 기준:

- Compare run이 정상 실행된다.
- 기준 후보의 Data Trust / Real-Money 신호가 깨지지 않는다.
- 후보가 목적에 맞는 상대 우위를 설명할 수 있다.
- 다음 단계에서 어떤 후보 역할로 Candidate Draft에 넘길지 말할 수 있다.

현재 실습에서는 `GTAA Balanced Top-2`를 기본 후보로 두고,
저변동 대안, 고수익 대안, 또는 benchmark 성격의 기준 후보와 비교한 뒤
Candidate Draft로 넘길 후보를 고른다.

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

- `GTAA Balanced Top-2`를 기준 후보로 둔다.
- 저변동 대안과 고수익 대안을 같은 화면에 올린다.
- 각 후보의 CAGR / MDD뿐 아니라 Data Trust, Promotion, Deployment, blocker를 함께 본다.
- 후보가 살아남으면 `Review As Candidate Draft`로 6단계에 넘긴다.
