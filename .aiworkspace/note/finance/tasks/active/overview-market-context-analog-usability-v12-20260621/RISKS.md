# Overview Market Context Analog Usability V12 Risks

## Residual Risks

- Local DB may still have stale daily price coverage after repair if upstream provider collection cannot fill the missing dates.
- Matrix UI must avoid implying forecast, recommendation, or trade signal language.
- The existing single large UI component file increases CSS / markup regression risk; service contract tests and Browser QA are required.

## Closed During Task

- The historical analog UI no longer leaves stale common price basis as a non-actionable mismatch; it exposes a bounded refresh action for limiting ETF symbols.
- The primary broad analog no longer opens with duplicate method grid / sample-count repetition before the result readout.
