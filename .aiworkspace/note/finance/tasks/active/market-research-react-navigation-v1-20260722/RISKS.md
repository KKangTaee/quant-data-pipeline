# Market Research React Navigation V1 Risks

Status: Complete
Last Updated: 2026-07-22

## Resolved Risks

1. component event와 Streamlit rerun 사이에 duplicate event가 발생하지 않도록 nonce와 validated current-view comparison이 필요하다.
2. iframe height가 viewport/payload 변경 뒤 늦게 줄어 빈 공간을 만들 수 있어 ResizeObserver QA가 필요하다.
3. React-first와 Streamlit fallback이 서로 다른 state result를 만들지 않도록 하나의 Python resolver를 공유해야 한다.
4. 420px에서는 family 목적 설명을 screen-reader text로 유지하면서 시각적으로 숨긴다. actual QA에서는 label 3열의 clipping과 focus outline만 확인한다.
5. component static bundle 누락 시 page가 비지 않도록 availability test와 fallback 회귀가 필요하다.

각 항목은 validated current-view comparison, ResizeObserver actual QA, shared Python resolver, 420px actual QA, availability/fallback test로 닫았다.

## Deferred

- sticky navigation
- drawer/off-canvas
- recent/saved research
- module body redesign

## Remaining External Validation Gap

- broad service-contract 18건은 이번 변경 전부터 존재한 Backtest/Practical Validation, Futures Macro, Sentiment/AAII 비범위 failure다. 이번 Market Research 변경 파일과 실패 소스가 겹치지 않는다.
