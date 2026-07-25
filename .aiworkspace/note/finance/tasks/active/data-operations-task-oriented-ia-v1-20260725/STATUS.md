# Status

Status: Complete
Updated: 2026-07-26
Roadmap: 3차 구현·QA 완료 / 4차 durable execution·scheduling 후보 보류

## Completed

- Data Operations 제품 audit를 implementation task로 전환했다.
- 사용자가 `Task-oriented Hybrid` 방향을 승인했다.
- primary user, explicit execution, data correctness boundary를 설계 assumption으로 고정했다.
- five-section IA와 네 consumer workflow를 정의했다.
- 활성 action 30개의 primary / recovery / advanced ownership을 정의했다.
- 기본 UI 제거 대상과 backend 보존 contract를 분리했다.
- target module structure, error handling, responsive QA, test contract를 정리했다.
- `데이터 준비 / 공식 파일 / 문제 복구 / 실행 이력 / 고급 도구` 5개 section을 실제 화면에 반영했다.
- Market Research, Portfolio Lab, Institutional Holdings, Practical Validation 목적 카드와 순서형 action handoff를 구현했다.
- 공식 XLSX/ICS, 읽기 전용 진단, 수동 복구 entry를 목적별로 분리하되 기존 action form·dispatcher는 한 벌만 유지했다.
- Runtime/Build, 정적 4-step 안내, raw log/failure CSV/full payload history viewer를 기본 제품 화면과 코드에서 제거했다.
- 실행 이력은 active Data Operations job만 `시각 / 작업 / 목적 / 상태 / 범위 / 결과 / 다음 행동`으로 표시한다.
- 선택한 action의 기존 expander와 event/validation 하위 tab을 자동으로 펼치는 advanced focus를 구현했다.
- focused Python 59개와 desktop/mobile actual Browser QA를 통과했다.
- 후속 UX 정리에서 중복 `Reference help · Ingestion` contextual panel을 제거해
  제목·설명 다음에 목적 section이 바로 시작하도록 했다. canonical Reference
  Center와 Ingestion catalog item은 유지한다.
- `공식 파일 / 문제 복구 / 실행 이력 / 고급 도구`의 selector-equivalent
  본문 제목을 제거하고 설명·작업군·개별 도구 제목만 유지했다.
- 고급 도구 직접 진입은 모든 collector / diagnosis expander를 닫고,
  목적·이력 handoff가 있는 경우에만 해당 action을 펼치도록 통일했다.
- 고급 도구를 떠날 때 이전 action focus를 지워 재진입 시 과거 도구가
  다시 열리는 sticky-focus 문제를 해소했다.
- active action 30개의 workflow ownership, renderer, dispatcher, guide와
  26개 write action의 explicit-button scheduling 경로를 비파괴적으로 점검했다.
- focused Python 91개와 1280×720 / 420×900 actual Browser QA를 통과했다.

## Current

- 1차 audit, 2차 설계, 3차 구현·QA를 완료했다.
- collector, DB schema, loader, write behavior는 변경하지 않았다.
- explicit click, preflight, progress, partial-success, run artifact backend는 유지한다.
- 고급 도구 기능 진단에서 blocking correctness gap은 발견하지 않았다.
- 접힌 Streamlit expander도 내부 form / DB-backed preflight를 평가하는 초기
  성능 부담과 `_bind_page_globals()` 동적 결합은 후속 engineering risk로 남는다.

## Next

4차 후보는 durable execution이 실제로 필요하다는 운영 근거가 생겼을 때만 연다.

1. background queue / scheduler / cancellation / resume 필요성 검증
2. multi-user authorization과 remote deployment security 검토
3. consumer-origin refresh까지 포함할 history scope 재검토
4. Advanced form을 action 선택 뒤에만 렌더해 collapsed-body 초기 평가 비용 제거
5. `_bind_page_globals()`를 명시적 dependency/interface로 교체
