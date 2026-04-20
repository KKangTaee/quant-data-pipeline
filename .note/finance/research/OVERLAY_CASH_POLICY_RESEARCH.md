# Overlay Cash Policy Research

## Question

현재 `Quality / Value / Quality + Value` monthly stock-selection backtest에서
overlay가 일부 종목만 탈락시킬 때,

- 탈락한 비중을 `cash / T-bills`로 남겨야 하는지
- 아니면 남은 종목들에 다시 균등배분해야 하는지

를 실무 관행 관점에서 정리하고,
현재 프로젝트에 더 맞는 정책을 결정하는 것이 목적이다.

이번 문서는 **현재 전략 아키텍처 우선** 기준으로 정리한다.
즉, `top-N stock selection` 이후 overlay가 적용되는 현재 strict family와 가장 유사한 사례를 우선 본다.

---

## Current Repo Behavior

현재 구현은 **부분 탈락 시 survivor reweighting**이다.

- `top_N`으로 raw 후보를 먼저 고른다.
- trend overlay는 raw 후보 중 일부를 탈락시킨다.
- 하나라도 생존 종목이 남으면, 그 생존 종목들에 대해 `base_balance / len(held_tickers)`로 다시 100% 균등배분한다.
- 따라서 **부분 탈락만으로는 현금 비중이 남지 않는다.**
- `100% cash`가 되는 경우는 현재 두 가지다.
  - trend overlay가 raw 후보를 전부 탈락시킨 경우
  - market regime overlay가 `risk_off`여서 포트폴리오 전체를 막은 경우

현재 코드 근거:

- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L675)
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L699)
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L705)

현재 구현과 문구 사이에는 작은 불일치가 있다.

- runtime warning 문구는 아직
  `Close < MA(window)`인 선택 종목이 `cash`로 간다고 읽히는 표현이 남아 있다.
- selection interpretation 일부 문구도
  부분 탈락분이 `cash`로 간다고 읽힐 수 있다.
- 하지만 실제 코드 의미는
  **부분 탈락 -> 생존 종목 재배분**
  이다.

관련 문구 위치:

- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py#L952)
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py#L1171)
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/pages/backtest.py#L2315)

---

## Practitioner Patterns

실무 사례를 현재 질문과 가장 가까운 세 가지 버킷으로 나눠 보면 패턴이 비교적 분명하다.

### A. Stock-selection / factor-filter portfolios

이 유형은

- 주식 유니버스를 정하고
- factor / screen / filter로 상위 종목을 고른 뒤
- 그 결과 바스켓을 **다시 equal-weight 또는 정해진 규칙으로 구성**

하는 구조다.

이 경우 실무 문헌과 운용 설명은 대체로
**“탈락한 종목의 slot을 현금으로 남긴다”**보다
**“남은 종목들로 포트폴리오를 다시 구성한다”**
에 가깝다.

근거:

1. **Alpha Architect - Value and Momentum Investing: Combine or Separate?**
   - top 50/75/100/... stocks를 factor signal로 고르고
   - `All the portfolios are equal-weighted`
   - 즉 screen/selection 이후의 결과 바스켓을 full-investment equal-weight 포트폴리오로 다룬다.

2. **Alpha Architect - Our Value Momentum Trend Philosophy (VMOT)**
   - QVAL / QMOM 등 underlying stock sleeves는
     - 40~50 stocks
     - equal-weight
     - periodic rebalance
   - stock-selection layer 자체는 **concentrated stock basket construction**
     로 설명되고, 개별 탈락 slot을 현금으로 남기는 구조로 설명되지 않는다.

3. **OLZ - Beating the equally weighted portfolio – using simple factor filters**
   - weakest momentum, highest volatility 등 나쁜 종목을 제외하고
   - `equal weighting of the remaining stocks`
   - 필터 후 남은 종목을 다시 equal-weight하는 구조를 매우 직접적으로 보여준다.

요약:

- **개별 종목 filter / screen / top-N selection**의 문맥에서는
  partial rejection 뒤에 **survivors를 재구성하는 방식**이 더 일반적이다.

