# Notes

## 2026-08-17 Root Causes

- RTDSM DB는 IPT/H/EMPLOY 2026-07, RUC 2026-05 빈티지까지 정상 저장돼 있었다.
- RUC 2026-02 빈티지에 2025-10 관측이 없어 exact 3M transform만 실패했다.
- exact-lag 실패가 rolling level/momentum을 통해 current state 전체를 끊었다.
- BAML 공개 이력 제한과 ANFCI realtime start 때문에 all-feature intersection은
  27 origins / 5 transitions로 축소됐다.
- BAA10Y required substitute shadow audit은 274 origins / 52 transitions와 모든
  destination/holdout support를 충족했다.
- 하나의 38-feature 모델은 두 과제 모두 baseline보다 나빴다. compact core destination은
  READY, compact core + directional driver pressure는 READY였으므로 task별 계약을 분리한다.
