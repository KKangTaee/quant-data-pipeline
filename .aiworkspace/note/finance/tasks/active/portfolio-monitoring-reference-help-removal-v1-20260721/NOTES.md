# Portfolio Monitoring Reference Help Removal V1 Notes

- `final_selected_portfolio_dashboard.py`에는 동일 contextual helper import가 두 번 존재한다.
- Portfolio Monitoring page는 React workspace render 전에 contextual help를 호출한다.
- canonical Reference 세 item은 이미 검색, related item, stable deep link, owner destination을 제공한다.
- 2026-06 Backtest Analysis UX research와 2026-07 Practical Validation/Final Review 정리에서도 기본 업무 화면의 Reference help는 제거하는 방향을 채택했다.
- current contextual-help catalog는 Overview부터 Final Review까지 6개 surface를 소유한다. Portfolio Monitoring의 안내 source-of-truth는 Reference Center다.
- actual app은 제거 후 첫 product content로 `PORTFOLIO COMMAND CENTER`를 렌더링했고 기존 group/KPI/진단/종목 상세 흐름은 유지됐다.
