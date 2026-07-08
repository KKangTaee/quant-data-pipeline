# Design

## Documentation Refresh Strategy

이번 작업은 문서 체계 재설계가 아니라 병합 후 drift 정리다.
따라서 `docs/`에는 오래 유지될 current product / code flow만 남기고, 조사 과정과 상세 리뷰 결과는 이 task 기록에 둔다.

## Edit Boundaries

| Area | Action |
|---|---|
| Current state pointer | `INDEX.md`, `ROADMAP.md`, task manifest / README가 같은 latest completed task를 가리키게 한다 |
| Product direction | 현재 Overview primary tabs와 market context boundary를 반영한다 |
| Architecture / flow docs | 코드 흐름을 `overview/page.py`, `overview/*_helpers.py`, `services/overview/*`, `Futures Macro` 중심으로 정리한다 |
| Runbook | 실행 절차에서 legacy `Futures Monitor` primary tab 표현을 현재 `Futures Macro` / Market Movers / Market Context 흐름으로 낮춘다 |
| Review notes | future development needs는 durable roadmap candidate로 확정하지 않고 task `NOTES.md` / `RISKS.md`에 남긴다 |

## Non-Goals

- UI 동작 변경
- 코드 refactor
- registry / saved JSONL 변경
- generated artifacts stage
