# Economic Cycle Gold / Dollar Price Confirmation V1 Design

- Canonical spec: `docs/superpowers/specs/2026-07-16-economic-cycle-gold-dollar-price-confirmation-design.md`
- Execution plan: `docs/superpowers/plans/2026-07-17-economic-cycle-gold-dollar-price-confirmation.md`
- 금은 `GC=F`, 달러는 `DX-Y.NYB` stored daily futures를 사용한다.
- 거시 배경과 가격 확인을 독립 계산하고 같은 방향인지 별도 종합한다.
- UI/provider 직접 호출과 경제사이클 모델 gate 변경은 금지한다.
