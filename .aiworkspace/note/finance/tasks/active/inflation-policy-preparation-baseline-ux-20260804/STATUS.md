# Inflation Policy Preparation Baseline UX Status

State: complete
Last Verified: 2026-08-04

## 완료 상태

- 전체 roadmap 2/2를 완료했다.
- `다음 Core PCE 발표 전 준비표`에 현재 물가 재가속 구성·합계와 연말 순인상
  1회·2회·3회 이상 구성·합계를 소수 둘째 자리까지 표시한다.
- 실제 DB Browser QA에서 16.04%와 49.29% 및 세 순인상 bucket을 확인했다.
- 오래된 23:59 LIMITED row가 나중에 materialize된 03:15 READY current snapshot을
  가리던 loader 선택 문제를 근본 수정했다. 명시적 과거 조회의 PIT cutoff는 유지한다.
- 이 task 범위의 남은 차수는 없다. 다음 작업은 같은 탭의 별도 사용자 요청에서 시작한다.
