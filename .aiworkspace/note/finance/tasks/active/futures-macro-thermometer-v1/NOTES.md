# Futures Macro Thermometer V1 Notes

## Design Notes

- The macro thermometer uses daily candles (`interval_code = '1d'`) rather than current 1m monitor rows.
- Score direction follows economic interpretation, not raw contract price direction:
  - Treasury futures down means rate pressure up.
  - Major FX futures down means dollar pressure up.
  - Natural gas has lower inflation score weight because weather / inventory effects dominate.
- The UI must show this as interpretation support, not a predictive trading signal.

## Score Components

- Risk-On Score: `ES=F`, `NQ=F`, `YM=F`, `RTY=F`.
- Growth Score: `RTY=F`, `HG=F`, `CL=F`, `6A=F`.
- Rate Pressure Score: inverted `ZN=F`, `ZB=F`.
- Dollar Pressure Score: inverted `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F`.
- Safe Haven Score: `GC=F`, `ZN=F`, `ZB=F`, `6J=F`.
- Inflation Pressure Score: `CL=F`, `HG=F`, lower-weight `NG=F`.
