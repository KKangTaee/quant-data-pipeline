# Portfolio Monitoring Tracking End UX Fix V1 Risks

- 요청일 이전 최신 저장 row가 오래된 경우 종료 평가일도 오래될 수 있다. 실제 적용일을 명시한다.
- 종료 기록을 기본 접힘으로 바꾸면 과거 항목 발견성이 낮아질 수 있다. count를 summary에 표시한다.
- Streamlit session의 last command가 유지되므로 dismiss는 React local presentation만 닫는다.
- Browser policy로 실제 종료 click과 responsive layout을 확인하지 못했다. 자동 회귀·typecheck·build는 통과했지만 visual QA gap은 남는다.
