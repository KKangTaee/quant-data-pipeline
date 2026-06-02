# Notes

- User explicitly excluded section 4 from this pass.
- The current saved setup file is dirty and should remain untouched.
- Streamlit can support this level of polish with custom HTML/CSS and disciplined layout; no frontend framework migration is needed for this slice.
- `3. 포트폴리오 모니터 시나리오` is explicitly portfolio-wide. It aggregates completed strategy scenario results by slot balance and marks unrun / partial states rather than implying a full result.
- The new portfolio-wide run action loops existing per-strategy recheck logic and stores results in the same session state keys as the strategy tabs.
- Detailed dataframe views remain available under expanders for audit / debugging, but the primary workflow is now shelf -> command band -> strategy board -> scenario cockpit.
