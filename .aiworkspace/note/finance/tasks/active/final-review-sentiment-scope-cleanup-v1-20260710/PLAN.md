# Final Review Sentiment Scope Cleanup V1

## 이걸 하는 이유?

Final Review는 Gate 통과 후보를 비교하고 Portfolio Monitoring 후보로 저장할지 판단하는 화면이다. CNN / AAII 시장심리는 현재 gate, score, 저장 가능 여부, monitoring signal을 바꾸지 않는데도 first-read 영역에서 큰 패널과 원자료 table을 차지해 사용자가 판단 근거처럼 읽을 수 있다.

## Goal

Final Review first-read 화면에서 시장심리 패널과 CNN / AAII detail expander를 제거하고, 시장심리 해석은 `Workspace > Overview > Sentiment`와 `Operations > Portfolio Monitoring`의 read-only context에 남긴다.

## Scope

- `app/web/backtest_final_review/page.py`
  - Final Review render path에서 market sentiment overlay 호출을 제거한다.
  - Final Review 전용 sentiment display helper를 제거한다.
- `tests/test_service_contracts.py`
  - Final Review가 sentiment panel / detail expander를 렌더링하지 않는 source contract로 갱신한다.
  - Practical Validation / Portfolio Monitoring sentiment boundary test는 유지한다.
- `.aiworkspace/note/finance/docs/flows/`
  - Final Review flow와 Portfolio Selection flow에서 sentiment compact 표시 설명을 제거한다.
  - timing / rebalance research-only 경계는 유지한다.
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
  - Final Review page 책임에서 sentiment overlay를 제거한다.

## Out Of Scope

- 시장심리를 마켓타이밍 / 리밸런싱 / selection gate / monitoring signal로 연결하지 않는다.
- Overview > Sentiment React workbench와 Operations > Portfolio Monitoring sentiment context는 변경하지 않는다.
- registry / saved JSONL / run history / generated QA artifact는 stage하지 않는다.

## Completion

- RED/GREEN focused service contract를 확인한다.
- `app/web/backtest_final_review/page.py` py_compile과 `git diff --check`를 통과한다.
- Browser QA로 Final Review 상단에 `시장 심리`, `CNN / AAII detail`, `Timing / Rebalance` first-read 패널이 없는지 확인한다.
- coherent commit을 만든다.
