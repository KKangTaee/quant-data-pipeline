# Global Relative Strength 5A Plan

## 이걸 하는 이유?

Backtest Analysis 4C 이후 방향은 새 evidence / workbench 패널을 늘리는 것이 아니라 전략 실행과 후보 생성의 질을 높이는 것이다.
5A는 Global Relative Strength의 실제 전략 runtime, transform, result bundle 계약을 고도화해 cash proxy, benchmark, 제외 ticker, stale price, top-N concentration, rebalance interval, momentum window 해석을 더 명확하게 만든다.

## Scope

- GRS strategy runtime / transform / result bundle 개선
- Streamlit-free focused tests 추가
- Backtest Analysis UI는 필요한 최소 연결만 수정
- 사용자-facing 설명은 한국어 중심
- registry / saved JSONL / run_history / generated artifact는 수정하거나 커밋하지 않음
- 새 evidence / log / workbench 패널 추가 금지

## Tentative Roadmap

### 5A-1 Task setup and failing tests

- 목적: GRS core behavior를 Streamlit-free test로 고정한다.
- 범위: `tests/test_global_relative_strength_strategy.py`, task docs.
- 완료 조건: 현재 코드에서 rebalance interval / cash concentration / runtime contract 관련 테스트가 실패한다.
- 다음 연결: 실패 테스트가 구현 변경의 기준이 된다.

### 5A-2 Strategy and transform contract

- 목적: interval 이중 적용 가능성과 momentum score normalization을 바로잡는다.
- 범위: `finance/sample.py`, `finance/strategy.py`, 필요 시 `finance/transform.py`.
- 완료 조건: `interval=3`이 3개월 cadence로만 동작하고 score window / weights가 일관되게 해석된다.
- 다음 연결: runtime result bundle이 같은 계약을 meta로 보존한다.

### 5A-3 Runtime / result bundle metadata

- 목적: cash proxy, 제외 ticker, stale price, top-N concentration, benchmark contract를 결과 해석에 남긴다.
- 범위: `app/runtime/backtest.py`, `app/runtime/backtest_result_bundle.py` 필요 시 read model.
- 완료 조건: GRS bundle meta에 cash / concentration / benchmark / freshness / exclusion contract가 유지된다.
- 다음 연결: 기존 Backtest Analysis 표시와 history / replay가 같은 meta를 읽는다.

### 5A-4 Minimal UI connection

- 목적: 새 패널 없이 기존 결과 화면에서 GRS 설명과 계약값을 읽게 한다.
- 범위: `app/web/backtest_single_forms.py`, `app/web/backtest_result_display.py`, 필요 시 history helper.
- 완료 조건: 사용자-facing 문구가 한국어 중심이고 새 evidence/log/workbench 패널이 추가되지 않는다.
- 다음 연결: Browser QA는 레이아웃 변경 리스크가 있을 때만 수행한다.

### 5A-5 Verification and doc sync

- 목적: 구현 결과를 focused tests, compile/check, task docs, durable docs 기준으로 닫는다.
- 범위: tests, task `STATUS/RUNS/RISKS`, 필요한 durable docs.
- 완료 조건: 관련 검증 결과가 기록되고 registry / saved / run history / generated artifact가 stage되지 않는다.

## Out Of Scope

- Practical Validation / Final Review / Portfolio Monitoring 동작 변경
- registry / saved JSONL / run_history 재작성
- provider / FRED direct fetch
- 새 evidence / log / workbench 패널
- GRS 성과를 live approval 또는 broker order로 해석하는 변경
