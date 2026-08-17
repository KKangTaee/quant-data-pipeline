# Futures Macro Observation Copy V3 Notes

Last Updated: 2026-08-17

## Decisions

- 카드마다 관측 결과와 해석 한계를 분리한 두 문장을 사용한다.
- 너무 자세한 수치 설명은 방법론 disclosure에 남기고 카드에는 넣지 않는다.
- 기존 payload 구조는 유지하고 summary 문자열만 구체화한다.

## Implemented Result

- 실제 화면의 현재 값은 `달러 압력 완화` 단일 축 사례였다.
- 1D는 같은 변화가 하루 흐름에서도 이어지지만 전환 근거로는 부족하다고 설명한다.
- 5D는 달러 압력 완화만 뚜렷하고 다른 핵심축이 동조하지 않아 정렬되지 않았다고 설명한다.
- 20D는 기존 배경과 같은 방향이지만 중기 전체가 굳어진 상태는 아니라고 설명한다.
- canonical doc change 없음: payload 구조, 계산식, 데이터·화면 ownership은 바뀌지 않았다.
