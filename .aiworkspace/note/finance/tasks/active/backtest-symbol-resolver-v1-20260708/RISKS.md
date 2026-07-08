# Backtest Symbol Resolver V1 Risks

- 1차는 current 기준 repair만 다룬다. PIT backtest의 old/new ticker split은 official effective_date가 확실한 후속 차수에서 다뤄야 한다.
- `nyse_symbol_lifecycle`의 existing current snapshot row만으로 ticker change official proof를 보장하지 않는다.
- UI에서 candidate를 자동 적용하지 않고 사용자의 버튼 action을 요구해야 한다.
- existing DB가 아직 `resolution_status` / `confidence` column을 갖지 않아도 loader는 candidate fallback query를 사용하지만, active repair 저장 path는 schema sync가 성공해야 한다.
- 3차 split contract는 metadata only다. `split_status=ready`가 실제 price series stitching 완료를 뜻하지 않도록 UI/docs에서 계속 구분해야 한다.
