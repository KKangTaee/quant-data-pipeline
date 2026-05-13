# NOTES - Product Research Output Contract

Status: Active
Last Updated: 2026-05-13

## Decision

실제 제품 방향 리서치 산출물은 `.aiworkspace/note/finance/researches/active/<research-id>/` 아래에 둔다.

`tasks/active/`에는 리서치 workflow를 만들거나 수정한 실행 작업 기록을 남긴다.

## Naming Decision

폴더 이름은 repo의 복수형 convention에 맞춰 `researches/`로 둔다.
문장 안에서는 product direction research처럼 자연스러운 표현을 유지하되, 경로는 `researches/active/<research-id>/`를 쓴다.

## Proposed Research Bundle

```text
.aiworkspace/note/finance/researches/active/<research-id>/
  RESEARCH_PLAN.md
  CURRENT_PROJECT_AUDIT.md
  BENCHMARKS.md
  UI_PATTERNS.md
  FEATURE_CANDIDATES.md
  RECOMMENDATION.md
  SOURCES.md
  RISKS.md
```

## Promotion Rule

- 조사 중 사실, 추측, 비교표, source notes는 research folder에 둔다.
- 사용자가 채택한 장기 방향만 `docs/PRODUCT_DIRECTION.md` 또는 `docs/ROADMAP.md`로 승격한다.
- 승인된 개발 단위만 `phases/active/` 또는 `tasks/active/`로 전환한다.
