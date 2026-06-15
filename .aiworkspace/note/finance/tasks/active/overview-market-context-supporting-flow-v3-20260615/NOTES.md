# Notes

- Current `interpretation_cues` mixes Events, Sentiment, and Data Health.
- Data Health is not a market variable; it should remain visible as source/evidence context, not as a main cue row.
- The retained model key `interpretation_cues` is compatibility-only after V3; user-facing copy now presents it as `다음 맥락 체크`.
- Live local data still shows historical analog coverage as `자료 부족`, but the section is now styled as muted reference rather than a primary decision block.
- Streamlit reload alone can retain previously built session data; a server restart was needed during Browser QA to verify service-level cue label changes.
