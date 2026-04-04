# Phase 12 Real-Money Promotion Contract

## 목적

- 현재 전략군을 “실행 가능” 수준에서
  **실전 투자 판단에 가까운 계약**
  으로 끌어올리기 위해 필요한 공통 기준을 고정한다.

## 이 문서에서 말하는 promotion의 뜻

여기서 promotion은
단순히 UI에 전략을 더 노출하는 뜻이 아니다.

promotion은
다음 질문에 더 defensible하게 답할 수 있는 상태를 뜻한다.

1. 이 전략의 universe/data contract가 명확한가
2. investability 문제가 표면화되어 있는가
3. turnover / cost를 무시하지 않는가
4. 결과를 benchmark / drawdown / underperformance 관점에서 읽을 수 있는가
5. current limitation이 과장 없이 드러나는가

## 용어 정리

아래 용어들은
이 문서에서 반복해서 쓰이므로,
먼저 짧게 뜻을 맞춰두고 읽는 것이 좋다.

### `contract`

- 여기서 `contract`는 코드 문법이 아니라,
  **이 전략을 어떤 규칙과 전제 위에서 읽을 것인지에 대한 약속**
  을 뜻한다.

### `universe`

- 전략이 후보로 삼는 종목/ETF 묶음이다.
- 쉽게 말하면
  “이 전략이 처음부터 살펴보는 대상 집합”
  이다.

### `universe / data contract`

- 어떤 universe를 썼는지
- 그 universe를 어떤 시점 기준 데이터로 만들었는지
- 그 데이터의 한계가 무엇인지
를 함께 설명하는 약속이다.

### `fixed ETF set`

- 미리 정해둔 ETF 목록을 계속 쓰는 방식이다.
- 예:
  - 특정 자산배분 전략에서 정해진 ETF 바구니만 사용하는 경우

### `managed static research universe`

- 현재 기준으로 관리 중인 종목 묶음을 먼저 정하고,
  그 묶음을 들고 과거를 돌려보는 연구용 universe 계약이다.
- 빠른 연구에는 유용하지만,
  완전한 실전형 historical universe와는 다르다.

### `historical dynamic PIT universe`

- 각 리밸런싱 시점마다
  그 당시 기준으로 universe membership를 다시 계산하는 방식이다.
- 실전 투자 검증에 더 가까운 contract다.

### `PIT` / `point-in-time`

- 과거 어느 시점의 데이터만 사용해서
  그 시점에서 알 수 있었던 정보로 판단하는 방식이다.
- look-ahead를 줄이기 위한 핵심 개념이다.

### `look-ahead bias`

- 과거 백테스트를 할 때
  사실은 그 당시 몰랐어야 할 미래 정보를 써버리는 왜곡이다.

### `survivorship bias`

- 지금까지 살아남은 종목만 보고 과거를 되돌아보는 왜곡이다.
- 이미 사라진 종목이 빠지면,
  과거 성과가 실제보다 좋아 보일 수 있다.

### `continuity`

- 가격/상장 상태/프로필 정보가
  시간축에서 자연스럽게 이어지는지 보는 개념이다.
- 쉽게 말하면
  “이 종목을 그 기간 동안 끊김 없이 추적할 수 있었는가”
  를 보는 것이다.

### `investability`

- 이론상 계산만 가능한 종목이 아니라,
  실제로 매매 가능한 대상인지 보는 개념이다.

### `investability filter`

- 너무 비싸거나 싼 종목이 아니라,
  유동성/상장상태/데이터 상태를 고려해
  실제 매매 가능한 후보만 남기는 필터다.

### `liquidity proxy`

- 거래대금, 거래량 같은 값으로
  유동성을 대략 추정하는 지표다.

### `listing-age`

- 상장 후 얼마나 시간이 지났는지를 뜻한다.
- 너무 신생 종목은 실전 운용에서 제외할 수도 있다.

### `stale`

- 최신이어야 할 가격/프로필/기타 데이터가
  특정 시점 이후 멈춰 있는 상태를 뜻한다.

### `delisted`

- 상장폐지되었거나,
  현재 정상 거래 대상으로 보기 어려운 상태를 뜻한다.

### `profile issue`

- asset profile이나 symbol metadata에
  오류, 누락, 상태 이상이 있는 경우를 뜻한다.

### `turnover`

- 포트폴리오가 리밸런싱 때 얼마나 많이 교체되는지 보는 지표다.
- turnover가 높을수록 실제 비용도 커지기 쉽다.

### `transaction cost`

