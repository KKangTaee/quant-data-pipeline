# Overview Market Context Macro Polish V17 Status

Status: Complete
Date: 2026-06-21

## Current

- V17 started to address two user-facing UX issues:
  - GLD / 금리선물 조건 적용 단계의 뜻이 basis bar 안에서 바로 읽히지 않는다.
  - `현재 Macro 배경 참고`가 긴 설명 텍스트 중심으로 보여 과거 유사 맥락 섹션 대비 덜 정돈되어 보인다.

## Done

- Added user-facing condition meaning text to the Macro narrowing bar:
  - broad basis: sector ETF vs SPY relative-strength analog pool
  - GLD: current-like GLD bucket
  - futures: current-like ZN=F / ZB=F rate-pressure bucket
- Reworked the reference Macro backdrop block to Korean-first status badges, current value, same-state broad-sample ratio, and compact source description.
- Kept verbose condition / source rows inside `Macro 조건 상세`.
- Verified focused tests, full service contract tests, py_compile, diff check, and Browser QA.

## Next

- No immediate follow-up required for this V17 slice.
