# Risks

- current transition display helper가 persisted state machine 의미를 덮어쓰지 않도록 별도 nested contract로 둔다.
- 역사 이력에 previous observed row가 없으면 persistence는 `UNAVAILABLE`로 fail-closed 처리한다.
- `LEGACY_OBSERVED` 앵커를 confirmed로 표현하지 않는다.
