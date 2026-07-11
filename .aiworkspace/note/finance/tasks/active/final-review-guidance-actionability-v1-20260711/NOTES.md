# Notes

- 기존 구현은 validation 전체 텍스트의 token 일치로 패턴을 판정해 10개가 모두 `indicative`가 되기 쉽다.
- source가 없으면 내부 dict path를 사용자 source처럼 노출한다.
- 기존 6개 Final Review 후보는 registry를 재작성하지 않고 새 read model로 해석한다.
- 실제 Distinct Strategy는 `판단 가능 3 / 조건부 추적 5 / 추가 검증 필요 1 / 적용 제외 1`로 분류됐고 first-read 6개만 표시됐다.
- 실제 REVIEW는 `직접 결정 1 / 2단계 인수 제한 8`로 분리됐으며 Final Review 사용자 행동에 Flow4 문구가 남지 않았다.
