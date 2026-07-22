# Market Research Editorial Navigation V2 Plan

Status: Complete
Roadmap: 3/3 implementation stages complete
Last Updated: 2026-07-23

## 이걸 하는 이유?

V1 React 전환으로 Streamlit widget 느낌과 상태 불일치는 제거했지만, 큰 제목·family 카드·view 외곽 박스가 세 개의 독립된 가로 띠를 만들어 상단이 여전히 form 또는 prototype처럼 보인다. navigation 폭도 module 본문보다 좁아 시각축이 끊긴다.

Editorial Tabs 방향은 리서치 문서의 목차처럼 family를 얇은 text tab으로, local view만 compact pill로 표현해 본문을 더 빨리 시작하고 선택 위계는 유지한다.

## Roadmap

1. Editorial visual contract와 React/CSS 회귀 테스트를 확정한다.
2. header·family·view를 Editorial Tabs 구조로 구현하고 static bundle을 갱신한다.
3. 1280px·760px·420px actual Browser QA와 문서 closeout을 수행한다.

## Scope

- Market Research React header 높이와 typography 축소
- family card를 underline text tab으로 교체
- view rail의 외곽 surface 제거, active view compact pill 유지
- navigation 폭을 선택 module content axis에 정렬
- desktop/mobile responsive, focus, selected-state QA

## Out Of Scope

- 3-family/7-view 정보 구조와 label 변경
- Python payload/event/query/session/legacy normalization 변경
- module body, 데이터, DB, loader, provider 변경
- drawer, sticky rail, command bar, recent/saved research

## Stop Condition

- 상단에서 카드형 family와 view 외곽 박스가 제거된다.
- desktop header/navigation이 module 본문과 같은 축으로 정렬된다.
- mobile은 family 3열과 view 2열을 유지하며 clipping/overflow가 없다.
- 기존 7-view route, URL, fallback, keyboard/focus 계약이 회귀하지 않는다.

## Completion

- 1차: React header/family markup과 접근 가능한 family label 계약을 확정했다.
- 2차: Editorial Tabs CSS와 production static bundle을 적용했다.
- 3차: 1280px·760px·420px actual Browser QA, 7-view 전환, focus/overflow/console 검증과 문서 closeout을 완료했다.
