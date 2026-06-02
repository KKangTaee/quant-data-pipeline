# Futures Macro Thermometer Validation V1 Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Stored daily futures history is shorter than 3 years | validation sample can be too small | Return `Not Enough History` / low confidence and show sample counts |
| ETF proxy data is present but futures target is missing | user may mistake proxy validation for futures validation | Label target source as `futures` or `ETF proxy` in summary |
| Scenario hit definition can be oversimplified | hit rate may overstate efficacy | Keep hit definition transparent and include average / median forward returns |
| Continuous futures roll differences | provider history may diverge from tradable contract returns | Show yfinance continuous futures caveat in UI and docs |
| Mixed scenario forced into risk-on/off | misleading interpretation | Keep `혼재된 매크로 흐름` as a valid scenario and do not force direction |
