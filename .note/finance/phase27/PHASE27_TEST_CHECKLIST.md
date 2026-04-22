# Phase 27 Test Checklist

## 목적

이 checklist는 Phase 27에서 추가하는 데이터 신뢰성 표시가
사용자가 실제 백테스트 결과를 검수할 때 이해 가능한지 확인하기 위한 문서다.

현재는 Phase 27 active 상태의 QA 초안이다.
Phase 27 구현 범위가 닫히면 최종 checklist로 다시 갱신한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Global Relative Strength preflight 확인

- 확인 위치:
  - `Backtest > Single Strategy > Global Relative Strength`
- 체크 항목:
  - [ ] 실행 전 `Price Freshness Preflight`가 보이는지
  - [ ] `Requested`, `Covered`, `Common Latest`, `Newest Latest`, `Spread`가 보이는지
  - [ ] stale / missing ticker가 있을 때 상세 정보가 접힘 영역에서 확인되는지
  - [ ] 이 preflight가 투자 판단이 아니라 데이터 가능 범위 점검이라는 점이 이해되는지

## 2. Latest Backtest Run Data Trust Summary 확인

- 확인 위치:
  - `Backtest > Single Strategy > Run Global Relative Strength Backtest > Latest Backtest Run`
- 체크 항목:
  - [ ] 결과 상단에 `Data Trust Summary`가 보이는지
  - [ ] `Requested End`와 `Actual Result End`를 비교할 수 있는지
  - [ ] `Effective Trading End`, `Common Latest Price`, `Newest Latest Price`, `Latest-Date Spread`가 보이는지
  - [ ] 결과 기간이 짧아졌을 때 데이터 문제인지 전략 문제인지 구분하는 데 도움이 되는지

## 3. Data Quality Details 확인

- 확인 위치:
  - `Latest Backtest Run > Data Trust Summary > Data Quality Details`
- 체크 항목:
  - [ ] excluded ticker가 있으면 어떤 ticker가 제외됐는지 보이는지
  - [ ] malformed / missing price row가 있으면 어떤 ticker와 날짜가 문제인지 보이는지
  - [ ] 해당 정보가 결과를 자동 보정했다는 뜻이 아니라, 원본 데이터를 확인하라는 뜻으로 읽히는지

## 4. Meta / history 연결 확인

- 확인 위치:
  - `Latest Backtest Run > Meta`
  - `Backtest > History > 해당 실행 record`
- 체크 항목:
  - [ ] `price_freshness`가 Meta에 남는지
  - [ ] `actual_result_start`, `actual_result_end`, `result_rows`가 Meta에서 확인되는지
  - [ ] history record를 다시 열었을 때 데이터 신뢰성 정보를 잃지 않는지

## 5. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase27/PHASE27_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase27/PHASE27_COMPLETION_SUMMARY.md`
  - `.note/finance/phase27/PHASE27_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 27 상태가 현재 구현 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 단계로 넘어가는 이유가 충분히 설명되어 있는지
  - [ ] next phase preparation에 다음 phase에서 실제로 할 작업이 쉽게 설명되어 있는지

## 한 줄 판단 기준

이번 checklist는
**백테스트 결과 숫자가 좋은가**가 아니라,
**그 숫자가 어떤 데이터 조건에서 나온 것인지 사용자가 먼저 확인할 수 있는가**
를 확인하는 문서다.
