# Inflation Policy Core Engines Notes

- 승인 설계의 값 `4.7`, `3.5`, `0.4~0.5`는 fixture/scenario에는 사용할 수 있지만
  production 전역 상수로 사용하지 않는다.
- 실제 DB policy decision history는 현재 2026년 5회다. policy rolling-origin sample이
  publication gate에 부족하면 2026 replay는 `LIMITED`가 정상 결과다.
- ACM current workbook은 historical release archive가 아니므로 term-premium probability
  calibration에는 아직 사용할 수 없다.
