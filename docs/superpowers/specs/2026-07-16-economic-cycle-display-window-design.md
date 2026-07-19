# Economic Cycle Display Window Design

Status: Approved
Last Updated: 2026-07-16

## Purpose

경제사이클 화면의 계산 결과와 장기 저장 이력은 유지하면서 첫 화면의 선과 월별 리본을 더 빠르게 읽을 수 있도록 표시 기간만 줄인다.

## Display Contract

- Cycle Map은 최근 18개월 대신 최근 12개 월말을 실선으로 표시한다.
- 현재, +1개월, +2개월의 미래 모델 경로는 그대로 유지한다.
- Regime Ribbon은 최근 121개 월말 대신 최근 60개 월말을 표시한다.
- Ribbon의 현재, +1개월, +2개월 표시는 그대로 유지한다.
- 화면 문구는 각각 `실선은 최근 12개월`, `최근 5년 + 2개월 전망`으로 변경한다.
- DB snapshot, artifact, 전체 replay history와 validation 계약은 변경하지 않는다.

## Data Boundary

Overview service는 DB에서 화면에 필요한 최근 60개월만 요청하고 read model도 최대 60개 history row만 반환한다. 데이터 삭제나 재물질화는 실행하지 않는다.

## Acceptance Criteria

- Cycle Map source contract가 `payload.history.slice(-12)`를 사용한다.
- Read model history가 최대 60개 월말만 반환한다.
- Regime Ribbon 안내 문구가 최근 5년을 명시한다.
- 현재/+1M/+2M 카드, 잠정/검증/판단불가 상태, 결측 구간 분리 계약은 유지한다.
- React production build, 경제사이클 service/UI 회귀 테스트, desktop/420px Browser QA가 통과한다.
