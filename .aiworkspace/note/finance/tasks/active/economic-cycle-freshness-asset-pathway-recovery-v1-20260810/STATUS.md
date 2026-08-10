# Economic Cycle Freshness and Asset Pathway Recovery Status

State: active
Last Updated: 2026-08-10

## Current Position

- 1차 완료: 17개 빈티지 series의 provider fetch를 최대 4개로 제한해 병렬화
- DB upsert는 catalog 순서의 단일 thread 처리로 기존 저장 안정성 유지
- 2차 완료: 자산 경로 15개 입력 전용 갱신 job과 평일 일일 자동화 추가
- 3차 완료: 일간 영업일/주간 달력일 기준의 자산 경로 최신성 범위 분리
- 전체 최신성 payload가 경기 국면과 자산 경로의 갱신 필요 범위를 구분
- 4차 완료: 경기 국면/자산 경로 중 stale 범위만 선택 실행
- 갱신 후 DB 기준일 또는 stale/missing 감소를 확인한 범위만 cache 반영
- 5차 완료: 지연 측정값/변화량 보존과 현재 신호 eligibility 분리
- 지연 값은 `DELAYED`, 현재 집계는 `supports_current_signal=false`로 보수성 유지
- 6차 완료: 기존 자산 카드 layout/order를 유지한 `갱신 지연` 표시와 scope-aware freshness 문구 반영
- 1분 고정 안내 제거, 버튼은 필요한 범위만 갱신한다는 동작과 일치하도록 정리
- 7차 진행: 실제 provider/DB 성능 검증, Browser QA, 문서 동기화
- 설계 승인과 실제 지연/DB stale 진단 완료
