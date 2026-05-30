# Risks

- Provider quote timeout can turn a normally short snapshot into a multi-minute run.
- Daily intraday return and previous daily return use different end points, so UI text must avoid implying perfect apples-to-apples comparison.
- Raw volume favors high-share-count / low-price names; dollar volume is a useful companion but not a substitute for relative volume.
- Browser QA used the existing local Streamlit server on port 8501; it verified render stability but did not trigger provider collection because US market hours were closed.
