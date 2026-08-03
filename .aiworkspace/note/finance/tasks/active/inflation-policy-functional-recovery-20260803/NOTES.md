# Inflation Policy Functional Recovery Notes

## 2026-08-03 재감사 결론

- actual snapshot의 overall/model/inflation/policy status는 `LIMITED`다.
- actual reverse/equity status는 `NOT_AVAILABLE`이다.
- Core one-month artifact는 내부 baseline보다 우수하지만
  `benchmark_suite_incomplete` 하나로 강제 `LIMITED`다.
- Q4 path, policy path와 reverse는 production pipeline에서 각각 상태가 하드코딩돼 있다.
- actual `sp500_index_earnings`는 0건이며 `joint_macro_paths` artifact도 없다.
- current S&P official workbook parser는 release date 이전 period를 모두 actual로 저장하므로
  historical forward EPS consensus vintage source를 대신할 수 없다.

## 보존 경계

- 사용자 수정 registry와 untracked research/run history/QA artifact는 stage하지 않는다.
- 기존 app server는 사용자 실행으로 간주해 종료하지 않는다.

## 2026-08-03 Core PCE Q4 복구 결론

- official anchor는 Philadelphia Fed SPF의 `PRCPCE1..20` mean probability다.
  current-year 1~10, next-year 11~20을 target year별 10개 bin으로 분리한다.
- 공식 release-date 파일은 날짜만 제공하므로 미국 동부시간 해당 날짜의 종료시각을
  UTC로 변환해 보수적인 `released_at`으로 저장한다.
- official workbook의 잘못된 `T 2:...` OpenXML metadata는 다운로드 원본을 수정하지
  않고 메모리에서 zero-padding한 뒤 파싱한다. 2007년 이전 `#N/A` horizon은 건너뛴다.
- Core PCE chain index는 정기 rebasing이 있으므로 월별 first-release level들을 서로
  나눌 수 없다. Q4 actual은 December가 처음 공개된 시각에 알려진 6개 Q4 month level을
  같은 vintage에서 선택해 계산한다.
- deploy weight는 completed prior target만 사용한 rolling selection과 전체 completed
  target 재학습에서 50% monthly model / 50% official SPF로 선택됐다.
- 다음 발표 시나리오는 첫 미공개 month를 0.1~0.5%로 고정하고 이후 month는 기존
  component/residual 분포를 유지한다. inflation 변화는 READY이며 hike 변화는 3차
  policy validation 전까지 독립적으로 비공개다.
