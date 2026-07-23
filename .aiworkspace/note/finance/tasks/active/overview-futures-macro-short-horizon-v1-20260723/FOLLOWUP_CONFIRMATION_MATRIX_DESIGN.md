# Futures Macro Confirmation Matrix Follow-up Design

Date: 2026-07-23
Status: User-approved direction; written-spec review pending

## 이걸 하는 이유?

현재 `확인 신호`는 경기민감 성장과 안전자산 선호를 카드로 나누고 값 아래에
`최근 1D · 5D · 20D`를 한 줄로 표시한다. 값이 `강화 · 강화 · 강화`처럼
반복되면 각 값과 기간의 수직 정렬이 없어 사용자가 어느 값이 어느 기간인지
즉시 파악하기 어렵다.

## 선택한 방식

확인 신호는 핵심 4개와 의미상 구분하되, 표시 형식은 같은 열 정렬을 사용한다.

```text
확인 신호          최근 1D    최근 5D    최근 20D
경기민감 성장        강화        강화         강화
안전자산 선호        중립        중립         약화
```

- `확인 신호`와 deterministic 요약 문장은 별도 영역에 유지한다.
- 경기민감 성장과 안전자산 선호는 카드가 아니라 두 개의 행으로 표시한다.
- 기간 제목은 값 위에 한 번만 명시한다.
- 핵심 4개 표와 동일한 방향 badge/tone을 재사용한다.
- confirmation은 별도 block과 낮은 강조색을 유지해 핵심 체제축처럼 보이지 않게 한다.

## 검토한 대안

1. 카드마다 `1D / 5D / 20D` 헤더 반복: 읽을 수는 있지만 작은 화면에서 중복이 크다.
2. 핵심 4개와 확인 2개를 완전히 한 표로 통합: 가장 단순하지만 core/confirmation 의미 경계가 사라진다.

## 변경 범위

- `app/web/streamlit_components/futures_macro_workbench/src/FamilyDirectionSection.tsx`
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- `tests/test_overview_futures_macro_short_horizon.py`
- Vite production bundle

Python payload, family 계산, 문구 생성, `NO_EDGE`, refresh와 snapshot 계약은 변경하지 않는다.

## 검증 계약

- source contract는 confirmation 영역에 `최근 1D`, `최근 5D`, `최근 20D` 헤더가 있음을 검증한다.
- 기존 카드 전용 `최근 1D · 5D · 20D` footer는 없어야 한다.
- 핵심 4개와 확인 2개 순서 및 값은 유지한다.
- Vite build와 focused Python tests를 통과한다.
- actual desktop/420px Browser QA에서 열 정렬, 가로 overflow 0, console error 0을 확인한다.

## Scope Review

- Placeholder: 없음
- Ambiguity: confirmation은 별도 미니 매트릭스이며 core 표와 완전 통합하지 않는다.
- Scope: presentation-only 후속 수정이다.
- Compatibility: payload/schema/model/DB 변화 없음
