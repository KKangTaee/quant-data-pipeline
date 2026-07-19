# Portfolio Monitoring React Command Center V1 Notes

## Durable Decisions

- `Streamlit 제거`는 app/navigation 제거가 아니라 Portfolio Monitoring visible product UI를
  React one-shell로 교체하는 의미다.
- direct security data가 DB에 없으면 UI/provider fetch나 부분 등록을 하지 않는다.
- dollar mode는 fractional virtual units, share mode는 integer shares only다.
- tracking end는 history deletion이 아니라 exit value to cash다.
- dividends are cash, not automatically reinvested.
- group KPI uses a common basis date across active items.
- macro signal begins as observation state with confidence/coverage, not loss probability.

## Visual Decisions

- page layout: `Portfolio-first Command Center` A안
- item add interaction: `Context Drawer` A안
- reference language: Overview economic cycle/Market Context/Futures Macro
- first-read: KPI -> group chart -> changes -> strength/weakness -> items/detail

## Existing Reuse Boundary

- Final Review monitoring candidate filter and selected strategy replay are reusable.
- existing user monitoring portfolio JSONL is preserved and imported non-destructively.
- current monolithic read model remains compatibility source only; it is not the new product owner.
