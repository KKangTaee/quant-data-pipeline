# Notes

## Decisions

- 전체 expander 삭제가 아니라 역할 분리를 채택했다.
- preset 자체와 validation threshold 계산식은 유지한다.
- profile answer 변경은 replay 결과를 재사용하고 판정 결과만 다시 만든다.
- recheck mode는 실제 검증 기간을 바꾸므로 Step 2 primary control로 승격한다.
- raw source/replay/result는 읽기 전용 감사 disclosure로 남긴다.
- 하단 disclosure는 `후보 원본 / 재검증 원본 / 판정 원본` 세 tab만 소유하고 설정 select/radio를 두지 않는다.
- actual Browser interaction에서 drawdown 답변 변경 뒤 MDD 검토선이 `-10%`로 갱신되면서 replay `NOT_RUN`을 보존했고, stored-period 선택 뒤 해당 mode가 pressed 상태가 되면서 replay/result는 `NOT_RUN`으로 유지됐다.

## Preserved Boundaries

- Ingestion -> DB -> Loader -> UI 경계 유지.
- registry/saved JSONL rewrite 없음.
- live approval, broker order, auto rebalance 의미 추가 없음.
- profile preset과 threshold 계산식 자체는 변경하지 않았고 placement와 invalidation ownership만 바꿨다.
