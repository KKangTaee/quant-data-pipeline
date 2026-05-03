# Finance Term Glossary

## 목적
이 문서는 퀀트, 백테스트, 실전형 전략 문서에서 반복해서 나오는 용어를
한 곳에서 쉽게 다시 확인할 수 있도록 만든 공통 용어 사전이다.

앞으로 새 용어가 반복적으로 등장하면, 정의를 채팅에만 남기지 말고 이 문서에 누적한다.

## 사용 원칙
- 반복해서 쓰이는 용어만 넣는다.
- 각 용어는 아래 3가지를 기본으로 적는다.
  - `기본 설명`
  - `왜 사용되는지`
  - `예시 / 필요 상황`
- 문서마다 같은 설명을 길게 반복하기보다, 문서 안에는 짧은 요약을 두고 자세한 정의는 이 사전을 참고한다.

---

## Universe Contract

### 기본 설명
백테스트에서 "어떤 종목 집합을 어떤 규칙으로 후보로 삼을 것인가"를 정한 약속이다.

### 왜 사용되는지
같은 전략이라도 어떤 종목들을 후보로 넣느냐에 따라 결과가 크게 달라지기 때문이다.
그래서 전략 자체와 별개로 모집군 규칙을 명확히 분리해서 봐야 한다.

### 예시 / 필요 상황
- `Coverage 1000`을 쓴다고 해도
  - 현재 기준 1000개를 고정해서 쓰는지
  - 매 리밸런싱 날짜마다 그 시점 기준 1000개를 다시 뽑는지
  결과가 달라질 수 있다.

---

## Managed Static Research Universe

### 기본 설명
현재 시점 기준으로 정해진 종목 묶음을 run 전체에서 고정해서 사용하는 연구용 모집군 방식이다.

### 왜 사용되는지
빠르게 전략 아이디어를 비교하거나 프로토타입을 시험할 때 구현과 운영이 단순하기 때문이다.

### 예시 / 필요 상황
- `US Statement Coverage 1000`을 현재 기준으로 정해두고,
  과거 기간 전체를 같은 후보 집합으로 테스트할 때 사용한다.

---

## Historical Dynamic PIT Universe

### 기본 설명
리밸런싱 날짜마다 그 시점 기준으로 후보 종목 집합을 다시 계산하는 모집군 방식이다.

### 왜 사용되는지
실전 투자에 더 가까운 검증을 하려면, 과거 시점의 실제 후보군 변화가 반영되어야 하기 때문이다.

### 예시 / 필요 상황
- 2019년 1월 리밸런싱 때의 후보군과
  2024년 1월 리밸런싱 때의 후보군을 다르게 잡고 싶은 경우

---

## PIT / Point-In-Time

### 기본 설명
그 날짜에 실제로 알 수 있었던 정보만 사용한다는 뜻이다.

### 왜 사용되는지
나중에 알게 된 정보를 과거 투자 판단에 섞으면 백테스트가 과도하게 좋아질 수 있기 때문이다.

### 예시 / 필요 상황
- 2020년 3월 투자 판단을 할 때
  2020년 5월에 공개된 재무제표를 쓰면 안 된다.

---

## Look-Ahead Bias

### 기본 설명
과거 시점에서는 알 수 없었던 미래 정보를 실수로 사용해서 백테스트가 좋아 보이게 되는 왜곡이다.

### 왜 사용되는지
실전에서는 재현되지 않을 결과를 만드는 대표적인 오류이기 때문이다.

### 예시 / 필요 상황
- filing date보다 늦게 공개된 데이터를
  더 이른 월말 리밸런싱 계산에 써버리는 경우

---

## Survivorship Bias

### 기본 설명
지금까지 살아남은 종목들만 기준으로 과거를 테스트해서 결과가 좋아 보이는 왜곡이다.

### 왜 사용되는지
실제로는 과거에 상장폐지되거나 사라진 종목도 투자 대상이었을 수 있기 때문이다.

### 예시 / 필요 상황
- 현재 남아 있는 대형주만 들고 10년 전 전략을 검증하면,
  당시 실패 종목이 빠져서 결과가 왜곡될 수 있다.

---

## Universe Drift

### 기본 설명
시간이 지나면서 후보 종목 집합이 바뀌는 현상이다.

### 왜 사용되는지
시장가치, 상장 여부, 유동성, 커버리지 상태가 시간이 지나며 바뀌기 때문이다.

### 예시 / 필요 상황
- 어떤 종목은 2018년에는 top 1000이 아니었지만,
  2024년에는 top 1000 안에 들어올 수 있다.

---

## Prototype

### 기본 설명
아이디어와 동작 가능성을 먼저 확인하기 위한 초기 버전이다.

### 왜 사용되는지
모든 실전형 조건을 다 넣기 전에, 전략 로직과 데이터 흐름이 성립하는지 빨리 확인할 수 있기 때문이다.

### 예시 / 필요 상황
- `Strict Quarterly Prototype`은
  방향성은 맞지만 아직 실전형 계약이 완전히 붙지 않은 상태를 뜻한다.

---

## Research-Only

### 기본 설명
연구용으로는 쓸 수 있지만, 실전형 전략으로 아직 승격하지 않은 상태다.

### 왜 사용되는지
전략이 존재한다고 해서 바로 투자에 써도 된다는 뜻은 아니기 때문이다.

### 예시 / 필요 상황
- quarterly strict family는 현재 결과 해석과 비교는 가능하지만,
  아직 real-money candidate로 보지 않는다.

---

## Cadence

### 기본 설명
백테스트에서 리밸런싱과 factor 계산을 어떤 주기로 할지 정한 실행 리듬이다.

### 왜 사용되는지
같은 전략이라도 annual, quarterly, monthly처럼 주기가 달라지면
사용하는 데이터와 리밸런싱 날짜가 달라지고 결과 해석도 달라지기 때문이다.

### 예시 / 필요 상황
- `Strict Annual`은 연간 재무제표와 연간 리밸런싱 흐름에 가깝다.
- `Strict Quarterly`는 분기 재무제표와 더 잦은 업데이트를 반영하려는 흐름이다.

---

## Productionization

### 기본 설명
이미 동작하는 prototype 기능을 사용자가 반복해서 쓸 수 있는 제품 기능으로 다듬는 작업이다.

### 왜 사용되는지
한 번 실행되는 것과, 나중에 다시 불러오고 비교하고 저장해도 같은 의미로 재현되는 것은 다르기 때문이다.

### 예시 / 필요 상황
- quarterly strict family가 single strategy에서만 실행되는 수준을 넘어,
  compare, history, saved replay에서도 설정과 해석이 유지되도록 만드는 작업

---

## Alternate Cadence

### 기본 설명
annual 또는 quarterly 외에 추가될 수 있는 다른 실행 주기다.

### 왜 사용되는지
전략마다 가장 자연스러운 데이터 갱신 주기와 리밸런싱 주기가 다를 수 있기 때문이다.

### 예시 / 필요 상황
- 반기 리밸런싱
- 월간 리밸런싱
- annual factor를 쓰되 quarterly로 risk rule만 확인하는 혼합형 실행

---

## Hardening

### 기본 설명
프로토타입 기능에 실전형 제약과 해석 기준을 붙여 더 믿고 쓸 수 있게 만드는 작업이다.

### 왜 사용되는지
실전에서는 단순 수익률만으로 부족하고,
거래 비용, 유동성, guardrail 같은 조건이 추가로 필요하기 때문이다.

### 예시 / 필요 상황
- ETF 전략에
  - `Minimum Price`
  - `Transaction Cost`
  - `Benchmark`
  를 붙이는 작업

---

## Promotion

### 기본 설명
연구용 전략을 한 단계 더 높은 신뢰 수준의 전략으로 올리는 판단 과정이다.

### 왜 사용되는지
전략을 무작정 실전 투입하지 않고,
명확한 기준을 통과했을 때만 다음 단계로 올리기 위해서다.

### 예시 / 필요 상황
- `research-only` 전략이
  충분한 validation과 contract를 갖추면 `production candidate`가 될 수 있다.

---

## Investability Filter

### 기본 설명
실제로 매매 가능한 자산만 남기기 위한 최소 조건 필터다.

### 왜 사용되는지
백테스트 상으론 보이지만 실제로는 거래가 너무 어렵거나 비현실적인 자산을 걸러내기 위해서다.

### 예시 / 필요 상황
- 최소 가격 조건
- 거래량/유동성 조건
- 상장 기간 조건

---

## Rejected Slot Fill / Next-Ranked Eligible Fill

### 기본 설명
`Trend Filter` 때문에 raw top-N 중 일부가 탈락했을 때,
그 빈 슬롯을 현금으로 비워 두거나 survivor만 다시 가중하기 전에
랭킹의 다음 후보 중 trend를 통과하는 종목으로 먼저 채우는 방식이다.

### 왜 사용되는지
부분 탈락이 생길 때 cash drag가 너무 크면
`CAGR`가 빠르게 낮아질 수 있다.
그래서 “빈 슬롯을 그대로 둘 것인가”가 아니라
“같은 ranking universe 안에서 다음 후보로 메울 것인가”를
별도 contract로 분리해서 검증한다.

### 예시 / 필요 상황
- raw top-10 중 3개가 `Trend Filter`에 걸리면,
  다음 ranked 후보들 중 trend를 통과하는 이름으로
  그 3자리를 먼저 메운다.
- 그래도 채울 수 없으면 그때
  `partial cash retention` 또는 survivor reweighting이 남은 shortfall을 처리한다.

---

## Minimum Price

### 기본 설명
후보 자산의 가격이 너무 낮지 않도록 거는 최소 가격 조건이다.

### 왜 사용되는지
가격이 너무 낮은 자산은 스프레드가 넓거나,
체결이 불안정하거나, 실전에서는 예상보다 거래 품질이 나쁠 가능성이 커지기 때문이다.

### 예시 / 필요 상황
- `5.0`이라면:
  - 가격이 `5달러`보다 낮은 자산은 후보에서 제외하겠다는 뜻이다.
- penny stock처럼 너무 낮은 가격대 자산을 실전 후보에서 빼고 싶을 때 사용한다.

---

## Minimum History

### 기본 설명
전략이 어떤 자산을 후보로 인정하기 전에,
최소한 몇 개월 이상의 가격 이력이 있어야 하는지를 정하는 조건이다.

### 왜 사용되는지
이력이 너무 짧은 자산은 모멘텀, drawdown, benchmark 비교 같은 검토가 불안정해질 수 있기 때문이다.

### 예시 / 필요 상황
- `12M`이라면:
  - 최근 `12개월` 이상 가격 이력이 있는 자산만 후보로 보겠다는 뜻이다.
- 막 상장한 종목이나 ETF가 성과는 좋아 보여도,
  검증 구간이 너무 짧다면 보수적으로 제외하고 싶을 때 사용한다.

---

## Liquidity Clean Coverage

### 기본 설명
리밸런싱 행 중에서 유동성 제외가 발생하지 않은 비율이다.

### 왜 사용되는지
유동성 필터가 있다는 사실만으로는 부족하고,
실제로 전략이 얼마나 자주 유동성 제약에 막히는지를 알아야 하기 때문이다.

### 예시 / 필요 상황
- `95%`라면 리밸런싱 20번 중 19번은 유동성 제외 없이 지나간 것으로 볼 수 있다.
- `70%`라면 유동성 제약이 꽤 자주 발생하는 전략일 수 있다.

---

## Liquidity Policy

### 기본 설명
전략이 유동성 기준을 promotion 관점에서 얼마나 잘 만족하는지 요약한 상태값이다.

### 왜 사용되는지
유동성은 실전형 승격에서 중요한데,
그 상태를 `normal / watch / caution / unavailable`로 빠르게 읽을 수 있어야 하기 때문이다.

### 예시 / 필요 상황
- `normal`: 유동성 제외가 드물고 policy 기준을 충족함
- `watch`: 유동성 제외가 조금 잦아서 추가 검토가 필요함
- `caution`: 유동성 제외가 자주 발생해서 승격 보류가 맞음
- `unavailable`: 유동성 필터가 꺼져 있거나 판단 근거가 부족함

