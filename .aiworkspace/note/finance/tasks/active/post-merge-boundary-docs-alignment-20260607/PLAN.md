# Post-Merge Boundary Docs Alignment 2026-06-07

Status: Active
Last Updated: 2026-06-07

## 이걸 하는 이유?

master 병합 이후 Overview, Backtest Analysis, Practical Validation, Final Review, Operations Portfolio Monitoring, ingestion / loader / runtime work가 한 브랜치에 모였다.

1차에서는 현재 제품 흐름과 최근 merged work를 roadmap / project map에 맞췄다.
2차에서는 이후 개발자가 코드를 고치기 전에 `UI`, `app services`, `app runtime`, `finance runtime`, `loader`, `DB`, `ingestion`, `JSONL / saved / reports`의 책임 경계를 한 번에 확인할 수 있게 durable docs를 정리한다.

## Scope

- architecture / data / flow 문서의 경계 설명을 같은 언어로 맞춘다.
- `SYSTEM_BOUNDARIES.md`를 새 중심 문서로 추가한다.
- 기존 README, roadmap, project map이 현재 2차 task와 새 boundary 문서를 가리키도록 갱신한다.
- root handoff log에는 milestone / decision pointer만 남긴다.

## Out Of Scope

- 코드 동작 변경
- registry / saved JSONL rewrite
- `.note/` legacy/local 산출물 정리
- active task / phase 대량 이동 또는 archive cleanup
- Risk-On Momentum 5D governance 연결 구현
- Overview Why It Moved V2 storage / AI summary / catalyst classifier 설계

## Completion Criteria

- `docs/architecture/SYSTEM_BOUNDARIES.md`가 layer, product surface, storage boundary를 설명한다.
- architecture / data / flow index 문서가 새 boundary 문서를 찾을 수 있게 한다.
- data schema / storage docs의 오래된 Selected Dashboard / FRED-only 표현을 현재 상태에 맞춘다.
- 검증 명령과 결과를 `RUNS.md`에 남긴다.
- coherent docs commit을 만든다.
