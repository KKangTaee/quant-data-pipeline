# 확인한 사실

- Next Ticker 빈 목록에 `or current`를 적용해 기존 종목을 재사용했다.
- current card에 변경 후 Cash를 더했고 target card에서 Cash를 누락했다.
- target row 선택이 빈 종목 목록을 건너뛰어 이전 리밸런싱 구성으로 후퇴했다.
- 비용 후 Total Balance와 비용 전 보유액의 혼용으로 100% 초과 비중이 나왔다.

- 다른 전략의 End Ticker 계약이 동일하지 않으므로 GTAA/Equal Weight만 변경 전 리밸런싱 구성을 표시한다. GRS/strict 등에는 이유와 확인 불가를 표시하며 변경 후와 기존 매매 기록을 보존한다.
- focused durable BACKTEST_UI_FLOW의 보유/표시 의미만 정렬. INDEX/ROADMAP/PROJECT_MAP/root log 변경 없음.
