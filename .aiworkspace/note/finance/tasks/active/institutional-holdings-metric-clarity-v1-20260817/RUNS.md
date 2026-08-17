# Runs

- RED: `.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -k "separates_positive or popularity_model_ranks or source_caveats" -q` → expected 2 failures: sign-separated contributor list and missing `reported_value_label`.
- RED: `InstitutionalPortfolioReadModelTests::test_visual_workbench_payload_prioritizes_portfolio_chart_and_change_boards` → expected missing `source_caveats.title` failure.
- GREEN: `.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q` → 76 passed, 3 third-party `edgar` deprecation warnings, 4 subtests passed.
- Review: `git diff --check` → clean.
- Task 4 regression: `.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q` → `76 passed, 3 warnings, 4 subtests passed in 1.70s`.
- Task 4 React: `npm test && npm run typecheck && npm run build` → `1` file / `9` tests passed, typecheck exit `0`, Vite `173` modules transformed and production build exit `0`.
- Task 4 compile/check: `.venv/bin/python -m py_compile app/services/institutional_quarter_review.py app/services/institutional_portfolios.py app/web/institutional_portfolios.py && git diff --check` → exit `0`.
- Actual Browser QA: local Streamlit `http://127.0.0.1:8502/institutional-portfolios`, Berkshire `2026-03-31 → 2026-06-30` review. `%/%p` and sign-specific lists pass; formula computed color `rgb(250, 250, 250)` on light card fails visible guide.
- Ranking manual load pass; loaded GOOGL row showed `보유 기관 7개`, but reported-value emphasis had `text: ''`, height `0`; market-cap/volume clarification counts were `0`.
- Disclosure initially collapsed, but summary text was empty and body remained English `6` bullets instead of Korean `3` bullets.
- Layout: desktop iframe `clientWidth=1109`, `scrollWidth=1109`; 390px iframe `clientWidth=347`, `scrollWidth=347`; mobile tablist alone scrolls (`309/580`, `overflow-x:auto`) and tabpanel has no overflow (`309/309`).
- Console: `0` errors, `0` warnings.
- Screenshot: `institutional-holdings-metric-clarity-v1-qa.png` (generated, untracked, not staged).

## Resume / Final QA

- Existing `:8502` process를 피하고 current HEAD `7b8fd606`에서 fresh Streamlit `:8521`을 시작했다. QA 후 해당 process를 정상 종료했다.
- Fresh regression: Python `77 passed, 3 warnings, 4 subtests passed in 1.67s`; React `1` file / `9` tests passed; typecheck/build exit `0`; Vite `173` modules transformed.
- 분기 리뷰는 formula guide와 세 metric을 표시했다. Formula는 foreground `rgb(23, 35, 55)` / background `rgb(247, 250, 252)`로 읽을 수 있었다.
- 종목 수익률은 `%`, 포트폴리오 기여는 `%p`로 분리됐고 contributor/detractor는 각각 양수/음수 row만 포함했다.
- 랭킹은 manual load를 유지했고 첫 row가 `보유 기관 7개 / 13F 보고 보유가액 합계 $31.4B`를 표시했다. 시가총액, 거래량, 현재 보유액이 아니라는 설명도 표시했다.
- Disclosure는 initial `open=false`, Korean title/subtitle, expanded Korean bullets 정확히 `3`개를 확인했다.
- Desktop iframe `1109/1109`, 390px iframe `347/347` client/scroll width로 page overflow가 없었다. 모바일 tablist만 `309/580`, `overflow-x:auto`이고 ranking card/metric label collision은 없었다.
- Browser console error/warning `0/0`; 최종 screenshot을 `institutional-holdings-metric-clarity-v1-qa.png`로 교체했다.
