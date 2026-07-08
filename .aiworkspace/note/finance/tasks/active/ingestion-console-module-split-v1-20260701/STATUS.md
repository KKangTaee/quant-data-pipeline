# Ingestion Console Module Split V1 Status

Status: Done
Started: 2026-07-01

## Current

- 6차 완료: `app/jobs/ingestion/common.py` 공통 helper 분리와 durable docs / root handoff log sync를 완료했다.

## Milestones

- Done: 1차 package facade
- Done: 2차 registry split
- Done: 3차 guide / style / result split
- Done: 4차 dispatcher split
- Done: 5차 section split
- Done: 6차 job common / docs sync

## Result

- `app/web/ingestion_console.py`: legacy compatibility facade.
- `app/web/ingestion/page.py`: Streamlit page shell / session-state boundary.
- `app/web/ingestion/registry.py`: section / action registry.
- `app/web/ingestion/guides.py`: job guide / domain metadata.
- `app/web/ingestion/styles.py`: responsive CSS.
- `app/web/ingestion/results.py`: pure result summary helpers.
- `app/web/ingestion/dispatcher.py`: UI action dispatch and diagnostic job wrapping.
- `app/web/ingestion/sections.py`: collection workbench section renderers.
- `app/jobs/ingestion/common.py`: shared ingestion job parsing / result / progress helpers.
