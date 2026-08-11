# Plan

## 이걸 하는 이유?

RTDSM으로 장기 표본은 확보했지만 현행 8지표와 장기 4지표가 서로 다른 국면을
정답으로 사용해 예측 모델을 만들 수 없었다. 과거와 현재에 같은 핵심 국면을 적용하고,
그 국면에서만 다음 목적지와 전환압력을 검증해야 사용자가 해석 가능한 확률을 얻는다.

## Goal

장기 공통 core state를 확정하고 episode-safe destination/imminence 모델을 시간순으로
검증한다. 통과한 결과만 persistence/service/UI 후보로 승격한다.

## Whole Roadmap

1. core state semantic/revision gate
2. episode-weighted transition dataset과 모델
3. chronological OOS/baseline/calibration gate
4. 통과 시 persistence/service/UI/Browser QA

## Stop Conditions

- core-state gate 실패 시 2~4차 중단
- pressure 또는 destination publication gate 실패 시 probability persistence/UI 중단
- 임계값 완화, row-level random split, 사후 indicator 선택 금지
- 자산별 확인 포인트 변경 금지
