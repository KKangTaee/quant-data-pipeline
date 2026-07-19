# Plan

## 이걸 하는 이유?

현재 Overview 심리 탭은 CNN 구성요소가 여러 영역에서 반복되고 AAII는 보조 정보처럼 보여, 시장 행동과 개인투자자 인식의 엇갈림을 빠르게 판단하기 어렵다. CNN과 AAII를 독립된 두 축으로 균형 있게 읽고 상세 근거와 그래프를 검산할 수 있는 1차 workflow로 개선한다.

## 전체 잠정 로드맵

1. CNN·AAII 판정, 균형 UI, 중복 제거, 그래프 분리
2. 장기 이력과 발표 당시 값의 축적·품질 점검
3. 예측 필요성이 유지될 때 독립 데이터 후보 검토
4. point-in-time 검증 후 1주·1개월 전망 제공 여부 결정

## 이번 범위

- 합성점수 없는 CNN 시장 행동 / AAII 투자자 인식 두 축
- 문장형 교차 판정과 확인 조건
- CNN·AAII 동등한 source card와 중복 없는 상세 근거
- CNN, AAII 응답, AAII Spread 그래프 분리
- focused service/payload/frontend regression과 Browser QA

## 승인된 시각 개편 follow-up

- Market Context·Futures Macro와 같은 서사형 Hero와 section hierarchy
- 동일한 너비·밀도의 CNN·AAII current evidence box
- source box 상단 colored rounded rail 제거
- CNN graph 고정 + `AAII 응답`/`AAII Spread` 전환 graph로 동시에 두 panel만 표시
- 원본 관측점의 실제 날짜 간격과 직선 연결, raw value hover
- 1W·1M 기간 card UI와 검증 상태 계약. 실제 확률 산출기는 장기 이력·point-in-time 검증 이후 별도 차수

## 중단 조건

- 신규 데이터, DB schema, ingestion job, 확률 예측으로 범위가 확대되면 구현을 멈추고 별도 차수로 재합의한다.
- 한 source 결측 상태에서도 근거 없는 종합 판정을 만들지 않는다.

Authoritative spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-cnn-aaii-v1-design.md`

Visual redesign spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-visual-redesign-design.md`

Implementation plan: `docs/superpowers/plans/2026-07-19-overview-sentiment-cnn-aaii-v1.md`

Visual redesign implementation plan: `docs/superpowers/plans/2026-07-19-overview-sentiment-visual-redesign.md`

CNN component status badge implementation plan: `docs/superpowers/plans/2026-07-20-overview-sentiment-cnn-status-badges.md`
