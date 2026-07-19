# Portfolio Monitoring Item Builder UX Fix V1 Status

Status: Complete
Last Updated: 2026-07-19

## Current Position

- 전체 roadmap: `3/3차 구현·회귀·Browser QA 완료`
- current milestone: item-builder UX follow-up closeout
- implementation: natural workbench frame, 560px drawer panel, one-shot transient recovery, immediate date input 반영
- verification: Portfolio Monitoring Python 90 tests, React 17 tests, typecheck/build, static distribution PASS
- Browser QA: body `1,803px` / drawer `560px`, X 닫기 후 동일 recovery 재전송에도 closed 유지, 정상 재오픈 PASS

## Delivered

1. 등록 drawer가 열려도 iframe 자연 높이를 유지하고 drawer panel body만 스크롤한다.
2. catalog search rerun 뒤 drawer step/query/draft를 일회성 recovery projection으로 복원한다.
3. 날짜 input은 `onInput` 값을 즉시 캡처하며 blur server rerun을 발생시키지 않는다.
4. 새 catalog 검색은 이전 requested date session 값을 제거한다.
5. 동일 catalog recovery snapshot은 stable key로 한 번만 소비해 X 닫기를 다시 덮어쓰지 않는다.

## Remaining Boundary

- effective start date와 entry close의 최종 권위는 기존 add command이며 review에서는 `등록 시 확정`으로 표시한다.
- DB schema, valuation, diagnosis, persistence 계약은 변경하지 않았다.
