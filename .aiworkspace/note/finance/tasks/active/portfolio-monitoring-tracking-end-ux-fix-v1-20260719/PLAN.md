# Portfolio Monitoring Tracking End UX Fix V1 Plan

## 이걸 하는 이유?

사용자가 `추적 종료`를 눌렀는데 항목이 계속 `추적 중`으로 보이면 종료 기능을 신뢰할 수
없다. 기록 보존이라는 제품 계약은 유지하되 활성 추적과 종료 이력을 명확히 분리하고,
휴장일에도 즉시 종료되며 실패 시 이유를 볼 수 있게 한다.

## Goal

- 요청일 현재의 최신 사용 가능 가치로 추적 종료를 확정한다.
- 활성 목록과 종료 기록을 분리한다.
- lifecycle 상태와 command 결과를 일관되게 표시한다.

## Execution

### Task 1 — RED: 종료 산정 계약

- [ ] 요청일 당일 row가 없을 때 이전 최신 row를 고르는 Python 실패 테스트를 작성한다.
- [ ] 요청일 이전 row도 없으면 명확한 오류가 발생하는 실패 테스트를 작성한다.
- [ ] 테스트가 기존 `date >= requested_end` 구현 때문에 실패하는지 확인한다.

### Task 2 — RED: React lifecycle presentation

- [ ] active/ended item 분리 helper와 lifecycle label 실패 테스트를 작성한다.
- [ ] 최신 command를 drawer 밖에서 읽는 source contract 테스트를 작성한다.
- [ ] Vitest가 기존 단일 목록/raw lane status 구현 때문에 실패하는지 확인한다.

### Task 3 — GREEN: 최소 구현

- [ ] Python 종료 resolver가 요청일 이하 최신 row를 선택하고 실제 적용일을 반환하게 한다.
- [ ] command 결과에 종료 요청일/적용일을 포함한 사용자 메시지를 저장한다.
- [ ] React 목록을 활성 추적과 접힌 종료 기록으로 분리한다.
- [ ] 상세 lifecycle label과 본문 dismissible command 배너를 구현한다.

### Task 4 — Verification and closeout

- [ ] focused Python unittest와 React Vitest를 실행한다.
- [ ] TypeScript typecheck, Vite build, Python compile, `git diff --check`를 실행한다.
- [ ] 로컬 앱이 가능하면 Browser QA와 스크린샷을 남긴다.
- [ ] task 문서와 root handoff log를 동기화하고 coherent commit을 만든다.

## Stop Condition

휴장일 종료가 최근 거래일로 성공하고, 종료 항목이 `종료 기록`에 남으며, 화면에서 성공·실패와
실제 적용일을 확인할 수 있으면 완료한다.

