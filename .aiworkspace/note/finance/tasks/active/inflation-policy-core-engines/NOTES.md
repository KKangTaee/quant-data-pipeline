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
- SEP rate dots는 현재 midpoint 대비 순이동 marginal로만 변환한다. 2026년 6월 실제
  분포는 1회 인하 1명, 동결 8명, 1회 인상 3명, 2회 5명, 3회 이상 1명이다.
- 최근 FOMC 표결은 실제 action에 찬성한 표와 dissent의 명시적 선호 방향을 다음 회의
  committee marginal로만 쓴다. 임의 hawkish score로 압축하지 않는다.
- 경제 component는 versioned state-to-policy reaction matrix를 요구하므로 충격성 재가속도
  100% 인상 boolean이 되지 않는다. missing optional market prior는 제외 후 재정규화한다.
- 저항 기준은 strict pivot high가 오른쪽 확인 window를 채운 `known_at` 이후에만 사용한다.
  63/252/504일에서 반복 발견된 같은 pivot은 confluence는 3개지만 touch는 1회다.
- zone tolerance는 `max(5bp, 최근 63일 절대 일간변화 중앙값)`이며 값 자체를 고정하지 않는다.
- 명목 10년물은 `실질+breakeven` lens와 `2년 정책 proxy/ACM` lens를 분리한다. 두 lens를
  하나의 additive decomposition으로 중복 합산하지 않는다.
- 10년물 `CONFIRMED/HOLD`만으로 물가 확인이 되지 않는다. breakeven, driver와 Core PCE
  재가속 posterior 상승이 결합돼야 `INFLATION_CONFIRMED`다.
- joint simulation path는 Core PCE, 평균 남은 MoM, 정책 순이동과 instrument별 금리 path를
  함께 보존한다. 정책 25bp와 10년물 25bp를 기계적으로 매핑하지 않고 두 rate lens의
  calibrated weight로 10년물 path를 만든다.
- 역산은 `REACH/BREAK/HOLD`를 만족한 path likelihood를 재정규화해 정책 횟수·연말 PCE·
  필요 MoM 조건부분포를 반환한다. support count와 effective sample이 부족하면
  `NOT_AVAILABLE`이며 외삽하지 않는다.
- 다음 PCE `0.1~0.5` 시나리오는 각 path의 다음 MoM likelihood로 target posterior를
  재가중한다. 어떤 발표치도 boolean 인상 trigger가 아니다.
