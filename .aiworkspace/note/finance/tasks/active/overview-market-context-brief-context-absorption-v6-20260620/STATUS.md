# Status

Status: Completed
Last Updated: 2026-06-20

## Summary

`Overview > Market Context`에서 V5 `브리프 신뢰도` 섹션을 제거하고, 이벤트 / Futures 자료 제한을 별도 가이드가 아니라 `오늘의 시장 브리프` 안의 시장맥락 결론으로 흡수했다.

## Completed

- `brief_caveats` payload와 `브리프 신뢰도` 렌더러 / CSS를 제거했다.
- `brief_rows`는 최대 4행까지 표시하며, 이벤트 finding이 있으면 `이벤트 배경` 행을 추가한다.
- Events REVIEW / estimate 상황은 `직접 원인 근거 약함`으로 표시해 오늘 움직임의 원인으로 단정하지 않도록 정리했다.
- Data Health 전체 priority items 중 Futures Monitor / OHLCV 항목이 있을 때만 `Futures/Macro 배경`을 `장중 macro 해석 보류`로 낮춘다.
- 하단 `근거: 자료 기준 / 출처 상태` disclosure는 유지했다.

## Boundary

이번 작업은 read model projection, Streamlit render flow, 문구/레이아웃 계약만 수정했다. 저장 자료 경계, ingestion boundary, registry / saved JSONL, validation / monitoring / trading semantics는 변경하지 않았다.
