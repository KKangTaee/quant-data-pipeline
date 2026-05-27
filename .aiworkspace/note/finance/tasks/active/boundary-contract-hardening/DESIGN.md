# Boundary Contract Hardening Design

Status: Complete
Created: 2026-05-27

## Current Baseline

`check_ui_engine_boundary.py`는 현재 `app/services/*.py`, `app/runtime/*.py`에서 다음을 hard violation으로 본다.

- `streamlit` import
- `st.` access
- staged generated / registry / saved / run-history / local artifact

`app.web` import는 transition 기간 advisory로 남아 있었지만, Task 6에서 Practical Validation web helper import를 제거했고 boundary lint advisory도 0건이 됐다.

## Target Behavior

`app/services`와 `app/runtime`은 UI layer를 참조하지 않는다.

따라서 아래 import는 hard violation이어야 한다.

```python
from app.web.backtest_common import ...
import app.web.backtest_common
```

## Test Direction

DB-backed runtime smoke보다 boundary checker behavior test를 우선한다.

Test should verify:

- temp boundary file containing `from app.web...` produces `kind == "app_web_import"` in violations.
- advisory list remains empty for that case.
- existing import tests still prove service/runtime imports do not load Streamlit.

## Browser QA

This task changes helper scripts, tests, and docs only.
There is no visible Streamlit screen behavior change, so browser QA is not required.
