# Status

Status: Completed
Last Updated: 2026-06-20

## Summary

`Overview > Market Context`의 V3 `맥락 검토 결과` 레일을 기본 사용자 흐름에서 제거하고, Events / 자료 신뢰도 caveat를 `오늘의 시장 브리프` 안으로 통합했다.

## Completed

- `brief_rows`가 기존 3행에서 Events / 자료 신뢰도 caveat를 포함하는 5행 흐름으로 확장됨.
- P1/P2에 해당하는 가격 움직임 / Futures-Macro finding은 별도 레일에서 반복하지 않음.
- 기본 reading flow는 `context_findings` / `next_checks`를 자동 렌더링하지 않고, historical analog / source confidence만 이어서 보여줌.
- Market Context 탭의 no-op reading-flow 호출을 제거함.
- Service contract tests를 RED -> GREEN으로 갱신함.

## Boundary

이번 작업은 read model projection과 Streamlit render flow만 수정했다. 저장 자료 경계, ingestion boundary, registry / saved JSONL, validation / monitoring / trading semantics는 변경하지 않았다.
