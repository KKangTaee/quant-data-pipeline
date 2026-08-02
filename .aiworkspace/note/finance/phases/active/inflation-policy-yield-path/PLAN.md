# Inflation Policy Yield Path Phase Plan

## 이걸 하는 이유?

Core PCE 발표와 FOMC 정책 전망을 10년물의 동적 저항대, 조건부 주가 스트레스까지
연결하되 기존 경제 사이클 확률이나 사후 수정 데이터를 재사용하지 않는 독립 분석
흐름이 필요하다.

## Goal

`Core PCE -> 정책 경로 -> 국채금리 저항 -> 조건부 자산 스트레스`를 point-in-time
데이터와 검증된 확률로 제공하고, 침체 확률은 별도 검증 gate 뒤에만 연결한다.

## Stages

1. point-in-time 데이터 기반
2. Core PCE·정책·금리 확률 엔진
3. 순방향·10년물 목표 역산 workbench
4. 조건부 S&P 500 스트레스
5. 독립 침체 위험 모델

## Stop Condition

각 단계는 자체 테스트와 publication gate를 통과해야 다음 단계로 이동한다. 검증되지
않은 확률은 `LIMITED` 또는 `NOT_AVAILABLE`로 남긴다.

