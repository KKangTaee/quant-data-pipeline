# Distinct Strategy Portfolio Discovery 2026-06-09

Status: In Progress
Last Verified: 2026-06-09

## Purpose

이전 GTAA U5 / GTAA U3 / GRS 후보는 SPY 대비 CAGR / MDD 조건과 Monitoring 등록 조건을 만족했지만, GTAA family가 두 번 들어갔다.
이번 작업은 각 component가 서로 다른 strategy family를 쓰는 조건으로 다시 탐색한다.

## 이걸 하는 이유?

사용자는 단순 성과 우위뿐 아니라 구성 논리의 다양성을 원한다. 같은 strategy family를 두 개 넣으면 universe만 다른 tactical momentum sleeve를 중복 보유하는 셈이라, portfolio construction 측면에서 아쉬움이 남는다.

## Tentative Roadmap

| 차수 | 목적 | 범위 | 완료 조건 |
|---|---|---|---|
| 1차 | 제약 정의 | strategy family 중복 금지, existing workflow chain 확인 | 중복 금지 기준과 탐색 universe 확정 |
| 2차 | 후보 탐색 | replay-supported strategy family 조합과 숫자 조건 탐색 | SPY 대비 CAGR 우위, MDD 우위, MDD 15% 미만 후보 도출 |
| 3차 | 검증 chain | Practical Validation replay, Final Review selected-route gate 확인 | `NOT_RUN` critical 없이 Final Review 저장 가능 |
| 4차 | Monitoring 등록 | Final Review decision과 Portfolio Monitoring setup 저장 / recheck | dashboard ready, missing strategy 0, complete slot 1 |

## Scope

- 서로 다른 strategy family만 최종 component로 사용한다.
- 현재 코드 / UX는 변경하지 않고 기존 runtime helper를 운용한다.
- strict/factor와 Risk-On Momentum은 탐색 참고 대상이지만, 현재 gate를 `NOT_RUN` 없이 통과하지 못하면 최종 등록 후보에서는 제외한다.

## Not In Scope

- 새 전략 개발.
- Streamlit UX 변경.
- provider 직접 fetch.
- live approval, broker order, account sync, auto rebalance.