---

## Liquidity

### 기본 설명
원하는 시점에 자산을 너무 큰 가격 충격 없이 사고팔 수 있는 정도를 말한다.

### 왜 사용되는지
백테스트 숫자가 좋아도 실제로는 거래가 얇아서 원하는 가격에 체결하기 어려우면,
실전 성과가 크게 달라질 수 있기 때문이다.

### 예시 / 필요 상황
- 거래대금이 너무 적은 종목은
  소액 연구용으로는 보일 수 있어도 실전형 후보로는 보수적으로 봐야 한다.
- strict annual에서 `Min Avg Dollar Volume 20D`를 두는 이유도 이 때문이다.

---

## Min Avg Dollar Volume 20D

### 기본 설명
최근 `20`거래일 동안의 평균 거래대금을 뜻한다.  
보통 하루 거래량(`Volume`)에 가격(`Close`)을 곱해서 일별 거래대금을 만들고,
그 값을 최근 20거래일 평균으로 본다.

### 왜 사용되는지
주가가 높아 보여도 실제 거래대금이 너무 작으면,
원하는 시점에 사고팔 때 가격 충격이 커질 수 있다.  
그래서 이 값은 "이 종목이 실전에서 너무 얇지 않은가?"를 거르는
가장 단순한 유동성 필터로 쓰인다.

### 예시 / 필요 상황
- `5.0M`이라면:
  - 최근 20거래일 평균 하루 거래대금이 대략 `500만 달러` 이상인 종목만 후보로 보겠다는 뜻이다.
- `0.0M`이라면:
  - 유동성 필터를 사실상 끈 상태다.
  - 이 경우 product에서는 보통 `Liquidity Policy = unavailable`로 읽히고,
    승격용 유동성 검토를 제대로 하지 못한다.
- 값이 너무 높으면:
  - 후보가 과도하게 줄어들 수 있다.
- 값이 너무 낮으면:
  - 실전에서는 거래하기 불편한 종목까지 후보에 남을 수 있다.

---

## Validation

### 기본 설명
이 전략이 benchmark 대비로 봤을 때 최근 구간과 전체 구간에서 너무 불안정하지 않은지 점검하는 검토 단계다.

### 왜 사용되는지
절대 수익만 좋다고 끝이 아니라,
benchmark보다 얼마나 자주 뒤처지는지, drawdown이 과도한지, 최근 구간에서도 일관성이 있는지를 같이 봐야 실전 해석이 가능하기 때문이다.

### 예시 / 필요 상황
- `Underperformance Share`
  - rolling window 기준으로 benchmark보다 뒤처진 비율
- `Worst Rolling Excess`
  - 최근 구간 중 가장 나빴던 상대 성과
- `Validation Status = watch / caution`
  - 지금은 결과를 더 보수적으로 읽어야 함

---

## Validation Frame

### 기본 설명
여러 후보를 같은 조건에서 비교하기 위해 미리 고정해 두는 검증 기준표다.

쉽게 말하면 "이번 비교에서는 기간, universe, 후보 묶음, benchmark / guardrail, 결과 기록 방식을 이렇게 맞춰서 보자"라고 정한 약속이다.

### 왜 사용되는지
백테스트 결과는 설정이 조금만 달라도 달라진다.
기간이나 universe가 서로 다르면 결과 차이가 전략 때문인지, 설정 차이 때문인지 헷갈릴 수 있다.

그래서 중요한 후보를 다시 비교할 때는 먼저 validation frame을 고정하고,
그 안에서 current candidate와 대안을 나란히 본다.

### 예시 / 필요 상황
- `Phase 21`에서는 다음 조건을 같은 validation frame으로 고정했다.
  - 기간:
    - `2016-01-01 ~ 2026-04-01`
  - universe:
    - `US Statement Coverage 100`
    - `Historical Dynamic PIT Universe`
  - 후보 묶음:
    - `Value`, `Quality`, `Quality + Value` current anchor와 lower-MDD alternative
  - 결과 기록:
    - phase21 report
    - strategy backtest log
    - current candidate summary

---

## Portfolio-Level Candidate

### 기본 설명
전략 하나가 아니라 여러 전략을 정해진 비중으로 섞은 포트폴리오 후보다.

단순히 화면에서 weighted portfolio를 한 번 만든 결과가 아니라,
어떤 전략을 섞었는지, 어떤 비중을 썼는지, 날짜를 어떻게 맞췄는지,
저장 후 다시 실행해도 같은 결과가 나오는지까지 함께 남아 있어야 한다.

### 왜 사용되는지
실제 운용에서는 단일 전략 하나만 쓰기보다 여러 전략을 섞어 쓰는 경우가 많다.
하지만 기준 없이 조합만 늘리면 어떤 조합이 진짜 후보인지 알기 어려워진다.

그래서 portfolio-level candidate는 단일 전략 후보와 별도로,
source, weight, date alignment, replay, 해석이 함께 남은 재현 가능한 후보로 관리한다.

### 예시 / 필요 상황
- `Phase 21`의 `Value / Quality / Quality + Value = 33 / 33 / 34` weighted portfolio는
  workflow 재현성을 확인한 portfolio bridge였다.
- `Phase 22`에서는 이 결과를 바로 최종 후보로 승격하지 않고,
  portfolio-level candidate 기준에 맞춰 baseline 후보 pack으로 다시 볼지 검토한다.

---

## Portfolio Proposal

### 기본 설명
후보 여러 개를 하나의 포트폴리오 제안 초안으로 묶은 기록이다.

단순히 weighted portfolio 결과를 저장한 것이 아니라,
어떤 목적의 포트폴리오인지,
각 후보가 어떤 역할을 하는지,
비중을 왜 그렇게 주는지,
data trust / Real-Money / Pre-Live 상태와 미해결 blocker가 무엇인지까지 함께 남긴다.

### 왜 사용되는지
최종 목표는 단일 전략 후보를 많이 쌓는 것이 아니라,
사용자가 실제로 검토할 수 있는 포트폴리오 구성안과 가이드를 제시하는 것이다.

Portfolio Proposal은 단일 후보 registry와 live approval 사이에서,
후보 묶음의 목적, 비중, 위험 경계, 검토 근거를 사람에게 설명하기 위해 사용한다.

