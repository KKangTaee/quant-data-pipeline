# Institutional Holdings Content-First UI V1 Status

State: complete
Last Updated: 2026-08-17

## Current Progress

- 전체 roadmap `3/3차` 완료.
- manager 선택 전에 requested CIK을 로드하고 성공할 때만 선택 CIK과 검색어를 함께 확정한다.
- 실패 시 기존 manager body를 유지하고 picker 내부에 오류를 표시한다.
- dark rail / mobile drawer를 content-first header, bounded manager picker, data context와
  horizontal destination tabs로 교체했다.
- active tab은 subtle background와 short bottom underline으로 표시한다.
- `.stMain` scroll container를 보존해 연속 manager 전환 뒤 상단 맥락이 유지된다.
- production Vite bundle과 focused Python/React tests를 갱신했다.
- actual Browser QA에서 Bill Ackman → David Tepper → Warren Buffett, 분기 리뷰 탭,
  desktop / 390px responsive와 console error 0건을 확인했다.

## Next Action

없음. 다음 개선은 새 사용자 승인 뒤 별도 task로 연다.

## Current Scope Boundary

- 이번 task는 Institutional Holdings manager selection state, React shell, responsive UI,
  focused tests, production component build와 Browser QA만 소유한다.
- 13F ingestion, DB schema, amendment/quarter performance semantics와 다른 top-level surface는
  변경하지 않는다.

## Documentation Closeout

- canonical flow와 Roadmap baseline을 현재 content-first 구조로 갱신했다.
- Product Direction과 Project Map의 제품 약속·ownership boundary는 바뀌지 않아 수정하지 않았다.
