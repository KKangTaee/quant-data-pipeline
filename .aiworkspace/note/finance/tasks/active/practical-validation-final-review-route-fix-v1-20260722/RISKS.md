# Risks

- custom component callback과 fragment 본문이 같은 intent를 서로 다른 시점에 볼 수 있으므로 persistence action의 소비 위치를 하나로 제한해야 한다.
- idempotency가 source id 기준이면 다른 validation history를 잘못 합칠 수 있으므로 stable `validation_id`만 사용한다.
- current Final Review active key가 allowed candidate에 없을 때는 기존 safe fallback을 보존해야 한다.
- 실제 registry를 사용하는 Browser QA는 새 validation append를 만들 수 있으므로 isolated in-memory lifecycle QA를 우선하고 protected user registry를 추가로 변경하지 않는다.
