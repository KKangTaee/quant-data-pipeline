# Web Backtest UI Flow

## 목적

이 문서는 Streamlit Backtest 화면의 single strategy, compare, history, saved portfolio 흐름을 설명한다.
UI form, payload 복원, history replay, saved portfolio replay를 수정할 때 먼저 확인한다.

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | top navigation과 page entry |
| `app/web/pages/backtest.py` | Backtest page 대부분의 UI / state / render logic |
| `app/web/runtime/backtest.py` | UI payload를 실행 가능한 runtime call로 변환 |
| `.note/finance/BACKTEST_RUN_HISTORY.jsonl` | local run history. 보통 commit하지 않음 |
| `.note/finance/SAVED_PORTFOLIOS.jsonl` | saved portfolio persistence |

## 화면 흐름

Backtest page는 현재 네 panel 중심으로 본다.

- `Single Strategy`: 하나의 전략을 실행하고 latest result를 확인한다.
- `Compare & Portfolio Builder`: 여러 전략을 같은 기간으로 비교하고 weighted portfolio를 만든다.
- `History`: 저장된 실행 기록을 inspect하고, 가능한 경우 run again 또는 load into form을 수행한다.
- `Pre-Live Review`: current candidate를 실전 전 운영 상태로 기록하고 저장된 Pre-Live record를 확인한다.

## Single Strategy 흐름

```text
strategy 선택
  -> strategy-specific form 입력
  -> _handle_backtest_run(...)
  -> app/web/runtime/backtest.py run_*_backtest_from_db(...)
  -> latest result bundle 저장
  -> result table / summary / selection history / real-money surface 표시
  -> history record 저장
```

주의:

- `Load Into Form`은 입력값만 복원한다.
- 복원 후 결과를 갱신하려면 사용자가 다시 실행해야 한다.
- selection history가 있는 전략은 latest result의 `Selection History Table` / `Interpretation Summary`에서 상세를 본다.

## Compare 흐름

```text
strategy multi-select
  -> Compare Period & Shared Inputs
  -> strategy별 box에서 variant / advanced inputs 설정
  -> Run Strategy Comparison
  -> strategy별 result bundle 실행
  -> comparison table / overlay / focused strategy 표시
  -> Weighted Portfolio Builder로 전달
```

현재 UX 기준:

- common date / timeframe / option은 공유 입력으로 둔다.
- strategy-specific advanced inputs는 strategy별 box 안에서 보이게 한다.
- variant 변경은 버튼 없이 즉시 아래 옵션이 바뀌는 방향이 선호된다.
- 최대 compare 전략 수는 operator가 읽을 수 있는 범위로 유지한다.

## Strategy Capability Snapshot 흐름

Phase 28 이후 `Single Strategy`와 `Compare & Portfolio Builder`의 strategy box에는
`Strategy Capability Snapshot` 접힘 영역을 둔다.

목적:

- annual strict, quarterly strict, price-only ETF 전략이 서로 다른 이유를 UI에서 먼저 설명한다.
- cadence, data trust, selection history, Real-Money/Guardrail, history/replay 지원 범위를 표로 보여준다.
- 기능이 없는 것처럼 보이는 부분이 버그인지, 아직 annual 중심으로 남긴 의도적 차이인지 구분하게 한다.

현재 기준:

- strict annual은 가장 성숙한 Real-Money / Guardrail surface로 설명한다.
- strict quarterly prototype은 Data Trust와 Portfolio Handling은 지원하지만, Real-Money promotion / Guardrail 판단은 아직 annual strict 중심으로 설명한다.
- Global Relative Strength는 재무제표 selection history 대상이 아니라 price-only ETF relative strength strategy로 설명한다.

## Data Trust Summary 흐름

Phase 27 이후 `Latest Backtest Run` 상단에는 `Data Trust Summary`를 둔다.

목적:

