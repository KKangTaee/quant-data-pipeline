# Overview Context Refresh / Korean Copy V1 Notes

## Findings

- Overview entry rerenders DB-backed snapshots, but data collection is owned by existing bounded refresh actions.
- `app/jobs/overview_actions.py` is the correct boundary for Overview-triggered collection wrappers.
- Existing cockpit loads SP500 daily movers, SP500 daily sector leadership, futures macro thermometer, sentiment, events, and collection ops status.
- Browser QA initially caught a stale Streamlit process holding the old `overview_actions` module; restarting the local server fixed the ImportError and confirmed the new UI.

## Decisions

- Keep `Market Context`, `Deep Tab`, `Source Confidence`, and tab names as product terms, but translate explanatory copy to Korean.
- Add one manual bundle button, not auto/scheduled collection.
- Bundle scope covers SP500 market movers, futures 1m/daily, sentiment, FOMC, earnings, and macro calendar. Top1000/Top2000 extended universes remain separate.
