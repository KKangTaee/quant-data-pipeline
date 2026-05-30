# Notes

- yfinance remains the primary bounded symbol calendar source.
- Nasdaq is used as alternate free provider cross-check by event date, not as an official company source.
- Generic company IR parsing is intentionally not implemented in this task because IR calendar markup differs heavily by company. The fallback order records `company_ir_calendar` as the future official source candidate.
- Confidence defaults: yfinance estimate `0.65`, Nasdaq cross-checked provider estimate `0.75`, Nasdaq checked but not confirmed `0.60`.
