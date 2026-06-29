# Overview Source Confidence Catalog V1 - 4차

## 이걸 하는 이유?

1~3차로 Overview 첫 화면과 deep tab 상단에 market context, data-health handoff, breadth / macro week 요약이 생겼다. 4차는 이 context가 어떤 source / provider / collector 상태에 기대는지 더 가까운 위치에서 보여준다. 사용자가 futures, sentiment, events, movers를 context로 읽되, source freshness와 partial / review 상태를 투자 판단처럼 오해하지 않게 하는 것이 목적이다.

## 전체 흐름

1. **1차 - Macro Context Cockpit V1**: Overview 상단에 movers, breadth, futures, sentiment, events, data-health 요약을 연결했다. 완료.
2. **2차 - Data Health -> Ingestion Handoff V1**: Data Health 탭 상단에 due / stale / failed / missing 상태와 owning collection surface를 연결했다. 완료.
3. **3차 - Breadth / Heatmap + Macro Week First Pass**: Sector / Industry와 Events 탭 상단에 breadth / concentration, macro week lane을 추가했다. 완료.
4. **4차 - Source / Provider Confidence Catalog First Pass**: 기존 read model의 source, freshness, coverage, caveat, next check를 compact catalog로 노출한다. 현재 작업.
5. **5차 - Overview IA Closeout 후보**: 1~4차 결과를 기준으로 Overview IA, durable docs, 남은 후보를 정리한다.

## 4차 범위

- 기존 DB-backed read model만 사용한다.
- 새 provider, collector, DB schema, registry / saved JSONL write를 추가하지 않는다.
- Overview UI render 중 외부 provider, FRED, crawler를 직접 fetch하지 않는다.
- `build_overview_macro_context_cockpit()`가 이미 모은 snapshots에서 source confidence catalog를 만든다.
- catalog는 source, owner surface, status, freshness, caveat, next check, downstream tab을 보여준다.
- context-only boundary를 명시한다.

## 이번 차수에서 하지 않는 것

- futures provider 교체 / paid provider 도입
- provider reliability scoring을 DB에 저장
- Events quality 수집 정책 변경
- Ingestion Action Queue persistence
- Reference companion 본격 연결
- Candidate Ops IA 변경
- Practical Validation / Final Review / monitoring gate 연결

## 완료 조건

- service contract가 source confidence catalog의 상태 계산과 boundary copy를 보호한다.
- Overview cockpit renderer가 source confidence lane을 표시한다.
- `py_compile`, focused service contract tests, UI boundary check, `git diff --check`를 통과한다.
- Streamlit Browser QA로 source confidence lane을 확인하고 screenshot을 남긴다.
- STATUS / NOTES / RUNS / RISKS와 root handoff log를 짧게 갱신한다.
