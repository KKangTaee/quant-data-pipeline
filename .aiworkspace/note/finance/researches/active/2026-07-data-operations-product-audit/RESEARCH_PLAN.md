# Data Operations Product Audit

Status: Audit Complete
Date: 2026-07-25

## 이걸 하는 이유?

`Data > Data Operations`는 Research, Portfolio Lab, Practical Validation,
Portfolio Monitoring이 읽는 DB-backed data를 준비하는 핵심 경계다.
하지만 현재 화면은 활성 action 30개, 실행 기록, 로컬 로그와 failure artifact,
runtime/build 정보가 한 탭에 함께 있어 실제 사용자가 어떤 작업을 언제 해야 하는지
판단하기 어렵다.

이번 조사는 기능 수를 늘리기 전에 현재 기능의 제품 가치와 사용자 흐름을 다시 분류하고,
유지·통합·고급 경로 이동·제거 후보와 부족한 기능을 정리한다.

## Scope

포함:

- `Data > Data Operations` 현재 화면과 실제 브라우저 사용 흐름
- Ingestion UI, action registry, dispatcher, diagnostics, job boundary
- Research / Portfolio / Validation consumer와의 handoff
- 유지, 통합, UI 제거, backend 보존 후보
- 다음 설계·구현 차수 제안

제외:

- 이 조사에서 직접 UI 또는 collector 구현
- DB schema, registry, saved setup, run history 재작성
- scheduler, background worker, broker integration 구현
- `financial_advisor`
- 사용자 승인 없는 raw run/job/status 진단 패널 추가

## Method

1. 현재 docs, active task, 최근 commit을 확인한다.
2. UI entrypoint와 action registry에서 실제 노출 기능을 센다.
3. desktop 1280px, mobile 420px에서 첫 행동 탐색 비용과 화면 역할을 확인한다.
4. 제품 기능과 내부 운영 도구를 분리한다.
5. 구현 사실, 권고, 열린 질문을 구분한다.

## Output

- [CURRENT_PROJECT_AUDIT.md](./CURRENT_PROJECT_AUDIT.md)
- [RISKS.md](./RISKS.md)

외부 benchmark와 확정 design은 다음 차수에서 사용자 승인 후 별도로 진행한다.
