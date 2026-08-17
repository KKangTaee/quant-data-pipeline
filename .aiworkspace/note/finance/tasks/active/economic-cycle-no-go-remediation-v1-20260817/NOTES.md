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

## 2026-08-17 Implemented Contract

- exact lag가 없을 때 과거 방향 한 달 이내 실제 관측만 사용하고 actual elapsed month로
  정규화한다. 해당 origin은 `LIMITED`이며 값 보간이나 미래 관측은 없다.
- required pressure driver는 FEDFUNDS 3M 변화, Core PCE 2% gap, 10Y-2Y curve 3M 변화,
  BAA10Y 3M 변화, PERMIT 6M 변화다.
- destination은 compact core, pressure는 compact core + directional driver가 소유한다.
- final outcome은 extended pressure READY + positive common-origin skill과 compact-core
  destination READY를 각각 요구한다.

## Actual GO Interpretation

- confirmed current phase는 2026-07 `recovery`, candidate 없음, duration 7 releases다.
- 2026-05 raw contraction은 1회 후보에 그쳐 공식 전환되지 않았고 2026-06 recovery로
  해소됐다.
- state 593 usable origins / 116 transitions, driver 312 origins / 55 transitions다.
- pressure OOS 53 events, ECE 0.0856, common-origin compact-core 대비 mean skill
  +2.175%다.
- destination OOS 76 events, 14/23/14/25 four-phase support와 final 25%
  4/5/4/6 support를 확보했다.
