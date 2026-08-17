# Main-dev Master Merge Resolution Notes

State: complete
Last Updated: 2026-08-17

## Integration Decisions

- merge direction은 `codex/main-dev` ← `origin/master`다.
- conflict는 모두 finance Markdown 5개이며 code conflict는 없다.
- `ROADMAP.md`의 current economic-cycle contract는 current branch가 더 최신이다.
- master의 Futures Macro 장중 관측·재가격화와 Sentiment `3/4차 paused`는 distinct
  behavior이므로 함께 보존한다.
- normalized task status상 active product task와 active phase는 없다.
- incoming shared Market Research header CSS는 Sentiment뿐 아니라 Economic Cycle과 Events
  source에도 포함되므로 세 component static bundle을 integrated source에서 다시 생성했다.
- broad service-contract의 병합 전 baseline은 18 failures였다. 병합 직후 19 failures 중
  신규 1건은 primary UI에서 제거된 Pattern Map을 계속 렌더링한다고 가정한 stale assertion이었다.
  compatibility/shadow evidence는 보존하고 primary root가 Market Repricing을 렌더하는 계약으로
  단일 assertion을 RED→GREEN 정렬해 baseline 18 failures로 복구했다.
- 독립 리뷰에서 manifest의 `active product task: none`과 네 task의 stale `State: active`가
  source-of-truth 우선순위상 충돌함을 발견했다. Inflation Policy 세 task는 완료 phase와
  functional recovery를, Economic Cycle 설계 task는 후속 feasibility·interpretability
  task를 근거로 `complete`와 handoff pointer로 정렬했다.
