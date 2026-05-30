# Risks

- Fed page markup can change. Parser should fail loudly through the job result instead of silently storing zero rows.
- Cross-month ranges such as `Apr/May 30-1` need special handling because the event date belongs to the second month.
- Historical meetings may contain special notation votes. The first collector focuses on regular FOMC meeting rows exposed by the official calendar markup.
- Browser smoke passed after restarting the stale Streamlit process. Keep in mind Streamlit may need a restart when newly imported job functions are added.
