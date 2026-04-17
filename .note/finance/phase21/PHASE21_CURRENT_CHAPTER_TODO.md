# Phase 21 Current Chapter TODO

## 상태
- `practical_closeout / manual_validation_pending`

## 1. Validation Frame Definition

- `completed` integrated validation scope 초안 확정
  - `Value`, `Quality`, `Quality + Value`에서 어떤 current anchor / alternative를 다시 볼지 고정
- `completed` 공통 validation frame 상세 확정
  - 기간
  - universe / cadence
  - benchmark / guardrail interpretation
  - 결과 기록 위치
- `completed` rerun pack naming 정리
  - family별 rerun report와 strategy log entry 이름을 통일
- `completed` Phase 18 closeout decision 반영
  - remaining structural second-slice backlog는 future option으로 남기고
    immediate next main phase는 integrated deep validation으로 고정
- `completed` representative portfolio bridge frame 고정
  - `Load Recommended Candidates` 기반 compare source
  - near-equal weighted bundle
  - representative saved portfolio naming 기준 정의

## 2. Annual Strict Family Integrated Rerun

- `completed` rerun pack execution order 고정
  - `Value -> Quality -> Quality + Value -> portfolio bridge`
- `completed` `Value` current anchor / lower-MDD alternative rerun
  - current practical point 유지 여부 확인
  - lower-MDD rescue 가능성 재점검
- `completed` `Quality` current anchor / cleaner alternative rerun
  - current practical point 유지 여부와 cleaner alternative의 comparator 성격 재확인
- `completed` `Quality + Value` strongest practical point / lower-MDD alternative rerun
  - strongest point 유지 여부
  - lower-MDD alternative의 실제 후보성 재판단

## 3. Portfolio Bridge Validation

- `completed` representative compare -> weighted portfolio rerun
  - weighted bundle가 candidate lane인지, 단순 operator artifact인지 재판단
- `completed` saved portfolio replay validation
  - representative saved portfolio scenario를 다시 확인
- `completed` portfolio-level interpretation 초안
  - 이후 phase에서 promotion / shortlist semantics를 어떻게 읽을지 메모

## 4. Reporting And Candidate Decision

- `completed` strategy hub / backtest log sync
  - `Value` first-pass rerun 결과를 durable report와 strategy log에 반영
  - `Quality` first-pass rerun 결과도 durable report와 strategy log에 반영
  - `Quality + Value` first-pass rerun 결과도 durable report와 strategy log에 반영
  - portfolio bridge validation 결과도 phase21 archive와 summary에 반영
- `completed` current candidate summary refresh
  - `Value` first-pass 기준 current anchor 유지 / alternative weaker-gate 판단 반영
  - `Quality` first-pass 기준 current anchor 유지 / cleaner alternative comparison-only 판단 반영
  - `Quality + Value` first-pass 기준 current anchor 유지 / `Top N 9` weaker-gate 판단 반영
  - portfolio bridge validation 기준 Phase 22 portfolio-level candidate construction 필요성 반영
- `completed` phase21 closeout 판단 문서화
  - 다음 phase가 portfolio-level construction인지
  - quarterly productionization인지
  - new strategy expansion인지 판단 근거 남김

## 5. Documentation Sync

- `completed` phase21 redesign kickoff
  - 기존 automation/plugin work를 main phase가 아닌 support track으로 재분류
  - main roadmap의 새 `Phase 21`을 integrated deep validation으로 재설계
- `completed` roadmap / doc index sync
- `completed` work log / question log sync
- `completed` phase21 plan / TODO / checklist 기준 정리
- `completed` phase18 closeout과 phase21 kickoff 연결 문맥 반영
- `completed` validation frame first work unit 문서화
- `completed` annual strict family rerun 3종 문서화
- `completed` portfolio bridge validation first pass 문서화
- `completed` manual QA terminology cleanup
  - `Validation Frame`을 shared glossary에 추가
  - Phase 21 plan의 current anchor / rescue candidate / deferred Phase 18 backlog 설명을 사용자 검수용 문장으로 정리
- `completed` manual QA rerun location clarification
  - Phase 21 checklist에서 family별 integrated rerun 확인 위치를 phase21 archive / family별 report / strategy hub / backtest log 링크로 명확히 정리
- `completed` manual QA decision criteria and backtest log readability cleanup
  - Phase 21 checklist에 유지 / 교체 / 보류 판단 기준 추가
  - annual strict family backtest log 3종에 최신 날짜순 기록 규칙과 최근 판단 요약표 반영
  - `Value`, `Quality + Value` 로그에서 뒤쪽에 밀려 있던 `2026-04-14` concentration-aware weighting 항목을 날짜순 위치로 이동
- `completed` manual QA portfolio bridge report location clarification
  - Phase 21 checklist에서 portfolio bridge 공식 rerun report와 UI 확인 위치를 분리해 설명
  - `Weighted Portfolio Builder`, `Weighted Portfolio Result`, `Saved Portfolios / Replay Saved Portfolio`의 역할을 체크리스트에 명시
- `completed` portfolio bridge report readability rewrite
  - `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`를 결론 / 용어 / 왜 이 조합을 썼는지 / 검증 흐름 / 결과 / 한계 / Phase 22 질문 순서로 재정리
  - `first pass`를 첫 검증으로 풀어 설명하고, 최종 포트폴리오 후보 확정 문서가 아니라 workflow 재현성 검증 문서라는 점을 명확히 반영
- `completed` portfolio bridge checklist alignment
  - Phase 21 checklist section 3을 새 portfolio bridge report 흐름에 맞춰 조정
  - 최종 winner 선정이 아니라 workflow 첫 검증인지, 3개 전략을 묶은 이유와 한계가 함께 설명되는지 확인하도록 체크 항목 보강
- `completed` full checklist readability cleanup
  - `PHASE21_TEST_CHECKLIST.md` 전체를 `무엇을 확인하나 / 어디서 확인하나 / 체크 항목` 구조로 재정리
  - section 3의 공식 report, UI 재현 경로, 읽는 순서, 체크 항목을 표와 순서형 안내로 정리
