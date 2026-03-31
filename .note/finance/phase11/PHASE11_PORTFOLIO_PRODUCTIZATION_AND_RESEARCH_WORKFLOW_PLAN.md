# Phase 11 Portfolio Productization And Research Workflow Plan

## 목적

- 여러 전략 실행 결과를 실제 사용자 중심 포트폴리오 워크플로우로 끌어올린다.
- 단발성 백테스트를 넘어서
  저장, 재사용, 비교, 구성, 해석 가능한 포트폴리오 surface를 정리한다.

## 현재 상태 메모

- Phase 11은 이제 실제 active phase다.
- current first-pass slice는
  **saved portfolio contract + load/rerun workflow**
  로 고정되었다.

## 왜 이 phase가 필요한가

현재 프로젝트는

- 데이터 수집
- 개별 전략 백테스트
- 비교 실행
- weighted portfolio builder first pass

까지는 갖추고 있다.

하지만 최종 제품 목표를 생각하면,
다음 단계는
**사용자가 여러 전략과 가상의 포트폴리오를 반복적으로 구성하고 비교하는 경험**
을 더 탄탄하게 만드는 것이다.

즉 Phase 11은
data / strategy foundation 이후의
**portfolio productization phase**
에 가깝다.

## 이번 phase의 핵심 질문

1. 사용자가 여러 전략 가중 조합을 어떻게 저장/재실행할 것인가
2. compare 결과와 weighted portfolio builder를 어떤 흐름으로 이어줄 것인가
3. 포트폴리오 결과에서 contribution / exposure / attribution을 어디까지 보여줄 것인가
4. 반복 연구 workflow를 어떤 단위로 저장할 것인가

## 범위 안

### A. saved portfolio workflow

- weighted portfolio preset 저장
- 다시 불러오기 / 수정 / 재실행
- strategy set + weight set + 기간 입력을 재사용 가능한 unit으로 정리

### B. compare-to-portfolio bridge

- compare 결과에서 선택 전략을 포트폴리오 빌더로 보내는 flow
- focused drilldown과 weighted builder 연결

### C. richer portfolio readouts

- contribution breakdown
- strategy-level exposure summary
- rebalance-level change summary
- risk / drawdown / benchmark 비교 강화

### D. research workflow surface

- saved run / saved portfolio / rerun payload 관계 정리
- operator / researcher가 반복 실험을 관리하는 방식 문서화

## 범위 밖

- live trading
- order management
- real brokerage integration
- full optimization engine

## 추천 구현 순서

1. saved portfolio data model 정의
2. compare-to-portfolio bridge 정리
3. saved portfolio UI first pass
4. contribution / exposure readout 강화
5. history / rerun / saved portfolio 연결
6. docs / checklist sync

## 완료 기준

- 사용자가 strategy 조합을 저장하고 다시 실행할 수 있음
- compare와 weighted portfolio builder가 더 자연스럽게 연결됨
- 포트폴리오 결과가 단순 equity curve를 넘어 해석 가능한 수준으로 확장됨

## 권고

Phase 11은
새 전략을 더 추가하는 phase라기보다,
**지금까지 만든 전략/비교/히스토리 surface를 실제 제품형 워크플로우로 묶는 단계**
로 두는 것이 좋다.

다만 실전 투자용 최종 검증 기준을 우선시한다면,
portfolio productization보다 먼저
`historical dynamic PIT universe` workstream이 선행될 수 있다.

즉:

- product/workflow 관점에서는 여전히 유효한 phase이지만
- real-money validation 관점에서는
  Phase 10(dynamic PIT universe) 이후에 열리는 편이 더 자연스럽다

함께 볼 준비 문서:

- `PHASE11_CURRENT_CHAPTER_TODO.md`
- `PHASE11_EXECUTION_PREPARATION.md`
- `PHASE11_TEST_CHECKLIST.md`
