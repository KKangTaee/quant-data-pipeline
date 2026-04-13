# Phase 16 Current Chapter TODO

## 목표

`Value > Strict Annual` current practical anchor를 유지하면서
`MDD`를 더 낮추는 bounded downside refinement를 진행한다.

## 현재 앵커

- family: `Value`
- variant: `Strict Annual`
- anchor: `Top N = 14 + psr`
- result: `CAGR 28.13% / MDD -24.55% / real_money_candidate / paper_probation / review_required`

## 완료된 작업

- [x] `Top N` narrow band first pass
  - `13 / 14 / 15`와 바깥쪽 확인용 `12 / 16`까지 확인
- [x] bounded one-factor addition sweep
  - `psr`, `per`, `pbr`, `por`, `ev_ebit`, `fcf_yield`
- [x] bounded replacement probe
  - `replace_sales_with_psr_t14`
  - `replace_ocf_with_psr_t14`
- [x] minimal overlay sensitivity
  - `trend on/off`, `market regime on/off`

## 이번 단계 결론

- `Top N = 14 + psr`가 여전히 best practical point다
- 더 낮은 `MDD`를 유지하면서 gate를 통과하는 bounded variant는 찾지 못했다
- overlay는 practical gate를 보존하는 데 도움이 되지 않았다

## 다음 판단

- `Value` strategy log에 이번 bounded search를 append한다
- 필요하면 `Quality + Value`로 같은 방식의 downside follow-up을 연다
- 아니면 이 결과를 기준으로 Phase 16 first pass를 closeout 한다