### 예시 / 필요 상황
- `core_anchor`, `diversifier`, `defensive_sleeve` 후보를 묶어 drawdown을 낮추는 포트폴리오 제안 초안을 만든다.
- proposal row에는 후보별 `target_weight`, `weight_reason`, `open_blockers`, `operator_decision`이 함께 남아야 한다.
- Phase 30에서는 `Backtest > Portfolio Proposal`에서 proposal draft를 만들고 `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append-only로 저장한다. `Monitoring Review`에서는 저장된 proposal의 blocker와 review gap을 다시 확인하고, `Pre-Live Feedback`에서는 proposal snapshot과 현재 Pre-Live 상태를 비교하며, `Paper Tracking Feedback`에서는 proposal 저장 당시 evidence snapshot과 현재 Pre-Live result snapshot의 CAGR / MDD 변화를 비교한다. 이 저장과 review는 live trading 승인이나 주문 지시와는 분리한다.

### Proposal Role 사용 기준
- `core_anchor`: 포트폴리오의 중심 후보. active weight가 있는 proposal에는 최소 1개가 필요하다.
- `return_driver`: 수익률 기여를 기대하는 공격 후보. core anchor 없이 이것만 있으면 Live Readiness 전에 차단된다.
- `diversifier`: core anchor와 다른 위험 원천을 섞어 변동성이나 drawdown을 낮추는 보조 후보.
- `defensive_sleeve`: 시장 악화나 risk-off 구간을 완충하기 위한 방어 후보.
- `satellite`: 작은 비중으로 특정 아이디어를 더하는 보조 후보.
- `watch_only`: 이번 proposal에서는 관찰만 하고 보통 active weight를 주지 않는 후보.

---

## Paper Tracking Feedback

### 기본 설명
Portfolio Proposal에 포함된 후보가 현재 paper tracking 상태에서 어떤 성과 snapshot을 갖는지 다시 읽는 보조 화면이다.

현재 구현에서는 별도 paper PnL 시계열을 계산하지 않고,
proposal 저장 당시의 `evidence_snapshot`과
최신 Pre-Live record의 `result_snapshot`에 있는 CAGR / MDD를 비교한다.

### 왜 사용되는지
proposal 저장 당시에는 좋아 보였던 후보라도,
paper tracking 중에 CAGR이 크게 낮아지거나 MDD가 더 깊어지면
live readiness 전에 다시 확인해야 한다.

그래서 Paper Tracking Feedback은 proposal이 현재 관찰 성과와 어긋나지 않는지 보는
운영 재확인 신호로 사용한다.

### 예시 / 필요 상황
- `paper_tracking` 상태가 아닌 component가 proposal에 active weight로 남아 있는지 확인한다.
- proposal 저장 당시 CAGR 28.0, MDD -20.0이던 후보가 최신 Pre-Live snapshot에서 CAGR 25.0, MDD -26.0으로 바뀌었다면 `worsened`로 읽는다.
- `stable_or_better`가 보여도 live approval이나 주문 가능 상태가 아니다. 최종 승인은 별도 Live Readiness / Final Approval phase에서 다룬다.

---

## Portfolio Bridge

### 기본 설명
compare에서 나온 여러 전략 결과를 weighted portfolio와 saved portfolio replay까지 이어보는 연결 검증이다.

쉽게 말하면 "전략 비교 결과를 실제 포트폴리오 조합으로 만들고, 저장 후 다시 실행해도 같은 결과가 나오나"를 확인하는 흐름이다.

### 왜 사용되는지
compare 결과가 좋아 보여도,
그 결과를 weighted portfolio로 만들고 저장 / 재실행할 수 없다면 실사용 후보로 관리하기 어렵다.

portfolio bridge는 최종 포트폴리오 후보를 고르는 단계라기보다,
후보를 만들 수 있는 workflow가 실제로 이어지는지 확인하는 단계다.

### 예시 / 필요 상황
- `Phase 21`에서 `Load Recommended Candidates -> Weighted Portfolio Builder -> Save Portfolio -> Replay Saved Portfolio` 흐름을 검증했다.
- saved replay가 exact match로 재현되면,
  그 다음 phase에서 portfolio-level candidate construction을 다룰 근거가 된다.

---

## Saved Portfolio Replay

### 기본 설명
저장해 둔 weighted portfolio 구성을 다시 불러와 같은 결과가 나오는지 확인하는 재현성 검증이다.

### 왜 사용되는지
포트폴리오 후보는 한 번 만든 화면 결과로 끝나면 안 된다.
나중에 다시 열어도 같은 전략, 같은 비중, 같은 기간, 같은 결과로 재현되어야 후보로 관리할 수 있다.

### 예시 / 필요 상황
- 저장된 portfolio를 `Replay Saved Portfolio`로 다시 실행했을 때
  `CAGR`, `MDD`, `End Balance`가 기존 결과와 맞는지 확인한다.
- 재현되지 않으면 그 조합은 후보가 아니라 일회성 실험으로 본다.

---

## Date Alignment

### 기본 설명
여러 전략 결과를 하나의 portfolio로 섞을 때,
각 전략의 날짜를 어떻게 맞출지 정하는 방식이다.

### 왜 사용되는지
전략마다 결과가 시작되는 날짜나 빠지는 날짜가 다를 수 있다.
날짜를 맞추는 방식이 다르면 portfolio 결과도 달라지므로,
portfolio-level candidate에는 date alignment가 반드시 기록되어야 한다.

### 예시 / 필요 상황
- `intersection`
  - 모든 전략 결과가 공통으로 존재하는 날짜만 사용한다.
  - 비교는 깔끔하지만, 사용 기간이 줄어들 수 있다.
- `union`
  - 가능한 날짜를 더 넓게 쓰지만, 빈 구간 처리 방식이 필요하다.

---

## Validation Policy

### 기본 설명
validation 결과를 실전형 승격 기준으로 해석하기 위한 정책 요약이다.

### 왜 사용되는지
validation 지표가 숫자로만 있으면 해석이 제각각 될 수 있어서,
"여기까지는 normal, 여기부터는 watch/caution" 같은 기준이 필요하기 때문이다.

### 예시 / 필요 상황
- `Max Underperformance Share`
  - benchmark보다 뒤처지는 구간이 이 비율보다 많으면 보수적으로 본다.
- `Min Worst Rolling Excess`
  - 최근 구간 중 가장 나빴던 상대 성과가 이 기준보다 더 나쁘면 caution으로 해석할 수 있다.

---

## Rolling Window

### 기본 설명
전체 기간을 한 번에 보지 않고,
일정 길이의 작은 평가 창을 한 칸씩 옮겨가며 반복해서 보는 구간이다.

### 왜 사용되는지
전체 CAGR이 좋아 보여도,
어떤 시기에는 benchmark보다 계속 약했을 수 있기 때문이다.

### 예시 / 필요 상황
- `12개월 rolling`이라면
  - `2016-01 ~ 2016-12`
  - `2016-02 ~ 2017-01`
  - `2016-03 ~ 2017-02`
  같은 식으로 창을 계속 밀어가며 비교한다.
- `Max Underperformance Share`, `Min Worst Rolling Excess`는 이 rolling 구간 개념을 기준으로 계산한다.

---

## Turnover

### 기본 설명
리밸런싱 때 포트폴리오를 얼마나 많이 바꿨는지 보여주는 비율이다.

### 왜 사용되는지
포트폴리오를 많이 바꿀수록 실제 거래 비용과 실행 난이도가 커지기 때문이다.

### 예시 / 필요 상황
- `1.0`에 가까우면 거의 전부 갈아탄 것에 가깝고,
  `0.1`이면 일부만 조정한 것으로 볼 수 있다.

---

## Transaction Cost

### 기본 설명
매매할 때 드는 비용을 추정해서 반영한 값이다.

### 왜 사용되는지
실전에서는 수수료, 슬리피지, 스프레드 같은 비용 때문에
백테스트 수익률보다 실제 성과가 낮아질 수 있기 때문이다.

### 예시 / 필요 상황
- turnover가 큰 전략은
  거래 비용을 반영하면 성과가 크게 줄 수 있다.
- `10 bps`는 대략 `0.10%` 비용을 뜻한다.
- 예를 들어 `1만 달러`를 거래할 때 `10 bps`를 쓰면,
  단순 계산 기준으로 약 `10달러`의 거래 비용을 가정하는 셈이다.

---

## Real-Money Contract

### 기본 설명
전략 폼의 `Advanced Inputs` 안에서,
실전형 승격과 배치 해석에 직접 연결되는 입력값 묶음이다.

### 왜 사용되는지
기본 백테스트 숫자만으로는
실제로 투자 가능한지, benchmark 대비 의미가 있는지,
거래가 현실적인지까지 판단하기 어렵기 때문이다.

### 예시 / 필요 상황
- 위치:
  - `Backtest > 전략 선택 > Advanced Inputs > Real-Money Contract`
- 이 안에서는 보통
  - investability filter
  - transaction cost
  - benchmark contract
  - promotion policy threshold
  - ETF operability 기준
  을 함께 본다.

---

## Real-Money 검증 신호

### 기본 설명
개별 백테스트 실행 결과에 붙는 실전 검토용 신호다.
거래비용, benchmark 비교, drawdown, 유동성, ETF 운용 가능성, promotion 상태 같은 항목을 보여준다.

### 왜 사용되는지
백테스트 수익률만 보고 전략을 좋다고 판단하면 위험하다.
Real-Money 검증 신호는 "이 결과를 실전 후보로 검토하기 전에 무엇을 조심해야 하는가"를 빠르게 보여준다.

### 예시 / 필요 상황
- `Backtest 결과 > Real-Money`
- `Promotion = real_money_candidate`
- `ETF 운용 가능성 = caution`
- `Deployment Readiness = paper_only`

### Pre-Live 운영 점검과의 차이
Real-Money 검증 신호는 **개별 실행의 진단 결과**다.
Pre-Live 운영 점검은 그 진단 결과를 받아
paper tracking, watchlist, 보류, 재검토를 어떻게 운영하고 기록할지 정하는 **운영 절차**다.
Pre-Live는 상태값만 저장하는 것이 아니라
`operator_reason`, `next_action`, `review_date`, `tracking_plan`을 함께 남긴다는 점이 핵심 차이다.

---

## Benchmark Ticker

### 기본 설명
전략 결과를 비교할 기준 ETF ticker다.

### 왜 사용되는지
절대 수익뿐 아니라,
"같은 기간에 그냥 benchmark를 들고 있었으면 어땠는가"를 같이 봐야
전략의 상대적 의미를 읽을 수 있기 때문이다.

### 예시 / 필요 상황
- `SPY`
  - 미국 주식 broad benchmark와 비교
- `TLT`
  - 장기채 benchmark와 비교

---

## Benchmark Contract

### 기본 설명
무엇을 benchmark로 해석할지 정하는 비교 계약이다.

### 왜 사용되는지
같은 `Benchmark Ticker`를 써도,
단일 ETF와 비교할지, 후보군 equal-weight와 비교할지에 따라
validation과 승격 해석이 달라지기 때문이다.

### 예시 / 필요 상황
- `ticker`
  - `SPY` 같은 기준 ETF와 직접 비교
- `candidate_universe_equal_weight`
  - 같은 후보군을 단순 균등 보유했을 때와 비교

---

## Candidate Universe Equal-Weight

### 기본 설명
같은 후보 universe 안에서 그 시점에 투자 가능했던 종목들을
그냥 동일 비중으로 담았다고 가정한 기준 benchmark다.

### 왜 사용되는지
`SPY` 같은 외부 ETF와 비교하는 것과는 다른 질문을 보기 위해서다.
즉, "같은 후보군 안에서 복잡한 ranking 전략을 쓰는 것이
그냥 고르게 사는 것보다 실제로 더 낫나?"를 확인할 수 있다.

### 예시 / 필요 상황
- strict annual quality/value 전략
  - `SPY`와 비교하면 시장 ETF 대비 성과를 보는 의미가 강하다
  - `Candidate Universe Equal-Weight`와 비교하면
    같은 후보군 안에서 단순 equal-weight보다 전략 selection이 더 나은지 볼 수 있다
- 화면에서 `SPY`가 같이 보일 때
  - 그것이 항상 benchmark 자체를 뜻하는 것은 아니다
  - `Candidate Universe Equal-Weight` 계약에서는 `SPY`가 guardrail/reference ticker로 남아 있을 수 있다

---

## Portfolio-Level Benchmark

### 기본 설명
여러 전략을 섞은 portfolio 후보를 비교할 때 쓰는 기준점이다.

단일 전략의 benchmark와 다르게,
portfolio-level benchmark는 "이 portfolio 조합이 다른 portfolio 조합보다 나은가"를 보기 위해 쓰는 경우가 많다.

### 왜 사용되는지
portfolio 후보는 여러 component strategy가 섞여 있기 때문에,
component마다 쓰던 benchmark를 그대로 하나로 합치면 해석이 꼬일 수 있다.

그래서 `Phase 22`에서는 portfolio 후보의 1차 benchmark를 `SPY`가 아니라
`phase22_annual_strict_equal_third_baseline_v1`으로 둔다.

### 예시 / 필요 상황
- equal-third baseline:
  - `Value / Quality / Quality + Value`를 각각 1/3씩 섞은 기준 portfolio
- weight alternative:
  - `25 / 25 / 50`이나 `40 / 40 / 20`이 baseline보다 나은지 비교할 때 사용

---

## Portfolio-Level Guardrail

### 기본 설명
portfolio 후보가 너무 위험하거나, 재현성이 없거나, 특정 component에 과도하게 쏠렸는지 보는 경고 기준이다.

### 왜 사용되는지
portfolio 후보는 단일 전략보다 좋아 보일 수 있지만,
실제로는 한 component가 대부분의 성과를 만들거나,
저장 후 replay가 안 되거나,
baseline보다 낙폭이 더 깊어지는 경우가 있다.

이런 경우를 숫자만 보고 지나치지 않기 위해 portfolio-level guardrail을 둔다.

### 예시 / 필요 상황
- saved replay가 재현되지 않으면 후보가 아니라 일회성 결과로 본다.
- MDD가 baseline보다 2~3%p 이상 깊어지면 `watch / caution`으로 읽는다.
- 한 component contribution이 50%를 넘으면 concentration risk를 따로 확인한다.

---

## Weight Alternative

### 기본 설명
같은 component strategy를 쓰되, 포트폴리오 안에서 각 component 비중만 다르게 준 대안 조합이다.

### 왜 사용되는지
equal-weight가 항상 최선은 아니다.
strongest component를 조금 더 키우거나, drawdown이 낮은 component를 더 키우면
수익 / 낙폭 / Sharpe tradeoff가 달라질 수 있다.

### 예시 / 필요 상황
- `quality_value_tilt`
  - `25 / 25 / 50`
  - strongest blended component를 더 키우는 조합
- `value_quality_defensive_tilt`
  - `40 / 40 / 20`
  - blended component 편중을 줄이고 Value / Quality를 더 키우는 조합

---

## Min Benchmark Coverage

### 기본 설명
전략과 benchmark가 충분히 겹쳐 비교되었다고 인정하는 최소 coverage 비율이다.

### 왜 사용되는지
겹치는 기간이 너무 적으면 benchmark 비교 자체가 공정하지 않을 수 있기 때문이다.

### 예시 / 필요 상황
- `95%`
  - 전략 구간 대부분에서 benchmark 데이터가 같이 있어야 한다는 뜻

---

## Min Net CAGR Spread

### 기본 설명
전략의 net CAGR이 benchmark CAGR보다 최소 어느 정도는 높거나 덜 나빠야 하는지를 정한 기준이다.

### 왜 사용되는지
benchmark보다 거의 나을 게 없으면
굳이 더 복잡한 전략을 실전 후보로 볼 이유가 약해지기 때문이다.

### 예시 / 필요 상황
- `-2%`
  - benchmark보다 조금 못해도 허용하지만,
    그 이상 열세면 promotion을 보수적으로 본다는 뜻

---

## Min Liquidity Clean Coverage

### 기본 설명
리밸런싱 행 대부분이 유동성 제외 없이 지나가야 한다는 later-pass 기준이다.

### 왜 사용되는지
유동성 필터가 켜져 있는 것보다,
전략이 실제로 얼마나 자주 유동성 때문에 막히는지가 더 중요하기 때문이다.

### 예시 / 필요 상황
- `90%`
  - 리밸런싱 10번 중 최소 9번은 유동성 제외 없이 지나가야 실전 승격 해석이 자연스럽다.

---

## Max Underperformance Share

### 기본 설명
rolling window 중 benchmark보다 뒤처진 비율이 이 값보다 높으면 승격을 더 보수적으로 보는 기준이다.

### 왜 사용되는지
전체 CAGR이 좋아도,
benchmark 대비로 지는 구간이 너무 많으면 consistency가 약할 수 있기 때문이다.

### 예시 / 필요 상황
- `55%`
  - 절반이 넘는 rolling 구간에서 benchmark에 밀리면 `Validation Policy`가 약해질 수 있다.

---

## Min Worst Rolling Excess

### 기본 설명
rolling excess return 최악 구간이 이 값보다 더 나쁘면 승격을 보수적으로 보는 기준이다.

### 왜 사용되는지
일부 구간에서 benchmark 대비 성과 붕괴가 너무 크면,
실전에서는 그 구간을 감당하기 어렵기 때문이다.

### 예시 / 필요 상황
- `-15%`
  - 최악 rolling 구간이 benchmark보다 `15%`보다 더 나쁘면 caution 쪽으로 읽기 쉽다.

---

## Max Strategy Drawdown

### 기본 설명
전략 자체 최대 낙폭이 어느 수준보다 더 깊어지면 승격을 보수적으로 보는 기준이다.

### 왜 사용되는지
수익률이 좋아도 손실 구간이 감당 범위를 넘으면 실전 후보로 보기 어렵기 때문이다.

### 예시 / 필요 상황
- `-35%`
  - 전략 최대낙폭이 `-35%`보다 더 깊으면 `Portfolio Guardrail Policy`가 약해질 수 있다.

---

## Max Drawdown Gap vs Benchmark

### 기본 설명
전략의 최대 낙폭이 benchmark보다 얼마나 더 나쁠 수 있는지 정하는 허용 범위다.

### 왜 사용되는지
절대 낙폭뿐 아니라 benchmark 대비 downside behavior도 같이 봐야
전략의 상대적 리스크를 읽을 수 있기 때문이다.

### 예시 / 필요 상황
- `8%`
  - 전략 낙폭이 benchmark보다 `8%` 이상 더 나쁘면 승격을 더 보수적으로 본다.

---

## Trend Filter

### 기본 설명
현재 가격이 일정 기간 이동평균보다 위에 있을 때만 보유를 허용하는 추세 확인 장치다.

### 왜 사용되는지
상대적으로 강한 자산이라도 큰 하락 추세에 들어간 자산은
그대로 들고 가기보다 한 번 더 걸러내는 게 더 안전할 수 있기 때문이다.

### 예시 / 필요 상황
- `MA200` 기준 trend filter라면:
  - 가격이 `200일 이동평균` 아래로 내려간 자산은 보유하지 않거나 제외할 수 있다.
- 추세추종 전략에서 하락장 노출을 줄이고 싶을 때 자주 쓴다.

---

## Market Regime

### 기본 설명
지금 시장이 위험자산에 우호적인지,
아니면 방어적으로 대응해야 하는지를 구분하는 상태 판단이다.

### 왜 사용되는지
같은 전략이라도 시장 환경이 완전히 달라지면
공격적으로 갈지 방어적으로 갈지 다르게 해석해야 하기 때문이다.

### 예시 / 필요 상황
- 벤치마크가 장기 이동평균 아래에 있으면 `risk-off`로 보는 식의 규칙이 대표적이다.
- 시장이 약세 구간일 때 현금이나 방어 자산 비중을 높이는 판단에 쓴다.

---

## Underperformance Guardrail

### 기본 설명
전략이 benchmark보다 일정 기간 계속 뒤처질 때,
그 상태를 경고하거나 실제로 더 보수적으로 행동하게 만드는 안전장치다.

### 왜 사용되는지
절대 수익이 잠깐 괜찮아 보여도 benchmark 대비 상대 성과가 오래 나쁘면,
전략이 현재 환경에서 잘 안 맞고 있을 수 있기 때문이다.

### 예시 / 필요 상황
- 최근 `12개월` rolling 상대성과가 기준보다 많이 나쁘면
  `watch`나 `caution`으로 읽거나,
  다음 리밸런싱을 더 보수적으로 처리할 수 있다.

---

## Drawdown Guardrail

### 기본 설명
전략의 낙폭이 너무 깊어지거나,
benchmark보다 낙폭이 지나치게 커질 때 작동하는 안전장치다.

### 왜 사용되는지
실전에서는 손실이 커지는 구간에서
“계속 밀고 갈지, 한 번 더 보수적으로 볼지”를 나누는 기준이 필요하기 때문이다.

### 예시 / 필요 상황
- 전략 drawdown이 `-35%`보다 깊어지거나,
  benchmark 대비 낙폭 차이가 너무 벌어지면
  `guardrail`이 작동해 `watch/caution`으로 읽히거나 다음 행동을 제한할 수 있다.

---

## Benchmark

### 기본 설명
전략 결과를 비교할 기준 자산 또는 기준 지수다.

### 왜 사용되는지
전략이 절대 수익만 좋은지 보는 것보다,
기준 대비 얼마나 나은지 같이 봐야 해석이 더 실전적이기 때문이다.

### 예시 / 필요 상황
- ETF 전략을 `SPY`와 비교해서
  같은 기간에 얼마나 더 나았는지 확인

---

## Benchmark Policy

### 기본 설명
전략이 benchmark와 비교했을 때, 최소한 어느 정도는 납득 가능한 상대 성과와 데이터 coverage를 갖췄는지 보는 기준이다.

### 왜 사용되는지
benchmark가 있다고 해서 충분한 것은 아니고,
그 benchmark와의 비교가 실제로 의미 있게 성립하는지 같이 봐야 하기 때문이다.

### 예시 / 필요 상황
- benchmark coverage가 너무 낮으면
  전략과 benchmark를 공정하게 비교했다고 보기 어렵다.
- net CAGR spread가 너무 낮거나 음수면
  "굳이 이 전략을 쓸 이유가 있나?"를 다시 봐야 한다.

---

## Gross Total Balance

### 기본 설명
거래 비용을 차감하기 전 기준의 전략 잔고다.

### 왜 사용되는지
전략 자체의 순수 성과와,
거래 비용까지 반영한 실전형 성과를 분리해서 보기 위해서다.

### 예시 / 필요 상황
- gross는 좋아 보여도,
  비용 차감 후 net 결과는 더 낮아질 수 있다.

---

## Total Balance

### 기본 설명
현재 프로젝트 문맥에서는 보통 최종적으로 보여주는 잔고이며,
real-money hardening이 붙은 전략에서는 비용 차감 후 net 기준으로 읽는 경우가 많다.

### 왜 사용되는지
사용자가 실제 투자 결과에 더 가까운 잔고를 바로 볼 수 있게 하기 위해서다.

### 예시 / 필요 상황
- `Gross Total Balance`와 `Total Balance`를 같이 보면
  비용 영향이 어느 정도인지 바로 읽을 수 있다.

---

## Estimated Cost

### 기본 설명
해당 리밸런싱 시점에 turnover를 바탕으로 추정한 거래 비용 금액이다.

### 왜 사용되는지
그 시점의 매매가 실제로 얼마나 비용을 유발했는지 보기 위해서다.

### 예시 / 필요 상황
- turnover가 큰 달에는 `Estimated Cost`가 평소보다 크게 나올 수 있다.

---

## Cumulative Estimated Cost

### 기본 설명
시작일부터 현재 시점까지 누적된 예상 거래 비용 총액이다.

### 왜 사용되는지
전략이 장기적으로 비용을 얼마나 소모하는지 보기 위해서다.

### 예시 / 필요 상황
- 단기 성과가 괜찮아 보여도,
  누적 비용이 너무 빠르게 쌓이면 실전성은 낮아질 수 있다.

---

## Portfolio Guardrail

### 기본 설명
전략이 너무 위험하거나 비정상적인 상태로 가는 것을 막기 위한 안전 규칙이다.

### 왜 사용되는지
실전에서는 수익률뿐 아니라,
감당 가능한 위험 범위 안에서 움직이는지도 중요하기 때문이다.

### 예시 / 필요 상황
- 최대 허용 drawdown 점검
- 특정 자산 집중도 제한
- 과도한 turnover 경고

---

## Guardrail Policy

### 기본 설명
전략의 위험 상태를 승격 판단 관점에서 요약해 읽는 기준이다.

### 왜 사용되는지
단순히 수익률이 좋아 보여도,
최대 낙폭이 너무 깊거나 benchmark보다 drawdown이 지나치게 나쁘면 실전형 후보로 보기 어렵기 때문이다.

### 예시 / 필요 상황
- `Max Strategy Drawdown`
  - 전략 자체의 최대 낙폭이 허용 범위를 넘는지 본다.
- `Max Drawdown Gap vs Benchmark`
  - benchmark보다 얼마나 더 깊게 빠졌는지 본다.
- `Guardrail Policy Status = caution`
  - 지금은 승격보다 drawdown 계약 재검토가 우선이라는 뜻이다.

---

## AUM / Assets Under Management

### 기본 설명
ETF나 펀드가 현재 얼마나 큰 규모의 자산을 운용하고 있는지 보여주는 값이다.

### 왜 사용되는지
너무 작은 ETF는 거래가 얇거나, 상품이 닫히거나, 운용 효율이 떨어질 가능성이 상대적으로 크기 때문이다.

### 예시 / 필요 상황
- `Min ETF AUM ($B)`를 `1.0`으로 두면
  현재 운용자산이 `10억 달러`보다 너무 작은 ETF는
  실전형 관점에서 주의 대상으로 읽을 수 있다.

---

## Min ETF AUM ($B)

### 기본 설명
실전형 ETF 후보로 볼 때 요구하는 최소 운용자산 규모다.

### 왜 사용되는지
너무 작은 ETF는 유동성, 상품 지속성, 체결 품질 관점에서 더 보수적으로 읽어야 하기 때문이다.

### 예시 / 필요 상황
- `1.0`
  - 현재 AUM이 `10억 달러`보다 작으면 `ETF Operability`가 약해질 수 있다.
- `0.0`
  - 이 기준을 사실상 끈 상태로 읽을 수 있다.

---

## Bid-Ask Spread

### 기본 설명
현재 시장에서 사는 가격(`ask`)과 파는 가격(`bid`) 사이의 차이다.

### 왜 사용되는지
spread가 넓으면 실제로 거래할 때 숨은 비용이 커지고,
백테스트보다 실제 체결 성과가 나빠질 가능성이 커지기 때문이다.

### 예시 / 필요 상황
- `Max Bid-Ask Spread (%)`를 `0.50%`로 두면
  현재 호가 차이가 너무 넓은 ETF는 실전형 승격을 보수적으로 보게 된다.

---

## Max Bid-Ask Spread (%)

### 기본 설명
현재 ETF 호가 스프레드가 어느 수준보다 넓으면 보수적으로 보겠다는 상한선이다.

### 왜 사용되는지
spread가 넓을수록 실제 체결 비용이 커져서,
백테스트보다 실전 성과가 나빠질 가능성이 높아지기 때문이다.

### 예시 / 필요 상황
- `0.50%`
  - 현재 스프레드가 이보다 넓으면 `ETF Operability`가 `watch` 또는 `caution`으로 읽힐 수 있다.
- `100.0%`
  - 사실상 제한을 크게 완화한 상태로 읽을 수 있다.

---

## ETF Operability

### 기본 설명
현재 시점 기준으로 그 ETF가 실전에서 쓰기 무난해 보이는지 요약해서 읽는 상태값이다.

### 왜 사용되는지
ETF 전략은 단순 수익률뿐 아니라,
현재 상품 규모와 호가 상태까지 같이 봐야 실제 투자에 더 가까운 판단이 되기 때문이다.

### 예시 / 필요 상황
- `etf_operability_status = normal`
  - AUM과 spread 기준이 대체로 무난함
- `watch`
  - 일부 ETF가 기준에 걸리거나 데이터가 부분적으로 부족함
- `caution`
  - AUM/spread 기준 위반이 뚜렷해서 승격 보류가 맞음
- `unavailable`
  - 현재 snapshot 정보가 부족해서 판단 근거가 약함

---

## Real-Money Tab

### 기본 설명
백테스트 실행 후 결과 영역에서, 실전 투자 관점의 해석 정보를 모아 보여주는 탭이다.

### 왜 사용되는지
일반 summary만 보면 수익률 숫자는 보이지만,
실전형 승격 판단에 필요한 benchmark, policy, checklist 상태까지 한 번에 보기 어렵기 때문이다.

### 예시 / 필요 상황
- `Backtest > Single Strategy`에서 전략 실행 후
  결과 상단 탭 중 `Real-Money`를 열면
  `Promotion Decision`, `Candidate Shortlist`, `Deployment Readiness Checklist` 같은 섹션을 볼 수 있다.

---

## Promotion Decision

### 기본 설명
현재 백테스트 결과를 기준으로,
이 전략을 실전형 후보로 어느 정도까지 해석할 수 있는지를 요약한 상위 판단값이다.

### 왜 사용되는지
전략이 존재하고 백테스트가 돌아간다고 해서
곧바로 실전 투자 후보가 되는 것은 아니기 때문이다.
benchmark, validation, liquidity, guardrail 같은 조건을 먼저 함께 보고 큰 방향을 정해야 한다.

### 예시 / 필요 상황
- `real_money_candidate`
  - 현재 계약 기준에서는 실전형 후보로 읽을 수 있는 상태
- `production_candidate`
  - 아직 robustness review가 더 필요한 상태
- `hold`
  - 지금은 보류하고 validation gap이나 contract issue를 먼저 해결해야 하는 상태

---

## Candidate Shortlist

### 기본 설명
`Promotion Decision`보다 한 단계 더 운영에 가까운 후보 관리 상태다.
즉 "좋은 전략인가?"보다 "지금 어떤 후보 상태로 관리할 것인가?"를 말한다.

### 왜 사용되는지
실제 운용에서는 전략을 바로 투자하지 않고,
watchlist, paper probation, small-capital trial 같은 단계로 나눠 관리하는 편이 현실적이기 때문이다.

### 예시 / 필요 상황
- 어떤 전략이 `real_money_candidate`여도
  바로 live가 아니라 `paper_probation`으로 먼저 둘 수 있다.
- annual strict 중 조건이 더 잘 맞는 전략은 `small_capital_trial`까지 검토할 수 있다.

---

## Shortlist Status

### 기본 설명
현재 전략이 shortlist 안에서 어느 운영 단계에 있는지를 나타내는 값이다.

### 왜 사용되는지
같은 후보 전략이라도
지금은 단순 감시 대상인지,
paper tracking 대상인지,
소액 trial 대상인지가 다르기 때문이다.

### 예시 / 필요 상황
- `watchlist`
  - 아직은 후보 감시 단계
- `paper_probation`
  - paper tracking으로 먼저 봐야 하는 단계
- `small_capital_trial`
  - 소액 실전 trial까지 검토 가능한 단계
- `hold`
  - 지금은 shortlist로 올리기보다 보류가 맞는 단계

---

## Shortlist Next Step

### 기본 설명
현재 shortlist 상태에서 다음으로 해야 할 실무 행동을 짧게 적어둔 값이다.

### 왜 사용되는지
상태만 보면 "그래서 지금 뭘 해야 하지?"가 애매할 수 있기 때문이다.
다음 review action을 같이 보여주면 운영 판단이 빨라진다.

### 예시 / 필요 상황
- `manual_review_then_paper_probation_gate`
  - 먼저 수동 검토를 하고, 그다음 paper probation으로 올릴지 본다
- `start_paper_probation_and_monitor_monthly`
  - 이제 paper tracking을 시작하고 월별로 review한다
- `start_small_capital_trial_with_monthly_review`
  - 소액 trial을 시작하되 월별 점검을 같이 한다

---

## Execution Context

### 기본 설명
이번 run이 어떤 계약과 상태로 실행되었는지를 한 번에 요약해서 보여주는 결과 영역이다.

### 왜 사용되는지
`Real-Money` 탭은 해석 중심이고,
`Execution Context`는 "이번 run이 어떤 입력/정책/상태로 계산되었는지"를 한 곳에서 재확인하는 용도이기 때문이다.

### 예시 / 필요 상황
- 실행 후
  - `Universe Contract`
  - `Promotion Decision`
  - `Shortlist Status`
  - `Probation Status`
  - `Deployment Readiness`
  - `Rolling Review`
  를 한 곳에서 같이 확인할 수 있다.

---

## Watch

### 기본 설명
오류나 강한 실패는 아니지만, 추가 검토가 권장되는 경계 상태다.

### 왜 사용되는지
전략을 너무 일찍 보류하지 않으면서도,
지금 단계에서 더 보수적으로 읽어야 하는 신호를 구분하기 위해서다.

### 예시 / 필요 상황
- 최근 구간 성과가 조금 흔들리는 경우
- liquidity나 validation 지표가 기준선 근처에서 약한 경우

---

## Caution

### 기본 설명
현재 승격 판단을 직접 막고 있는 강한 경고 상태다.

### 왜 사용되는지
단순 주의 신호와, 실제로 승격/배치를 멈춰야 하는 상태를 분리해야 하기 때문이다.

### 예시 / 필요 상황
- `Validation = caution`
- `Liquidity Policy = caution`
- `Portfolio Guardrail Policy = caution`

---

## Unavailable

### 기본 설명
판단에 필요한 데이터나 계약이 부족해서 상태를 확정할 수 없는 상태다.

### 왜 사용되는지
실패와 데이터 부족은 원인이 다르기 때문에,
무조건 나쁜 전략으로 해석하지 않고 먼저 근거를 채우도록 하기 위해서다.

### 예시 / 필요 상황
- benchmark가 연결되지 않음
- liquidity filter가 꺼져 있음
- aligned history가 부족함

---

## Error

### 기본 설명
데이터 또는 계산 오류 때문에 현재 결과를 신뢰하기 어려운 상태다.

### 왜 사용되는지
단순 성능 문제와 달리,
오류 상태는 먼저 데이터/계산 문제를 해결해야 하기 때문이다.

### 예시 / 필요 상황
- `Price Freshness = error`
- 계산에 필요한 series가 비어 있음
- refresh 없이 오래된 가격을 사용함

---

## Hold 해결 가이드

### 기본 설명
`Promotion Decision = hold`일 때, 지금 막히는 항목과 바로 해볼 일을 표로 안내하는 결과 섹션이다.

### 왜 사용되는지
`hold`라는 결과만 보면 사용자가 “그래서 무엇을 수정해야 하지?”에서 멈추기 쉽기 때문이다.

### 예시 / 필요 상황
- 위치:
  - `Backtest 결과 > Real-Money > 현재 판단 > 전략 승격 판단`
- 이 표에서는 보통
  - `항목`
  - `현재 상태`
  - `상태를 보는 위치`
  - `이 상태의 뜻`
  - `바로 해볼 일`
  을 같이 본다.

---

## Probation

### 기본 설명
실제 자금 투입 전, 전략을 일정 기간 관찰하고 검증하는 운영 단계다.

### 왜 사용되는지
좋아 보이는 전략도 바로 live로 올리기보다,
paper tracking이나 소액 trial을 거쳐 검증하는 편이 현실적이기 때문이다.

### 예시 / 필요 상황
- `not_ready`
- `watchlist_review`
- `paper_tracking`
- `small_capital_live_trial`

---

## Probation Review

### 기본 설명
probation 상태를 어떤 주기로 다시 점검할지 보여주는 review 주기다.

### 왜 사용되는지
관찰 단계는 방치가 아니라 정해진 cadence로 review해야 의미가 있기 때문이다.

### 예시 / 필요 상황
- `monthly`
- `biweekly`
- `quarterly`

---

## Monitoring

### 기본 설명
probation 중인 전략을 어떤 강도로 모니터링해야 하는지 보여주는 상태다.

### 왜 사용되는지
같은 probation 전략이라도 routine review면 충분한지,
아니면 더 강한 경고 감시가 필요한지 구분해야 하기 때문이다.

### 예시 / 필요 상황
- `routine_review`
- `heightened_review`
- `breach_watch`
- `blocked`

---

## Monitoring Review

### 기본 설명
monitoring 상태를 어떤 주기로 확인해야 하는지 보여주는 review cadence다.

### 왜 사용되는지
monitoring 강도가 높을수록 더 자주 확인해야 할 수 있기 때문이다.

### 예시 / 필요 상황
- `monthly`
- `biweekly`
- `weekly`

---

## Monitoring Focus

### 기본 설명
현재 전략을 모니터링할 때 특히 유심히 봐야 하는 핵심 항목 목록이다.

### 왜 사용되는지
모든 지표를 같은 강도로 보는 대신,
지금 가장 취약한 부분을 집중적으로 추적하기 위해서다.

### 예시 / 필요 상황
- `validation`
- `liquidity`
- `drawdown_gap`
- `benchmark_relative_consistency`

---

## Monitoring Breach Signals

### 기본 설명
probation 중 “이 조건이 다시 깨지면 더 보수적으로 봐야 한다”는 경고 신호 목록이다.

### 왜 사용되는지
실전 관찰 단계에서는 어떤 신호가 재발하면 비중 확대를 멈출지 미리 정해두는 편이 안전하기 때문이다.

### 예시 / 필요 상황
- rolling underperformance 재악화
- drawdown gap 확대
- liquidity clean coverage 급락

---

## Rolling Review

### 기본 설명
최근 일정 구간에서 benchmark 대비 consistency가 어떤지 따로 보는 검토다.

### 왜 사용되는지
전체 기간 성과만 좋고 최근 구간은 무너지는 전략을 걸러내기 위해서다.

### 예시 / 필요 상황
- 최근 12개월 excess return
- 최근 구간 drawdown gap
- `normal / watch / caution / unavailable`

---

## Out-of-Sample Review

### 기본 설명
전후반 구간을 나눠서 성과가 특정 시기 우연에 크게 의존하지 않았는지 보는 검토다.

### 왜 사용되는지
한 구간에서만 좋았던 전략을 더 보수적으로 해석하기 위해서다.

### 예시 / 필요 상황
- `In-Sample Excess`
- `Out-Sample Excess`
- `Excess Change`

---

## Recent Excess

### 기본 설명
최근 rolling review 구간에서 benchmark 대비 얼마나 초과 수익이 났는지를 뜻한다.

### 왜 사용되는지
최근 구간 robustness를 빠르게 읽기 위한 핵심 지표 중 하나이기 때문이다.

### 예시 / 필요 상황
- 값이 음수면 최근 구간에서 benchmark보다 뒤처졌다는 뜻이다.

---

## Recent DD Gap

### 기본 설명
최근 rolling review 구간에서 전략 drawdown이 benchmark보다 얼마나 더 깊었는지 보여주는 값이다.

### 왜 사용되는지
최근 구간 downside behavior가 benchmark보다 악화됐는지 빠르게 보려면 필요하기 때문이다.

### 예시 / 필요 상황
- 값이 크게 음수면 최근 구간에서 benchmark보다 더 큰 낙폭을 겪었다는 뜻이다.

---

## In-Sample Excess

### 기본 설명
전반부 구간에서 benchmark 대비 초과 성과가 얼마나 났는지 보여주는 값이다.

### 왜 사용되는지
후반부 구간과 비교해 성과 안정성을 보기 위해서다.

### 예시 / 필요 상황
- 전반부는 매우 좋고 후반부는 급격히 나빠졌다면 OOS 해석이 더 보수적일 수 있다.

---

## Out-Sample Excess

### 기본 설명
후반부 구간에서 benchmark 대비 초과 성과가 얼마나 났는지 보여주는 값이다.

### 왜 사용되는지
최근에 가까운 구간에서도 전략 강점이 유지됐는지 확인하기 위해서다.

### 예시 / 필요 상황
- 후반부 excess가 급격히 악화되면 OOS review가 `watch` 또는 `caution`으로 읽힐 수 있다.

---

## Excess Change

### 기본 설명
전반부 excess와 후반부 excess의 차이를 뜻한다.

### 왜 사용되는지
성과 체질이 얼마나 달라졌는지 한 값으로 빠르게 읽을 수 있기 때문이다.

### 예시 / 필요 상황
- 값이 크게 나쁘면 과거에는 좋았지만 최근에는 강점이 약해졌을 가능성이 있다.

---

## Deployment Readiness

### 기본 설명
실제 배치 직전 checklist를 요약해, 지금 배치를 열 수 있는지 보여주는 운영 상태다.

### 왜 사용되는지
`Promotion`과 `Shortlist`는 후보 평가에 가깝고,
`Deployment Readiness`는 실제 운영 직전 상태를 더 직접적으로 보기 위해서다.

### 예시 / 필요 상황
- `blocked`
- `review_required`
- `watchlist_only`
- `paper_only`
- `small_capital_ready`

---

## Pre-Live 운영 점검

### 기본 설명
실제 자금 투입 전 단계에서,
후보 전략을 paper run / watchlist / 보류 / 재검토로 어떻게 관리할지 정하는 운영 절차다.

### 왜 사용되는지
Real-Money 검증 신호가 좋아 보여도
그 자체가 live 투자 승인은 아니다.
실전 투입 전에는 paper tracking 기간, 재검토 날짜, 중단 조건, 데이터 재수집 필요 여부를 별도로 기록해야 한다.

### 예시 / 필요 상황
- `paper run`으로 한 달 이상 관찰
- 특정 drawdown 또는 benchmark 부진이 나오면 재검토
- 데이터 결측 warning이 있으면 후보 판단 전 재수집
- `watchlist`에는 두되 아직 paper tracking은 시작하지 않음

### Real-Money 검증 신호와의 차이
Real-Money 검증 신호는 **백테스트 결과에 붙는 진단표**다.
Pre-Live 운영 점검은 그 진단표를 보고
"이제 어떤 운영 행동을 할 것인가"를 정하고 남기는 **운영 기록 흐름**이다.
여기서 운영 행동은 단순 상태값이 아니라,
왜 그렇게 두었는지, 다음에 무엇을 볼지, 언제 다시 볼지, 어떤 조건이면 중단하거나 다음 단계로 갈지를 포함한다.

---

## Pre-Live 운영 상태

### 기본 설명
Pre-Live 운영 점검에서 후보를 어디에 둘지 표시하는 상태값이다.
Phase 25 기준 대표 상태는 `watchlist`, `paper tracking`, `hold`, `reject`, `re-review`다.

### 왜 사용되는지
백테스트 결과가 좋아 보여도 모든 후보가 같은 다음 행동을 갖지는 않는다.
어떤 후보는 관찰하고, 어떤 후보는 보류하고, 어떤 후보는 특정 날짜에 다시 봐야 한다.
Pre-Live 운영 상태는 이 차이를 기록하기 위해 쓴다.
다만 상태값만으로는 부족하다.
`paper_tracking`이라고만 쓰면 Real-Money의 `paper_only`나 `paper_probation`과 비슷하게 읽힐 수 있다.
따라서 Pre-Live 운영 상태는 항상 `operator_reason`, `next_action`, `review_date`, `tracking_plan`과 함께 읽는다.

### 예시 / 필요 상황
- `watchlist`: 다시 볼 가치는 있지만 아직 paper tracking은 시작하지 않음
- `paper tracking`: 실제 돈 없이 정해진 기간 동안 관찰
- `hold`: 데이터 품질이나 risk blocker 때문에 보류
- `reject`: 현재 기준에서는 더 추적하지 않음
- `re-review`: 특정 날짜나 조건이 지나면 다시 확인

---

## Pre-Live 다음 행동 기록

### 기본 설명
Pre-Live 후보를 어떻게 관리할지 구체적으로 남기는 action package다.
대표 구성은 `operator_reason`, `next_action`, `review_date`, `tracking_plan.cadence`,
`tracking_plan.stop_condition`, `tracking_plan.success_condition`이다.

### 왜 사용되는지
Pre-Live 상태값만 있으면 Real-Money promotion / shortlist와 거의 비슷하게 보일 수 있다.
다음 행동 기록이 있어야
"왜 이 후보를 보고 있는가", "무엇을 확인해야 하는가",
"언제 다시 판단해야 하는가"를 복원할 수 있다.

### 예시 / 필요 상황
- `operator_reason`: 최근 drawdown은 크지만 blocker가 없어 1개월 paper tracking
- `next_action`: 월 1회 성과, MDD, benchmark gap, Real-Money blocker 변화를 확인
- `review_date`: 다음 점검일
- `tracking_plan.stop_condition`: drawdown이 더 악화되거나 blocker가 생기면 중단
- `tracking_plan.success_condition`: 관찰 기간 동안 blocker 없이 후보 성격이 유지되면 재검토

---

## Deployment Checklist Status Count

### 기본 설명
deployment checklist 안에서 `Pass / Watch / Fail / Unavailable`가 각각 몇 개인지 세어 보여주는 요약이다.

### 왜 사용되는지
한 항목씩 다 읽기 전에,
현재 배치 준비 상태가 전체적으로 어느 정도인지 빠르게 스캔할 수 있기 때문이다.

### 예시 / 필요 상황
- `Pass`
  - 기준을 무난하게 충족한 항목 수
- `Watch`
  - 배치는 가능할 수 있지만 더 보수적으로 봐야 하는 항목 수
- `Fail`
  - 현재 배치를 직접 막는 항목 수
- `Unavailable`
  - 판단 근거가 부족한 항목 수

---

## Strategy Highlights

### 기본 설명
compare 결과에서 여러 전략의 핵심 상태를 한 번에 훑기 위한 compare 전용 요약 표면이다.

### 왜 사용되는지
single run의 `Real-Money` 탭은 한 전략을 깊게 읽는 용도이고,
compare에서는 여러 전략을 빠르게 스캔하는 표면이 따로 필요하기 때문이다.

### 예시 / 필요 상황
- 위치:
  - `Compare 결과 > Strategy Comparison > Strategy Highlights`
- 여기서는 보통
  - `Shortlist`
  - `Probation`
  - `Monitoring`
  - `Deployment`
  - `Rolling Review`
  - `OOS Review`
  같은 상태를 전략별로 한 줄씩 비교한다.

---

## Gate Calibration

### 기본 설명
전략을 통과시키거나 보류시키는 기준선이 지금 적절한지 다시 맞추는 작업이다.

### 왜 사용되는지
기준이 너무 빡빡하면 좋은 전략도 계속 `hold`가 되고,
너무 느슨하면 실전에서 위험한 전략도 통과할 수 있기 때문이다.

### 예시 / 필요 상황
- `Validation = caution`이 너무 자주 `hold`를 만든다면
  그 기준이 실제로 적절한지 다시 본다.
- strict annual과 ETF family에 같은 문턱을 쓰는 게 맞는지도 calibration 대상이 될 수 있다.
- 예를 들어
  - `Min Worst Rolling Excess`
  - `Min ETF AUM`
  - `Max Drawdown Gap vs Benchmark`
  같은 threshold를 family별로 다시 보는 작업이 여기에 들어간다.

---

## Partial Cash Retention

### 기본 설명
Trend Filter가 raw selected top-N 중 일부만 탈락시켰을 때,
탈락한 슬롯 비중을 현금으로 남기는 strict annual 구조 옵션이다.

### 왜 사용되는지
기존 survivor reweighting은 살아남은 종목에 다시 100%를 몰아주기 때문에,
실제 노출을 조금 더 보수적으로 낮춰서 `MDD`를 줄여보려는 구조 실험이 어려웠다.
이 옵션은 같은 factor / same gate 후보에서
부분 risk-off를 더 직접적으로 실험하기 위한 레버다.

### 예시 / 필요 상황
- `Top N = 10`인데 trend filter에서 2개가 탈락한 경우
  - `off`:
    남은 8개에 100% 재배분
  - `on`:
    8개만 보유하고 20%는 현금 유지
- 현재 first slice는
  `Trend Filter`의 **부분 탈락**에만 적용된다.
  `market regime`나 guardrail의 전체 risk-off는 여전히 전부 현금 처리다.

---

## Concentration-Aware Weighting

### 기본 설명
strict annual top-N을 pure equal-weight로만 두지 않고,
상위 ranked 종목에 조금 더 높은 비중을 주는 weighting contract다.

### 왜 사용되는지
동일한 factor / same gate 후보에서도
equal-weight가 너무 평평한 노출을 만들 수 있기 때문에,
순위 신호를 조금 더 살리면서
`MDD`와 `CAGR`의 tradeoff를 다시 보려는 구조 레버로 사용된다.

### 예시 / 필요 상황
- `equal_weight`
  - 선택된 종목을 모두 같은 비중으로 보유
- `rank_tapered`
  - 상위 ranked 종목을 조금 더 크게,
    하위 ranked 종목을 조금 더 작게 보유
- Phase 17 first pass에서는
  `Value`와 `Quality + Value` current anchor에 적용했지만
  same-gate lower-MDD rescue는 만들지 못했다.

---

## Rank-Tapered Weighting

### 기본 설명
`Concentration-Aware Weighting`의 current first-slice 구현으로,
top-ranked 종목에서 lower-ranked 종목으로 갈수록
비중이 완만하게 줄어드는 weighting mode다.

### 왜 사용되는지
optimizer나 volatility targeting처럼 무거운 구조를 바로 도입하지 않고도,
equal-weight보다 덜 평평한 포지션 구조를 bounded하게 실험할 수 있기 때문이다.

### 예시 / 필요 상황
- strict annual UI에서
  `Weighting Contract = Rank-Tapered`
  로 선택할 수 있다.
- current first slice는
  mild linear taper를 normalize해서 사용한다.
- same gate는 유지할 수 있지만,
  lower-MDD rescue를 보장하는 contract는 아니다.

---

## Strategy Hub

### 기본 설명
전략 하나에 대한 핵심 결과와 관련 문서를 한 곳에서 안내하는 요약 허브 문서다.

### 왜 사용되는지
같은 전략에 대해 결과 문서, 세부 실험 문서, 실행 기록 문서가 여러 개 생기기 때문에
무엇부터 봐야 하는지 먼저 알려주는 입구 페이지가 필요하기 때문이다.

### 예시 / 필요 상황
- `VALUE_STRICT_ANNUAL.md`
- `QUALITY_STRICT_ANNUAL.md`
- `QUALITY_VALUE_STRICT_ANNUAL.md`
- 보통 이 문서에서는
  - 현재 다시 볼 만한 후보
  - 관련 one-pager
  - backtest log
  - 세부 phase report
  로 이동한다.

---

## One-Pager

### 기본 설명
후보 전략 하나를 한 장에서 빠르게 읽을 수 있게 정리한 단일 요약 문서다.

### 왜 사용되는지
전략 허브는 여러 결과를 묶는 문서이고,
실제 후보 하나를 다시 실행하거나 설명할 때는
입력값과 결과가 한 장에 모여 있는 문서가 더 편하기 때문이다.

### 예시 / 필요 상황
- strongest candidate
- downside-improved candidate
- value replacement candidate
- 보통
  - 전략 구성
  - factor
  - contract
  - 기대 결과
  를 함께 적는다.

---

## Backtest Log

### 기본 설명
같은 전략을 어떤 세팅으로 여러 번 돌렸는지 시간순으로 누적 기록하는 문서다.

### 왜 사용되는지
좋은 run과 실패한 run을 같이 남겨야,
나중에 왜 지금 후보가 이렇게 정리됐는지 추적할 수 있기 때문이다.

### 예시 / 필요 상황
- `VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
- 각 entry에는 보통
  - 목표
  - 기간 / universe
  - 핵심 설정
  - 결과
  - 해석 / 다음 액션
  이 들어간다.

