# Phase 18 Larger Structural Redesign Plan

## 목적

- Phase 17 first three structural lever 이후에도
  current `Value` / `Quality + Value` anchor를 교체하는
  same-gate lower-MDD exact rescue가 없었기 때문에,
  더 큰 selection-structure redesign을 실제로 검증한다.
- 지금 핵심 질문은
  “새 전략을 늘릴까”가 아니라
  **기존 strongest family를 더 실전적으로 만들 수 있는 더 큰 구조가 있는가**
  이다.

## 이번 phase의 핵심 질문

1. trend rejection으로 비는 raw top-N slot을
   survivor reweighting이나 현금 유지 말고
   **다른 ranked candidate로 메우면**
   cash drag와 gate quality를 동시에 개선할 수 있는가
2. 이 redesign이
   current practical anchor를 바로 대체하진 못하더라도,
   적어도 meaningful rescue lane으로 남는가
3. `Value`와 `Quality + Value`에서
   같은 redesign이 같은 방향으로 작동하는가,
   아니면 family별로 반응이 분리되는가

## 현재 첫 구현 후보

- `Fill Rejected Slots With Next Ranked Names`
- 해석:
  - raw top-N을 먼저 고른다
  - `Trend Filter` 때문에 일부가 탈락하면
  - 랭킹의 다음 후보 중 trend를 통과하는 이름으로 빈 슬롯을 채운다
  - 그래도 빈 슬롯이 남으면 그때 기존
    `partial cash retention` 또는 survivor reweighting이 처리한다

## 왜 이 방향이 첫 slice인가

- `partial cash retention`은 `MDD`를 크게 낮췄지만 cash drag가 너무 컸다
- `defensive sleeve risk-off`는 gate는 유지했지만 `MDD` 개선이 없었다
- `concentration-aware weighting`은 gate는 유지했지만 downside 개선이 없었다

즉 지금은
“남는 cash를 어떻게 처리할까”보다
**애초에 빈 슬롯을 ranked candidate로 다시 채우는 구조**
가 더 직접적인 다음 질문이다.

## 첫 pass 성공 기준

- `Value`
  - trend-on structural probe에서
    `hold / blocked`보다 더 높은 gate recovery가 있는지
- `Quality + Value`
  - strongest blended point에서도
    cash share와 `MDD` 외에 gate recovery까지 같이 일어나는지
- 공통:
  - actual current anchor replacement가 가능한지
  - 아니면 “의미 있는 redesign lane이지만 anchor update는 아님”인지
    분명히 남길 것

## 현재 상태

- `in_progress`
- first slice 구현과 representative rerun first pass는 완료
- current first-pass reading:
  - `Value`: meaningful rescue 있음
  - `Quality + Value`: 개선은 있으나 still hold

## 주요 산출물

- current board
  - `.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md`
- implementation note
  - `.note/finance/phase18/PHASE18_NEXT_RANKED_FILL_IMPLEMENTATION_FIRST_SLICE.md`
- representative rerun report
  - `.note/finance/backtest_reports/phase18/PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md`
