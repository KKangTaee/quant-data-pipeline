# Portfolio Monitoring Tracking End UX Fix V1 Notes

## Root Cause

- UI는 `requested_end_date=today`를 보낸다.
- Python resolver는 `lane.date >= requested_end_date`만 허용한다.
- 휴장일이나 당일 close 미저장 시 eligible row가 없어 command가 실패하고 item status는 유지된다.
- React의 command state는 add-item draft command id만 찾고 drawer 안에서만 렌더링해 종료 실패가 보이지 않는다.
- read model의 `lane_status`는 item lifecycle과 독립적이어서 종료 상세에서도 raw `ACTIVE`가 남을 수 있다.
