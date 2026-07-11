# Notes

- 기존 구현은 validation 전체 텍스트의 token 일치로 패턴을 판정해 10개가 모두 `indicative`가 되기 쉽다.
- source가 없으면 내부 dict path를 사용자 source처럼 노출한다.
- 기존 6개 Final Review 후보는 registry를 재작성하지 않고 새 read model로 해석한다.