- 요청 종료일과 실제 결과 종료일을 먼저 비교한다.
- price freshness, common latest price, latest-date spread를 결과 해석 전에 보여준다.
- excluded ticker와 malformed price row가 있으면 `Data Quality Details`에서 확인하게 한다.

첫 적용 대상:

- `Global Relative Strength` single strategy 실행 전 `Price Freshness Preflight`
- `Latest Backtest Run`의 공통 `Data Trust Summary`

## Weighted Portfolio / Saved Portfolio 흐름

```text
compare result bundles
  -> weight 입력
  -> make_monthly_weighted_portfolio(...)
  -> weighted result
  -> optional save
  -> Load Saved Setup Into Compare or Replay Saved Portfolio
```

구분:

- `Load Saved Setup Into Compare`: 저장된 compare 구성과 weight를 form에 다시 채운다.
- `Replay Saved Portfolio`: 저장 당시 context로 compare와 weighted portfolio를 다시 실행한다.

저장된 portfolio는 live trading 승인 기록이 아니다.
후보 조합을 다시 재현하고 검증하기 위한 operator workflow artifact다.

Phase 28 이후 Saved Portfolio 영역에는
`Saved Portfolio Replay / Load Parity Snapshot`을 둔다.
이 표는 저장 포트폴리오를 다시 열거나 재실행하기 전에 아래 값이 남아 있는지 보여준다.

- compare 공용 입력: start / end / timeframe / option
- selected strategy list
- weights percent / date alignment
- strategy override map
- strategy별 핵심 override: cadence, universe, factor, overlay, handling, benchmark, guardrail, score 설정

## History 흐름

History는 compact summary 중심이다.
모든 selection history row를 그대로 저장하지 않는다.

대표 action:

- `Inspect`: 저장된 record를 읽는다.
- `Run Again`: 저장된 payload로 다시 실행한다.
- `Load Into Form`: 저장된 입력값을 single strategy form에 복원한다.

Phase 28 이후 History의 selected record 영역에는
`History Replay / Load Parity Snapshot`을 둔다.
이 표는 선택한 record에 재실행 / form 복원에 필요한 핵심 값이 남아 있는지 보여준다.

주요 확인 항목:

- strategy key, 입력 기간, timeframe, option
- universe / ticker / preset
- actual result start / end, result row count
- price freshness, excluded ticker, malformed price row
- strict family factor cadence, universe contract, overlay, portfolio handling
- annual strict real-money / guardrail / promotion settings
- GRS score, cash ticker, trend window, ETF operability inputs

## Pre-Live Review 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Pre-Live Review
  -> current candidate 선택
  -> Real-Money 신호와 기본 Pre-Live 상태 확인
  -> operator reason / next action / review date 수정
  -> 저장 전 JSON draft 확인
  -> Save Pre-Live Record
  -> PRE_LIVE_CANDIDATE_REGISTRY.jsonl append
  -> Pre-Live Registry tab에서 active record 확인
```

구분:

- current candidate registry는 후보 자체를 정의한다.
- pre-live registry는 그 후보를 실전 전 어떻게 관찰하거나 보류할지 기록한다.
- `Save Pre-Live Record`는 live trading 승인 버튼이 아니다.
- `paper_tracking`도 실제 돈을 넣는다는 뜻이 아니라 paper 관찰 상태다.

## Streamlit form 주의

Streamlit `st.form()` 내부 widget은 submit 전까지 app state가 즉시 rerun되지 않는다.
따라서 variant 선택처럼 아래 UI를 즉시 바꿔야 하는 값은 form 밖에 두는 것이 낫다.
반대로 한 번에 제출되어야 하는 detailed contract 입력은 form 내부에 유지할 수 있다.

## 갱신해야 하는 경우

- Backtest panel 구조가 바뀔 때
- strategy-specific form 위치나 payload key가 바뀔 때
- compare / weighted / saved portfolio 계약이 바뀔 때
- history record schema나 replay 가능 범위가 바뀔 때
- `Load Into Form`, `Run Again`, `Replay Saved Portfolio` semantics가 바뀔 때
