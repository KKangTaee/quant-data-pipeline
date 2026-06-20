# Overview Market Context Brief Flow Redesign V1 Plan

## 이걸 하는 이유?

사용자가 `Workspace > Overview > Market Context`를 직접 사용해 본 결과, 화면에 필요한 내용은 있으나 정보 구조가 카드 중심으로 흩어져 있어 시장 브리프를 읽는 경험보다 프로토타입형 UI가 먼저 보인다고 판단했다.

이번 작업은 카드 제거가 목적이 아니다. 카드가 실제 비교 / 우선순위 / 표본 요약에 도움이 되는 곳에만 쓰이도록 역할을 제한하고, Market Context를 "오늘 시장을 읽고, 필요한 자료를 보강하고, 과거 유사 맥락을 참고하는" 흐름으로 재배치한다.

## 전체 Roadmap

### 1차: 현재 브리프 흐름 정리

- 목적: `오늘의 시장 맥락`과 `시장 브리프` 중복을 줄이고, 상단 상태 배지가 무엇을 뜻하는지 바로 알 수 있게 한다.
- 화면 범위: `Market Context` 상단 cockpit / reading flow.
- 완료 조건: 사용자가 같은 시장 요약을 두 번 읽지 않고, `일부자료 상태확인`의 대상이 compact하게 드러난다.

### 2차: 과거 유사 맥락 기준 위치와 설명 정리

- 목적: `기준 시점 / 기준일 / 패턴 기간`이 시장 브리프를 바꾸는 옵션처럼 보이지 않게 하고, historical analog 전용 컨트롤로 보이게 한다.
- 화면 범위: `참고: 과거 유사 맥락` 섹션.
- 완료 조건: selected as-of / pattern window가 과거 유사 맥락 계산 전용임을 화면에서 바로 이해할 수 있다.

### 3차: Historical Analog 설명 UX 정리

- 목적: sector / ETF proxy / 계산 기준일 / sample / 계산식 / replay 한계를 긴 한 줄 텍스트가 아니라 구조화된 basis ledger로 보여준다.
- 화면 범위: `참고: 과거 유사 맥락`.
- 완료 조건: 표를 보기 전에 "무슨 기준으로 계산된 참고 통계인지"를 시각적으로 읽을 수 있다.

### 4차: Macro 조건 포함 pilot 비교 UI

- 목적: broad analog와 macro-conditioned pilot이 같은 정보 반복처럼 보이지 않게, sample funnel과 broad-vs-macro 비교로 분리한다.
- 화면 범위: `Macro 조건 포함 pilot`.
- 완료 조건: macro 조건 추가 전/후 표본 감소와 조건 사용 상태가 분명히 보인다.

### 5차: 자료 상태 / 갱신 액션 / QA

- 목적: `다음 맥락 체크`, `근거: 자료 기준 / 출처 상태`, `보조 갱신`을 guide/card 모음이 아니라 source ledger + 필요 자료 보강 action으로 정리한다.
- 화면 범위: next checks, source confidence, refresh assist.
- 완료 조건: 필요한 자료와 갱신 액션이 보이되, raw job table이 화면의 주인공이 되지 않는다.

## 이번 Task에서 하지 않는 일

- FRED / events / sentiment hard historical conditioning.
- 새 provider, DB schema, loader, registry, saved JSONL path 추가.
- UI render 중 provider / FRED / yfinance direct fetch.
- Backtest / Practical Validation / Final Review / Operations core logic 연결.
- trade signal, prediction, recommendation, validation gate, monitoring signal 생성.
