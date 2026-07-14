# Overview Market Context US Stock Valuation V1 Plan

Status: Design Approved — Detailed Implementation Plan Pending Written Spec Review
Last Updated: 2026-07-14

## 이걸 하는 이유?

현재 Market Context의 Nasdaq-100 가치평가는 무료·무계정 QQQ proxy를 구성종목 단위로 재구성하기 때문에 과거 편입종목, 상장폐지, 기업별 EPS와 EOD 가격 누락을 동시에 해결해야 한다. 이 복잡도에 비해 Nasdaq 적정가 시나리오의 사용자 판단 가치는 제한적이다.

반면 미국 개별주식은 선택된 한 기업의 가격과 SEC 실적만 있으면 동일한 상대 멀티플·EPS 시나리오를 계산할 수 있다. 기존 Nasdaq 사용자 화면을 개별주식 검색·평가 흐름으로 교체해, 사용자가 관심 기업의 과거 대비 상대적 고평가·저평가와 거시·기업 실적 결합 시나리오를 확인하게 한다.

## Goal

- Market Context의 `Nasdaq-100` 선택지를 `미국 개별주식`으로 교체한다.
- 기업명 또는 티커 검색 후 선택 기업의 월별 point-in-time TTM EPS와 PER를 계산한다.
- Graph 1은 최근 5년 log(PER) 구간과 3년 민감도를 제공한다.
- Graph 2는 FOMC 거시 기준과 기업 초과 EPS 성장률을 결합한 보수·기준·낙관 시나리오를 제공한다.
- 자료가 부족하면 선택 기업만 동기 수집하는 명시 action을 제공한다.
- PER로 평가할 수 없는 기업은 값을 합성하지 않고 이유를 명확히 표시한다.

## Scope

- 사용자-facing Nasdaq selector 제거와 미국 개별주 검색 흐름
- current U.S.-listed common-stock 검색 계약
- selected-symbol DB loader와 bounded valuation calculator
- filing-aware monthly TTM diluted EPS carry-forward
- monthly P/E, log multiple band, hybrid EPS scenario
- selected-symbol price/SEC statement collection action
- READY/COLLECTABLE/NOT_APPLICABLE/ERROR UI
- S&P regression, actual DB smoke, desktop/mobile Browser QA

## Tentative Five-Stage Roadmap

1. 계산 정확도와 point-in-time 계약
2. 개별주 loader·월별 가치평가 엔진
3. 기업 검색·자료 준비 상태·선택 종목 수집 action
4. Nasdaq 화면을 미국 개별주 화면으로 교체
5. actual QA·문서 정렬·구현 커밋

상세 TDD task와 파일별 구현 순서는 written spec 승인 후 `superpowers:writing-plans`로 작성한다.

## Stop Condition For This Design Commit

- 승인된 설계를 `DESIGN.md`와 task handoff 문서에 고정한다.
- 모순·누락·범위 확대 여부를 자체 검토한다.
- 구현 코드는 변경하지 않는다.
- 사용자가 written spec을 검토하고 승인할 때까지 상세 구현 계획과 코딩을 시작하지 않는다.