---

## Strongest Practical Point

### 기본 설명
현재까지 실험한 후보들 중에서,
성과와 gate 상태를 함께 봤을 때 가장 실무적으로 강하다고 판단한 기준점이다.

### 왜 사용되는지
수익률만 가장 높은 후보와
실제로 다시 써볼 만한 후보는 다를 수 있기 때문이다.

### 예시 / 필요 상황
- `CAGR`는 아주 높지만 `hold`면 strongest practical point가 아닐 수 있다.
- gate는 좋지만 수익률이 너무 약하면 strongest practical point가 아닐 수 있다.
- 그래서 보통
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`
  를 같이 보고 정한다.

---

## Current Candidate

### 기본 설명
지금 시점에서 다시 참고하거나 재현할 가치가 있다고 판단한 현재 기준 후보다.

### 왜 사용되는지
모든 과거 실험을 같은 강도로 다시 볼 필요는 없고,
현재 운영/검토 기준에서 다시 볼 후보를 분리해 두는 편이 효율적이기 때문이다.

### 예시 / 필요 상황
- strongest current candidate
- downside-improved current candidate
- cleaner alternative current candidate

---

## Current Candidate Snapshot

### 기본 설명
전략 허브 문서 안에서 현재 가장 중요한 후보를 짧게 다시 보여주는 요약 구간이다.

### 왜 사용되는지
문서 처음부터 끝까지 다 읽지 않아도
“지금 무엇을 먼저 보면 되는지”를 빠르게 잡을 수 있어야 하기 때문이다.

### 예시 / 필요 상황
- strongest candidate 요약
- balanced candidate 요약
- lower-drawdown alternative 요약

---

## Downside-Improved Candidate

### 기본 설명
기존 strongest 후보보다 낙폭(`MDD`)을 줄이는 방향으로 조정한 후보다.

### 왜 사용되는지
raw 수익률이 아주 강한 후보라도 낙폭이 너무 깊으면
실전에서는 부담이 커질 수 있기 때문이다.

### 예시 / 필요 상황
- strongest baseline:
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
- downside-improved candidate:
  - `CAGR`는 조금 낮아져도
  - `MDD`를 `-24%`대까지 줄인 후보

---

## Structural Rescue

### 기본 설명
같은 family 안에서 factor를 조금 바꾸는 정도로는 안 풀릴 때,
benchmark, overlay, top-N 같은 구조를 바꿔 실제 후보를 다시 살리는 탐색이다.

### 왜 사용되는지
어떤 전략은 factor 자체보다
비교 기준이나 구조 계약 때문에 `hold`에 머무를 수 있기 때문이다.

### 예시 / 필요 상황
- `Quality`에서 bounded factor addition만으로는 안 풀렸지만,
  `LQD + trend on + regime off` 구조 조정으로
  `real_money_candidate`를 회복한 경우

---

## Structural Rescue Report

### 기본 설명
전략을 다시 usable candidate 상태로 살리기 위해
benchmark, overlay, cadence, top-N 같은 구조 조정을 탐색한 보고서다.

### 왜 사용되는지
단순 factor 실험과
구조 자체를 바꾸는 실험은 성격이 다르기 때문에 따로 구분해 읽는 편이 명확하기 때문이다.

### 예시 / 필요 상황
- `PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md`

---

## Downside Report

### 기본 설명
현재 후보에서 `MDD`를 줄일 수 있는지 중심으로 다시 본 세부 탐색 보고서다.

### 왜 사용되는지
수익률을 조금 희생하더라도 drawdown을 줄이는 대안이 실전적으로 더 매력적일 수 있기 때문이다.

### 예시 / 필요 상황
- `Top N`을 늘리거나
- factor를 조금 더 방어적으로 바꾸거나
- overlay를 조정해 더 낮은 낙폭을 노리는 문서

---

## Alternate Contract Report

### 기본 설명
같은 전략 anchor를 유지한 채,
benchmark나 overlay 같은 계약만 바꿨을 때 해석이 어떻게 달라지는지 본 보고서다.

### 왜 사용되는지
같은 전략이라도 어떤 benchmark를 쓰는지,
어떤 overlay를 켜는지에 따라
`Promotion`, `Deployment`, `Validation` 해석이 달라질 수 있기 때문이다.

### 예시 / 필요 상황
- `LQD benchmark`는 strongest practical point였지만
- `SPY benchmark`는 cleaner but more conservative alternative였는지 비교하는 경우

---

## Capital Discipline

### 기본 설명
`Quality > Strict Annual` 쪽에서 자본 효율과 재무 건전성을 같이 보려는 quality factor 묶음 이름이다.

### 왜 사용되는지
quality factor가 많을 때
어떤 조합을 중심 테마로 묶어 읽는지 이름을 붙여두면
실험 결과를 다시 비교하기 쉬워지기 때문이다.

### 예시 / 필요 상황
- 보통 아래와 같은 factor 묶음을 뜻했다:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`

