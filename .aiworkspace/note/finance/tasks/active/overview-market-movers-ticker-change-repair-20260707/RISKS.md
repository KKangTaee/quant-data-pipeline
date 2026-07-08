# Risks

- False-positive ticker alias matching can contaminate price evidence. First version must require explicit apply and should only propose high-confidence candidates.
- Alias application must preserve original universe symbol identity while recording quote symbol evidence.
- Provider search / quote endpoints are unstable; tests should mock provider rows rather than depend on network.
- Browser visual QA confirmed the Market Movers view renders in the live Streamlit app. The current default DB state had no alias candidate, so visible button placement for the candidate-only action remains covered by focused React payload/action tests.
