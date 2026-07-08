# Post-Merge Docs / Code Flow Refresh 2026-07-08

Status: Active

## 이걸 하는 이유?

`sub-dev` / `backtest-dev` 병합 이후 공용 문서가 한 차례 정리됐지만, 현재 master의 최신 코드 흐름과 장기 문서의 pointer / 화면명 / 역할 설명이 완전히 맞지 않을 수 있다.
이번 작업은 구현을 새로 벌리기보다, 다음 개발자가 `docs/`와 active state 문서만 보고 현재 제품 경계와 코드 흐름을 오해 없이 따라갈 수 있게 만드는 refresh다.

## 잠정 Roadmap

### 1차: 현재 상태 진단

- 목적: master 병합 후 active phase / task pointer, 충돌 마커, stale surface name을 확인한다.
- 파일 범위: `docs/INDEX.md`, `docs/ROADMAP.md`, task / phase manifest, root handoff log, 주요 architecture / flow docs.
- 완료 조건: 현재 active state와 stale 후보가 정리된다.
- 다음 차수 연결: stale 후보만 2차 문서 편집 대상으로 보낸다.

### 2차: 공용 문서 / 코드 흐름 최신화

- 목적: 현재 코드의 Overview / Backtest / Practical Validation / Operations 흐름과 문서의 surface 이름을 맞춘다.
- 파일 범위: `docs/PRODUCT_DIRECTION.md`, `docs/ROADMAP.md`, `docs/architecture/*`, `docs/flows/*`, `docs/runbooks/*`.
- 완료 조건: current / latest pointer가 하나로 수렴하고, `Futures Monitor` / `Sector / Industry` 같은 legacy primary surface 표현이 현재 `Futures Macro` / Market Context 내부 evidence 경계로 정리된다.
- 다음 차수 연결: 리뷰 결과와 후속 개발 필요사항을 task / root handoff에 남긴다.

### 3차: 리뷰 / 검증 / handoff

- 목적: 코드 리뷰 관점으로 병합 후 문서 drift, stale path, generated artifact staging 위험을 확인한다.
- 파일 범위: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`, root handoff logs.
- 완료 조건: `git diff --check`, conflict marker scan, pointer consistency scan, focused Python compile / tests를 가능한 범위에서 실행하고 결과를 남긴다.

## 이번 작업에서 하지 않는 일

- 새 product UX / stage 구조 변경
- registry / saved JSONL rewrite
- run history / generated QA screenshot 정리 또는 commit
- provider ingestion, DB schema, strategy runtime 변경
- live approval / broker order / auto rebalance 의미 추가
