# Risks

- 확장 driver의 strict PIT common period는 actual 27 origins / 5 transitions로 부족하다.
- current cutoff 2026-07의 official state는 2026-01 이후 unavailable이다. RTDSM source
  갱신 없이 historical state의 마지막 값을 현재 국면으로 carry-forward할 수 없다.
- 지배적 병목은 high-yield OAS의 현재 저장 PIT 시작점 2023-08이다. public series의 더
  오래된 관측이 존재하더라도 당시 known-at을 재현하는 공식 수집·저장 검증 전에는
  revised current history로 대체할 수 없다.
- market continuous futures는 historical contract quality가 probability input 기준을
  통과하지 못할 수 있다.
- fiscal impulse는 승인된 장기 monthly PIT source가 없어 이번 모델에서 빠질 수 있다.
- macro episode 수가 적어 core보다 복잡한 extended model이 baseline을 이기지 못할 수 있다.
- 이번에는 driver coverage에서 fail-closed하여 model skill 자체는 측정하지 않았다.
- 124초 actual research run은 production Data Freshness 경로와 분리돼 있지만, 향후 반복
  연구 운영 전에 100만 행 ANFCI interval 처리의 cache/vectorization 최적화가 필요하다.
- 4·5차를 재개할 때 결과를 보고 BAML을 제거하거나 support threshold를 낮추면 안 된다.
  source 보강 또는 사전 승인한 대체 credit feature로 2차 audit부터 다시 실행해야 한다.
