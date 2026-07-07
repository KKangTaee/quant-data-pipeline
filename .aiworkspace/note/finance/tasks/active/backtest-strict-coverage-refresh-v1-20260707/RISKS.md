# Risks

- Runnable coverage backfill은 price freshness, statement shadow coverage, liquidity를 함께 읽어야 하므로 4차에서 과도하게 넓어질 수 있다.
- 4차 backfill은 `Historical Dynamic PIT Universe` 선택 시 적용된다. `Static Managed Research Universe`는 기존 재현성을 위해 선택 preset 자체를 그대로 사용한다.
- 현재 task에서는 기존 run history / generated QA artifacts를 stage하지 않는다.
