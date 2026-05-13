# NOTES - Product Research Skill Stage 3

## Stage 2 Retrospective

실제 운영한 research bundle:

- `.aiworkspace/note/finance/researches/active/2026-05-ui-platform-research/`

잘 된 점:

- `researches/active/<research-id>/` 구조가 실제 product direction research 본문을 담기에 적합했다.
- `CURRENT_PROJECT_AUDIT.md -> BENCHMARKS.md / UI_PATTERNS.md -> FEATURE_CANDIDATES.md -> RECOMMENDATION.md` 흐름이 자연스럽게 이어졌다.
- root handoff log에는 상세 분석 대신 research bundle pointer만 남기는 방식이 작동했다.
- official source 중심 benchmark와 local audit 근거를 한 research bundle 안에서 묶을 수 있었다.

드러난 혼동:

- 사용자는 `RECOMMENDATION.md`가 1차 실행안인지, 최종 전체 migration plan인지 다시 확인해야 했다.
- "Streamlit internal console"이 현재 앱에 이미 분리되어 있다는 뜻인지, 앞으로 나눌 역할인지 설명이 더 필요했다.
- `research worktree에서 실제 운영`이라는 표현이 있었지만, 현재 research worktree는 오래된 `.note` 구조라 main-dev의 canonical `.aiworkspace` 구조에서 실행하는 것이 안전했다.
- Stage 3는 실제 product research가 아니라 skill / workflow hardening task이므로 `researches/active`가 아니라 `tasks/active`에 기록해야 한다.

보강 방향:

- recommendation template은 `Immediate next build`, `Decision checkpoint`, `Longer roadmap`, `Not approved yet`를 분리해야 한다.
- product audit은 화면을 `user-facing product surface`, `internal/ops console`, `mixed/transitional`로 분류하도록 해야 한다.
- benchmark skill은 제품뿐 아니라 framework/API/frontend architecture도 benchmark 대상이 될 수 있음을 명시해야 한다.
- feature opportunity skill은 research 결과가 곧 ROADMAP 변경 승인이나 full rewrite 승인이 아님을 더 선명하게 써야 한다.
- task intake는 research worktree가 canonical 구조와 다를 경우 현재 canonical worktree에서 research bundle을 만들고 이유를 남기도록 안내해야 한다.
