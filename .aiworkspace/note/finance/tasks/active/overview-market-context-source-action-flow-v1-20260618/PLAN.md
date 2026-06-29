# Overview Market Context Source Action Flow V1

Status: Active
Date: 2026-06-18
Worktree: `sub-dev`

## 이걸 하는 이유?

`Workspace > Overview > Market Context`는 현재 시장 배경을 빠르게 읽는 화면이지만, `일부 자료 확인 필요`가 어떤 자료인지 바로 연결되지 않고 `시장 브리프`와 `다음 맥락 체크`가 비슷한 값을 반복해 보이는 문제가 남아 있다.

이번 작업은 자료 진단 패널을 전면화하지 않고, 사용자가 오늘의 시장 맥락을 읽은 뒤 어떤 source / tab / action을 확인해야 하는지 바로 알 수 있게 만드는 1차 개선이다.

## 전체 Roadmap

1차: Market Context 읽기 흐름 / 자료상태 명확화
- `오늘의 시장 맥락`, `시장 브리프`, `다음 맥락 체크`, `근거: 자료 기준 / 출처 상태`, `참고: 과거 유사 맥락`의 역할을 분리한다.
- 완료 조건: `next_checks`가 실제 UI checklist가 되고, source/action/freshness가 보이며, raw job result는 접힌 보조 정보로 남는다.

2차: Historical Analog 기준 시점 / 기간 확장 설계
- 5D/20D/monthly current pattern window, as-of replay 가능성, 필요한 schema/저장소 승인점을 조사한다.
- 이번 차수에서는 구현하지 않고 후속 설계 메모로만 남긴다.

3차: Macro-conditioned Historical Analog Pilot 설계
- sector ETF relative strength, yield curve/rates, gold, futures macro thermometer, events/sentiment context 결합 가능성을 조사한다.
- 이번 차수에서는 구현하지 않고 후속 설계 메모로만 남긴다.

## Scope

- `app/services/overview_market_intelligence.py`
  - `next_checks`를 Data Health handoff / Events source review / Futures / Market Movers 중심의 UI checklist read model로 강화한다.
  - summary copy가 시장 값 반복보다 읽는 방법을 먼저 말하게 조정한다.
  - Source Confidence footer가 review source와 action hint를 접힌 상태에서도 보여준다.
- `app/web/overview_ui_components.py`
  - `다음 맥락 체크` 렌더링을 `interpretation_cues`가 아니라 `next_checks` 중심으로 바꾼다.
  - historical analog 기준 시점 / data window / 계산식 설명을 더 명확히 표시한다.
- `app/web/overview_dashboard.py`
  - 보조 갱신 expander에서 source/action 이유가 먼저 보이고 job table은 접힌 보조 정보로 유지한다.
- `tests/test_service_contracts.py`
  - read model, render ordering, source/action footer, historical analog context-only metadata, refresh 보조영역 계약을 검증한다.

## Out Of Scope

- 새 provider, 새 DB schema, 새 loader 추가.
- UI render 중 provider / FRED / yfinance 직접 fetch.
- macro-conditioned analog 계산 구현.
- historical analog anchor replay 저장소 구현.
- 예측, 추천, 매수/매도, trade signal, Practical Validation PASS/BLOCKER, Final Review decision, Operations monitoring signal.
- Backtest Analysis, Practical Validation, Final Review, Operations core logic.
- registry/saved JSONL, run_history, generated screenshot/artifact stage.

## Completion Criteria

- `다음 맥락 체크`가 `model["next_checks"]`를 렌더링한다.
- Market Brief와 Next Check가 같은 value/detail을 반복하지 않는다.
- Data Health REVIEW 시 어떤 source / tab / action을 확인할지 보인다.
- Event review는 추정 일정, 공식 macro/source freshness, earnings estimate 확인을 뭉뚱그리지 않는다.
- Historical analog는 current as-of, data window, 현재 계산식을 context-only 문구와 함께 보여준다.
- focused tests, py_compile, diff check, Browser QA가 완료된다.
