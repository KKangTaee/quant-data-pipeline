# Portfolio Monitoring Initial Correction Local Preview V1 Design

## 이걸 하는 이유?

`개별 추적 결과 > 보유내역 > 최초 설정 정정`의 날짜와 수량 입력은 현재 `onChange`마다 `lookup_initial_position_entry`를 Python으로 전송한다. Streamlit 전체 rerun과 React 재마운트가 이어지면서 native date picker가 닫히거나 표시 월이 초기화되어 사용자가 과거 월을 탐색하기 어렵다.

입력 편집과 DB 기반 변경 후 미리보기를 분리해, 달력을 조작하는 동안 화면 전체가 갱신되지 않도록 한다.

## 확인한 원인

- `PositionLedgerPanel.requestInitialEntry()`는 draft를 갱신한 직후 `lookup_initial_position_entry`를 emit한다.
- `새 추적 시작일`과 `새 최초 수량`의 `onChange`가 이 함수를 직접 호출한다.
- Python dispatcher가 날짜·수량·editor recovery를 session state에 넣고 Streamlit이 workspace를 다시 만든다.
- React component가 새 workspace로 재마운트되며 date picker의 임시 탐색 상태가 보존되지 않는다.
- 실제 correction 저장이나 가치곡선 재계산이 일어난 것은 아니지만, 사용자가 보기에는 전체 화면이 갱신된 것처럼 느껴진다.

## 검토한 대안

### A. 명시적 `변경값 확인` action — 채택

- 날짜·수량 입력은 React local draft만 변경한다.
- 사용자가 `변경값 확인`을 누를 때만 기존 lookup event를 보낸다.
- DB 적용일·종가·최초 투자금이 현재 draft와 일치할 때만 저장할 수 있다.
- 입력을 다시 바꾸면 이전 preview를 즉시 stale로 취급한다.

장점은 rerun 시점이 예측 가능하고 기존 비교 확인·서버 검증 계약을 보존한다는 점이다.

### B. 입력 debounce 후 자동 조회 — 제외

입력을 멈춘 뒤 조회하더라도 달력 조작 중 예기치 않은 rerun이 남고 네트워크·DB 조회 횟수도 불명확하다.

### C. 미리보기 없이 저장 시 서버 검증 — 제외

rerun은 줄지만 변경 후 적용일·종가·최초 투자금을 저장 전에 확인한다는 기존 안전장치를 잃는다.

## 사용자 흐름

1. 사용자가 `최초 설정 정정`을 연다.
2. 기존 시작일·수량의 변경 후 preview는 최초 한 번 표시할 수 있다.
3. 날짜 달력의 연·월을 이동하거나 날짜를 선택해도 서버 event를 보내지 않는다.
4. 수량을 바꿔도 서버 event를 보내지 않는다.
5. 현재 입력이 마지막으로 확인한 preview와 다르면 `변경값 확인` 버튼을 보여주고 `저장`은 비활성화한다.
6. `변경값 확인`을 누르면 현재 날짜·수량과 editor recovery를 담은 기존 `lookup_initial_position_entry` event를 한 번 보낸다.
7. rerun 뒤 현재 입력과 일치하는 적용일·종가·최초 투자금 preview를 표시하고 `저장`을 활성화한다.
8. 입력을 다시 바꾸면 이전 preview는 표시 근거로 사용하지 않고 5단계로 돌아간다.
9. `저장`을 누를 때만 기존 correction command가 append-only revision을 만들고 거래 이력과 성과를 다시 계산한다.

## 컴포넌트 및 경계

### React

- `PositionLedgerPanel.tsx`가 local draft와 명시적 preview request action을 소유한다.
- date/quantity `onChange`는 `setDraft`만 호출한다.
- preview의 날짜·수량이 현재 draft와 일치하는지 기존 `initialEntryReady`로 판단한다.
- `변경값 확인`은 유효한 날짜와 1주 이상의 정수 수량일 때만 활성화한다.
- 미확인 상태에서 저장 버튼은 비활성화하고 `변경값을 먼저 확인해 주세요.` 안내를 표시한다.

### Python / DB

- `lookup_initial_position_entry` event와 `_resolve_initial_position_entry()`의 DB 조회 계약은 변경하지 않는다.
- `correct_initial_quantity` command, append-only revision, 거래 이력 검증, 가치곡선 재계산 계약은 변경하지 않는다.
- partial component rerun이나 별도 endpoint는 추가하지 않는다.

## 오류 처리

- 날짜가 없거나 수량이 유효하지 않으면 preview event를 보내지 않고 기존 입력 오류를 표시한다.
- 해당 날짜 이후 저장 가격이 없으면 기존 `MISSING` projection과 이유를 표시하고 저장을 비활성화한다.
- preview 조회 후 draft가 바뀌면 이전 `READY` 또는 `MISSING` 결과를 현재 입력의 결과처럼 표시하지 않는다.
- 조회 rerun 후 editor recovery는 현재 날짜·수량·메모를 복원한다.

## 테스트 및 완료 조건

- React 계약 테스트가 날짜·수량 변경 함수가 preview event를 만들지 않는 흐름을 검증한다.
- component source 계약이 date/quantity `onChange`와 `lookup_initial_position_entry` emit을 분리하고 `변경값 확인` action을 요구한다.
- 기존 initial-entry lookup, correction validation, command event 테스트가 계속 통과한다.
- actual Browser QA에서 date picker로 이전 월을 이동·선택하는 동안 화면과 dialog가 유지된다.
- `변경값 확인` 1회 후 preview가 표시되고 저장이 활성화된다.
- 저장 전에는 DB correction이나 가치곡선 재계산이 발생하지 않는다.

## 제외 범위

- 매수·매도 거래일 종가 조회 UX 변경
- 최초 설정 정정의 DB schema, revision identity, valuation 정책 변경
- Streamlit fragment/API 전환
- date picker 자체를 custom calendar로 교체
