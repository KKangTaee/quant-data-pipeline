# Final Review Responsive Evidence V1

## 이걸 하는 이유?

Final Review `남은 판단 근거`에서 review impact의 공통 직계 `div` 2열 selector가 내부 trace list에도 적용돼, 브라우저 폭을 줄이면 첫 evidence card가 좁은 열로 찌그러지고 긴 lifecycle 문자열이 옆 열을 밀어낸다. REVIEW 근거를 축소 화면에서도 같은 읽기 순서와 폭으로 유지한다.

## 단계

1. review impact header와 trace list의 selector 책임을 분리한다.
2. trace card를 항상 1열로 유지하고 긴 evidence 문자열 wrapping을 보강한다.
3. 중간 폭과 mobile breakpoint를 Browser QA한다.

## 완료 조건

- trace card가 형제 카드의 내용 길이에 따라 폭이 달라지지 않는다.
- 긴 lifecycle / provider 문자열이 card 밖으로 밀려나거나 세로 한 글자 폭으로 찌그러지지 않는다.
- desktop / compact / mobile에서 탭과 REVIEW 근거 순서가 유지된다.
- Python evidence / score / gate / 저장 계약은 변경하지 않는다.
