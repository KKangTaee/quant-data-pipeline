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

## 2026-08-03 정책·공동 금리 경로 복구 결론

- 기존 FOMC collector는 2026 press index 하나를 기본 URL로 쓰고 target range 문구의
  `at`만 허용해 과거 회의와 `to` 문구를 놓쳤다. 공식 multi-year calendar의
  `Statement:` 링크만 선택하고 `by ... to X to Y percent` 형식을 파싱하도록 바꿨다.
- 2025-08-22 monetary policy strategy/notation release처럼 rate decision이 아닌 문서는
  meeting history에서 제외한다. current calendar만으로는 연말 정책 검증의 시간순 표본이
  부족하므로 2016~2020 historical page의 exact `Statement`와 SEP compilation 링크를
  official accessible page로 연결한다. 실제 rate decision 86건, SEP 40개 release와
  5,787개 row가 2016~2026 범위로 저장됐다.
- 12월 SEP는 같은 시각에 이미 발표된 그해 마지막 정책결정을 연말 forecast target으로
  평가할 수 없다. 최초 13개 연말 origin에는 이 동시결과가 섞여 있었으므로 폐기했고,
  `release_at < final_decision.released_at`인 28개 completed origin만 구성해 calibration 6개
  이후 22개 평가 origin으로 다시 검증했다.
- historical statement는 공식 index의 `Meeting - YYYY` panel 안 exact `Statement`만
  수집한다. target-range parser 실패를 비금리 문서로 추정해 건너뛰지 않으며, 실제 회의
  문구가 새 형식이면 전체 수집을 fail-closed한다.
- 정책 분포는 익명 SEP dot marginal과 실제 표결/dissent marginal을 시간순 완결 target으로
  검증한다. SEP Core PCE participant와 rate-dot participant를 개인별로 연결하지 않는다.
- 공동 금리 경로는 DGS2/DGS10/DFII10/T10YIE의 같은 historical episode 변화와 현재
  검증된 Q4/policy marginal의 rank dependence를 사용한다. 미래 Core PCE actual을 현재
  feature로 넣지 않으며, 역사 Q4 값은 completed episode의 결합 순위에만 사용한다.
- dynamic resistance event도 origin 당시 알려진 63/252/504일 pivot으로 다시 만들고
  후속 실제 path의 reach 여부를 target으로 검증한다. 현재 4.79%는 전역 상수가 아니라
  2025-01-16에 확인된 다음 overhead zone이다.
- snapshot overall은 equity/recession 미완료 때문에 `LIMITED`지만 이미 READY인
  inflation/policy/rates/reverse를 제한 상태로 설명하면 안 된다. read model headline은
  네 macro component 자체의 상태를 사용한다.
- stored reverse 결과와 form 기본 target이 달라 보이던 UI 문제를 제거했다. form은 exact
  stored target 4.79%/REACH에서 시작하고 같은 artifact로 command를 실행한다. snapshot
  identity가 바뀌면 새 target으로 재동기화하고, 같은 snapshot의 command rerender는 dirty
  input을 유지한다.
