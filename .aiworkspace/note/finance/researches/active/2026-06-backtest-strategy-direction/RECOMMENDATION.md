# Recommendation

Status: Active
Last Verified: 2026-06-08

## One-Line Recommendation

3차 새 세션의 첫 개발 scope는 `Strategy Evidence Inventory / Direction Panel`로 시작하고, 그 안에서 strict annual 3종과 GTAA / Equal Weight bridge를 첫 usable candidate group으로 고정한다.

## Why This Direction

현재 Backtest는 전략 실행 범위가 넓지만, 제품적으로 믿고 다음 단계로 넘길 수 있는 evidence maturity는 전략마다 다르다.
따라서 새 전략을 추가하거나 Risk-On Momentum을 바로 monitoring에 붙이는 것보다, 먼저 전략군별 성숙도와 next action을 사용자에게 보이게 하는 편이 안전하다.

이 방향은 현재 제품 원칙과 맞다.

- Backtest Analysis는 후보 source 생성 단계다.
- Practical Validation / Final Review가 investability evidence와 selected-route gate를 소유한다.
- Portfolio Monitoring은 read-only monitoring이며 live approval이 아니다.

## Recommended 1st Build Scope

### Step 1. Strategy Evidence Inventory Read Model

- 각 strategy key에 대해 maturity row를 만든다.
- 최소 컬럼: strategy, family, intended role, runtime support, compare support, candidate replay support, validation readiness, monitoring readiness, current anchor, main weakness, next action.
- Streamlit-free service/read model로 시작한다.

### Step 2. Backtest Analysis Direction Panel

- `Backtest > Backtest Analysis` 또는 Reference / report surface 중 한 곳에 read-only direction panel을 붙인다.
- 첫 구현에서는 registry write, saved setup write, backtest execution change를 만들지 않는다.

### Step 3. Strict Annual + GTAA / EW Bridge Handoff

- Value / Quality / Quality+Value strict annual current anchors와 GTAA / EW sleeve 역할을 한 table로 보여준다.
- `component role`, `known weakness`, `required validation`, `recommended next workflow`를 표시한다.

### Step 4. Next Scope Selector

- 사용자가 다음 구현 scope를 고를 수 있게 아래 선택지를 남긴다.
  - strict annual + GTAA/EW bridge validation
  - Risk-On Momentum governance
  - ETF strategy evidence expansion
  - quarterly prototype maturation

## Recommended Next Phase After 1st Build

| Phase | Output | Why |
| --- | --- | --- |
| 3A | Strategy Evidence Inventory / Direction Panel | 전략별 성숙도와 next action을 제품에서 확인한다. |
| 3B | Strict Annual + GTAA/EW Portfolio Bridge | 가장 evidence가 강한 후보군을 Practical Validation-ready bridge로 정리한다. |
| 3C | Risk-On Momentum Governance | daily swing lane을 validation / monitoring에 연결할지 별도 설계한다. |
| 3D | ETF Evidence Expansion | GRS / Risk Parity / Dual Momentum의 current anchor와 report gap을 채운다. |

## What Not To Do Yet

- Risk-On Momentum 5D를 바로 Final Review 후보나 monitoring signal로 승격하지 않는다.
- Quarterly prototype을 strict annual과 같은 readiness로 표현하지 않는다.
- 새 strategy discovery나 optimizer를 추가하지 않는다.
- `docs/ROADMAP.md`를 research 결과만으로 확정 변경하지 않는다.
- registry / saved JSONL을 정리하거나 rewrite하지 않는다.
- live approval, broker order, account sync, auto rebalance를 설계하지 않는다.

## Decision Rules

Proceed when:

- 3차 새 세션이 이 research bundle을 읽고 첫 scope를 하나 고른다.
- 구현 범위가 read-only inventory / direction panel인지, validation bridge인지 분명하다.
- 필요한 owner skill이 선택된다.
  - Backtest UI / workflow: `finance-backtest-web-workflow`
  - Strategy runtime: `finance-strategy-implementation`
  - 통합 / diff 검토: `finance-integration-review`
  - 구현 후 durable docs sync: `finance-doc-sync`

## Final Recommendation

이 세션에서는 2차 direction research를 여기서 닫고, 3차는 새 구현 세션으로 분리한다.

새 세션의 시작 문장은 아래처럼 잡는 것이 좋다.

> `.aiworkspace/note/finance/researches/active/2026-06-backtest-strategy-direction/NEXT_SESSION_HANDOFF.md`를 읽고, 3A `Strategy Evidence Inventory / Direction Panel` 구현 task를 열어줘.

이렇게 하면 새 세션은 분석을 반복하지 않고, product boundary와 첫 구현 범위를 바로 잡을 수 있다.
