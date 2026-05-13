# RISKS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## Risks

| Risk | Status | Mitigation |
|---|---|---|
| 이미 로드된 세션에는 삭제된 `finance-phase-management` metadata가 남을 수 있음 | accepted | 다음 세션부터 skill inventory가 갱신된다 |
| global `~/.codex/skills` 변경은 repo commit에 포함되지 않음 | mitigated | repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`를 원본으로 만들고 global은 mirror로 동기화 |
| 새 workflow skill은 현재 세션 skill inventory에 즉시 표시되지 않을 수 있음 | mitigated | repo-local source와 global mirror를 동기화하고 `quick_validate.py`로 검증했다 |
| `finance-doc-sync`가 아직 길고 많은 역할을 들고 있음 | mitigated | 3차에서 update matrix를 `references/doc-sync-matrix.md`로 분리 |
| repo-local plugin은 여전히 draft placeholder가 남아 있음 | mitigated | 4차에서 TODO placeholder와 존재하지 않는 component 참조를 제거했다 |
| repo-local plugin install / trigger는 현재 세션에서 완전 재로딩 확인이 어려움 | accepted | marketplace path, manifest, skill validation, global mirror trigger metadata까지 검증하고 다음 세션에서 자연 trigger를 확인한다 |
| candidate refinement skill 제거로 후보 탐색 workflow가 약해질 수 있음 | accepted | 후보 탐색 / 백테스트 리서치는 research worktree로 넘기고, main-dev worktree에서는 Backtest / strategy / doc skill 조합으로 처리한다 |
