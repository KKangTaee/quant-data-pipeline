# Market Research Top Navigation Visual Polish V1 Risks

Status: Active
Last Updated: 2026-07-22

## Open Risks

1. Streamlit widget DOM/testid가 version에 따라 바뀔 수 있으므로 scoped CSS selector를 actual Browser QA와 structural test로 고정해야 한다.
2. native segmented/pills selected state가 theme primary red를 상속할 수 있어 navigation state에 경고색이 남지 않는지 확인해야 한다.
3. single-view `지수 가치평가`에서 secondary surface가 비거나 높이가 달라지면 family 전환이 불안정해 보일 수 있다.
4. desktop content-width와 mobile equal-column contract가 같은 CSS에서 충돌할 수 있다.
5. page header CSS가 다른 Streamlit page title에 누출되지 않도록 keyed container로 scope해야 한다.
6. actual module마다 상단 hero 높이가 달라 nav-to-content gap을 view별로 확인해야 한다.

## Deferred

- sticky top rail
- left drawer/off-canvas
- watchlist, recent research, saved research navigation
- module body redesign
