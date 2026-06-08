# Risks

- yfinance may legitimately return unchanged or delayed rows. The UI can only show latest stored data plus stale status; it cannot force provider freshness.
- Browser QA used a temporary port 8502 server because port 8501 was already occupied by an existing Python process.
- QA screenshot is a generated local artifact and should not be staged unless explicitly requested.
