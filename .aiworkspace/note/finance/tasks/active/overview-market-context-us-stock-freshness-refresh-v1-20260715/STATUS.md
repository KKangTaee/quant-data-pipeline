# Overview Market Context US Stock Freshness Refresh V1 Status

Last Updated: 2026-07-15

## Current Stage

- 전체 roadmap: 1차~3차
- 현재: 1차 freshness/collection · 2차 unified action/UI · 3차 actual/Browser QA와 문서 정렬 complete
- 구현 완료 차수: 3/3
- task 상태: Completed record

## Completed

- 사용자가 선택 종목 상단의 PER/전환 공통 `최신 데이터로 다시 계산` CTA 방향을 승인했다.
- NET actual DB에서 price `2026-07-07`, profile snapshot `2026-02-04`, latest statement period `2026-03-31`/available `2026-05-08`, CIK missing을 확인했다.
- 별도 button과 automatic refresh를 제외하고 exact-scope unified action을 authoritative design으로 정리했다.
- 사용자가 cached UI 즉시 표시 + 자동 최신성 판정 + 명시적 상단 CTA의 hybrid 흐름을 승인했다.
- file/interface/RED-GREEN/commit 단위의 상세 TDD 계획을 `PLAN.md`에 고정했다.
- 공용 NYSE 완료 session helper, unified freshness read model, CIK-independent profile/price와 SEC-only identity gate를 RED-GREEN으로 구현했다.
- 1차 focused calendar/freshness/PER/turnaround/Market Context 111개 테스트와 target py_compile을 통과했다.
- Streamlit event를 `refresh_us_stock_data` 하나로 통합하고 legacy PER/turnaround event는 current UI에서 제거했다.
- 선택 종목 header와 분석 selector 사이에 freshness bar/CTA를 한 번만 렌더링하고 가격·재무·공개 기준일을 구분했다.
- Actual NET explicit refresh로 price를 `2026-07-14`, profile을 `2026-07-15`까지 보강했다. statement는 period end `2026-03-31`, available `2026-05-08`이며 과거 분기라는 이유만으로 stale 처리하지 않는다.
- Actual AAPL stale 화면과 NET READY 화면을 desktop/420px에서 검증했다. CTA/freshness bar 중복, horizontal overflow, 새 console error는 모두 0이었다.
- Focused 114개 테스트, target py_compile, React production build를 통과했다. 전체 discovery의 기존 unrelated assertion 4건과 Streamlit 재import 격리 error 154건은 `RUNS.md`에 분리 기록했다.

## Next Action

- 필수 후속 없음. 다음 범위가 필요하면 SEC CIK 자동 복구, provider별 profile basis 정밀화, 저장소 전체 unittest 격리 정리를 별도 task로 연다.
