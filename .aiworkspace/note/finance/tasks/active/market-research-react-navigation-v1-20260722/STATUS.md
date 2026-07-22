# Market Research React Navigation V1 Status

Status: Complete
Roadmap: 3/3 implementation stages complete
Last Updated: 2026-07-22

## Completed

- `market_research_navigation_v1` Python payload와 validated `select_view` event 계약을 구현했다.
- header, 3-family selector, family-local 7-view selector를 하나의 responsive React/Vite surface로 전환했다.
- Python을 canonical query/session/legacy normalization owner로 유지하고 static bundle 누락 시 기존 Streamlit header/navigation fallback을 보존했다.
- 선택 event가 도착한 같은 run의 iframe에 이전 payload가 남던 문제를 state 저장 후 changed-view rerun으로 해소했다.
- 1280·760·420px에서 전 family/view 이동, URL/selected state, frame height, overflow 0, keyboard focus를 actual Browser QA로 확인했다.

## Current

- 전체 roadmap `3/3차` 완료.
- QA screenshot: `market-research-react-navigation-qa.png` (generated, commit 제외)

## Next

- module body redesign, sticky/drawer, recent/saved research는 별도 승인 범위다.
- Market Research 상단 후속은 `app/web/overview/navigation.py`, wrapper, React source/static bundle에서 이어간다.