- 실제 매매할 때 드는 비용 전체를 말한다.
- 수수료, spread, slippage 등을 포함해 생각한다.

### `commission`

- 매매 수수료다.

### `spread`

- 매수호가와 매도호가 차이에서 생기는 거래 비용이다.

### `slippage`

- 내가 기대한 가격과 실제 체결 가격 사이에서 생기는 차이다.

### `portfolio guardrail`

- 포트폴리오가 너무 위험하게 움직이지 않도록 두는 안전 규칙이다.
- 예:
  - 종목 수 제한
  - 최대 비중 제한
  - cash 처리 규칙

### `benchmark`

- 전략과 비교할 기준 지수나 기준 포트폴리오다.

### `drawdown`

- 고점 대비 얼마나 크게 빠졌는지를 보여주는 지표다.

### `rolling underperformance`

- 일정 기간 기준으로
  benchmark보다 뒤처지는 구간이 반복되는지 보는 개념이다.

### `validation surface`

- 전략 결과를 해석하기 위해 보는 화면/지표 묶음이다.
- 단순 수익률이 아니라,
  benchmark, drawdown, turnover 같은 판단 재료를 포함한다.

### `hardening`

- 전략을 더 현실적으로 읽을 수 있게
  규칙, 필터, 비용, 안전장치를 보강하는 작업이다.

### `promotion`

- 연구용 전략을 더 높은 신뢰도의 후보로 올리는 작업이다.
- 단순 노출 확대가 아니라,
  더 엄격한 계약을 붙이는 과정이다.

### `research-only`

- 연구와 탐색에는 쓰되,
  실전 판단 근거로는 아직 쓰지 않는 상태다.

### `production candidate`

- 실전형으로 키울 가치가 크고,
  현재 hardening 대상이 되는 전략 상태다.

### `real-money candidate`

- investability / cost / guardrail / validation이 어느 정도 갖춰져서,
  실제 투자 판단 참고에 더 가까워진 상태다.

### `hold`

- 이번 phase에서 우선순위를 올리지 않고,
  현재 상태를 유지하면서 다음 조건을 기다리는 뜻이다.

## 공통 계약 축

## 1. Universe / Data Contract

쉬운 뜻:

- 이 전략이 **어떤 종목 묶음**을 대상으로 돌아가는지,
  그리고 그 종목 묶음을 **어떤 시점 기준 데이터로 만들었는지**
  를 명확히 적는 축이다.
- 쉽게 말하면
  “이 백테스트가 애초에 어떤 재료로 시작했는가”
  를 설명하는 부분이다.

- fixed ETF set인지
- managed static research universe인지
- dynamic PIT validation contract인지
- look-ahead / survivorship / continuity 한계가 어디까지인지

왜 필요한가:

- 같은 전략이라도
  어떤 universe를 쓰느냐에 따라 결과가 크게 달라질 수 있다.
- 이 부분이 불명확하면
  결과가 좋아도
  “실제로 그때도 이 종목들을 알 수 있었는가?”
  라는 질문에 답하기 어렵다.
- 즉 실전형 전략으로 읽히려면
  수익률보다 먼저
  **대상 universe와 데이터 계약이 명확해야 한다.**

실전형으로 읽히려면
이 계약이 먼저 명시되어야 한다.

## 2. Investability Filter

쉬운 뜻:

- 백테스트에서 고른 종목이
  **실제로 매매 가능한 상태였는지**
  를 확인하는 필터다.
- 쉽게 말하면
  “이 종목을 현실에서도 살 수 있었는가?”
  를 점검하는 부분이다.

- 최소 가격
- 최소 유동성 proxy
- listing-age / continuity
- stale / delisted / profile issue 처리

왜 필요한가:

- 백테스트는 종종
  너무 싸거나,
  거래가 거의 없거나,
  사실상 상장 초반이라 불안정한 종목까지
  그대로 집어넣기 쉽다.
- 하지만 실전에서는 그런 종목은
  체결이 어렵거나,
  슬리피지가 크거나,
  아예 접근 자체가 불편할 수 있다.
- 그래서 investability filter는
  **이론상 가능한 결과를 현실에 가까운 결과로 바꾸는 첫 번째 장치**
  다.

실전에서 살 수 없는 종목/상태가
백테스트에서 자연스럽게 걸러지도록 만드는 축이다.

## 3. Turnover / Transaction Cost

쉬운 뜻:

- 전략이 얼마나 자주 갈아타는지,
  그리고 그때마다 비용이 얼마나 들 수 있는지
  를 반영하는 축이다.
