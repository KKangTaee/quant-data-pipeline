# Futures Macro Evidence / Original Data UX Plan

## 이걸 하는 이유?

`Workspace > Overview > Futures Macro`의 React 보드는 현재 상태 해석을 잘 보여주기 시작했지만, 하단 `근거 해석 / 원본 데이터` expander에는 React 근거와 과거점검 / 원본표가 섞여 남아 있다. 특히 `과거 발생`, `과거 점검 요약`, 원본표 expanders가 어떤 판단 재료인지 바로 연결되지 않아 사용자가 계산 결과를 확인해도 무엇을 봐야 하는지 흐름이 끊긴다.

## 1차: 역할 분리

- 목적: React 보드는 현재 macro 근거, 하단 expander는 계산 근거 / 원본표로 역할을 분리한다.
- 파일 범위: `app/web/overview/futures_macro_helpers.py`, `tests/test_service_contracts.py`, task docs.
- 완료 조건: payload title / expander title / 하단 caption이 중복되지 않고 focused contract test가 통과한다.
- 다음 차수 연결: 과거점검 문구를 바꾸기 전에 화면의 책임 경계를 고정한다.

## 2차: 과거점검 의미 정리

- 목적: `과거 발생`, `과거 점검 요약` 같은 모호한 표현을 `비슷한 과거 상태`, `현재 해석의 과거 일관성`처럼 판단 의미가 보이는 표현으로 바꾼다.
- 파일 범위: `app/services/futures_macro_validation.py`, `app/web/overview/futures_macro_helpers.py`, `tests/test_service_contracts.py`.
- 완료 조건: directional 적용 / 비적용 상태가 각각 표본, 적용 여부, confidence 영향으로 읽힌다.
- 다음 차수 연결: raw table 이름과 요약 용어를 같은 말로 맞출 수 있게 한다.

## 3차: 원본표 구조 개선

- 목적: 원본표를 단순 data dump가 아니라 `현재 점수`, `구성 기여`, `선물 일봉 변화`, `과거 표본`의 계산 순서로 확인하게 한다.
- 파일 범위: `app/web/overview/futures_macro_helpers.py`, `tests/test_service_contracts.py`.
- 완료 조건: expander 이름과 section framing이 원본표의 역할을 드러내고, raw data 자체는 유지한다.
- 다음 차수 연결: React 근거 item과 원본표 section을 같은 score / symbol 언어로 연결한다.

## 4차: React 근거와 원본표 연결

- 목적: React 근거 item에 score label / symbol / contribution metadata를 유지해 하단 구성 기여 표와 자연스럽게 대조하게 한다.
- 파일 범위: `app/web/overview/futures_macro_helpers.py`, `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`, `tests/test_service_contracts.py`.
- 완료 조건: payload contract와 React render가 metadata를 노출하고 Vite build가 통과한다.
- 다음 차수 연결: 최종 Browser QA에서 상단/하단 흐름을 눈으로 확인한다.

## 5차: 최종 QA / 문서 / 커밋

- 목적: 전체 변경을 Browser QA와 durable docs에 반영하고 후속 handoff를 남긴다.
- 파일 범위: task docs, `.aiworkspace/note/finance/docs/ROADMAP.md`, `.aiworkspace/note/finance/docs/PROJECT_MAP.md`, `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`, root handoff logs.
- 완료 조건: focused tests, py_compile, React build, diff check, Browser screenshot을 남기고 최종 문서 commit을 만든다.

## Boundaries

- 새 provider, DB schema, registry / saved JSONL rewrite는 하지 않는다.
- historical validation을 trading signal, Practical Validation gate, monitoring signal, broker order, auto rebalance로 확장하지 않는다.
- 실행 job 결과 / raw status table 중심의 운영 패널을 새로 만들지 않는다.
- generated screenshot, run history, local temp artifact는 stage하지 않는다.