---

## Trend On / Trend Off

### 기본 설명
`Trend Filter`를 켠 상태인지(`on`), 끈 상태인지(`off`)를 뜻하는 짧은 표기다.

### 왜 사용되는지
전략 조합을 짧게 요약할 때
overlay 사용 여부를 빠르게 적기 위해서다.

### 예시 / 필요 상황
- `trend on`
  - 추세 필터를 적용한 상태
- `trend off`
  - 추세 필터 없이 순수 전략만 본 상태

---

## Regime On / Regime Off

### 기본 설명
`Market Regime` overlay를 켠 상태인지(`on`), 끈 상태인지(`off`)를 뜻하는 짧은 표기다.

### 왜 사용되는지
시장 환경 해석을 후보 비교에 반영했는지 여부를 짧게 표시하기 위해서다.

### 예시 / 필요 상황
- `regime on`
  - market regime overlay 적용
- `regime off`
  - market regime overlay 없이 순수 전략 비교

---

## Defensive Sleeve Risk-Off

### 기본 설명
포트폴리오 전체를 쉬어야 할 때
포트폴리오를 전부 현금으로 두는 대신,
미리 정한 방어 자산 묶음으로 옮기는 contract다.

### 왜 사용되는지
`cash only`는 downside를 막는 데는 강하지만
현금 비중이 커지면 수익률 drag가 커질 수 있다.

