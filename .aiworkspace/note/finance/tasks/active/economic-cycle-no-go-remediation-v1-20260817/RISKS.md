# Risks

- RUC bounded lag tolerance는 전체 historical revision/NBER semantic gate를 다시
  통과했다. fallback origin은 계속 `LIMITED`로 표시해야 한다.
- BAA10Y는 high-yield OAS가 아니라 Baa-Treasury spread proxy다. UI에서는 두 지표를
  같은 이름으로 표현하면 안 된다.
- pressure model의 마지막 25% 별도 shadow 구간은 duration baseline 대비 약 -0.7%였고
  calibration은 개선됐다. locked full OOS gate 결과와 함께 이 한계를 기록한다.
- pressure model의 full OOS gate는 통과했지만 최근 25% 별도 shadow 비교는 duration
  baseline 대비 약 -0.7%였다. production UI는 확률을 확정 예언으로 표현하지 않고
  조건부 전환압력으로 설명해야 한다.
- 4·5차에서 BAML/ANFCI를 다시 required intersection에 넣거나 destination에 directional
  driver를 강제하면 검증 계약이 깨진다.
