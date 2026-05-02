# Phase 18 Next-Ranked Fill Implementation First Slice

## 목적

- strict annual family에
  `Fill Rejected Slots With Next Ranked Names`
  contract를 실제로 연결한다.
- 이 slice는
  `partial cash retention`과 `rank_tapered`의 중간 보정이 아니라,
  **selection-structure redesign**
  으로 읽어야 한다.

## 구현 범위

### 코드 연결

- `finance/strategy.py`
  - strict annual rebalancing block에서
    raw top-N 확정 후 trend rejection이 생기면
    ranked 다음 후보 중 trend를 통과하는 이름으로 빈 슬롯을 채우는 로직 추가
- `finance/sample.py`
  - strict annual DB-backed sample wrapper에
    `rejected_slot_fill_enabled` contract 추가
- `app/web/runtime/backtest.py`
  - strict annual runtime wrapper와 meta/warning surface에
    contract 연결
- `app/web/pages/backtest.py`
  - single / compare strict annual family form에
    `Fill Rejected Slots With Next Ranked Names` 옵션 추가
  - selection history / interpretation surface에
    `Filled Tickers`, `Rejected Slot Fill Count` 등 반영

### 새 result/meta surface

- result row
  - `Rejected Slot Fill Enabled`
  - `Rejected Slot Fill Active`
  - `Rejected Slot Fill Ticker`
  - `Rejected Slot Fill Count`
- runtime/meta
  - `rejected_slot_fill_enabled`

## 해석 원칙

1. raw top-N을 먼저 고른다
2. `Trend Filter`가 일부를 탈락시킨다
3. fill contract가 켜져 있으면 next-ranked eligible name으로 빈 슬롯을 먼저 채운다
4. 그래도 빈 슬롯이 남으면
   기존 `partial cash retention` 또는 survivor reweighting이 처리한다
5. `market regime`, `underperformance guardrail`, `drawdown guardrail`
   같은 full risk-off는 이 lane과 분리해서 읽는다

## 왜 이 slice가 의미 있는가

- Phase 17의 first three levers는 모두
  cash handling 또는 weighting 개선에 가까웠다
- 이번 slice는
  “빈 슬롯을 그대로 둘 것인가”가 아니라
  **“랭킹 안에서 다음 후보를 실제로 다시 뽑을 것인가”**
  를 묻는 더 큰 구조 변경이다

## 현재 first-pass 결과 요약

- `Value`
  - trend-on probe에서
    cash share와 `MDD`는 개선되지만
    still `hold / blocked`
- `Quality + Value`
  - `CAGR`, `MDD`, cash share는 개선
  - 그러나 `hold / blocked` 유지

## 현재 결론

- 이 contract는 구현 가치가 충분하다
- 특히 `Value`에서는 cash drag를 줄이는 selection-structure lane으로는 의미가 있다
- 다만 first pass 기준으로는
  `Value`, `Quality + Value` 모두 current practical anchor 자체를 교체하는 결과는 아니다