그래서:

- risk-off를 유지하되
- idle cash를 조금 줄이고
- 더 부드러운 downside profile을 만들 수 있는지

보려는 목적에서 사용된다.

### 예시 / 필요 상황
- `BIL, SHY, LQD`
  같은 defensive sleeve를 두고
  `drawdown guardrail`이나 `market regime`가
  factor 포트폴리오 전체를 멈추게 했을 때
  현금 대신 그 sleeve로 이동하는 경우

---

## Risk-Off Contract

### 기본 설명
strict annual에서
포트폴리오 전체를 쉬어야 할 때
현금으로 둘지, 방어 ETF sleeve로 옮길지를 정하는 계약이다.

### 왜 사용되는지
부분 trend rejection 처리와
포트폴리오 전체 전환 상황을 구분해서 읽기 위해서다.

여기서 `포트폴리오 전체를 쉰다`는 말은
개별 종목 몇 개만 빠지는 것이 아니라,
`Market Regime` 또는 guardrail 때문에
그 시점 factor 포트폴리오 전체를 그대로 쓰지 않고
현금 또는 방어 ETF로 전체 전환하는 상황을 뜻한다.

### 예시 / 필요 상황
- `Cash Only`
  - 포트폴리오 전체를 쉬어야 할 때 100% 현금
