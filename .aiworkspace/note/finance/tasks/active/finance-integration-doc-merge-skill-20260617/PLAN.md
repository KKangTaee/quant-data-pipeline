# Finance Integration Doc Merge Skill 2026-06-17

Status: Completed

## Purpose

Strengthen `finance-integration-review` so repeated multi-worktree merges can resolve `.aiworkspace/note/finance` documentation conflicts without losing either branch's durable context.

## 이걸 하는 이유?

Several worktrees will continue producing overlapping roadmap, root handoff, task manifest, and retained-task document updates. A general merge-review checklist is not specific enough to prevent accidental latest-task pointer loss, duplicated current-state claims, or unnatural document flow after conflict resolution.

## Scope

- Add a document-merge conflict checklist to the repo-local finance workflow skill source.
- Mirror the same checklist to the installed runtime skill.
- Link the checklist from `finance-integration-review/SKILL.md`.
- Validate skill metadata and basic Markdown / conflict-marker hygiene.

## Not In Scope

- Creating a separate new skill.
- Automating conflict resolution.
- Moving task folders between `active` and `done`.
- Rewriting registries, saved setup JSONL, run history, or generated artifacts.
