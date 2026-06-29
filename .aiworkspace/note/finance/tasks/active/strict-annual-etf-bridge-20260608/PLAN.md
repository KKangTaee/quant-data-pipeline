# Strict Annual + GTAA / Equal Weight Bridge 2026-06-08

Status: Completed
Last Verified: 2026-06-08

## Purpose

Backtest 3차 개발의 3B scope로, 3A에서 evidence-mature group으로 고정한 `Strict Annual 3종 + GTAA + Equal Weight`를 Practical Validation으로 이어가기 전 역할 / target use / required validation / next workflow로 정리한다.

## 이걸 하는 이유?

3A panel은 전략별 maturity를 보이게 했지만, 사용자가 보기에는 아직 "가이드"에 가깝다.
3B는 가장 성숙한 후보군을 실제 후보 조합 판단으로 한 단계 더 가까이 옮긴다.
다만 이번 차수도 live selection, registry write, runtime rerun이 아니라 Backtest Analysis 안의 read-only bridge/handoff 기능이다.

## Tentative 3차 Roadmap

| 차수 | 목적 | 바뀔 범위 | 완료 조건 | 다음 차수 연결 |
| --- | --- | --- | --- | --- |
| 3A | Strategy evidence inventory / direction panel | Streamlit-free read model, Backtest Analysis read-only UI, docs | Completed | 3B bridge 후보군 선택 근거 |
| 3B | Strict annual + GTAA / Equal Weight portfolio bridge | Streamlit-free bridge read model, Backtest Analysis read-only UI, docs | evidence-mature group의 component role / target use / validation gap / recommended workflow 표시 | Practical Validation 연결 설계 |
| 3C | Risk-On Momentum governance design | Daily swing governance plan | deferred 상태를 유지할지 승격할지 별도 승인 | Backtest Analysis와 monitoring 경계 유지 |
| 3D | ETF evidence expansion | GRS / Risk Parity / Dual Momentum evidence hub | current anchor와 weakness report 보강 | ETF family maturity 개선 |

현재 진행 차수는 3B다.

## Scope

- `Strict Annual 3종 + GTAA + Equal Weight`만 bridge group으로 다룬다.
- 각 전략의 component role, target use, current anchor, known weakness, required Practical Validation evidence, recommended next workflow를 read-only로 보여준다.
- Bridge-level suggested mix intent와 validation checklist를 함께 제공한다.
- Streamlit-free read model부터 만들고 focused tests를 붙인다.
- Backtest Analysis UI에 3A panel 아래 또는 근처에 read-only bridge section을 붙인다.

## Not In Scope

- registry / saved JSONL / run history rewrite.
- strategy runtime behavior 변경 또는 후보 rerun.
- Practical Validation result 저장 / Final Review decision 저장.
- DB schema 변경.
- provider / FRED direct fetch.
- Risk-On Momentum governance 구현.
- quarterly maturation 구현.
- GRS / Risk Parity / Dual Momentum current-candidate rerun.
- live trading / broker order / auto rebalance 설계.

## Stop Condition

- Bridge read model tests가 group membership, required validation, deferred exclusions, copy semantics를 검증한다.
- Backtest Analysis UI에서 bridge section이 보인다.
- UI / engine boundary check가 통과한다.
- Browser QA 결과가 RUNS에 기록된다.

## Closeout

3B is complete.
It added a read-only bridge/handoff layer only; it did not create Practical Validation results, Final Review decisions, registry writes, saved setup writes, or strategy runtime changes.
