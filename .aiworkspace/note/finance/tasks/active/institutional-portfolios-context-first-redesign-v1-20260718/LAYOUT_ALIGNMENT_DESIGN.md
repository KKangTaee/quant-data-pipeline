# Institutional Portfolios Hero Layout Alignment Design

Status: Approved Design
Last Updated: 2026-07-18

## 이걸 하는 이유?

Context-First hero의 정보 내용은 맞지만, 우측 `보고 근거` 카드와 아래 `최신 13F 데이터 갱신` 영역이 서로 다른 grid 비율과 수직 정렬 규칙을 사용한다.

- `DB snapshot`이 2열 grid의 첫 번째 cell만 사용해 오른쪽에 의도하지 않은 빈칸이 생긴다.
- hero는 `1.45fr / 0.75fr`, controls는 `1fr / 0.65fr`를 사용해 좌우 경계가 맞지 않는다.
- controls의 `align-items: center` 때문에 갱신 스트립이 검색 입력과 manager rail 사이 높이에 떠 보인다.
- 좁은 우측 열 안에서 action / period / collected time을 한 행에 배치해 수집 시각이 불필요하게 잘린다.

## Approaches Considered

### A. Shared Two-Column Grid And Matched Control Labels — Chosen

- hero와 controls에 동일한 좌우 column contract를 적용한다.
- `보고 기준 분기 | 제출일`은 첫 행 2열로 둔다.
- `DB snapshot`과 `SEC 원문 열기`는 각각 전체 폭을 사용한다.
- manager search와 freshness 영역 모두 label row를 가진다.
  - 왼쪽: `기관 / 투자 대가 검색`.
  - 오른쪽: `데이터 기준`.
- 검색 input과 freshness control의 상단선과 기본 높이를 맞춘다.
- freshness 내부는 action / report period를 첫 행, collected time을 전체 폭 둘째 행에 둔다.

장점: 현재 정보 구조와 event를 유지하면서 빈칸, 수직 부유, 말줄임을 함께 해결한다.

### B. Freshness를 보고 근거 카드 안으로 이동 — Rejected

- 우측 정보가 한 카드에 모이지만 보고 근거와 갱신 action의 의미가 섞이고 카드가 과밀해진다.

### C. Margin 보정만 적용 — Rejected

- 특정 viewport에서는 맞아 보여도 label 높이, 검색 결과 state, 글꼴 크기에 따라 다시 어긋난다.

## Approved Layout Contract

### Desktop

```text
┌────────────────────────── left context ──────────────────────────┬──────── right basis ────────┐
│ headline / summary / signals                                     │ report period | filing date │
│                                                                  │ DB snapshot (full width)    │
│                                                                  │ SEC source (full width)     │
├───────────────────────────────────────────────────────────────────┼──────────────────────────────┤
│ 기관 / 투자 대가 검색                                            │ 데이터 기준                  │
│ search input + button                                             │ refresh action | report date │
│ manager rail                                                      │ collected time (full width)  │
└───────────────────────────────────────────────────────────────────┴──────────────────────────────┘
```

- hero와 controls는 같은 `minmax(0, 1.45fr) minmax(320px, 0.75fr)` column contract를 쓴다.
- 두 grid 모두 child에 `min-width: 0`을 유지한다.
- controls는 `align-items: start`를 사용한다.
- freshness block의 label과 manager search label은 같은 font, line-height, bottom gap을 사용한다.
- freshness control은 한 행을 억지로 유지하지 않는다. 수집 시각은 둘째 행 전체 폭에서 줄바꿈 가능하게 표시한다.

### Tablet / Mobile

- 기존 `980px` 이하에서 hero와 controls를 1열로 전환하는 contract를 유지한다.
- `720px` 이하에서는 basis의 첫 행 2열을 유지할 수 있으나 `420px`에서는 1열로 전환한다.
- freshness action, report period, collected time은 모바일에서 자연스러운 1열 reading order를 사용한다.
- page / iframe horizontal overflow를 허용하지 않는다.

## Files And Boundaries

- `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
  - freshness block에 `데이터 기준` label wrapper를 추가한다.
  - 데이터/event/payload 의미는 변경하지 않는다.
- `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
  - shared desktop grid, basis span, freshness rows, responsive alignment를 수정한다.
- `tests/test_institutional_portfolios.py`
  - layout source/runtime contract regression을 추가한다.
- tracked `component_static/`
  - 검증된 Vite build 결과로 갱신한다.

## Validation Contract

- source contract가 hero와 controls의 동일 column rule, full-width snapshot, freshness label/row contract를 확인한다.
- Vitest, TypeScript typecheck, Vite build, focused Python suite를 통과한다.
- actual Browser QA:
  - desktop에서 우측 basis의 빈 cell이 없다.
  - search input과 freshness control의 상단선이 맞는다.
  - hero와 controls의 좌우 column boundary가 일치한다.
  - collected time이 의미 없이 잘리지 않는다.
  - 420px에서 1열 흐름과 no-overflow를 유지한다.
- QA screenshot 1장을 generated artifact로 남기고 stage하지 않는다.

## Out Of Scope

- context copy, manager search behavior, refresh event, portfolio chart, holdings explorer 변경.
- 데이터 schema 또는 payload version 변경.
- 새로운 운영 진단 panel 추가.
