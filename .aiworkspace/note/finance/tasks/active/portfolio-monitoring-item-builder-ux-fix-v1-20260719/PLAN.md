# Portfolio Monitoring Item Builder UX Fix V1 Plan

## 이걸 하는 이유?

Portfolio Monitoring의 종목·전략 등록 drawer가 Streamlit iframe 전체 높이를 사용해
`이전`/`다음` 버튼이 브라우저 가시 영역 아래로 밀린다. 또한 요청 시작일 입력의
`onBlur`가 catalog 조회와 Streamlit rerun을 발생시켜 React 로컬 draft를 잃을 수 있다.
사용자가 등록 wizard를 스크롤 탐색이나 재입력 없이 끝낼 수 있도록 이 두 결함을 함께 수정한다.

## Goal

- drawer footer를 브라우저 가시 영역 안에 유지한다.
- 요청 시작일을 선택한 뒤 review 단계까지 값이 유지되게 한다.
- 서버 catalog 검색 rerun 뒤에도 drawer 단계·검색어·draft를 복구한다.

## Scope

- React item-builder 상태와 event payload
- Python Streamlit bridge의 일회성 item-builder recovery projection
- drawer iframe 높이와 내부 scroll CSS
- Vitest, Python unit test, build, Browser QA

## Out Of Scope

- DB schema와 저장 command 의미
- 가격/가치곡선/진단 계산
- 그룹·항목 lifecycle 재설계
- provider 직접 조회

## Execution

### Task 1 — RED contracts

- [x] Vitest에 drawer frame height와 item-builder recovery/event round-trip 실패 테스트를 추가한다.
- [x] Python page test에 허용 필드만 보존하는 recovery projection 실패 테스트를 추가한다.
- [x] 두 테스트가 기존 구현에서 의도한 이유로 실패하는지 확인한다.

### Task 2 — Minimal implementation

- [x] React state helper에 recovery normalization과 catalog-search event builder를 구현한다.
- [x] component가 recovery state로 초기화되고 날짜 blur에서 서버 이벤트를 발생시키지 않게 한다.
- [x] Python bridge가 item-builder state를 정규화해 일회성 workspace projection으로 전달한다.
- [x] drawer open 동안 component frame을 560px로 제한하고 body만 scroll되게 한다.

### Task 3 — Verification and closeout

- [x] focused Vitest/Python tests, typecheck, Vite build, static distribution test를 실행한다.
- [x] 실제 화면에서 footer 가시성, 날짜 유지, 검색 rerun 복구를 확인한다.
- [x] task docs와 root handoff log를 최소 범위로 동기화하고 coherent commit을 만든다.

## Stop Condition

720px 높이 Browser QA에서 drawer를 연 직후 footer가 가시 영역 안에 있고, 날짜 선택 후
review에 같은 날짜가 표시되며, catalog 검색 뒤 drawer가 열린 상태로 유지되면 완료한다.
