# Plan

## 이걸 하는 이유?

3차까지는 데이터 최신성, source validation, lifecycle cleanup을 정식화했다. 4차 첫 작업은 사용자가 table을 끝까지 읽기 전에 강한 종목, 강한 섹터/산업, 수익률 분포를 빠르게 판단하게 만드는 것이다.

## Scope

- Market Movers ranking chart를 더 조밀하고 비교 가능한 색상 스케일로 개선한다.
- Market Movers에 sector pulse chart를 추가한다.
- Sector / Industry leadership에 equal-weight, cap-weighted, top-symbol return을 한 화면에서 비교하는 heatmap을 추가한다.
- 새 원격 수집이나 DB schema 변경은 하지 않는다.

## Done Criteria

- Market Movers에서 rank chart와 sector pulse chart를 볼 수 있다.
- Sector / Industry에서 heatmap과 table을 전환할 수 있다.
- Browser smoke와 service contract tests가 통과한다.
