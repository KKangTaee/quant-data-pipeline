# Today Contributor Performance Cards V1 Status

Status: Complete
Roadmap: 4/4 complete
Last Updated: 2026-07-22

## Completed

- `app/services/portfolio_monitoring/read_model.py` item row는 그룹 공통 `basis_date`의 exact flow-adjusted `total_return`만 additive하게 제공한다. 기준일 row/value가 없으면 이전·이후 값을 재사용하지 않고 `None`을 반환한다.
- selected-position은 기존 자체 최신일 의미를 유지해 `lane.latest_usable_date`의 exact row만 사용하며 trailing-null/missing latest는 `None`이다.
- `app/services/today.py` contributor projection을 `contribution_value` / `total_return`으로 명시하고 기존 `value` alias 호환을 유지했다.
- React primary와 Python fallback을 최대 4개의 compact performance card로 교체하고 독립 tone, 자료 부족, 기준일 footer와 양수 `+$…` / 음수 `-$…` contribution 표기를 구현했다.
- 최종 리뷰 지적을 RED로 재현한 뒤 Python `66 passed, 3 warnings, 2 subtests passed`, React `6 passed`, typecheck/build, py_compile, diff check를 fresh 실행으로 통과했다.
- root `/`의 actual Browser QA에서 1280·760 2열, 760 outer stack, 420 1열, horizontal overflow 0, clipping 0, console error 0을 확인했다.
- 전체 roadmap `4/4차`를 완료했고 DB·ingestion·provider·registry·saved·run-history·Portfolio Monitoring UI는 변경하지 않았다.

## Browser Evidence

- Server: `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8517 --server.headless true`
- URL: `http://localhost:8517/`
- Actual cards: AMD `+357.97% / +$11,915`, RKLB `+166.56% / +$4,319`, TEM `-21.46% / -$401`, SOXX `-7.84% / -$282`
- Footer: `종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 2026-07-21`
- Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/today-contributor-performance-cards-v1-browser-qa.png` (generated, commit 제외)

## Handoff

- 승인 범위의 남은 차수는 없다.
- 이후 Today contributor 변경은 `NOTES.md`의 field contract와 `RUNS.md`의 regression/viewport 기준에서 이어서 확인한다.
