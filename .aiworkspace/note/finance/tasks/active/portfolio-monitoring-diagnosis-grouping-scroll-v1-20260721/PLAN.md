# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Plan

## Goal

Portfolio Monitoring의 강점·취약점·데이터 부족 영역에서 같은 의미의 진단이 종목 또는 종목쌍마다 반복되는 문제를 줄이고, 근거가 많아져도 전체 화면이 무한히 길어지지 않게 한다.

## 이걸 하는 이유?

현재 진단값은 서로 다른 종목·종목쌍을 측정하지만 카드가 대상 identity를 숨긴 채 같은 문구를 반복한다. 사용자는 같은 경고가 중복 생성된 것으로 이해하며, 취약점이 많을수록 다른 Portfolio Monitoring 업무까지 과도하게 밀려난다.

## Scope

- 동일 진단 유형의 사용자 표시 그룹화
- 그룹 대표 요약과 개별 종목·종목쌍 근거 보존
- 진단 열별 건수 표시와 desktop 높이 제한/내부 스크롤
- mobile 중첩 스크롤 방지
- Python/React 회귀 테스트와 Browser QA

## Out Of Scope

- 진단 threshold, severity, confidence, exposure/behavior 계산 변경
- 진단 snapshot/registry 재작성
- 새로운 위험 지표 또는 투자 판단 추가

## Stop Condition

동일 상관·낙폭 진단이 유형별 한 카드로 표시되고 상세 근거에서 모든 원본 row를 확인할 수 있으며, desktop은 일정 높이 이후 진단 목록만 스크롤되고 mobile은 자연스러운 page scroll을 유지하면 완료한다.
