# Risks

- `Current=REVIEW`를 REVIEW로 유지하면 기존보다 Practical Validation 단계의 차단 수는 줄어든다. 의도는 `미실행 / 보강 필요`와 `최종 판단 필요`를 분리하는 것이며, Final Review selected-route gate는 별도로 남는다.
- Browser QA의 replay 실행은 session-only 화면 확인으로 사용했다. Generated screenshot과 run history artifact는 커밋 대상이 아니다.
