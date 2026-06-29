# Notes

Status: Active
Last Updated: 2026-06-18

## Decisions

- This is an implementation task, not a new product-direction research bundle.
- `finance-product-audit` and `finance-feature-opportunity` are used as product judgment lenses only; follow-up 2차/3차 material stays in this task as design/risk notes unless a later product research bundle is explicitly opened.
- `interpretation_cues` remains for backward-compatible service payloads, but the user-facing `다음 맥락 체크` must render `next_checks`.

## Product Friction

- `일부 자료 확인 필요` needs to expose source, owning tab, reason, and action before the user considers a refresh button.
- Market Context should remain context-only; no validation, monitoring, trading, or recommendation semantics are introduced.

## Closeout Notes

- `interpretation_cues` still exists for compatibility, but the visual `다음 맥락 체크` reads `next_checks`.
- Source Confidence footer now surfaces action hints while keeping full evidence details collapsed.
- Historical analog display now makes the current calculation basis explicit: current as-of, data window, and sector ETF vs SPY 5D relative strength.
