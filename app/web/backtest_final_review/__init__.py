from __future__ import annotations

from app.web.backtest_final_review import page as _page

for _name in dir(_page):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_page, _name)

__all__ = [name for name in globals() if not name.startswith("__")]
