# Today Home React Workbench V2 Plan

Status: Complete
Last Updated: 2026-07-22

## 이걸 하는 이유?

V1 Today 홈은 시장맥락의 색상 토큰을 일부 사용했지만 실제 렌더러는 React가 아니라 `st.markdown(..., unsafe_allow_html=True)` 기반 HTML/CSS였다. 이 때문에 경제사이클·S&P 500 React workbench와 카드 깊이, 반응형 동작, 그래프 좌표, 상호작용 품질이 달랐고 포트폴리오 곡선의 주기와 의미도 화면에서 알 수 없었다.

## Goal

Today 본문 전체를 시장맥락 계열과 같은 React/Vite Streamlit component로 전환하고, 판단 근거의 위험 분류와 대표 포트폴리오의 일별 종가 기반 성과곡선을 명시적으로 읽을 수 있게 한다.

## Scope

- Today header, 시장 판단, 판단 근거, 다음 일정, 대표 포트폴리오, 다음 행동을 하나의 React workbench로 렌더링
- 경제사이클·S&P 500의 blue-gray surface, radius, shadow, spacing, responsive grid 계승
- 판단 근거 좌측 색상선 제거
- `지지 신호 / 중립 신호 / 주의 신호 / 자료 제한·엇갈림` 텍스트 라벨과 색상 병행
- 승인 시안 대비 전체 typography 1px 확대
- 포트폴리오 그래프의 일별·종가·최근 관측·비장중 의미, X/Y축, tooltip 명시
- React action event를 기존 Market Research / Market Movers / Portfolio Monitoring 경로에 연결
- component 불가 시 compact read-only fallback 유지

## Out Of Scope

- 기존 경제사이클·S&P 500·미국 개별주식 내부 기능 변경
- 포트폴리오 계산식, 저장 데이터, provider fetch, ingestion 실행 변경
- 주봉 또는 장중 데이터 신규 수집
- live trading, broker order, auto rebalance

## Roadmap

1. **설계 확정 (`1/4차`)**
   - React ownership, payload, 위험 라벨, 차트 좌표 계약을 문서화한다.
   - 완료 조건: 사용자 spec 검토 승인.
2. **React component와 contract 구현 (`2/4차`)**
   - 신규 Vite component, Python wrapper, payload 확장을 TDD로 구현한다.
   - 완료 조건: frontend test/typecheck/build와 Python contract tests 통과.
3. **Today page 통합 (`3/4차`)**
   - React primary renderer, navigation event, explicit fallback을 연결한다.
   - 완료 조건: 기존 상세 URL과 read-only 경계 회귀 없음.
4. **실제 Browser QA와 문서 정렬 (`4/4차`)**
   - desktop/760px/420px에서 layout, axis, tooltip, action을 확인한다.
   - 완료 조건: overflow/console error 없음, QA screenshot, durable docs sync, coherent commit.

전체 `4/4차`를 완료했다. 기존 상세 탭의 내부 기능은 변경하지 않았고, 최초 진입 Today 본문만 React workbench로 교체했다.

## Stop Condition

React component가 실제 기본 렌더러로 동작하고, 그래프가 `일별 저장 종가 기반 누적 수익률`임을 축·기간·tooltip으로 설명하며, 기존 Today 데이터·navigation·read-only 계약을 보존한 상태로 Browser QA까지 통과하면 종료한다.