- 쉽게 말하면
  “이 전략이 수익은 좋아 보여도,
  실제로 갈아타는 비용 때문에 깎이면 얼마나 남는가?”
  를 보는 부분이다.

- commission
- spread / slippage first pass
- turnover summary
- rebalance 빈도와 turnover 해석

왜 필요한가:

- 백테스트가 매매 비용을 전혀 넣지 않으면
  특히 교체가 잦은 전략은
  결과가 과하게 좋아 보일 수 있다.
- 실전에서는
  거래 수수료뿐 아니라
  bid-ask spread, 슬리피지, 체결 타이밍 차이도 생긴다.
- 따라서 이 축은
  **전략 성과를 “차트상 수익률”에서 “실제로 남을 수익률”로 가까이 가져가는 역할**
  을 한다.

실전 투자용으로 읽으려면
비용 가정을 완전히 비워둔 채 결과만 보는 방식에서 벗어나야 한다.

## 4. Portfolio Guardrail

쉬운 뜻:

- 전략이 포트폴리오를 어떻게 운용할지에 대한
  **안전 규칙 / 행동 규칙**
  을 정하는 축이다.
- 쉽게 말하면
  “이 전략이 아무리 좋은 종목을 골라도,
  포트폴리오가 너무 위험하게 쏠리지 않게 막는 장치”
  다.

- 최대 종목 수
- 단일 종목 최대 비중
- cash handling
- overlay / regime 적용 시 동작 규칙

왜 필요한가:

- 실전에서는
  종목 하나에 너무 몰리거나,
  cash 처리 규칙이 모호하거나,
  overlay가 켜졌을 때 행동이 들쭉날쭉하면
  운영 자체가 어려워진다.
- 같은 전략이라도
  guardrail이 있느냐 없느냐에 따라
  체감 리스크와 운영 난이도가 크게 달라진다.
- 그래서 이 축은
  **전략 아이디어를 실제 포트폴리오 규칙으로 번역하는 역할**
  을 한다.

실전형 전략은
결과뿐 아니라 포트폴리오 행동 규칙도 읽혀야 한다.

## 5. Validation Surface

쉬운 뜻:

- 전략 결과를
  단순 누적 수익률 한 줄이 아니라,
  **실전 판단에 필요한 여러 각도에서 읽을 수 있게 보여주는 화면/지표**
  를 뜻한다.
- 쉽게 말하면
  “이 전략이 왜 괜찮아 보이는지, 혹은 왜 위험한지”
  를 사람이 해석할 수 있게 만드는 부분이다.

- benchmark 비교
- drawdown
- rolling underperformance
- turnover / rebalance summary
- strategy interpretation

왜 필요한가:

- 누적 수익률만 보면
  중간에 얼마나 크게 빠졌는지,
  benchmark보다 자주 뒤처지는지,
  리밸런싱이 과도한지
  를 놓치기 쉽다.
- 실전 투자에서는
  “얼마나 벌었나” 못지않게
  “어떤 위험을 감수했나”
  가 중요하다.
- 따라서 validation surface는
  **전략을 채택할지 말지 결정하는 판단면**이라고 보면 된다.

실전형 전략은
“수익률이 좋다”를 넘어서
**어떤 위험과 trade-off 위에서 나온 결과인지**
를 읽을 수 있어야 한다.

## Promotion Status Language

### `research-only`

- prototype
- exploratory path
- 실전 판단 기준으로 쓰지 않음

### `production candidate`

- 실전형 승격 가치가 크고
  Phase 12에서 hardening 대상으로 삼는 전략

### `real-money candidate`

- investability / cost / guardrail / validation surface까지 갖추고
  실제 투자 판단 참고에 가까워진 전략

## 이번 phase의 기본 적용 순서

1. ETF 전략군
2. strict annual family
3. quarterly strict prototype family는 hold

## 이번 phase에서의 보수적 원칙

- quarterly prototype을 억지로 승격하지 않는다
- portfolio workflow polish를 전략 계약보다 우선하지 않는다
- current limitation을 숨기지 않는다

## done condition

이번 phase는 아래가 만족되면 practical closeout 후보가 된다.

1. production-priority 전략군이 고정되었다
2. 공통 promotion contract가 current code 방향과 맞춰졌다
3. ETF 전략군에 first hardening이 들어갔다
4. strict annual family에 next promotion scope가 연결되었다
5. quarterly hold rule이 문서와 UI semantics에서 흔들리지 않는다
