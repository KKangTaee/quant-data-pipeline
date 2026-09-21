# Runs

- `.venv/bin/python -m pytest ...`: 프로젝트 venv에 pytest가 없어 실행 불가.
  README의 `PYTHONPATH=. uv run --with pytest` 경로를 사용하며 dependency manifest는 변경하지 않는다.

모든 pytest 실행은 `PYTHONPATH=. uv run --frozen --inexact --with pytest python -m pytest`를 사용했다.

1. Baseline: `tests/test_economic_cycle_refresh.py tests/test_economic_cycle_asset_freshness.py tests/test_economic_cycle_asset_refresh.py tests/test_economic_cycle_freshness.py tests/test_market_context_economic_cycle.py -q`
   - 54 passed, 2 failed. 기존 `test_latest_refresh_date_uses_previous_friday_on_weekend`,
     `test_stale_intramonth_exposes_manual_action`이 현재 전월 말 계약과 충돌했다.
2. RED: 신규 `tests/test_economic_cycle_refresh_reference_date.py -q` → 9 failed.
   - stale 자산 collection이 호출되지 않음, 최신 자산을 월말로 잘라 불필요하게 수집하는 오류를 재현했다.
3. GREEN: 위 baseline 5개 파일 + 신규 회귀 파일 → 65 passed, edgartools deprecation warning 3개.
   - 기존 freshness 테스트를 공식 월간 계약에 정렬하고 연초/윤년 월말도 확인했다.
4. Downstream: `tests/test_economic_cycle_service.py -q` → 42 passed.
5. 실제 QA 전 월간 snapshot checksum:
   `6d5d5f39b4deddd0ce9998a8ebeaf3851d3cb820921905f1d915d325f5148a13`.
   as_of_date `2026-08-31`, updated_at `2026-09-01 08:26:19`.
6. 앱 재시작 후 `2026-09-21 09:02` 경기 국면의 `최신 데이터 반영`을 실제 클릭했다.
   - 09:02:39–09:02:56, 16.699초, `success`, 15개 처리/실패 없음.
   - requested/refreshed/cache scopes는 모두 `asset_pathways`만 포함.
   - 67,542행 UPSERT 처리(새 unique row 수를 뜻하지 않음).
   - 갱신 전후 공식 snapshot checksum 동일. as_of_date와 updated_at도 동일.
   - DB 재조회: asset status `READY`, stale/missing 없음, 원천 최신 관측일 09-20.
   - 화면: `경제사이클 계산 최신 · 자산 경로 최신`, 공식 관측 월 `2026-08-31`,
     마지막 성공 수집 `2026-09-21 09:02:56`. 정상 완료 후 갱신 버튼은 숨겨진다.
   - QA screenshot: `.playwright-mcp/economic-cycle-refresh-fixed-20260921.png`
     (generated, 커밋 제외).
7. 독립 review P2 재현: economic_cycle_freshness의 clock을 2027-01-01로 설정한
   `-k None` 실행에서 2 failed. 두 clock 참조를 함께 고정한 뒤 동일 조건에서
   전체 focused 7개 파일을 실행해 **107 passed, 3 warnings** (4.49초).
   - warnings는 기존 edgartools deprecated module 안내 3건.
   - review follow-up: 추가 수정 필요 사항 없음.
8. `git diff --check` 통과. Python compile 및 staged diff 확인 후 이번 파일만 커밋.
