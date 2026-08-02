# Inflation Policy Core Engines Notes

- 승인 설계의 값 `4.7`, `3.5`, `0.4~0.5`는 fixture/scenario에는 사용할 수 있지만
  production 전역 상수로 사용하지 않는다.
- 실제 DB policy decision history는 현재 2026년 5회다. policy rolling-origin sample이
  publication gate에 부족하면 2026 replay는 `LIMITED`가 정상 결과다.
- ACM current workbook은 historical release archive가 아니므로 term-premium probability
  calibration에는 아직 사용할 수 없다.
- Core PCE 연말 값은 이전/현재 Q4 index 평균의 비율로만 계산한다. 목표 역산도 같은
  compounded index path를 이분법으로 풀며 월별 MoM 합계를 사용하지 않는다.
- 다섯 상태 경계는 최신 eligible Core PCE SEP histogram의 weighted median, artifact의
  forecast error와 물가안정 목표에서 파생해 release hash가 붙은 definition으로 보존한다.
- path uncertainty는 rolling-origin에서 전달받을 component weight와 predictive residual
  history를 요구한다. residual evidence 없이 정밀 분포를 생성하지 않는다.
