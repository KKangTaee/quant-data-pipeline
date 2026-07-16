# Economic Cycle Provisional Hybrid V2 Status

Status: Complete — 1차~5차
Last Updated: 2026-07-16

| Stage | State |
|---|---|
| 1차 context/contract | Complete |
| 2차 state/TDD | Complete |
| 3차 hybrid UI | Complete |
| 4차 actual/Browser QA | Complete |
| 5차 docs/verification | Complete |

## Final Handoff

- Pipeline은 완전한 LIMITED artifact를 explicit provisional scoring으로 계산하지만 artifact publication status를 변경하지 않는다.
- Service는 `VERIFIED / PROVISIONAL / UNAVAILABLE`를 안정적으로 제공하고 legacy partial payload도 React가 안전하게 해석한다.
- Actual 122 snapshot을 origin-specific artifact로 다시 materialize했다. 336/366 horizon은 계산 가능했고 early missing-phase artifact 30 horizon은 판단 불가로 유지했다.
- Current 2026-06-30은 현재 회복 `46.7%`, +1M 회복 `40.5%`, +2M 회복 `47.4%`의 잠정 추정이다.
- 후속 UX 조정으로 2×2 path는 최근 12개월, ribbon은 최근 60개월+2개월 전망만 표시한다. DB의 121개월 replay는 유지한다.
- Ribbon은 실제 history 개수 기반 grid로 전체 너비를 채우며, 2×2 path의 과거·현재·+1M·+2M 확률점은 hover/focus 때만 날짜·국면·확률·추정 상태를 표시한다.
- Desktop/420px에서 2×2 tooltip, 62 ribbon cells/right-edge 정렬, console/page error 0, horizontal overflow 0을 확인했다.
- QA screenshot: `/Users/taeho/.codex/qa/economic-cycle-v2/overview-economic-cycle-ribbon-hover-desktop-20260716.png`.
