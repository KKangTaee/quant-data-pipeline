# Portfolio Monitoring Tracking End UX Fix V1 Status

Status: Implementation Complete / Browser QA Pending
Last Updated: 2026-07-19

## Current Position

- 전체 Portfolio Monitoring 개편 roadmap: 종료 UX 보완 `3/4차` 완료
- current milestone: backend/React 구현과 자동 검증 완료, 실제 Browser interaction QA 대기
- implementation: latest-on-or-before 종료 resolver, lifecycle list split, command feedback 완료
- verification: Python 47 tests, React 25 tests, typecheck/build, compile/static asset check PASS

## Approved Boundary

- 휴장일에는 요청일 이하 최신 저장 가치로 즉시 종료한다.
- 종료 row와 종료금액은 보존하되 활성 목록과 종료 기록을 분리한다.
- raw lane status 대신 item lifecycle을 표시한다.
- command 결과를 drawer 밖 본문에서 보여준다.

## Delivered

1. 주말·휴장일 종료 요청은 요청일 이하 최신 가치 row의 실제 날짜와 금액으로 종료된다.
2. 종료 item은 active count와 활성 목록에서 빠지고 접힌 `종료 기록`에 보존된다.
3. 상세의 raw `ACTIVE`는 lifecycle label로 교체됐다.
4. command 성공·실패는 drawer 밖 dismissible banner에 표시된다.

## Remaining Verification Boundary

- local Streamlit은 `8522`에서 정상 기동했지만 인앱 Browser URL policy가 탭 접근을 차단했다.
- 실제 종료 클릭, 종료 기록 자동 펼침, 배너 레이아웃 스크린샷은 후속 Browser QA로 남긴다.
