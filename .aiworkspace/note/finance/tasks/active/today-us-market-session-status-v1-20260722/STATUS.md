# Today U.S. Market Session Status V1 Status

Status: Complete
Roadmap: 3/3 implementation stages complete
Last Updated: 2026-07-22

## Completed

- Today React workbench ownership과 기존 Events holiday collector를 확인했다.
- 사용자가 프리마켓·애프터마켓 제외를 확정했다.
- 정규장 상태, 양쪽 현재 시각, 양쪽 개장·마감, 카운트다운 범위를 승인했다.
- DB-only official holiday/early-close schedule + React local clock 방향을 설계했다.
- written spec 사용자 승인을 받았다.
- TDD 구현 계획을 `IMPLEMENTATION_PLAN.md`에 `1/3차~3/3차`로 작성했다.
- `today_market_session.py`에 DST-safe 정규장 일정 판정과 휴장·조기폐장 경계를 구현했다.
- Today payload를 `today_home_v3`로 올리고 기존 FOMC 일정과 분리된 official market-calendar loader를 연결했다.
- Today hero 인접 strip에 정규장 상태, 뉴욕·한국 현재 시각, 양쪽 개장·마감 시각, 다음 전환 countdown을 추가했다.
- desktop·420px actual Browser QA에서 overflow와 console error가 없음을 확인했고, 09:30 ET 경계에서 `개장 전`이 `장 진행 중`으로 자동 전환되는 것을 확인했다.
- Python Today 39개, service contract 9개, React 10개, typecheck, production build, py_compile을 통과했다.
- 독립 코드 리뷰의 Important 2건과 Minor 1건을 반영해 loader 상태 전달, `LIMITED` 일정 fail-closed, 520px 단일 열 breakpoint를 보정했다.

## Closeout

- 전체 roadmap `3/3차`를 완료했다.
- 프리마켓·애프터마켓, 실시간 거래정지·긴급 휴장은 범위 밖이다.
- 상세 실행과 남은 경계는 `RUNS.md`, `RISKS.md`를 따른다.
