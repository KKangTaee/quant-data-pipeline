# Overview Market Movers Redesign V2 1차

Status: Active
Last Updated: 2026-06-29

## 이걸 하는 이유?

기존 Market Movers 개선은 데이터 기능은 늘었지만 화면 언어와 첫 인상이 여전히 prototype / diagnostic UI처럼 보였다. 사용자는 변동 종목을 빠르게 찾고, 왜 볼지 맥락을 확인하고, 자료 상태를 덜 헷갈리게 판단해야 한다.

## 1~6차 Roadmap

| 차수 | 목적 | 완료 조건 |
| --- | --- | --- |
| 1차 | 금융앱식 정보 구조 / 용어 reset | `변동종목 작업대`, `탐색 모드` 같은 내부 용어가 빠지고 `상승`, `하락`, `거래량`, `이상 거래량`, `섹터` 기준으로 읽힌다. |
| 2차 | 상위 변동종목 tape / list visual 재구성 | metric-card가 아니라 compact market list / tape 중심으로 상위 변동 종목이 먼저 보인다. |
| 3차 | 가격 / 거래량 chart workspace 재구성 | 선택한 랭킹 기준에 맞는 차트와 표가 하나의 분석 흐름처럼 연결된다. |
| 4차 | 섹터 / 시장 확산 시각화 재구성 | heatmap / sector strip / breadth 요약이 장식이 아니라 시장 확산 판단 보조로 읽힌다. |
| 5차 | 선택 종목 조사 flow 정리 | Why It Moved는 하단 부록이 아니라 선택 종목 detail / investigation pane 안에서 시작된다. |
| 6차 | Data trust / empty state / QA hardening | NASDAQ, stale, missing quotes 상태가 보조 UX로 명확하고 좁은 화면까지 QA 기준을 통과한다. |

## 1차 Scope

- 상단 command strip headline을 `변동 종목`으로 변경한다.
- 랭킹 선택 UI의 user-facing label을 `랭킹 기준`으로 바꾼다.
- 랭킹 기준 표시를 `상승`, `하락`, `거래량`, `이상 거래량`, `섹터`로 바꾼다.
- command strip의 현재 선택 항목을 `Mode` 대신 `보기`로 표시한다.
- 선택 종목 detail에서 `탐색 모드` 대신 `랭킹 기준`을 사용한다.

## Out Of Scope

- 새 DB schema / provider / UI direct external fetch.
- 자동 원인 판정, AI 요약, 매수 / 매도 / 추천 / 신호.
- 섹터 heatmap 전체 재설계와 tape/list 시각화 완성은 2차~4차로 넘긴다.
