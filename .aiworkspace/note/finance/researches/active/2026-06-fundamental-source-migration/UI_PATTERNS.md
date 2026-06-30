# UI / Workflow Patterns

## Goal

재무제표 source 전환 후 UI는 더 많은 진단값을 보여주는 것이 아니라, 사용자가 "이 숫자가 어디서 왔고 얼마나 최신인가"를 짧게 이해하게 해야 한다.

## Compact source display contract

Financial metric cards or rows should use this minimum evidence set:

- Source: `SEC EDGAR`, `EDGAR shadow`, `yfinance legacy`, `provider fallback`
- Period end: fiscal period end date
- Available at: filing accepted timestamp or conservative filing-date fallback
- Form: `10-K`, `10-Q`, amendment if applicable
- Scope: annual, quarterly, TTM, synthetic Q4, provider-normalized

## Recommended labels

| Data situation | Label |
| --- | --- |
| Annual statement shadow from 10-K | `SEC 10-K 기준` |
| Quarterly statement from 10-Q | `SEC 10-Q 기준` |
| Q4 synthetic from FY minus Q1-Q3 | `계산 Q4` |
| Broad yfinance fallback | `legacy yfinance fallback` |
| Missing source | `수집 필요` |
| Stale source | `갱신 필요` |

## Market Movers detail pattern

Recommended compact layout:

```text
재무 요약
  시총 / YTD / PER / EPS / 순이익
  source strip: SEC 10-K 2025-03-31 · accepted 2025-05-XX · price as of selected mover date
  fallback strip only when source is not EDGAR
```

Avoid:

- raw statement rows as default main UI
- multiple repeated source cards
- run/job/status rows in the financial research panel
- presenting EDGAR quarterly values without form/source context

## Backtest UI pattern

Strategy forms should distinguish:

- `Strict Annual`: production candidate, EDGAR statement shadow
- `Quarterly Prototype`: blocked or clearly experimental until Q4/FY policy is fixed
- `Legacy Broad Quality`: deprecated compatibility path, yfinance broad factors

This should be a small source badge / warning, not a large diagnostic panel.
