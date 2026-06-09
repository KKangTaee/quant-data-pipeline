# Overview Refresh Result UX V3

Status: Active
Date: 2026-06-10

## 이걸 하는 이유?

`Workspace > Overview > Market Context`의 일괄 갱신 버튼은 기존 Overview action boundary로 여러 DB-backed 수집 job을 순서대로 실행한다. 현재 결과 UI는 bundle status와 raw row만 보여서 `partial_success`일 때 사용자가 어떤 job을 다시 확인해야 하는지 빠르게 알기 어렵다.

## Scope

- Market Context 일괄 갱신 결과를 summary-first로 재구성한다.
- success / partial / failed / skipped / locked 상태를 한글로 표시한다.
- 확인 필요한 결과와 전체 결과를 분리해서 보여준다.
- 기존 `app/jobs/overview_actions.py` facade와 DB-backed read model 경계를 유지한다.

## Out Of Scope

- 새 provider 추가
- DB schema 변경
- registry / saved JSONL write 추가
- Overview render 중 external fetch
- 자동 스케줄러 / launchd / OS automation 변경
- Ingestion Action Queue, retry queue, provider hardening
- validation PASS/BLOCKER, Final Review decision, monitoring signal, trading action

## Done When

- focused regression test가 partial / failed 결과 분리를 검증한다.
- Overview UI가 result headline, metrics, issue rows, full rows를 렌더링한다.
- py_compile, focused tests, boundary check, git diff check가 통과한다.
- Browser QA screenshot을 남기되 generated artifact는 커밋하지 않는다.
