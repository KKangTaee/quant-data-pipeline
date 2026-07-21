# Risks

- 최신 완료 session 계산은 미국 동부 거래소 달력과 close time을 따라야 한다.
- 갱신 후에도 provider 누락이 크면 랭킹 기준일은 이전 날짜로 유지될 수 있다. 이는 coverage 보호 동작이며 UI에서 두 날짜를 구분해야 한다.
- 외부 provider를 호출하는 실제 수동 갱신은 자동 QA에서 실행하지 않는다.

## Closeout

- provider 실제 수집은 실행하지 않았으므로 갱신 후 coverage-qualified 랭킹 날짜의 전진 폭은 사용자 실행 결과에 달려 있다.
- Browser actual QA는 URL policy로 남았지만 source contract, production build, Python payload와 실제 DB preflight로 보완했다.
