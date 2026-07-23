# Market Research S&P 500 Manual Price Refresh V1 Notes

Status: Completed
Last Updated: 2026-07-24

## Confirmed Evidence

- 2026-07-24 KST 기준 최신 완료 NYSE session은 `2026-07-23`이다.
- DB `^GSPC` latest daily row는 `2026-07-16`, `SPY`는 `2026-07-22`였다.
- read-only provider probe는 두 symbol 모두 `2026-07-23` data를 반환했다.
- S&P valuation automation spec은 24시간 cadence로 존재하지만 해당 job run history는 0건이었다.
- 현재 시스템에는 이 프로젝트용 launchd/cron 등록이 없다.
- 현재 React freshness action은 미국 개별주식에만 표시된다.

## Confirmed Decisions

- 백그라운드 자동 실행은 현재 범위에서 제외한다.
- 화면 진입은 DB read-only를 유지한다.
- SPX price freshness가 stale/missing/error일 때만 action을 표시한다.
- action은 `^GSPC` / `SPY` EOD만 수집한다.
- Shiller, SEP, official EPS는 이 action의 수집 대상이 아니다.
- collector 반환 상태가 아니라 수집 후 DB 최신성으로 성공을 판정한다.
- raw run/status/row diagnostics panel은 만들지 않는다.

## Expected Value Change

2026-07-23 provider EOD를 DB write 없이 read model에 주입한 계산에서는:

- current provisional PER: `28.79x -> 28.31x`
- current Z: `1.30 -> 1.14`
- current vs baseline gap: `+8.3% -> +6.47%`
- bucket은 이번 표본에서 `HIGH`로 유지됐다.

가격 최신화는 분포·SEP·EPS 자체를 바꾸지는 않지만 현재 위치와 시나리오 괴리를 실질적으로 바꾼다.

## Implemented Contract

- `sp500_valuation_freshness.py`가 DB-only SPX latest price와 최신 완료 NYSE session을 비교한다.
- S&P read model은 freshness를 포함하고, Streamlit helper는 stale/missing action event를 nonce로 한 번만 소비한다.
- 수동 action은 canonical `run_collect_ohlcv`를 `^GSPC`, `SPY`, `1mo`, `1d`, `managed_safe`로 호출한다.
- 성공 판정은 collector 반환 문구가 아니라 수집 후 DB의 `^GSPC` 날짜 postcondition이다.
- 성공 시 S&P 단독/통합 valuation cache를 함께 비우고 rerun한다. 실패 시 기존 latest-good 값을 유지한다.
- React는 raw job/row/provider 세부값 대신 다음 행동, 실행 중 상태, 한 번의 compact 완료 안내만 표시한다.

## Actual Verification

- 수동 action 1회가 `overview_sp500_price_refresh`로 기록됐고 `success`, 저장 42행, 실패 0건, 2.971초였다.
- DB `^GSPC`와 `SPY`가 모두 `2026-07-23`까지 갱신됐다.
- 재계산 값은 `current_pe=28.3058798985`, `current_z=1.13710694`, `gap=6.468090506%`였다.
- reload 뒤 current 상태에서는 action과 완료 bar가 다시 나타나지 않았다.
