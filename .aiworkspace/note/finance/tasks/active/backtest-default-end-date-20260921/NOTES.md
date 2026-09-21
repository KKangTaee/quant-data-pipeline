# 조사

공통 `app/services/backtest_single_settings_workspace.py::_date_fields`의 literal `2026-07-18`이 원인. 기존 Streamlit form의 today 상수와 별개 경로다. 모든 13개 concrete variant가 같은 helper를 사용한다.

## 추가 사용자 질문: Cash/현금 의미

사용자는 Cash가 다음 10월 현금 보유 지시인지 질문했다. GTAA runtime의 Cash는 해당 행에서 Next Balance와 함께 갱신된 현금 잔액이다. `backtest_analysis_result_workspace::_single_holdings_projection`은 이 Cash를 End Ticker/End Balance와 함께 current_allocation으로 표시하고, target_row 선택은 비어 있지 않은 Next Ticker만 선택하므로 전량 현금 전환 시 이전 목표로 돌아갈 수 있다. 이번 날짜 수정과 별개 문제이며 아직 수정하지 않았다.

같은 Top-2 ADV20 프리셋, 종료 2026-09-18을 새 프로세스에서 재계산하면 Cash=0, Next Ticker=[SOXX, MTUM]이었다. 이전 브라우저 결과와 차이가 있어 표시 시점 혼재 외 기존 DB-derived cache 영향도 추가 확인이 필요하다. 이를 10월 확정 운용 지시로 해석할 수 없다고 설명했다.
