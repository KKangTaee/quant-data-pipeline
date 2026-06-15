# Notes

- The repair action is generated from actual coverage gaps, so it can target `XLC`, `XLF`, `XLV`, `XLK`, or other supported sector proxies depending on the current leadership sector.
- The UI does not auto-run collection on render. The user must open `보조 갱신` and click the explicit button.
- Current Browser QA live model showed `Communication Services -> XLC` with 63 / 756 rows, so the gap panel and repair action were visible without forcing a fake analog table.
- `자료 기준 / 출처 상태` still retains detailed rows inside the disclosure; V4 only adds a scan strip so users can read the source state before expanding it.
- Streamlit server restart may be needed after action facade import changes if the old process holds stale module state.
- The `다음 맥락 체크` cue row had a scoped CSS override that reduced left padding to zero; this made the accent rule look like it was overlapping the label. The follow-up restores explicit left padding.
- The historical analog repair button should stay visible in the main Market Context flow when gaps exist. The collapsed `보조 갱신` expander remains for broader refresh, not for the primary missing-data action.
