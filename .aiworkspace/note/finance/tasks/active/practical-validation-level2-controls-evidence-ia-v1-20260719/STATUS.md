# Status

Status: In Progress
Last Updated: 2026-07-19

## Roadmap

- [x] 1차 UX 검토와 분리안 사용자 승인
- [x] 1차 task design / implementation plan 작성
- [ ] 2차 Python read model / intent / fallback TDD
- [ ] 2차 React Step 1/2 / audit disclosure TDD
- [ ] 3차 focused verification / Browser QA
- [ ] 3차 durable docs / review / commit

## Current Position

이미 격리된 `codex/backtest-dev` worktree에서 기준 Python 테스트 34개와 React build가 통과했다. 기존 registry, run history, saved JSONL, QA 이미지는 보존 대상이다.

## Next Action

read model과 intent의 failing test부터 작성한다.