- `Defensive Sleeve Preference`
  - 포트폴리오 전체를 쉬어야 할 때 `BIL, SHY, LQD` 같은 방어 ETF sleeve 사용

---

## Defensive Sleeve Tickers

### 기본 설명
`Risk-Off Contract = Defensive Sleeve Preference`일 때
포트폴리오 전체를 쉬어야 하는 구간에서 현금 대신 담을 방어 ETF 목록이다.

### 왜 사용되는지
현금만 두는 대신
짧은 채권/우량 채권/초단기 ETF 같은 방어 자산으로
임시 회전할 수 있게 하기 위해서다.

### 예시 / 필요 상황
- `BIL, SHY, LQD`
  - risk-off 시 이 세 ETF를 동일가중으로 담는 경우

---

## Weighting Contract

### 기본 설명
최종 선택된 종목들 사이에
비중을 어떻게 나눌지 정하는 계약이다.

### 왜 사용되는지
같은 종목을 고르더라도
비중 규칙에 따라 수익률과 MDD가 달라질 수 있기 때문이다.

토글형 기능이라기보다,
백테스트를 돌릴 때 항상 같이 저장되는 기본 비중 규칙으로 읽는 것이 맞다.

### 예시 / 필요 상황
- `Equal Weight`
  - 모든 선택 종목을 동일 비중으로 담는다
- `Rank-Tapered`
  - 상위 rank 종목에 조금 더 높은 비중을 준다

---

## Rejected Slot Handling Contract

### 기본 설명
Trend Filter 때문에 raw top-N 일부가 탈락한 뒤
빈 슬롯을 어떻게 처리할지 정하는 계약이다.

### 왜 사용되는지
부분 rejection 이후에
- 생존 종목에 다시 재배분할지
- 현금으로 남길지
- 다음 순위 종목으로 먼저 채울지
를 명시적으로 구분해 읽기 위해서다.

이것도 토글형 기능이라기보다,
Trend Filter로 일부 종목이 실제로 탈락했을 때 어떻게 처리할지를 미리 정해두는 기본 계약이다.

### 예시 / 필요 상황
- `Reweight Survivors`
  - 남은 생존 종목에 다시 100% 재배분
- `Retain Unfilled Slots As Cash`
  - 빈 슬롯만큼 현금 유지
- `Fill Then Reweight Survivors`
  - 먼저 다음 순위 종목으로 채운 뒤, 남는 슬롯은 재배분
- `Fill Then Retain Unfilled Slots As Cash`
  - 먼저 다음 순위 종목으로 채운 뒤, 남는 슬롯은 현금 유지

---

## History Run

### 기본 설명
`Backtest > History`에서 고르는
저장된 백테스트 실행 기록 1건이다.

### 왜 사용되는지
이전에 어떤 설정으로 실행했는지 다시 보고,
`Run Again` 또는 `Load Into Form`으로 이어가기 위해서다.

### 예시 / 필요 상황
- 특정 strict annual 실행 기록을 다시 열어
  설정, gate snapshot, saved context를 확인할 때

---

## Interpretation Summary

### 기본 설명
selection history를 한 행씩 읽는 대신,
실행 전체에서 어떤 처리 규칙이 얼마나 자주 나타났는지 요약해 주는 표다.

### 왜 사용되는지
`Rejected Slot Handling`, `Weighting Contract`, `Risk-Off Contract`,
`Filled Events`, `Cash-Retained Events`, `Defensive Sleeve Activations`를
한 번에 훑기 위해서다.

### 예시 / 필요 상황
- 이번 실행에서 defensive sleeve가 실제로 몇 번 켜졌는지 빠르게 보고 싶을 때

---

## Row-Level Interpretation

### 기본 설명
selection history 표의 `Interpretation` 열에 들어가는
날짜별 한 줄 설명이다.

### 왜 사용되는지
각 리밸런싱에서
- trend rejection이 있었는지
- 현금으로 갔는지
- defensive sleeve로 돌았는지
- 최종 weighting contract가 무엇이었는지
를 날짜 단위로 바로 읽기 위해서다.

### 예시 / 필요 상황
- 특정 날짜에 왜 현금 비중이 커졌는지 빠르게 이해하고 싶을 때

---

## Development Validation

### 기본 설명
투자 결론을 내리기 전에,
프로그램 기능이 의도대로 작동하는지 확인하는 검증을 뜻한다.

### 왜 사용되는지
백테스트 숫자가 좋아 보여도,
그 숫자가 나온 기능 흐름이 저장, 재실행, 비교, 해석까지 안정적으로 이어지는지 먼저 확인해야 하기 때문이다.

### 예시 / 필요 상황
- `Phase 22`에서 portfolio workflow가
  여러 전략을 묶고 저장하고 replay할 수 있는지 확인한 작업
- 이 경우 `equal-third baseline`은 투자 benchmark가 아니라
  기능 검증용 기준이다.

---

## Fixture

### 기본 설명
개발이나 검증을 위해 일부러 고정해 둔 대표 입력값이나 테스트 조합을 뜻한다.

### 왜 사용되는지
매번 다른 전략 / 기간 / 비중으로 테스트하면
기능이 잘 작동하는지,
아니면 특정 결과가 우연히 좋아 보이는지 구분하기 어렵다.

### 예시 / 필요 상황
- `Value / Quality / Quality + Value` 3개를
  Phase 22 portfolio workflow 검증용 대표 전략 조합으로 사용한 경우
- fixture는 실전 추천 조합이라는 뜻이 아니다.

---

## User-Requested Analysis

### 기본 설명
기본 phase 진행과 별도로,
사용자가 명시적으로 요청해서 수행하는 백테스트 분석이나 투자 가능성 검토를 뜻한다.

### 왜 사용되는지
이 프로젝트의 기본 방향은 제품 개발이지만,
사용자가 QA 중 특정 전략이나 portfolio 결과를 분석해 달라고 요청할 수 있다.
이때 분석을 수행하되,
그것이 전체 phase 방향을 투자 분석으로 바꾼 것은 아니라고 구분하기 위해 사용한다.

### 예시 / 필요 상황
- 사용자가 "이 strategy 수치가 유효한지 봐줘"라고 요청한 경우
- 사용자가 "이 portfolio 조합을 한 번 더 백테스트해줘"라고 요청한 경우

---

## Contract