### B. Tactical asset allocation / sleeve-level overlays

이 유형은

- SPY, EFA, BND, VNQ 같은 asset sleeves가 처음부터 정해져 있고
- 각 sleeve가 자기 신호를 통과하면 유지
- 실패하면 그 **sleeve의 목표 비중을 cash / T-bills**로 둔다

는 구조다.

근거:

1. **Meb Faber / Cambria - A Quantitative Approach to Tactical Asset Allocation**
   - 대표적인 rule은:
     - monthly price > moving average -> 보유
     - monthly price < moving average -> `sell and move to cash`
   - 이것은 **slot-preserving asset sleeve 모델**이다.

2. **Quantpedia - Asset Class Trend Following**
   - 예시 구현도
     - 각 asset ETF를 기준으로
     - SMA 위에 있을 때만 보유
     - 아니면 `stay in cash`
   - 즉 자산군별 slot을 현금으로 대체하는 문맥이다.

요약:

- **정해진 asset sleeves / target weights**가 먼저 있는 TAA 구조에서는
  partial failure를 **cash / T-bills로 남기는 방식**이 흔하다.

### C. Market-regime / hedge overlays

이 유형은

- 개별 종목 몇 개를 떨어뜨리는 방식이 아니라
- 포트폴리오 전체의 net exposure를 조절하거나
- hedge ratio를 높이는 방식이다.

근거:

1. **Alpha Architect - VMOT**
   - trend-following component는
     - 개별 종목 제외가 아니라
     - U.S./International equity sleeves에 대해
     - broad index ETF short hedge를 붙이는 구조다.
   - signal이 하나면 50% hedge,
     둘 다면 fully hedged처럼
     **cash 대신 hedge overlay**를 쓴다.

요약:

- market-regime overlay는
  **cash retention**보다
  **hedge / net exposure control**
  로 구현되는 경우도 많다.

---

## When Reweighting Is Typical

다음 조건이면 **survivor reweighting**이 자연스럽다.

1. overlay가 **stock eligibility filter** 역할을 할 때
2. 포트폴리오가 `top-N names`라는 결과 바스켓으로 이해될 때
3. 목표가 “나쁜 종목 제외 후 남은 좋은 종목에 계속 fully invested”일 때
4. cash는 의도한 방어 자산이 아니라, 단지 no-position의 부산물일 뿐일 때
5. reporting에서 `Cash`를 “실제 보유 현금”으로 해석하고 싶을 때

장점:

- top-N factor strategy의 기본 의미를 유지한다
- 부분 탈락 때도 net exposure가 유지된다
- selection interpretation이 단순하다
- TAA와 다른 stock-selection 계열의 실무 관행과 더 잘 맞는다

단점:

- 사용자가 기대한 “탈락분은 안전자산으로 쉬게 한다”는 해석과는 다를 수 있다
- 방어성은 cash-retention보다 약하다

---

## When Cash Retention Is Typical

다음 조건이면 **partial cash retention**이 더 자연스럽다.

1. 각 slot이 원래부터 정해진 weight sleeve일 때
2. overlay의 목적이 단순 filter가 아니라 **capital preservation**일 때
3. 실패한 sleeve의 비중을 고의적으로 쉬게 만들고 싶을 때
4. 비교 대상이 stock-selection portfolio가 아니라 TAA / defensive allocation일 때
5. 사용자에게 `Cash Share`를 명시적인 리스크 관리 도구로 보여주고 싶을 때

장점:

- 방어 직관이 강하다
- 사용자 입장에서 이해가 쉬운 경우가 많다
- TAA/asset-sleeve 문법과 잘 맞는다

단점:

- current top-N stock-selection architecture와는 살짝 다른 철학이다
- partial rejection이 많아질수록 cash drag가 커진다
- factor portfolio의 full-investment 비교가 어려워질 수 있다

---

## Recommendation For This Project

현재 프로젝트의 strict family는

- 월말마다
- 상위 `N`개 stock names를 고르고
- 그 결과 바스켓에 overlay를 적용하는

