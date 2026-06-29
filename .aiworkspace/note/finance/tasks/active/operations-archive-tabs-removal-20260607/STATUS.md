# Operations Archive Tabs Removal Status

Status: Complete
Date: 2026-06-07

## Summary

- `app/web/streamlit_app.py`에서 Operations navigation의 `Archive: Backtest Runs`, `Archive: Candidates` entries를 제거했다.
- `app/web/operations_overview.py`에서 archive / reference secondary lane과 archive recovery action queue를 제거했다.
- surface audit은 archive 화면이 hidden compatibility path로 남고, 데이터 / helper code는 별도 audit 전까지 삭제하지 않는다고 표시한다.
- durable docs를 `Operations = Portfolio Monitoring + System / Data Health` 기준으로 갱신했다.

## Roadmap Position

- 전체 Operations 개편 중 이번 작업은 archive UI 정리 차수다.
- 완료한 차수: archive 탭 제거 / Operations 정체성 축소.
- 남은 차수: Portfolio Monitoring first summary 강화, System / Data Health와 monitoring evidence health 연결, archive 데이터 실제 삭제 audit.
