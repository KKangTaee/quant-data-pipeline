# Overview Market Context US Stock Freshness Refresh V1 Plan

Status: Awaiting Written Spec Review
Last Updated: 2026-07-15

## 이걸 하는 이유?

선택 종목의 가격·시장가치가 stale할 때 사용자가 한 번의 명시 action으로 필요한 자료만 최신화하고 PER/전환 분석을 함께 다시 계산할 수 있게 한다.

## Roadmap

1. 최신 완료 거래일·profile/price/statement exact gap과 CIK scope 분리를 TDD로 구현한다.
2. selected-stock 상단 single CTA, unified event/action, 두 분석 공동 rerun, basis label 분리를 구현한다.
3. NET actual/Browser QA, focused/full/build/compile, 문서 정렬과 closeout을 수행한다.

상세 file/interface/RED-GREEN 계획은 written spec 승인 후 `superpowers:writing-plans`로 확장한다.
