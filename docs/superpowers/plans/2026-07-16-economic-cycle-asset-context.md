# 경제 사이클 자산별 확인 포인트 구현 계획

## 1차 — 판정 모델

- `finance/economic_cycle_interpretation.py`에 자산별 orientation, 상태 판정, 근거 요약, 변경 조건을 추가한다.
- service 테스트로 실제 조합과 자료 부족 계약을 먼저 고정한다.
- 완료 조건: 네 상태 taxonomy와 비방향성 계약이 테스트로 검증된다.

## 2차 — 화면과 검증

- React payload type과 `시장의 다음 질문` UI를 자산별 카드로 교체한다.
- 2×2/1열 반응형 스타일과 상태 배지를 추가한다.
- component build, Python 회귀 테스트, Browser QA를 실행한다.
- task/root 문서를 동기화하고 coherent commit을 만든다.

## 제외 범위

- 자산 수익률 예측
- 매수·매도 추천
- 별도 market-price 데이터 수집
- 경제 사이클 모델 확률이나 검증 gate 변경
