# Status

Status: Completed
Last Updated: 2026-06-20

## Summary

`Overview > Market Context`의 `오늘의 시장 브리프`를 다시 3행 market story로 정리하고, Events / 자료 신뢰도는 별도 `브리프 신뢰도` 영역으로 분리했다.

## Completed

- `brief_rows`는 `무엇이 움직였나`, `확산/집중인가`, `Futures/Macro 배경`만 담도록 유지했다.
- `brief_caveats` payload를 추가해 Events / 자료 기준을 `브리프 신뢰도` 렌더러로 표시한다.
- Events는 `이벤트 요인은 약하게 읽기`, 자료 기준은 `선물 기반 장중 해석 제한`처럼 사용자가 브리프를 어떻게 읽어야 하는지 먼저 보이게 했다.
- 기본 Market Context 화면에서 `다음 맥락 체크` / `맥락 검토 결과` rail을 다시 만들지 않았다.
- Service contract tests를 RED -> GREEN으로 갱신했다.

## Boundary

이번 작업은 read model projection, Streamlit render flow, 문구/레이아웃 계약만 수정했다. 저장 자료 경계, ingestion boundary, registry / saved JSONL, validation / monitoring / trading semantics는 변경하지 않았다.