**stock-selection portfolio**에 가깝다.

따라서 현재 전략 타입에는
**partial overlay rejection -> survivor reweighting**
이 더 실무적으로 자연스럽고, 더 방어 가능한 기본값이라고 본다.

권고:

1. **현재 코드 로직은 유지**
   - 부분 탈락 시 생존 종목 재균등배분 유지
2. **설명 문구를 코드 의미에 맞게 수정**
   - “부분 탈락분은 cash로 간다”는 식의 표현 제거
3. 사용자가 원하면 나중에 별도 정책으로 추가
   - 예: `Overlay Cash Policy`
     - `reweight_survivors` (default)
     - `retain_rejected_weight_as_cash`

즉 이번 질문에 대한 최종 답은:

- **현재 전략 타입에서는 survivor reweighting이 더 일반적이고 더 적합하다**
- **partial cash retention은 다른 전략 철학으로 보는 편이 낫다**

---

## Implications For UI / Metrics / Future Code

이번 조사 기준으로, 현재 프로젝트의 다음 정리 방향은 명확하다.

### 1. UI / warning copy

현재 일부 문구는
부분 탈락분이 현금으로 간다고 읽히지만,
실제 동작은 그렇지 않다.

따라서 다음 정리가 필요하다.

- trend overlay warning 문구
- interpretation summary 문구
- `Cash Share` 도움말

를 **부분 탈락 = survivor reweighting** 의미에 맞게 수정

### 2. Cash / Cash Share 해석

현재 strict family에서 `Cash`가 커지는 경우는 주로:

- raw 후보 전부 탈락
- market regime risk-off

이다.

따라서 `Cash Share`는
“overlay가 몇 개 종목을 잘랐는가”의 직접 지표가 아니라,
**실제로 fully or near-fully de-risked 되었는가**
에 더 가깝다.

### 3. Future optional extension

사용자가 TAA식 의미를 원하면,
현재 overlay 자체를 뒤집기보다
**별도 정책 옵션**으로 추가하는 게 더 안전하다.

예:

- `reweight_survivors`
- `retain_rejected_weight_as_cash`

이렇게 두 policy를 노출하면,
strategy class와 해석이 분명히 분리된다.

---

## Sources

1. Alpha Architect, **Value and Momentum Investing: Combine or Separate?**
   - https://alphaarchitect.com/value-and-momentum-investing-combine-or-separate/
   - focused stock-selection portfolios, top-N selection, equal-weight construction

2. Alpha Architect, **Our Value Momentum Trend Philosophy (VMOT)**, 2018 PDF
   - https://funds.alphaarchitect.com/wp-content/uploads/2018/05/VMOT_vF.pdf
   - stock-selection sleeves are concentrated equal-weight baskets
   - regime/trend component is implemented as hedging, not per-name cash slots

3. OLZ, **Beating the equally weighted portfolio – using simple factor filters**
   - https://olz.ch/en/insights/beating-the-equally-weighted-portfolio-using-simple-factor-filters
   - explicit example of exclusion filter followed by equal weighting of remaining stocks

4. Mebane Faber / Cambria, **A Quantitative Approach to Tactical Asset Allocation**
   - https://www.cambriainvestments.com/wp-content/uploads/2018/01/A-Quantitative-Approach-to-Tactical-Asset-Allocation.pdf
   - canonical monthly moving-average TAA example using sell-and-move-to-cash semantics

5. Quantpedia, **Asset Class Trend-Following**
   - https://quantpedia.com/strategies/asset-class-trend-following
   - secondary explanatory source showing the common TAA convention:
     hold each asset sleeve only when above SMA, otherwise stay in cash

---

## Bottom Line

실무에서 두 방식이 모두 존재하지만,

- **stock-selection filter 전략**에서는 보통 `survivor reweighting`
- **asset-sleeve TAA 전략**에서는 보통 `cash retention`

이 더 일반적이다.

현재 repo의 strict family는 전자에 더 가깝기 때문에,
기본 정책은 **현재 코드 유지 + 문구 정정**이 가장 합리적이다.
