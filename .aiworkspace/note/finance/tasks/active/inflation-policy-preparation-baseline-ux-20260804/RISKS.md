# Risks

- 정책 경로 정보를 준비표와 정책 panel에 중복 표시한다. 변화량 해석을 위한 의도적인
  문맥 중복으로 제한한다.
- 합계와 bucket의 소수점 자릿수가 다르면 다시 불일치해 보일 수 있으므로 모두
  소수 둘째 자리까지 표시한다.
- 기본 current 선택은 가장 최근 갱신된 current materialization을 사용한다. 과거
  replay와 explicit `as_of_at` 요청은 여기에 섞지 않고 기존 cutoff 선택을 유지한다.
- READY gate를 완화하지 않았다. 실제 component가 LIMITED/NOT_AVAILABLE이면 숫자는
  계속 fail-closed된다.
