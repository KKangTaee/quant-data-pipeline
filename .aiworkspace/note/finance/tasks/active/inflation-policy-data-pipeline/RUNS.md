# Inflation Policy Data Pipeline Runs

- 2026-08-02: `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -q`
  - Result: 27 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_schema.py -q`
  - RED: `INFLATION_POLICY_SCHEMAS`가 없어 3 failed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_schema.py tests/test_economic_cycle_vintages.py -q`
  - GREEN: 30 passed
- 2026-08-02: `git diff --check`
  - Result: passed
- 2026-08-02: 실제 raw refresh 첫 실행
  - Result: FRED DGS10 2,000 vintage 경계, release별 SEP header/participant note,
    2026 FOMC 구형 vote paragraph 차이를 실제 source에서 발견하고 fail-closed
- 2026-08-02: FRED/SEP/FOMC source-format TDD 보강
  - Result: FRED window를 1,999 vintage safety slot으로 분할하고, SEP의 release-specific
    year·새 horizon colspan·현재 release participant note, FOMC nonbreaking hyphen·구형
    vote paragraph·mixed dissent group을 지원; 관련 28 passed
- 2026-08-02: 공식 2026 FOMC statement 5건 live parse
  - Result: 1월 10-2 CUT_25 2명, 3월 11-1 CUT_25 1명, 4월 8-4
    CUT_25 1명+`HOLD_NO_EASING_BIAS` 3명, 6월 12-0, 7월 9-3 HIKE_25 3명
- 2026-08-02: `.venv/bin/python -m app.jobs.inflation_policy_refresh --as-of-at 2026-08-02T12:00:00+09:00`
  - Result: `partial_success`, 283,733 rows written, macro 26/26 성공, SEP 3,980,
    decisions 5, ACM 16,246 `LIMITED`, BEA key 부재 `NOT_AVAILABLE`, 필수 gap 0,
    `materialization_allowed=true`
- 2026-08-02: actual DB evidence query
  - Result: 2026-06 dots `{3.375:1, 3.625:8, 3.875:3, 4.125:5, 4.375:1}`,
    Core PCE `3.5-3.6` 4명, 2026-07-29 target 3.50-3.75%·9-3·HIKE_25 3명
- 2026-08-02: strict PIT actual DB cutoff smoke
  - Result: `2026-07-29T18:00:00Z` bundle의 모든 `released_at`이 cutoff 이하,
    2026-06 Core PCE row 0건; 실제 2026-07-30 12:30Z release 이후 bundle에는 1건
- 2026-08-02: data foundation focused regression
  - Result: inflation-policy schema/source/loader/refresh와 economic-cycle compatibility,
    S&P valuation 133 passed; third-party `edgar` deprecation warning 3개
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fomc_policy_data.py -q`
  - RED: decision parser/history collector 부재 확인
  - GREEN: SEP와 결정 chronology 통합 9 passed
- 2026-08-02: 공식 `monetary20260729a.htm` live parser smoke
  - Result: 3.50-3.75%, 9-3, `HIKE_25` 반대 3명, `READY`
- 2026-08-02: `.venv/bin/python -m pytest tests/test_nyfed_term_premium.py -q`
  - RED: ACM collector module 부재로 3 failed
  - GREEN: discovery, no-forward-fill normalization, `LIMITED` collector 3 passed
- 2026-08-02: 공식 `ACMTermPremium.xls` live normalization smoke
  - Result: `ACM Daily` 최신 관측 2026-07-30, `ACMTP10` 정상화 성공
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_loaders.py -q`
  - RED: loader/store module 부재로 6 failed
  - GREEN: cutoff, latest vintage, ACM limitation, finite JSON, UPSERT, snapshot 6 passed
- 2026-08-02: strict loader/store focused regression 및 compile
  - Result: 28 passed, `py_compile` passed, `economic_cycle` reference 0건
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_refresh.py -q`
  - RED: refresh module/wrapper/scheduler 부재로 6 failed
  - GREEN: required gate, optional limit, macro coverage, scheduler, wrapper, CLI 6 passed
- 2026-08-02: ingestion/scheduler regression
  - Result: 관련 31 passed, third-party `edgar` deprecation warning 3개
- 2026-08-02: BEA/refresh/loader focused compile gate
  - Result: 18 passed, `py_compile` 및 `git diff --check` passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fred_vintages.py -q`
  - RED: module 부재로 7 failed
  - GREEN: release clock, pagination, normalization, UPSERT 7 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fred_vintages.py tests/test_economic_cycle_vintages.py tests/test_economic_cycle_refresh.py -q`
  - Result: 41 passed, dependency deprecation warning 3개
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_catalog.py tests/test_bea_pce_components.py -q`
  - RED: 독립 catalog와 BEA component module 부재로 6 failed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_inflation_policy_catalog.py tests/test_fred_vintages.py tests/test_bea_pce_components.py tests/test_economic_cycle_vintages.py -q`
  - Result: 42 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fomc_policy_data.py -q`
  - RED: SEP module/collector 부재와 불일치 fixture target 오류 확인
  - GREEN: 익명 분포, participant 합계, URL discovery, UPSERT, 수집 경계 6 passed
- 2026-08-02: `.venv/bin/python -m pytest tests/test_fomc_policy_data.py tests/test_inflation_policy_schema.py tests/test_fred_vintages.py tests/test_economic_cycle_vintages.py tests/test_sp500_valuation.py -q`
  - Result: 93 passed, third-party `edgar` deprecation warning 3개
- 2026-08-02: `git diff --check`
  - Result: passed
