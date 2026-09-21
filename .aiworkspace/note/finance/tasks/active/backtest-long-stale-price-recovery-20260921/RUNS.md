# 실행 기록

- 기존 두 run-history record를 입력으로 refresh plan을 재현: 첫 실행 QQQ/SOXX만 대상, 두 번째 provider_gap_only.
- DB loader read: IAU/IEF/MTUM/QUAL/TLT/USMV 2026-08-05, QQQ/SOXX 2026-09-18 확인.
- `python -m pytest`는 로컬 venv에 pytest가 없어 실행 불가. 저장소 기존 unittest 방식으로 회귀 테스트를 실행했다.
- RED: `python -m unittest tests.test_backtest_price_refresh -v` — 기대한 대상 누락/차단으로 3 failure.

## 수정 후 검증

- GREEN: 새 regression 2개(subtest 2개 포함) + BacktestRuntimeContractTests의 price_refresh 관련 15개 = 17개 통과.
- downstream: Level1 freshness 함수 7개 + GTAA runtime / Final Review refresh unittest 12개 = 19개 통과.
- 합계 36개 관련 테스트 통과. 최초 넓은 BacktestRuntimeContractTests 실행에서는 총 92개 중 기존 7 failure / 5 error가 있었으며 아래 baseline 재확인과 동일했다.
- 변경 전 persistent_source_gap marker를 프로세스 메모리에서 복원하여 unrelated 75개를 재검증: 같은 7 failure / 5 error 재현. 명세/코드 불일치 목록은 RISKS.md에 기록. 사용자 파일을 되돌리지 않았다.
- `git diff --check`, Python compile 통과.
- 독립 코드 리뷰: actionable finding 없음.

## 승인된 실제 데이터 복구

실행: 마지막 GTAA run-history record에서 start/end를 복원하고 수정한 `run_backtest_price_refresh`를 호출했다. 실행 직전 tickers 6개 및 2026-08-06~09-18 범위를 assert했다. 기존 ingestion의 일봉 종료일 포함 처리와 MySQL writer를 사용했다.

- 결과: status=success, rows_written=186, symbols_processed=6, failed_symbols=[]
- 전체 8개 종목의 DB latest_date=2026-09-18. 6개 복구 종목은 각각 31개 일봉이 추가됐다.
- CLI 재현: 기존 기록의 GTAA runner 파라미터를 복원하고 interval=4, top=2, 시작 2016-01-01, 종료 2026-09-18로 실행. registry write 없음.
- 확인 결과: {"requested_start": "2016-01-01", "requested_end": "2026-09-18", "actual_start": "2016-01-29", "actual_end": "2026-09-18", "result_rows": 129, "freshness_status": "ok", "common_latest": "2026-09-18", "stale_count": 0, "missing_count": 0, "tickers": ["QQQ", "SOXX", "MTUM", "QUAL", "USMV", "IAU", "IEF", "TLT"], "preset_name": "GTAA SPY Low-MDD Style Top-2 ADV20", "top": 2, "interval": 4}
- Browser QA: 별도 검증 탭에서 같은 프리셋과 종료일을 선택해 실행. 결과 헤더 2016-01-29 ~ 2026-09-18, 가격 최신성 ok, 가격 gap 경고 없음, Level2 인계 가능 표시. 후보 저장/인계는 실행하지 않았다.
- QA 이미지: `/tmp/gtaa-price-recovery-20260921-qa.png` (generated, commit 제외). UI 정상 실행으로 local run history가 append되며 commit 제외.
