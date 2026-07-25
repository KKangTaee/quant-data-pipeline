# Status

State: Complete
Roadmap: `3/3차`
Updated: 2026-07-25

## Completed

- 네 화면의 현재 header markup과 CSS 구조 비교
- A/B/C 시각 방향 제시
- 사용자 선택: `A. 공통 뼈대 + 가변 정보 슬롯`
- 우측 상태 카드의 좌측 컬러 테두리 제거
- 상태값 내부의 작은 점과 문구 색을 사용하는 V2 시안 승인
- 공통 `ResearchHeader` DOM 계약과 5개 adapter/component test 구현
- 경제사이클, 선물매크로, 심리, 일정의 기존 데이터 의미와 action dispatch를 유지한 채 공통 헤더로 전환
- 네 Vite production static bundle 갱신
- React DOM 9개, 관련 Python 33개, 네 production build 통과
- actual Browser QA에서 1280·760·420px 제목 계층, overflow, 중립 fact border, 상태 점 범위와 console error 0 확인

## Closeout

- 전체 roadmap `3/3차` 완료
- 계산, payload schema, DB / loader / collector는 변경하지 않았다.
- 기존 broad suite의 Backtest·AAII parser·구형 선물 thermometer 18개 실패는 사용자 승인에 따라 이번 task 회귀 범위에서 제외했다.
