# Master Merge Resolution Design

## Integration Direction

- Sentiment의 1W·1M 실제 관측 변화와 `3/4차 paused` 상태를 유지한다.
- Futures Macro의 latest closed 5m 기반 장중 임시 관측, completed daily fallback과
  1D·5D·20D 재가격화 해석을 current product 기준으로 통합한다.
- completed daily forecast/history는 호환성·shadow research backend로 보존하되
  primary UI에는 예측 gate, 5D 확률이나 가격 목표를 다시 노출하지 않는다.
- 사용자 registry/saved setup과 generated/local artifact는 통합 대상에서 제외한다.
