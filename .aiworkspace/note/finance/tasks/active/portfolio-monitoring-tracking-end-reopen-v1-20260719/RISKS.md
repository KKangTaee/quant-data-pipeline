# Portfolio Monitoring Tracking End Reopen V1 Risks

- 종료 취소 후에는 현재 projection에서 과거 종료 상태/종료금액이 보이지 않는다. command audit에는 종료 명령이 유지된다.
- Browser 정책이 localhost app 접근을 막으면 interaction QA는 자동 테스트와 build 검증까지만 수행한다.

## Verification Gap

- 인앱 Browser URL policy로 종료 기록 선택 → 확인창 → 활성 목록 복귀의 actual DOM/visual QA와 신규 스크린샷을 수행하지 못했다. 자동 command/page/component 계약과 production bundle은 통과했다.
