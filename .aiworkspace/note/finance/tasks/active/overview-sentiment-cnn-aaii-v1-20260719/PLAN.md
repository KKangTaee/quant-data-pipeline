# Plan

## 이걸 하는 이유?

현재 Overview 심리 탭은 CNN 구성요소가 여러 영역에서 반복되고 AAII는 보조 정보처럼 보여, 시장 행동과 개인투자자 인식의 엇갈림을 빠르게 판단하기 어렵다. CNN과 AAII를 독립된 두 축으로 균형 있게 읽고 상세 근거와 그래프를 검산할 수 있는 1차 workflow로 개선한다.

## 전체 잠정 로드맵

1. CNN·AAII 판정, 균형 UI, 중복 제거, 그래프 분리
2. 장기 이력과 발표 당시 값의 축적·품질 점검
3. 저장된 실제 관측을 이용한 1W·1M 기간별 심리 변화 제공
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

## 승인된 3차 범위

- `기간별 심리 경로`의 반복 unavailable 화면을 `기간별 심리 변화`로 교체
- 1W: CNN 최근 5개 관측 간격, AAII Spread 최근 1개 주간 관측 간격
- 1M: CNN 최근 20개 관측 간격, AAII Spread 최근 4개 주간 관측 간격
- source별 시작값·현재값·변화량·실제 날짜와 두 축 관계의 유지/전환 표시
- 같은 관측일은 최신 `collected_at` version을 사용하고 최신 값·날짜 근거가 불완전하면 source별 fail-closed
- 기존 전망 publication gate와 확률 비공개 정책 유지
- 신규 provider, DB, ingestion, estimator는 3차 범위에서 제외

## 중단 조건

- 신규 데이터, DB schema, ingestion job, 확률 예측으로 범위가 확대되면 구현을 멈추고 별도 차수로 재합의한다.
- 한 source 결측 상태에서도 근거 없는 종합 판정을 만들지 않는다.

Authoritative spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-cnn-aaii-v1-design.md`

Visual redesign spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-visual-redesign-design.md`

Implementation plan: `docs/superpowers/plans/2026-07-19-overview-sentiment-cnn-aaii-v1.md`

Visual redesign implementation plan: `docs/superpowers/plans/2026-07-19-overview-sentiment-visual-redesign.md`

CNN component status badge implementation plan: `docs/superpowers/plans/2026-07-20-overview-sentiment-cnn-status-badges.md`

Period change 3차 spec: `docs/superpowers/specs/2026-08-11-overview-sentiment-period-change-v3-design.md`

Period change 3차 implementation plan: `docs/superpowers/plans/2026-08-11-overview-sentiment-period-change-v3.md`
