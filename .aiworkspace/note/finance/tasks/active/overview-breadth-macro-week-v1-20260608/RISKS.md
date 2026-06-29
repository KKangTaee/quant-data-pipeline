# Risks

- 실제 DB에 event rows가 부족하거나 stale이면 macro week lane은 no-data / review 상태를 보여준다.
- 3차는 first pass라서 full market breadth heatmap이나 full macro week quality workflow는 후속 차수로 남는다.
- Sector / Industry heatmap은 기존 top group rows의 compact view다. full breadth heatmap, universe-wide participation distribution, drilldown interaction은 4~5차 이후 별도 후보로 남긴다.
- Events quality 자체의 수집/검증 policy는 바꾸지 않았다. stale / estimate / not-confirmed 상태는 그대로 노출하고 후속 source/provider hardening 후보에서 다룬다.
