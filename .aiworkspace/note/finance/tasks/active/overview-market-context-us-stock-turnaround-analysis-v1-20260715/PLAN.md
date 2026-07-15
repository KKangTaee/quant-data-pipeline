# Overview Market Context US Stock Turnaround Analysis V1 Plan

Status: Design Review
Last Updated: 2026-07-15

## 이걸 하는 이유?

현재 미국 개별주식 PER 화면은 P/E가 성립하지 않는 적자·전환기업을 정확히 제외하지만, 사용자는 그 기업의 영업 개선과 현금 생존 가능성을 같은 종목 흐름 안에서 분석할 수 없다. 별도 전환 분석은 negative P/E를 꾸며내지 않고 quarterly filing evidence에 맞는 질문을 제공한다.

## Goal

미국 개별주식 내부에 `PER 상대가치 | 전환 분석` selector를 추가하고, 선택 기업의 filing-aware 분기 실적으로 영업·현금 전환과 risk/valuation readiness를 판단한다.

## Scope

- selected-company turnaround analysis
- discrete-quarter/TTM correctness
- operating milestones and risk overlays
- stage-appropriate valuation readiness
- selected-symbol DB loader/service/collection
- React inner tabs and charts
- S&P/PER regression protection

## Stop Condition

- RIVN/LCID/PLTR actual DB에서 전환 분석이 evidence-backed로 표시된다.
- AMD/AAPL은 기존 PER 기본 진입과 결과가 유지된다.
- negative/zero denominator, missing quarter, stale EV input이 숫자로 위장되지 않는다.
- focused/full regression, React build, desktop/420px Browser QA가 fresh evidence로 남는다.

## Roadmap

1. 분기 계산 정확도
2. 전환 분석 엔진
3. Loader/Service/Collection
4. 내부 탭/UI
5. Actual QA/문서/커밋

현재는 written spec review 단계다. 사용자 spec 승인 전에는 구현 코드를 수정하지 않는다.
