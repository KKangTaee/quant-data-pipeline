# Market Research Top Navigation Visual Polish V1 Notes

Status: Active
Last Updated: 2026-07-22

## Confirmed Decisions

- core navigation은 상단 compact rail을 사용한다.
- 좌측 drawer/off-canvas는 이번 task에 넣지 않는다.
- 3-family/7-view IA, URL/session state, renderer/data boundary는 유지한다.
- page-global 공용정보를 다시 추가하지 않는다.
- sticky navigation은 initial implementation이 아니라 actual QA 이후 별도 판단이다.

## Visual Reference

- conversation inline mockup에서 family 전환과 view 선택 상태를 확인했다.
- mockup의 핵심은 header 축소, quiet primary rail, selected-family label을 가진 bounded secondary surface, module start 연결이다.
- inline visualization은 product source artifact가 아니며 app asset으로 복사하지 않는다.

## Preservation Notes

- dirty registry, run history, research bundle, 기존 QA image는 stage하지 않는다.
- module React/Vite assets와 data calculation은 변경 대상이 아니다.
