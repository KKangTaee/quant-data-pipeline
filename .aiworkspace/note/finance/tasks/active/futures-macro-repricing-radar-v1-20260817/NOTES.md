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

## 구현 중 발견

- 실제 2026-08-14 완료 snapshot은 5D core가 모두 중립이지만 1D 금리 부담 확대와 달러 압력 완화가 material하다.
- 5D만 중심축으로 선택하면 이 새 변화를 잃으므로, 5D material core가 없고 1D core가 material한 경우 가장 강한 1D 축을 `NEW_SHOCK`으로 표시한다.
- 실제 payload는 금리 부담 확대를 유력 해석, 달러 압력 완화와 방어 수요 약화를 반대 근거로 분리했다.
