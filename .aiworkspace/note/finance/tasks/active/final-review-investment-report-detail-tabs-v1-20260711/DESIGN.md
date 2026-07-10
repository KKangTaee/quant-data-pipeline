# Design

Status: Active
Last Updated: 2026-07-11

## Direction

- Replace repeated lower `details` expanders with one tab bar.
- Tab labels stay task-oriented: `근거 상세`, `저장 경계`, `개선 후보`, `Review 처리`, `Monitoring`.
- The selected tab renders one lower panel below the tab bar.
- Tab content reuses the existing Python-owned payload sections unchanged.

## Boundary

React remains presentation-only. The tab state is local UI state only and does not write Streamlit values, registries, saved setup, or run history.
