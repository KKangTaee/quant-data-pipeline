# Design

## Current State

- `app/services/reference_guides_catalog.py`는 task card, journey, concept, record, playbook을 Streamlit-free dict list로 제공한다.
- `app/web/reference_guides.py`는 Reference Center 기본 화면과 기존 Portfolio Selection Journey를 렌더링한다.
- 1차 playbook은 증상 / first check / safe action / stop condition만 보여준다.

## 2차 Direction

```text
Reference Center
  -> 제품 흐름
     -> journey summary table
     -> selected journey detail
        -> ordered steps
        -> common failures
        -> next owner screen
  -> 문제 해결
     -> selected playbook
        -> check steps
        -> evidence locations
        -> owner screen / safe action / stop condition
```

## Ownership

| File | Responsibility |
|---|---|
| `app/services/reference_guides_catalog.py` | Streamlit-free journey/playbook detail catalog. |
| `app/web/reference_guides.py` | Streamlit rendering only. Selectboxes, cards, tables, captions. |
| `tests/test_reference_guides_catalog.py` | Contract tests for V2 detail shape and read-only boundary. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Durable Reference guide flow summary. |

## Boundary

Reference remains read-only. It may explain owner screens and evidence locations, but it must not run jobs, write registries, mutate saved setup, or imply live trading actions.
