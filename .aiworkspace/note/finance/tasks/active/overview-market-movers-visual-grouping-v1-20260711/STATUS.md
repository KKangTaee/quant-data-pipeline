# Status

- 2026-07-11: 사용자 승인 완료.
- 2026-07-11: 색상 누락 원인이 React `Sector Breadth`에 outer/lane background 규칙이 없는 점과 이전 수정 대상이 Ranking Board row였던 점으로 확인됐다.
- 2026-07-11: React/fallback Sector Breadth에 3% outer surface와 4% lane direction tint를 적용했다.
- 2026-07-11: 선택 종목 조사 divider, selector, React 조사 패널, 조사 단서 tabs, Research Snapshot, 기본 지표 그래프를 keyed Streamlit 부모 container 하나로 묶었다.
- 2026-07-11: Market Movers 80 tests, React production build, py_compile, diff check, desktop/mobile Browser QA를 통과했다.
- 2026-07-11: 후속 UI 정리로 선택 종목 조사 상단을 다른 주요 섹션과 같은 `kicker -> title -> detail` 헤더 계층으로 통일했다.
- 2026-07-11: 사용자 후속 설명으로 `모드별 상세 표 전체 높이로 보기`는 실제 위치 변경 대상임을 재확인했다. 이 표는 Sector Breadth가 아니라 Ranking Board의 모드별 원자료이므로 `랭킹 모드별 전체 상세 표`로 이름을 바꾸고 Ranking Board keyed container의 마지막 행으로 이동했다.
- 상태: Complete.
