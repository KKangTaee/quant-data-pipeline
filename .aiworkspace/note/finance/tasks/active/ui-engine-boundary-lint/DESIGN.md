# UI Engine Boundary Lint Design

Status: Complete
Created: 2026-05-20

## Boundary Rules

Hard fail:

- `app/services/*.py`에서 `import streamlit` 또는 `from streamlit` 사용
- `app/services/*.py`에서 `st.` 사용
- staged diff에 generated / registry / saved JSONL / run history / local artifact가 포함됨

Advisory only:

- `app/services/*.py`에서 `app.web.*` import

현재 service는 transition 단계라 `app.web.runtime`과 일부 Streamlit-free helper를 아직 import한다.
이 경고는 다음 정리 후보를 보여주기 위한 것이며, 지금 task에서는 실패 조건으로 삼지 않는다.

## Script Shape

Location:

```text
.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Output:

- text report by default
- optional `--json`
- non-zero exit only for hard violations

## Why Not Phase?

이 작업은 새 architecture phase가 아니라, 이미 완료한 boundary phase를 보호하는 단일 automation task다.

## Implemented

- `check_ui_engine_boundary.py` added under repo-local workflow scripts.
- Hard violations cover Streamlit usage in services and staged generated / registry / saved artifacts.
- Transitional `app.web` imports from service files are reported as advisory.
