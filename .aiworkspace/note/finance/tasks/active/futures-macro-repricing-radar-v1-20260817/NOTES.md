# Futures Macro Repricing Radar V1 Notes

## 결정

- 정확한 5D 수익 방향이 아니라 현재 시장 재가격화와 조건부 시나리오를 제품 가치로 둔다.
- forecast backend/history는 지우지 않고 기본 사용자 화면에서만 제거한다.
- family overlap 때문에 confirmation 2개를 독립 신뢰도 개수로 세지 않는다.
- 기존 1D/5D/20D 카드와 장중 잠정/완료 fallback은 유지한다.

## 기존 상태

- 수집: 17개 continuous futures OHLCV
- family 직접 입력: 15개
- current observation: completed daily 또는 fresh latest-closed 5m 합성
- forecast gate: actual 5D `NO_EDGE`; 이번 화면에서는 제거 대상
