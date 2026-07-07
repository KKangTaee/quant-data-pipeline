# Risks

## 2026-07-07

- heuristic classification이 minor lag로만 잡히면 첫 클릭 전에는 provider no-data 여부를 알 수 없다. 이 경우 클릭 후 no-row unresolved 결과를 session state에서 읽어 재클릭을 막아야 한다.
- provider gap을 너무 넓게 제외하면 실제로 나중에 provider가 회복 가능한 심볼도 자동 refresh 대상에서 빠질 수 있다. 명백한 persistent/source/symbol lifecycle reason만 우선 제외한다.
- 향후 Data Trust가 provider no-data를 더 정확히 알 수 있게 되면 `classification_rows` reason taxonomy를 collector result와 연결하는 별도 개선이 가능하다.
