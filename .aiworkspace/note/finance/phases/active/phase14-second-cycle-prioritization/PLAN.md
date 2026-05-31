# Phase 14 Second-Cycle Prioritization Plan

Status: Active
Created: 2026-05-30

## 이걸 하는 이유?

Phase 13에서 Phase 8~12의 1차 hardening cycle은 investability evidence workflow로 closeout됐다.
하지만 carry-forward matrix에는 아직 high-priority 후보가 여러 개 남아 있다.

Phase 14의 목적은 이 후보들 중 무엇을 먼저 구현해야 실전 투자 판단력이 가장 크게 좋아지는지 정하는 것이다.
바로 코드를 추가하거나 새 저장 기능을 만들기보다, impact / dependency / effort / storage risk / verification 가능성을 비교해 2차 사이클의 첫 구현 단위를 확정한다.

이 phase는 broker order, live approval, account sync, auto rebalance를 만들지 않는다.
또한 user memo, preset, monitoring log auto-write, 의미 없는 JSONL 저장을 늘리는 작업이 아니다.

## Phase Goal

Phase 14는 아래 질문에 답한다.

- Phase 13 carry-forward 후보 중 2차 사이클의 첫 구현 후보는 무엇인가?
- 어떤 후보가 외부 source 불확실성 없이 현재 workflow 안정성을 가장 크게 높이는가?
- 어떤 후보는 구현 전에 product research 또는 data-source review가 필요한가?
- 다음 구현 phase / task가 어떤 파일, skill, QA 기준을 가져야 하는가?
- 저장 경계와 trading automation 경계를 유지하면서 개선할 수 있는가?

## Scope

포함한다.

- Phase 14 active board 생성
- Phase 13 carry-forward 후보 우선순위화
- high-priority 후보의 dependency / owner / QA 기준 정리
- 첫 구현 후보와 후속 후보 분리
- roadmap / index / root handoff log sync

포함하지 않는다.

- runtime / UI / DB code 구현
- 새 DB schema 또는 collector 구현
- 새 JSONL registry
- user memo / preset persistence
- monitoring log 자동 저장
- broker order, live approval, account sync, auto rebalance
- paid / approval-based data source 채택

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 14-0 | Phase 14 board open / scope and task split | Complete |
| 14-1 | Second-cycle candidate prioritization matrix | Next |
| 14-2 | First implementation slice design | Pending |
| 14-3 | Phase 14 handoff QA / closeout | Pending |

## Initial Hypothesis

Current best first implementation candidates are likely:

- `selected replay contract hardening`, because it reduces dependency on legacy Current Candidate Registry and strengthens selected monitoring continuity without new provider adoption.
- `weighted mix cost / turnover aggregation`, because it improves multi-component portfolio realism using existing runtime evidence.
- `profile-specific threshold policy`, because it makes current gates less one-size-fits-all.

Historical membership expansion and broker-grade execution realism remain important, but they likely need source review or product research before implementation.

## Done Criteria

- Phase 13 carry-forward candidates are ranked with clear impact / effort / dependency / risk reasoning.
- The next implementation unit is named, scoped, and assigned to the right domain skill.
- Candidates that need product research or data-source review are separated from immediately implementable tasks.
- No new registry / saved setup / monitoring log / memo / preset storage is introduced.
- `docs/`, phase docs, root handoff logs, and roadmap point to the chosen next step.
- `git diff --check` and artifact boundary checks pass.
