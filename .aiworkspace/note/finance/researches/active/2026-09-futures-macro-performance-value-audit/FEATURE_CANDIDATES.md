# 개선 후보와 우선순위

Date: 2026-09-21
Status: 후보, 미승인·미구현

| 우선순위 | 후보 | 사용자 가치 | 난도/위험 | 완료 조건 |
|---|---|---|---|---|
| 1 | 최신 관측 계산과 hidden 예측 재검증 분리 | 새 가격을 기다리는 동안 과거 검증을 기다리지 않음 | 중간; snapshot schema와 Today 등 downstream 호환성 | 입력 변경·동일·장중·실패 경우의 현재 관측 parity, 무거운 검증이 동기 refresh에 진입하지 않는 테스트, 단계별 실제 시간 측정 |
| 1 | 오늘의 핵심 관측과 확인 조건을 연결하는 설명 | 사용자가 어떤 자산을 왜 점검할지 이해 | 중간; 해석 과장과 방향 라벨 변경 회귀 | 실제 현재 사례를 사용자가 한 문장으로 설명하고 반전 조건을 찾을 수 있음 |
| 2 | 전망 입력 계약 복구와 후보 eligibility 사전 확인 | 평가 불가를 성능 부진과 구분, 불필요 계산 감소 | 중간~높음; contribution과 raw score 의미 혼동 위험 | 결측 이유별 상태 분리, eligible 후보만 계산, 알고리즘 버전과 재검증 |
| 2 | train 시점별 거리/순위 재사용, outcome 벡터화 | 검증 계산 자체의 속도 향상 | 중간; 시점 누출과 tie/de-overlap 차이 위험 | 과거-only train, purging, 선택·확률·gate 동등성 검증 후 실측 |
| 2 | 과거 완료 fold 재사용 및 준비 입력 공유 | 새 정보가 바꾸지 않은 검증과 feature 중복 계산 절감 | 중간~높음; 과거 correction과 context 수정의 invalidation | 동일 최종 입력/5m만 변경 시 nested 0회, 과거 입력 수정 시 재계산, 미래 append 후 과거 결과 불변 |
| 3 | provider overlap 단축과 bounded concurrency | 데이터 다운로드 부가 시간 감소 | 중간; 과거 수정 누락·rate limit | 짧은 overlap + 정기 깊은 보정, retry/부분 실패 검증; 10y bootstrap 보존 |
| 3 | 혼재 하위 원인·가격 근거와 이력 개선 | 무의미한 반복 색상 대신 변화를 구별 | 중간; 분류 재설계 및 UI 승인 필요 | 저신호·충돌·단일 축을 구분, 기준 고정 후 사례와 기간별 검증 |

1번을 단순히 `include_validation=False`로 해결할 수 없다. 기존 thermometer 플래그와 별도 outlook builder가 다르다. 수집을 병렬화하거나 spinner만 바꾸는 것도 주 병목 해결이 아니다.

예측 검증은 필요할 때 실행하는 별도 경로 또는 완료 세션 입력 변경 후 별도 작업으로 보존할 수 있다. 실제 scheduling 방식은 후속 구현에서 정한다. 오래된 validation을 새 관측의 validation처럼 합쳐 표시하지 않도록 각각의 as-of와 fingerprint를 보존해야 한다.

성능 acceptance는 먼저 대표 입력 변경/미변경/장중 케이스를 측정한 뒤 정한다. 현재 57.8초 경로를 분리할 여지는 크지만, 구현 전 특정 초 또는 배수 향상을 보장하지 않는다.
