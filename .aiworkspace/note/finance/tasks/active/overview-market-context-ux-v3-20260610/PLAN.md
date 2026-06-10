# Overview Market Context UX V3 Plan

## 이걸 하는 이유?

Market Context는 Overview의 첫 탭이 되었지만 첫 화면에서 갱신 버튼과 진단 표현이 요약보다 강하게 보인다.
이번 작업은 사용자가 `현재 시장 맥락을 어떻게 읽을지`, `무엇을 먼저 확인할지`, `자료가 오래됐으면 어디로 갈지`를 먼저 이해하게 만드는 실사용 UX 개선이다.

## 1차: 첫 화면 재구성

- 목적: 갱신 버튼보다 시장 맥락 요약과 다음 확인 순서가 먼저 보이게 한다.
- 변경 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`, 필요 시 `app/services/overview_market_intelligence.py`.
- 완료 조건: 첫 viewport에서 한 줄 요약, 자료 상태, 다음 탭 순서가 먼저 보이고 갱신은 보조 행동으로 내려간다.
- 다음 차수 연결: 2차에서 같은 영역의 문구와 상태값을 한국어 사용자 언어로 정리한다.

## 2차: 문구, 상태값, 카드 표현 정리

- 목적: `Source REVIEW`, `Freshness`, `in 1 days`, `confidence`, `review` 같은 기술/영문 혼합 표현을 줄인다.
- 변경 범위: cockpit read model과 renderer copy.
- 완료 조건: 데이터 상태 경고와 시장 위험 해석이 구분되고, 의미 없는 `-` 표시는 설명 가능한 문구로 대체된다.
- 다음 차수 연결: 3차에서 카드 위계와 다음 행동 안내를 강화한다.

## 3차: 카드 위계와 Deep Tab 연결 UX 개선

- 목적: 핵심 3개와 보조 3개의 정보 무게를 분리하고 Deep Tab 링크를 행동 안내로 바꾼다.
- 변경 범위: card model metadata, cockpit renderer, CSS.
- 완료 조건: 핵심 요약과 보조 근거가 구분되고, 다음 확인 순서가 실제 행동 안내로 보인다.
- 다음 차수 연결: 4차에서 실제 Streamlit 진입 / 라우팅 QA를 수행한다.

## 4차: 진입 / 라우팅 QA와 마무리

- 목적: Overview 진입 경험이 깨지지 않는지 확인한다.
- 변경 범위: 검증, Browser QA, task/root docs, commit.
- 완료 조건: compile, focused tests, diff check, Streamlit Browser QA, screenshot, `/overview` direct route 리스크 판단을 남긴다.

## Out Of Scope

- 새 provider, DB schema, registry/saved JSONL write.
- Overview render 중 provider/FRED 직접 fetch.
- run/job/raw row/status 중심 진단 패널 추가.
- Validation gate, Final Review decision, monitoring signal, broker order, auto rebalance.
