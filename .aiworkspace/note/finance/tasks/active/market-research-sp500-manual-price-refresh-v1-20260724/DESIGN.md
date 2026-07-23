# Market Research S&P 500 Manual Price Refresh V1 Design

Status: Approved
Last Updated: 2026-07-24

## Problem

현재 S&P 500 valuation read model은 DB의 최신 `^GSPC` / `SPY` 가격을 읽지만 `^GSPC` 가격일이 최신 완료 NYSE 거래일보다 오래됐는지 판정하지 않는다.

React header의 `기준일`은 `payload.basis.spx.date`를 그대로 표시하고, freshness action은 미국 개별주식에만 연결되어 있다. 백엔드에는 전체 S&P valuation context collector와 일일 automation spec이 있지만 실제 OS scheduler가 없고 현재 화면에도 S&P 전용 수동 action이 없다.

2026-07-24 진단 기준:

- latest completed NYSE session: `2026-07-23`
- DB `^GSPC`: `2026-07-16`
- DB `SPY`: `2026-07-22`
- provider probe `^GSPC` / `SPY`: `2026-07-23`
- `collect_sp500_valuation_context` run history: 0

## Product Decision

백그라운드 자동화는 만들지 않는다.

화면 진입은 DB read-only로 유지하고, 최신 완료 장과 저장된 SPX 가격을 비교한다. 최신이면 action을 숨기고, stale 또는 missing이면 사용자 질문과 다음 행동을 함께 보여준다.

이번 action은 가격 freshness 문제만 해결한다. Shiller, SEP, 공식 S&P EPS는 서로 다른 cadence와 source boundary를 가지므로 버튼 클릭마다 함께 수집하지 않는다.

## User Flow

### Current

```text
S&P 500 진입
-> 저장된 SPX 기준일 표시
-> READY valuation 표시
-> 기준일이 오래되어도 복구 action 없음
```

### Target

```text
S&P 500 진입
-> 최신 완료 NYSE 거래일 계산
-> DB 최신 ^GSPC 가격일 비교
   -> 같음: valuation 표시, refresh action 없음
   -> 오래됨/없음: compact freshness action 표시
      -> 사용자가 "최신 데이터로 다시 계산" 클릭
      -> ^GSPC / SPY EOD 수집
      -> DB 최신성 재검증
         -> 최신: cache clear -> rerun -> 새 valuation 표시
         -> 여전히 stale/실패: 기존 결과 유지 -> 이유와 retry action 표시
```

## Freshness Contract

### Inputs

- `expected_price_date`: `app.services.nyse_calendar.latest_completed_nyse_session()`
- `price_basis_date`: DB `^GSPC` latest daily date
- `spy_price_basis_date`: DB `SPY` latest daily date

### Status

| Status | Condition | UI |
|---|---|---|
| `READY` | `price_basis_date >= expected_price_date` | action 숨김 |
| `REFRESH_AVAILABLE` | `price_basis_date < expected_price_date` | stale 안내 + action |
| `MISSING` | SPX latest row 없음 | missing 안내 + action |
| `ERROR` | freshness 계산 실패 | 기존 valuation 유지 + 재시도 가능한 안내 |

미래 날짜가 저장된 비정상 상태는 `READY`로 조용히 통과시키지 않고 warning evidence를 남기되, 이번 V1에서는 자동 삭제나 DB 수정은 하지 않는다.

### Read Model

S&P instrument payload에 아래 `data_freshness`를 추가한다.

```python
{
    "status": "READY | REFRESH_AVAILABLE | MISSING | ERROR",
    "expected_price_date": "YYYY-MM-DD",
    "price_basis_date": "YYYY-MM-DD | None",
    "spy_price_basis_date": "YYYY-MM-DD | None",
    "gap_sessions": 0,
    "message": "...",
    "warnings": [],
    "action": {
        "id": "refresh_sp500_price_data",
        "label": "최신 데이터로 다시 계산",
        "enabled": True,
    } | None,
}
```

`gap_sessions`는 달력 일수 차이가 아니라 `price_basis_date` 다음 날부터 `expected_price_date`까지의 NYSE 거래일 수다.
미래 날짜처럼 freshness 계산은 가능하지만 정상으로 간주할 수 없는 경우는 `warnings`에 이유를 넣는다.

## Manual Collection Boundary

### Action Facade

`app/jobs/overview_actions.py`가 UI-facing action을 소유한다.

새 action은 기존 `run_collect_ohlcv()`를 통해 다음만 요청한다.

```python
symbols=["^GSPC", "SPY"]
period="1mo"
interval="1d"
execution_profile="managed_safe"
```

UI는 provider를 직접 호출하지 않는다.

### Postcondition

collector의 `status=success`만으로 화면 최신화를 성공 처리하지 않는다.

수집 후 DB를 다시 읽어:

```text
latest ^GSPC date >= expected completed NYSE date
```

를 만족해야 action 결과를 `success`로 판정한다. 그렇지 않으면 기존 valuation을 유지하고 `incomplete` 또는 `failed` 결과를 반환한다.

