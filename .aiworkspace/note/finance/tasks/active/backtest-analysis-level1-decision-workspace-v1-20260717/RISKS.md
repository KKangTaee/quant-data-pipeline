# Risks

## Current Risks

### Large Existing UI Surfaces

`backtest_result_display.py`와 `backtest_compare/page.py`가 크고 다수의 legacy
contract를 포함한다. one-shell이 기존 runtime을 직접 재작성하지 않도록 adapter
seam과 focused regression test를 먼저 만든다.

### Streamlit Rerun Lifecycle

script rerun 자체를 없앨 수는 없다. stable context와 mutable result projection을
분리하지 않으면 실행 시 전체 화면 reset처럼 보이는 문제가 재발할 수 있다.

### Persistence Side Effects

Run History, saved Mix, Level2 candidate registry가 서로 다른 경로에 기록된다.
테스트는 temp path를 사용하고 실제 registry / history / saved JSONL을 stage하지
않는다.

### Strategy Metadata Drift

purpose group과 maturity를 UI에서 중복 정의하면 React / fallback이 달라질 수 있다.
Python read model을 단일 source로 유지한다.

### Result Overclaim

높은 performance를 후보 적합성으로 잘못 해석할 위험이 있다. Level1 Gate는 실행,
data readiness, contract freshness만 소유하며 실제 투자 판단은 Level2 / Level3에
남긴다.

### Scope Expansion

Risk-On Momentum 5D runtime 완성, 신규 provider, DB / strategy runtime 재설계는
별도 승인 없이는 이번 task에 포함하지 않는다.
