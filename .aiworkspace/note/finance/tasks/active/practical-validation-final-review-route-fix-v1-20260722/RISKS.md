# Risks

- custom component callback과 fragment 본문이 같은 intent를 서로 다른 시점에 볼 수 있으므로 persistence action의 소비 위치를 하나로 제한해야 한다.
- idempotency가 source id 기준이면 다른 validation history를 잘못 합칠 수 있으므로 stable `validation_id`만 사용한다.
- current Final Review active key가 allowed candidate에 없을 때는 기존 safe fallback을 보존해야 한다.
- 실제 registry를 사용하는 Browser QA는 새 validation append를 만들 수 있으므로 isolated in-memory lifecycle QA를 우선하고 protected user registry를 추가로 변경하지 않는다.
- stable-id 검사는 read-then-append이므로 서로 다른 프로세스가 같은 validation을 완전히 동시에 저장하는 극단적 race까지 원자적으로 막지는 않는다. 일반 UI 반복 클릭과 rerun 중복은 차단한다.
- 기존 sentiment contract 2개는 branch의 현재 context-only 출력과 오래된 CNN/AAII expectation이 어긋난 baseline이다. 이번 저장/route 범위에서는 수정하지 않는다.
