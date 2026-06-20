# Overview Market Context Brief Flow Redesign V2 Plan

## 이걸 하는 이유?

V1 작업은 `Workspace > Overview > Market Context`의 기준 표시와 일부 섹션 위치를 정리했지만, 실제 화면은 여전히 작은 카드와 박스 안 문구가 반복되는 프로토타입형 UX로 보였다.

이번 V2는 같은 내용을 다시 카드에 넣는 방식이 아니라, 사용자가 시장 브리프를 넓게 읽고 다음 관찰 지점, 과거 참고 통계, macro 조건 비교, 자료 보강 근거로 자연스럽게 내려가도록 화면 언어를 바꾸는 보정 작업이다.

## Scope

- 상단 `오늘의 시장 맥락`과 `시장 브리프` 중복 제거.
- `시장 브리프` rows를 cockpit 안의 wide brief lane으로 흡수.
- `다음 맥락 체크`를 3열 card grid가 아니라 priority / observation / reason / action rail로 변경.
- `참고: 과거 유사 맥락`의 설명, basis ledger, summary strip typography를 키우고 card-like background를 줄임.
- `Macro 조건 포함 pilot`을 UI상 `Macro 조건 포함 비교`로 표시하고 broad vs macro 전/후 비교 흐름을 강화.
- `근거: 자료 기준 / 출처 상태`와 refresh assist는 보조 근거 / action 위치로 유지하되, card-first visual language에서 벗어남.

## 이번 Task에서 하지 않는 일

- 새 provider, DB schema, loader, registry, saved JSONL path 추가.
- UI render 중 provider / FRED / yfinance direct fetch.
- FRED / events / sentiment hard historical conditioning.
- Backtest / Practical Validation / Final Review / Operations core logic 연결.
- trade signal, prediction, recommendation, validation gate, monitoring signal 생성.
