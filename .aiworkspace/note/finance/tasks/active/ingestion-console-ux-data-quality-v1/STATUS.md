# Ingestion Console UX / Data Quality V1 Status

Status: Follow-up implementation complete / QA complete

## Progress

- Task opened.
- Initial review found the approved first slice: Korean purpose-first UI, result guidance, hidden lifecycle job exposure, and data-quality caveats.
- `Workspace > Ingestion` now separates routine operations / validation data from manual recovery / diagnostics.
- Major Run Jobs now show Korean names, purpose, DB target, downstream use, quality caveats, and next-action guidance while preserving user-controlled symbol / period / source inputs.
- Hidden lifecycle collectors for Nasdaq Symbol Directory snapshots, SEC CIK / ticker cross-check, and computed snapshot lifecycle are exposed under `상장 / 상폐 근거` with explicit survivorship caveats.
- Recent result, session history, and persistent run-history summaries now display Korean job titles and data-quality guidance while retaining internal English job ids for traceability.
- Follow-up responsive polish fixed narrow-width truncation for Ingestion result summaries, runtime/build metadata, job meta rows, symbol source labels, and persistent run-history selection display.
- Selectbox follow-up removed internal BaseWeb dropdown CSS overrides after user found the first option could appear blank or become hard to click; full-value captions remain outside the selectbox.
- Follow-up request accepted: improve the reviewed Ingestion UX/data-quality surface without forcing every term/button into Korean. Terms such as Provider, OHLCV, Period, PIT can remain as-is; explanatory content should be clearer in Korean.
- Ingestion now shows a top workflow overview: 수집 범위 선택 -> Preflight 확인 -> DB 저장 -> 결과 해석.
- Daily / manual OHLCV / core pipeline cards now show an execution contract before running: source, target count, period/window, interval, execution profile or freq.
- Bounded date-window price runs now show a lightweight DB coverage quick check before execution; large runs skip this automatically and point users to result diagnostics.
- Result summary metrics now use domain-aware labels such as 가격 Row, 증거 Row, 수집 대상, so row counts are not read as the same kind of symbol coverage.
- Result interpretation callouts were added for price, pipeline, lifecycle, provider snapshot, macro, and event jobs.
- Lifecycle tab now keeps the current-snapshot / partial-evidence warning visible as a callout, not only inside collapsed caveats.
- Preflight / symbol-source / runtime-estimate messages were adjusted to Korean explanatory text while preserving technical terms and option values where useful.

## Next

- User review at `http://localhost:8505/ingestion`.
- Follow-up candidate: full post-run requested-window coverage report for large price collections if UI quick check is not enough.
