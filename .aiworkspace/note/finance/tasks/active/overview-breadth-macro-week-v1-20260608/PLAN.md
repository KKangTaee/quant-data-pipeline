# Overview Breadth / Macro Week V1 - 3차

## 이걸 하는 이유?

Overview Macro Context Cockpit 1차와 Data Health -> Ingestion Handoff 2차는 첫 화면에서 시장 context와 데이터 상태를 한 번에 보게 만들었다. 3차는 사용자가 깊은 탭으로 들어가기 전에 움직임이 넓게 퍼졌는지, 특정 그룹에 집중됐는지, 그리고 이번 주 가까운 macro / earnings 이벤트가 무엇인지 더 빠르게 판단하도록 돕는다.

## 전체 흐름

1. **1차 - Macro Context Cockpit V1**: Overview 상단에 futures, sentiment, events, movers, data health 요약을 연결했다. 완료.
2. **2차 - Data Health -> Ingestion Handoff V1**: Data Health 탭 상단에 due / stale / failed / missing 상태와 기존 refresh boundary를 연결했다. 완료.
3. **3차 - Breadth / Heatmap + Macro Week First Pass**: Sector / Industry와 Events 탭 상단에 compact breadth, concentration, macro week 요약을 추가한다. 현재 작업.
4. **4차 - Source / Provider Hardening 후보**: source confidence, partial / missing 이유, provider별 신뢰도를 더 명시하는 후보를 검토한다.
5. **5차 - Overview IA Closeout 후보**: 1~4차 결과를 바탕으로 Overview 탭 구조와 durable docs를 정리한다.

## 3차 범위

- 기존 DB-backed read model만 사용한다.
- 새 provider, DB schema, registry / saved JSONL write를 추가하지 않는다.
- Overview UI render 중 외부 provider, FRED, crawler를 직접 fetch하지 않는다.
- Sector / Industry 탭에 breadth participation, concentration, top group, compact heatmap context를 추가한다.
- Events 탭에 향후 14일 macro week lane과 FOMC / CPI / PPI / Employment / GDP / earnings cluster 요약을 추가한다.
- 이 context는 trade signal, Practical Validation PASS/BLOCKER, Final Review decision, monitoring signal이 아니다.

## 이번 차수에서 하지 않는 것

- Market breadth heatmap 본격 구현
- Events Quality / Macro Week View 본격 구현
- Ingestion 전체 개편 또는 Data Health -> Action Queue
- Why It Moved V2 저장 정책
- Futures provider hardening
- React / API frontend migration
- Candidate Ops IA 변경

## 완료 조건

- service/helper/UI contract가 focused tests로 보호된다.
- `py_compile`, focused service contract tests, UI boundary check, `git diff --check`를 통과한다.
- Streamlit Browser QA로 Overview 화면의 3차 요약 UI를 확인하고 screenshot을 남긴다.
- STATUS / NOTES / RUNS / RISKS와 root handoff log를 짧게 갱신한다.
