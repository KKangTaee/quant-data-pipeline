# Streamlit Native Pages Sidebar Fix 2026-06-30

## 이걸 하는 이유?

앱을 처음 시작하거나 `/backtest` 경로가 브라우저에 남아 있을 때 Streamlit native multipage sidebar가 `streamlit app` / `backtest`를 노출했다. Finance Console은 `app/web/streamlit_app.py`의 top navigation이 canonical entry여야 하므로, native `pages/` auto-discovery와 top navigation이 경쟁하지 않게 한다.

## Scope

- `app/web/pages/backtest.py`를 `pages/` 밖의 Backtest shell module로 이동한다.
- `streamlit_app.py`는 새 Backtest shell module을 import한다.
- 회귀 테스트로 `app/web/pages/` native page directory가 다시 생기지 않게 막는다.
- durable code map / flow docs의 Backtest shell 경로를 맞춘다.

## Out Of Scope

- Backtest workflow stage 의미 변경
- Streamlit top navigation IA 개편
- registry / saved / run history 변경
- provider / DB / strategy runtime 변경