### 기본 설명
이 프로젝트에서 `contract`는
사용자가 화면에서 고르는 "명시적인 동작 규칙"을 뜻한다.

### 왜 사용되는지
체크박스 여러 개를 머릿속으로 조합해서 해석하는 대신,
"이 전략은 이런 방식으로 동작한다"를 이름 있는 규칙으로 고정해
history와 rerun에서 다시 읽기 쉽게 만들기 위해 사용한다.

### 예시 / 필요 상황
- `Rejected Slot Handling Contract`
- `Risk-Off Contract`
- `Weighting Contract`

---

## Usable Contract

### 기본 설명
코드 내부 규칙이 아니라,
사용자가 UI, history, interpretation에서 다시 읽어도
뜻이 바로 이해되는 형태로 정리된 contract를 뜻한다.

### 왜 사용되는지
전략 구조 옵션이 늘어나면
기능이 "있다"는 것만으로는 부족하고,
실제로 다시 읽고 비교할 수 있어야 하기 때문이다.

### 예시 / 필요 상황
- checkbox 두 개 조합으로 읽던 동작을
  하나의 named contract로 바꾸는 경우

---

## Payload

### 기본 설명
한 번의 백테스트 실행에 사용된 설정값 묶음을 뜻한다.

### 왜 사용되는지
history에서 다시 불러오거나,
같은 설정으로 rerun할 때
당시 입력값을 복원해야 하기 때문이다.

### 예시 / 필요 상황
- benchmark, top N, factor set, contract mode 등이 같이 저장된다.

---

## Boolean Combination

### 기본 설명
`true/false`, `on/off` 값 여러 개를
사용자가 직접 조합해서 뜻을 해석해야 하는 상태를 뜻한다.

### 왜 사용되는지
현재 문제를 설명할 때 자주 쓰인다.
`Phase 19`는 이런 조합 중심 해석을 줄이고,
더 직접적인 contract 언어로 바꾸려는 phase다.

### 예시 / 필요 상황
- `rejected_slot_fill_enabled = true`
- `partial_cash_retention_enabled = false`
를 사용자가 스스로 조합해 뜻을 읽어야 하는 경우

---

## Slice

### 기본 설명
phase 전체 작업을 한 번에 다 하지 않고,
작고 안전한 구현 단위로 나눠서 진행하는 한 조각 작업을 뜻한다.

### 왜 사용되는지
큰 구조 변경을 한 번에 넣으면
회귀 위험과 해석 혼란이 커지기 때문에,
작은 단위로 끊어서 구현하고 검증하기 위해 사용한다.

### 예시 / 필요 상황
- first slice:
  `Rejected Slot Handling Contract`
- second slice:
  history / interpretation cleanup

---

## Minimal Validation

### 기본 설명
deep backtest 대신,
우선 코드가 깨지지 않았는지와 기본 연결이 맞는지만 확인하는 최소 검증을 뜻한다.

### 왜 사용되는지
구현 우선 phase에서는
새 기능을 하나 넣을 때마다 큰 rerun을 반복하기보다,
먼저 안정적으로 연결되었는지를 빠르게 확인하는 편이 효율적이기 때문이다.

### 예시 / 필요 상황
- `py_compile`
- import smoke
- 아주 작은 representative check

---

## Structural Redesign Lane

### 기본 설명
기존 factor나 top N만 조금 바꾸는 수준이 아니라,
전략이 실제로 포지션을 채우고 줄이고 위험을 처리하는 구조 자체를 바꾸는 실험 흐름을 뜻한다.

### 왜 사용되는지
bounded tweak만으로는
same-gate lower-MDD 후보를 만들기 어려웠기 때문에,
더 큰 구조 변경 실험을 따로 묶어 관리하기 위해 사용한다.

### 예시 / 필요 상황
- partial cash retention
- defensive sleeve risk-off
- next-ranked fill
- concentration-aware weighting

---

## Phase Status

### 기본 설명
각 phase가 지금 어느 단계에 있는지 보여주는 상태값이다.
이 프로젝트에서는 phase 상태를 하나의 긴 문자열로 합치지 않고,
`진행 상태`와 `검증 상태`로 나누어 읽는다.

### 왜 사용되는지
`completed`만 쓰면 실제로 코드 구현만 끝난 것인지,
사용자가 checklist까지 확인한 것인지,
아니면 다음 phase로 넘어갈 수 있는 practical closeout인지 구분하기 어렵다.

### 예시 / 필요 상황
진행 상태:

- `planned`
  - 계획만 있고 아직 본격 작업 전이다.
- `active`
  - 지금 진행 중이다.
- `partial_complete`
  - 일부 작업 단위만 끝났다.
- `implementation_complete`
  - 구현과 문서 1차 작업은 끝났다.
- `practical_closeout`
  - 현재 범위는 다음 단계로 넘길 수 있을 만큼 정리되었다.
- `complete`
  - phase 자체가 종료되었다.

검증 상태:

- `not_ready_for_qa`
  - 아직 사용자 QA를 할 단계가 아니다.
- `manual_qa_pending`
  - 사용자 checklist 확인이 남아 있다.
- `manual_qa_completed`
  - 사용자 checklist 확인까지 끝났다.
- `smoke_checked`
  - 최소 자동/스모크 검증은 됐다.
- `superseded_by_later_phase`
  - 예전 checklist나 pending 상태가 이후 phase 구현 / QA / closeout에 흡수되어,
    현재 별도 manual QA gate로 다시 열 필요가 없다.
- `legacy_unknown`
  - 예전 phase라 검증 상태가 명확히 분리되어 남아 있지 않다.
- `not_applicable`
  - phase 검증 대상이 아닌 지원 트랙이나 참고 문서다.

Legacy 표현:

- `first_chapter_completed`
  - 정식 chapter 체계가 아니라, 예전 문서에서 "첫 번째 큰 작업 묶음이 끝났다"는 뜻으로 남은 표현이다.
  - 새 문서에서는 `partial_complete`로 바꿔 읽는다.

---

## Pre-Live Candidate Registry

### 기본 설명
Real-Money 검증 신호를 본 뒤,
후보를 `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중 어디에 둘지 기록하는 JSONL 저장소다.

### 왜 사용되는지
좋아 보이는 백테스트 결과를 바로 투자 승인으로 넘기지 않고,
실전 전 관찰 상태와 다음 행동을 남기기 위해 사용한다.

### 예시 / 필요 상황
- 파일 위치:
  - `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
- helper:
  - `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
  - current candidate에서 초안을 만들 때는 `draft-from-current <registry_id>`를 사용한다.
- `CURRENT_CANDIDATE_REGISTRY.jsonl`과의 차이:
  - current candidate registry는 후보 자체를 저장한다.
  - pre-live candidate registry는 그 후보의 운영 상태와 다음 행동을 저장한다.

---

## Candidate Review

### 기본 설명
백테스트 후보를 바로 투자 추천으로 확정하기 전에,
왜 후보로 남아 있는지와 다음에 무엇을 할지 검토하는 단계다.

### 왜 사용되는지
current candidate, near miss, scenario 후보가 섞이면
사용자가 성과표만 보고 바로 투자 후보처럼 오해할 수 있다.
Candidate Review는 후보를 먼저 읽고,
compare 또는 Pre-Live Review로 넘길지 판단하게 만든다.

### 예시 / 필요 상황
- `Backtest > Candidate Review`
- `Candidate Board`
- `Inspect Candidate`
- `Suggested Next Step`
- `Open Candidate In Pre-Live Review`

중요한 경계:

- Candidate Review는 live trading approval이 아니다.
- `Suggested Next Step`은 투자 추천이 아니라 다음 검토 행동 제안이다.
- Pre-Live Review로 넘겨도 저장 전 초안일 뿐이다.

---

## Candidate Intake Draft

### 기본 설명
`Latest Backtest Run` 또는 `History` 결과를 후보 검토 화면에서 읽기 위한 임시 초안이다.
현재 candidate registry에 저장된 후보가 아니다.

### 왜 사용되는지
좋은 백테스트 결과가 나왔다고 바로 current candidate로 저장하면
투자 추천이나 자동 승격처럼 오해될 수 있다.
Candidate Intake Draft는 result snapshot, Real-Money signal, data trust를 먼저 확인하게 만든다.

### 예시 / 필요 상황
- `Latest Backtest Run > Candidate Review Handoff > Review As Candidate Draft`
- `History > Selected History Run > Review As Candidate Draft`
- `Candidate Review > Candidate Intake Draft`

중요한 경계:

- current candidate registry에 자동 저장되지 않는다.
- suggested record type은 참고용 초안 분류다.
- 후보 등록 / near-miss 기록 / Pre-Live 저장은 별도 검토 후 진행한다.

---

## Candidate Review Note

### 기본 설명
`Candidate Intake Draft`를 보고 운영자가 남기는 검토 판단 기록이다.
후보 자체를 등록하는 파일이 아니라, 후보 등록 전 단계의 판단 메모다.

### 왜 사용되는지
좋은 백테스트 결과를 바로 current candidate로 등록하면 후보 승격처럼 보일 수 있다.
반대로 아무 기록도 남기지 않으면 왜 보류했는지, 왜 다시 봐야 하는지 사라진다.
Candidate Review Note는 이 중간 판단을 안전하게 남긴다.

### 예시 / 필요 상황
- `Candidate Review > Candidate Intake Draft > Save Candidate Review Note`
- `Candidate Review > Review Notes`
- 저장 위치:
  - `.note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl`

중요한 경계:

- Candidate Review Note는 투자 추천이 아니다.
- Candidate Review Note는 live trading approval이 아니다.
- Candidate Review Note를 저장해도 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 자동 등록되지 않는다.

---

## Current Candidate Registry Draft

### 기본 설명
`Candidate Review Note`를 실제 current candidate registry row로 남기기 전에 확인하는 저장 전 초안이다.

### 왜 사용되는지
review note는 판단 메모이고, current candidate registry는 후보 목록이다.
두 파일의 역할이 다르기 때문에 후보 목록에 남기기 전에는
record type, strategy family, candidate role, title, result snapshot을 다시 확인해야 한다.

### 예시 / 필요 상황
- `Candidate Review > Review Notes > Prepare Current Candidate Registry Row`
- `Current Candidate Registry Row JSON Preview`
- `Append To Current Candidate Registry`

중요한 경계:

- 이 초안을 보는 것만으로는 registry에 저장되지 않는다.
- append 후에도 투자 승인이나 live trading approval이 아니다.
- `Reject For Now` review note는 기본적으로 registry append 대상이 아니다.

---

## Backlog Rebase

### 기본 설명
예전 phase에 남은 pending 항목, practical closeout 항목, remaining backlog를
현재 제품 상태 기준으로 다시 분류하는 작업이다.

### 왜 사용되는지
프로젝트가 길어지면 과거에 중요했던 미완료 항목이
지금도 blocker인지, 후속 phase 입력인지, future option인지 헷갈릴 수 있다.
Backlog Rebase는 이 항목들을 다시 이름 붙여
다음 phase가 과거 문서 혼선 없이 진행되게 만든다.

### 예시 / 필요 상황
- Phase 8, 9, 12~15, 18의 `manual_qa_pending` 상태를 현재 기준으로 다시 읽을 때
- Phase 18 remaining structural backlog가 Phase 28 입력인지 future option인지 정할 때

---

## Live Readiness / Final Approval

### 기본 설명
실제 돈을 넣어도 되는지 최종 판단하는 단계다.
현재 Phase 26~30에서는 아직 직접 다루지 않고, Phase 30 이후 별도 phase 후보로 둔다.

### 왜 사용되는지
Real-Money는 백테스트 결과의 위험 신호를 보는 진단표이고,
Pre-Live는 후보를 관찰하고 다음 행동을 기록하는 운영 절차다.
Live Readiness / Final Approval은 그 이후에
paper tracking 결과, blocker 해소 여부, 최종 승인 / 보류 / 거절 판단을 다루는 단계다.

### 예시 / 필요 상황
- 후보가 충분히 관찰되었고 데이터 / 전략 / 운영 blocker가 없다고 판단될 때
- 실제 투자 전 최종 승인 기록이 필요할 때