명시적 사용자 action 결과는 shared web app run history에 기록하되, 화면에는 raw job detail을 표시하지 않는다.

Action result status는 다음으로 제한한다.

- `success`: SPX와 SPY가 모두 기대 기준일까지 갱신됨
- `partial_success`: SPX는 기대 기준일까지 갱신됐지만 SPY는 같은 기준일에 도달하지 못함
- `incomplete`: collector는 종료됐지만 SPX가 기대 기준일까지 도달하지 못함
- `failed`: collector 또는 DB postcondition 확인 중 예외 발생

## UI Design

### Header

- `기준일`을 `가격 기준일`로 변경한다.
- 값은 기존처럼 `basis.spx.date`를 표시한다.

### Freshness Action

S&P 500이고 status가 `REFRESH_AVAILABLE`, `MISSING`, `ERROR`일 때만 header와 그래프 사이에 표시한다.

예시:

```text
가격 자료 최신화 필요
가격 기준일 2026-07-16 · 최신 완료 장 2026-07-23
[최신 데이터로 다시 계산]
```

실행 중:

```text
최신 장 마감 데이터를 수집하는 중입니다.
[갱신 중]
```

실패:

```text
최신 완료 장까지 확인하지 못했습니다. 기존 2026-07-16 결과를 유지합니다.
[다시 시도]
```

최신 상태에서는 별도 success banner를 지속 노출하지 않는다. 갱신 직후 한 번의 compact confirmation만 허용하고, 이후 rerun에서는 action surface를 숨긴다.

## Event And Cache Flow

1. React emits `refresh_sp500_price_data`.
2. Streamlit validates the exact action id and current S&P context.
3. Python action facade runs bounded EOD collection.
4. Python reloads DB freshness.
5. On verified success:
   - clear `load_sp500_valuation_model`
   - clear `load_market_context_valuation_model`
   - store a compact collection reflection
   - `st.rerun()`
6. On incomplete/failure:
   - retain old cached valuation result
   - attach compact collection reflection
   - keep action enabled

Event nonce consumption must prevent the same component event from running twice across reruns.

## Error Handling

- Provider exception: old valuation remains visible; button remains.
- Empty provider result: incomplete, not success.
- `SPY` only succeeds: incomplete because SPX owns index valuation.
- SPX succeeds and SPY fails: SPX freshness succeeds; SPY same-date conversion remains unavailable and the compact result notes partial coverage.
- DB unavailable: show freshness/action error without blanking an already-built valuation payload when possible.
- Market open: expected date remains the last fully completed NYSE session.
- Weekend/holiday: expected date remains the nearest prior completed session.

## File Ownership

| File | Responsibility |
|---|---|
| `app/services/overview/sp500_valuation_freshness.py` | S&P price freshness contract |
| `app/services/overview/market_context_valuation.py` | attach freshness to S&P instrument payload |
| `app/jobs/overview_actions.py` | explicit manual SPX/SPY refresh facade and postcondition |
| `app/web/overview/market_context_helpers.py` | event consumption, action execution, cache clear, reflection |
| `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx` | S&P freshness action UI and event |
| `app/web/streamlit_components/market_context_valuation/src/style.css` | compact action styling |
| `tests/test_sp500_valuation.py` | freshness and price refresh behavior |
| `tests/test_service_contracts.py` | UI/action/cache boundary contracts |

No DB schema change is required.

## Testing

### Service

- same-day SPX -> `READY`, no action
- stale SPX -> `REFRESH_AVAILABLE`, action enabled
- missing SPX -> `MISSING`, action enabled
- market-open time -> previous completed session
- weekend/holiday -> previous completed session
- future-dated row -> warning evidence
- gap count uses NYSE sessions

### Action

- collector receives only `^GSPC`, `SPY`
- verified latest SPX -> success
- collector success but DB still stale -> incomplete
- SPY-only update -> incomplete
- SPX update with SPY failure -> price freshness success with partial coverage
- explicit action result is recorded once

### UI

- S&P stale payload renders action
- S&P ready payload hides action
- individual-stock freshness behavior remains unchanged
- action event id and nonce are consumed once
- verified success clears both valuation caches
- failed refresh retains old valuation and action

### Verification

- focused Python tests
- service contract tests
- Python compile
- TypeScript check
- React production build
- `git diff --check`
- actual DB refresh smoke
- desktop and 420px Browser QA
- QA screenshot kept as generated artifact

## Acceptance Criteria

1. S&P 500 진입 시 provider fetch 없이 freshness가 계산된다.
2. 최신 가격이면 refresh button이 없다.
3. 오래됐거나 없으면 기대 기준일과 실제 기준일이 함께 보인다.
4. 버튼은 `^GSPC` / `SPY` EOD만 기존 ingestion 경계로 수집한다.
5. DB postcondition을 만족한 경우에만 최신화 성공으로 처리한다.
6. 성공 후 새 가격 기준 PER, Z-score, scenario gap이 표시된다.
7. 실패 시 기존 평가를 유지하고 재시도할 수 있다.
8. 백그라운드 scheduler와 진단 패널은 추가하지 않는다.
