# Risks

- current transition display helper가 persisted state machine 의미를 덮어쓰지 않도록 별도 nested contract로 둔다.
- 역사 이력에 previous observed row가 없으면 persistence는 `UNAVAILABLE`로 fail-closed 처리한다.
- `LEGACY_OBSERVED` 앵커를 confirmed로 표현하지 않는다.
- `current_transition`은 발생 시점이나 확률 예측이 아니라 다음 인접 국면의 확인 조건이다.
- 기존 persisted transition monitor는 변경하지 않았고, 사용자용 nested contract만 파생하므로 state-machine migration은 필요 없다.
- 외부 의존성의 deprecation warning 3건은 이번 변경 범위 밖이며 테스트 실패는 아니다.
- repository-wide pytest는 기존 Streamlit singleton test isolation 결함으로 336건이 실패하므로, branch 통합 판단에서 전체 suite green을 주장할 수 없다. 경제사이클 집중 suite 219건은 별도 fresh process에서 통과했다.
