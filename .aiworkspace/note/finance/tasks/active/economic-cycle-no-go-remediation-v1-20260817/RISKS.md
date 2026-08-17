# Risks

- RUC bounded lag tolerance가 과거 episode distribution과 revision/NBER semantic gate를
  바꿀 수 있으므로 전체 historical audit를 다시 실행해야 한다.
- BAA10Y는 high-yield OAS가 아니라 Baa-Treasury spread proxy다. UI에서는 두 지표를
  같은 이름으로 표현하면 안 된다.
- pressure model의 마지막 25% 별도 shadow 구간은 duration baseline 대비 약 -0.7%였고
  calibration은 개선됐다. locked full OOS gate 결과와 함께 이 한계를 기록한다.
- GO 이전 persistence/service/UI 연결은 금지한다.
