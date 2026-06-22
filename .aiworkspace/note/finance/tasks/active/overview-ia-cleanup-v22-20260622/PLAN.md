# Overview IA Cleanup V22

## 이걸 하는 이유?

`Workspace > Overview`가 시장 맥락을 읽는 화면인데, `Data Health`와 `Candidate Ops`가 같은 top-level tab으로 남아 사용자가 시장 흐름과 운영 / 후보 관리 화면을 같은 정보 층위로 읽게 됐다. Market Context가 필요한 자료 상태와 보강 흐름을 이미 흡수했으므로, Overview의 primary tab은 시장 context drilldown에 집중시킨다.

## 단계

1. Overview primary tab selector에서 `Candidate Ops`를 제거한다.
2. `Data Health`를 Overview top-level tab에서 제외하고, 자료 관리는 Market Context source / refresh 흐름과 Operations / Ingestion 소유로 정리한다.
3. `Sector / Industry`는 삭제하지 않고 시장 breadth / leadership 상세 근거로 유지한다.
4. Sector / Industry raw table은 기본 탭이 아니라 접힌 상세로 낮춘다.
5. service contract, roadmap, project map, runbook, root handoff를 현재 IA에 맞춘다.

## 범위 제외

- registry / saved JSONL 삭제 또는 재작성
- run history / run artifacts 정리
- Backtest / Practical Validation / Final Review / Operations core workflow 변경
- provider / DB schema / loader 변경
- trading signal, recommendation, validation gate, monitoring signal 생성
