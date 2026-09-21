# 남은 검증 공백과 후속 주의점

Date: 2026-09-21

- 실 갱신 1회와 read-only 계산 재현 1회이므로 사용자 전체 지연 분포를 알 수 없다. 네트워크, 최초 bootstrap, 다른 머신, 입력 미변경에서는 시간이 다를 수 있다.
- 하위 profiler 시간은 중첩된다. 60.3초에 내부 forecast/ranking 시간을 다시 더하지 않는다.
- 완료 snapshot as-of는 09-18, UI는 09-21 잠정 세션을 포함했다. 양쪽을 같은 평가 시점의 예측/실적으로 혼동하지 않는다.
- NO_EDGE는 현재 보관된 모델·입력·검증 설정의 결과다. 관측 정보의 무효나 영구적 예측 불가능을 의미하지 않는다.
- M2 context 불일치는 향후 복구가 필요하지만 0-fill 또는 H0 contribution을 raw factor score로 조용히 교체하면 의미·분포가 달라진다. 명시적 schema/algorithm 변경과 재검증이 필요하다.
- 빠른 현재 관측과 느린 검증을 분리할 때 오래된 전망을 최신으로 표시하면 안 된다. as-of/fingerprint, 원자적 publication, 동시 갱신·실패·Today downstream을 함께 검증한다.
- 캐시가 이미 있다고 해서 계산 중복이 모두 제거된 것은 아니다. 다만 영속 캐시나 증분 계산은 과거 provider 수정, 모델 버전, calendar/context 변경 시 올바로 무효화되어야 한다.
- 임계값·지표 이름·체제 의미를 바꾸면 단순 copy 수정이 아닐 수 있다. 화면 변화는 사용자 승인 범위를 확인하고 관측 분류/설명 간 회귀를 검증한다.
- 전체 vintage PIT audit, contract-level roll 영향, 시간대별 장중 calibration, 상관/중복 입력의 영향, 투자성과 개선은 이번에 수행하지 않았다.
- 반복 재계산이나 provider 수집을 실행하지 않았고 제품 코드도 수정하지 않았다. 따라서 개선 성능 또는 개선 UI QA 통과를 주장할 수 없다.
