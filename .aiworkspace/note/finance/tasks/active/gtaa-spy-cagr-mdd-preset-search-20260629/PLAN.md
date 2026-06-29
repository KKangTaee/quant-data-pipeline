# GTAA SPY CAGR / MDD Preset Search 2026-06-29

## 이걸 하는 이유?

사용자는 GTAA를 활용해 SPY보다 CAGR과 MDD가 모두 개선되고, CAGR 11% 이상 / MDD 절대값 15% 이하 / 1차 후보 판단 통과 조건을 만족하는 포트폴리오를 확인한 뒤 프리셋으로 쓰고 싶어 한다.

이번 작업은 과거 문서에 남아 있는 GTAA 후보를 최신 로컬 DB / runtime 기준으로 다시 확인하고, 현재 promotion policy까지 통과하는 후보를 GTAA preset으로 고정하는 데 목적이 있다.

## Roadmap

| 차수 | 목적 | 범위 | 완료 조건 |
|---|---|---|---|
| 1차 | 후보 재검증과 제한 탐색 | 기존 후보 재실행, 상위 대안 sweep | 성과 조건과 1차 후보 판단을 모두 만족하는 대표 후보 확정 |
| 2차 | 프리셋 고정 | GTAA preset catalog, parameter default, runtime liquidity evidence | 대표 후보가 GTAA preset dropdown에서 재현 가능 |
| 3차 | 후속 검증 연결 | Practical Validation / Final Review | 사용자가 요청할 때 최신 검증 / 선정 흐름까지 진행 |

## 이번 차수에서 하지 않는 일

- Practical Validation result registry, Final Review decision registry, selected monitoring setup write.
- 새 자동 수집, provider refresh, live approval, broker order, auto rebalance.
- 대규모 exhaustive optimization.
