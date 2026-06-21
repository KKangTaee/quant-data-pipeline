# Overview Market Context Macro Meaning Gradient V19

Status: Active
Started: 2026-06-22

## 이걸 하는 이유?

`Workspace > Overview > Market Context`의 historical analog / Macro 비교 표는 사용자가 과거 표본의 중앙 경로를 빠르게 읽어야 하는 영역이다. 현재 HTML에는 색상 tone 값이 있지만 실제 화면에서는 양수/음수 강도가 약하게 보여 표의 정보 구조가 충분히 드러나지 않는다. 또한 조건에는 쓰지 않은 Macro 배경의 T10Y3M / VIXCLS / BAA10Y 값이 숫자와 bucket으로만 보여, 사용자가 그 값이 높은지 낮은지 또는 어떤 시장 배경을 뜻하는지 바로 이해하기 어렵다.

## Scope

- 핵심 자산 비교 matrix와 Macro 조건 결과 비교 matrix의 양수 / 음수 색상 강도를 더 명확하게 표시한다.
- T10Y3M / VIXCLS / BAA10Y reference-only Macro 배경에 현재 값의 상태 판단 문장을 추가한다.
- 기존 DB-backed read model과 hard condition 경계는 유지한다.
- 새 provider / FRED fetch, DB schema, loader, registry / saved JSONL, validation / monitoring / trading signal은 추가하지 않는다.

## Steps

1. RED: service contract HTML test에 matrix gradient visibility와 Macro backdrop state interpretation 기대값을 추가한다.
2. GREEN: `app/web/overview_ui_components.py`의 CSS / helper copy만 보강해 테스트를 통과시킨다.
3. QA: focused pytest, full service contract, py_compile, diff check, Streamlit Browser QA를 실행한다.
4. Docs: task docs와 root/doc index를 V19 기준으로 동기화한다.

## Stop Condition

- 화면에서 positive median / delta cell이 green gradient로, negative cell이 red gradient로 분명히 구분된다.
- Macro reference backdrop cards가 숫자뿐 아니라 현재 상태의 의미를 한 줄로 설명한다.
- forbidden copy인 예측 / 추천 / 매수 / 매도 / 신호 / PASS / BLOCKER 류 의미가 추가되지 않는다.
