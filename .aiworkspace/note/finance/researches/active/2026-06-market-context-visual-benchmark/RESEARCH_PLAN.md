# Market Context Visual Benchmark Research Plan

Status: Active
Created: 2026-06-15

## Research Question

`Workspace > Overview > Market Context`를 더 시각적이고 한눈에 읽히게 만들 때, 카드 중심 UI를 계속 쓸 필요가 있는가?
카드가 아니라면 어떤 금융 UI pattern이 더 적합한가?

## Scope

- Benchmark comparable market context / dashboard products and UI patterns.
- Synthesize 2-3 implementation directions for this project.
- Do not implement code before the user chooses a direction.

## Selection Criteria

- Fits DB-backed, context-only Overview boundary.
- Improves scanability without hiding source / freshness caveats.
- Avoids run/job diagnostic panels as the main product surface.
- Can be implemented incrementally in Streamlit first.

## Out Of Scope

- Live trading, broker order, auto rebalance.
- New provider / DB schema / registry writes.
- AI catalyst classification or article body summarization.
- Full platform migration decision.
