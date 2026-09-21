# 상태

State: complete

- 1차 완료: 장기 stale heuristic의 수집 제외를 제거. 특정 ETF whitelist 없이 공통 경로 수정. 관련 36개 테스트와 코드 리뷰 통과.
- 2차 완료: IAU, IEF, MTUM, QUAL, TLT, USMV의 2026-08-06~09-18 일봉 186개 저장, 실패 0. 전체 8종목 DB 최신일 09-18 확인.
- 3차 완료: 같은 GTAA SPY Low-MDD Style Top-2 ADV20 설정의 DB runtime 및 브라우저 재실행 확인. actual_result_end=2026-09-18, 가격 최신성 ok, stale/missing 0.
- 잔여 차수 없음. 기존에 열린 사용자 세션의 결과는 같은 설정으로 재실행하면 갱신된다.
- 다음 확인: `app/services/backtest_price_refresh.py`, 이 task의 `RUNS.md`와 `RISKS.md`.
- focused durable doc: `docs/flows/BACKTEST_UI_FLOW.md`의 가격 최신화 계약만 정렬. INDEX / ROADMAP / PROJECT_MAP 변경 없음.
