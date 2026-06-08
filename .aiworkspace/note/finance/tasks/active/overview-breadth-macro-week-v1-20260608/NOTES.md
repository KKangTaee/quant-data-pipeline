# Notes

- 기존 `app/web/overview_dashboard.py`에는 `_build_group_leadership_heatmap()`이 있으나 Sector / Industry 탭에서 아직 렌더링되지 않는다.
- Events 탭에는 summary strip과 source lane이 있으므로, 3차 macro week lane은 그 아래의 scan-first context로 연결한다.
- `build_overview_breadth_heatmap_summary()`는 기존 group leadership snapshot만 접는다. DB fetch, provider fetch, write side effect가 없다.
- `build_overview_macro_week_lane()`은 기존 event calendar rows의 `Days Until`, `Type`, `Freshness`, `Validation`, `Quality Action`을 접어서 14일 lane과 cluster를 만든다.
- Browser QA에서는 Events 탭에서 `Macro Week Lane`이 2개 near events, FOMC / Earnings cluster, source review 상태, context-only boundary를 표시하는 것을 확인했다.
