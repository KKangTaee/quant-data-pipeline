# Risks

- Full provider-backed `유니버스 기준 갱신` can be slow on a cold run because it runs listing candidate lookup, broad EOD refresh, and materialization in one action. Closeout smoke stopped TOP1000 full provider refresh after 6+ minutes and used SQL-only compute/store for verification.
- Browser QA depends on local Streamlit/component runtime availability.
- Materialized Top2000 can contain fewer than 2000 rows when listing coverage or recent EOD price rows are insufficient. Local DB smoke on 2026-07-05 produced 1,920 TOP2000 members from 6,012 listing candidates with ranking end date 2026-07-02.
- Daily intraday snapshot can still have missing rows after universe materialization. Local Browser QA showed TOP2000 universe 1,920, returnable 1,208, missing 712 before a fresh intraday snapshot refresh.
