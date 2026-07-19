# Notes

## Decisions

- 전체 expander 삭제가 아니라 역할 분리를 채택했다.
- preset 자체와 validation threshold 계산식은 유지한다.
- profile answer 변경은 replay 결과를 재사용하고 판정 결과만 다시 만든다.
- recheck mode는 실제 검증 기간을 바꾸므로 Step 2 primary control로 승격한다.
- raw source/replay/result는 읽기 전용 감사 disclosure로 남긴다.

## Preserved Boundaries

- Ingestion -> DB -> Loader -> UI 경계 유지.
- registry/saved JSONL rewrite 없음.
- live approval, broker order, auto rebalance 의미 추가 없음.
