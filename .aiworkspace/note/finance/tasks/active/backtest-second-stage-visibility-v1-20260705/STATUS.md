# Backtest Second Stage Visibility V1 Status

Status: Completed
Date: 2026-07-05

## 진행

- RED 테스트로 Handoff가 2차 상세 문구를 들고 있고 Data Trust가 `meta["warnings"]`를 1차 issue card로 펼치는 문제를 고정했다.
- Data Trust issue card는 excluded ticker / malformed price row 같은 직접 데이터 이슈만 확장하도록 수정했다.
- `meta["warnings"]`는 `second_stage_review_count`와 compact 2차 전달 안내로만 남기도록 변경했다.
- Handoff / Policy Signal handoff 문구에서 provider / data coverage / realism / robustness 같은 2차 상세 설명을 제거했다.

## 완료 조건

- Backtest Analysis Data Trust는 가격 기준, 계산 기준일, 제외 종목, 결측 row 같은 1차 data readability만 상세 표시한다.
- `meta["warnings"]` 기반 실전성 review focus는 Backtest Analysis에서 개수 / 위치 안내만 남기고 상세 row로 펼치지 않는다.
- Practical Validation `Backtest에서 넘어온 2차 확인 항목`은 기존처럼 상세 review queue를 받는다.
- source registration, registry / saved setup, strategy runtime, gate threshold는 변경하지 않았다.
- focused tests, py_compile, diff check, Browser QA screenshot을 완료했다.
