# Plan

## 이걸 하는 이유?

현행 경제사이클은 현재 국면은 계산하지만 미래 방향은 고정 순환의 인접 국면을
감시한다. RTDSM-only 후속 연구도 정책·물가·금리·신용·시장 해석을 예측 입력으로
다루지 않아 사용자의 원래 목적을 충족하지 못한다. UI 구현 전에 현재 국면과 확장
전환 모델의 실현 가능성을 실제 Point-in-Time 데이터로 검증한다.

## Goal

1차 제품 계약, 2차 PIT 데이터 적합성, 3차 shadow forecast 검증을 완료하고
`GO / LIMITED_GO / NO_GO`를 actual evidence로 판정한다.

## Scope

1. confirmed official state 계약 고정
2. policy/inflation/rates/credit/market feature coverage audit
3. core-only와 extended transition model chronological comparison
4. read-only final feasibility report와 문서 정렬

## Out Of Scope

- production persistence/service/UI
- Data Freshness 변경
- 자산별 확인 포인트 변경
- 신규 provider와 DB schema

## Stop Conditions

- confirmed state gate 실패 시 model fitting 중단
- extended driver support 실패 시 임의 대치나 threshold 완화 금지
- actual 결과를 본 뒤 target, feature group, gate 변경 금지
- 확률 gate 실패 시 4·5차 제품 구현 금지

## Whole Roadmap

1. 1차 제품·모델 계약
2. 2차 PIT 데이터 적합성
3. 3차 shadow forecast 검증
4. GO 범위만 persistence/service로 연결
5. GO 범위만 순환 경로 UI에 반영하고 Browser QA
