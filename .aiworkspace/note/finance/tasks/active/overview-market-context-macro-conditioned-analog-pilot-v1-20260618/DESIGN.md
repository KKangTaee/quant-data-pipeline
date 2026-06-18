# Design

Status: Complete
Last Updated: 2026-06-18

## Service Model

`build_historical_analog_snapshot()` remains the broad analog owner.
It still resolves current leadership sector to sector ETF proxy, compares the proxy ETF to SPY, builds anchor dates, and produces the existing rows with median / positive rate / best / worst / sample fields.

3차-A adds an additive nested payload:

```text
historical_analog["macro_conditioned_analog"]
```

This payload has its own schema version, status, headline, sample counts, sample quality, used conditions, insufficient conditions, excluded conditions, rows, and anchor dates.
The parent broad fields are not replaced.

## Conditions

Used in 3차-A:

- Required: sector ETF vs SPY relative strength, inherited from the broad analog anchor set.
- Additional: GLD price proxy safe-haven / gold context. Current GLD pattern-window return is bucketed into rising, falling, or neutral context; only broad anchors with the same GLD bucket remain in the pilot sample.

Not used in 3차-A:

- Stored futures daily OHLCV rate / safe-haven context: deferred to 3차-B candidate.
- 2Y / 10Y FRED rates: disabled because no new FRED collection or UI fetch is approved.
- Events / sentiment historical conditioning: disabled because this pilot only proves the framework.

## UI

`app/web/overview_ui_components.py` renders the pilot as a separate block titled `Macro 조건 포함 pilot` beneath the broad historical analog explanation and table.
The block shows broad sample count, macro-conditioned sample count, additional condition count, sample quality, sample reduction reason, used conditions, insufficient conditions, excluded conditions, and the same table shape when rows exist.

## Boundaries

The pilot is context-only historical distribution display.
It does not create a forecast, recommendation, buy/sell instruction, validation gate, monitoring signal, registry write, saved setup write, provider fetch, loader change, or schema change.
