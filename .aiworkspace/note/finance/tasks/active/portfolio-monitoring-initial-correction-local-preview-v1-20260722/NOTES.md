# Notes

## Root Cause

- `PositionLedgerPanel.requestInitialEntry()`가 날짜·수량 `onChange`마다 `lookup_initial_position_entry`를 전송했다.
- Python dispatcher는 preview 날짜·수량과 editor recovery를 session state에 저장하고 Streamlit workspace를 다시 만들었다.
- 이 서버 왕복으로 React component가 재마운트되어 native date picker가 닫히고 탐색 중인 월이 초기화됐다.
- correction 저장이나 가치곡선 재계산이 발생한 것은 아니지만 입력 interaction이 전체 rerun처럼 보였다.

## Implemented Contract

- date input은 React `onInput`, quantity input은 local `setDraft`만 사용한다.
- `변경값 확인` action만 기존 lookup event와 sanitized editor recovery를 보낸다.
- `canRequestInitialEntryPreview`는 correction mode, 날짜, 1주 이상 정수 수량을 검증한다.
- `matchesInitialEntryPreview`는 READY status, monitoring item, requested date, quantity가 현재 draft와 같아야 true다.
- MISSING 이유와 READY preview도 현재 draft와 일치할 때만 표시한다.
- correction 저장·재계산 command는 기존 계약을 그대로 사용한다.

## Browser Finding

- actual QA의 Streamlit component는 긴 iframe 높이 때문에 modal의 viewport 위치를 맞춰야 했지만, 입력·preview·recovery 동작 자체는 정상이다.
- explicit preview의 서버 왕복 뒤 editor recovery가 날짜 `2024-06-15`, 수량 `31`과 열린 dialog를 복원했다.
