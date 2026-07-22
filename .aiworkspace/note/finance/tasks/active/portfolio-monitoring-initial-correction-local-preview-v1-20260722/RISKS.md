# Risks

- 현재 범위의 미해결 기능 위험은 없다.
- native date input의 표시 형식은 브라우저 locale에 따라 달라지지만 저장되는 값은 ISO `YYYY-MM-DD`다.
- Streamlit custom component의 명시적 preview는 서버 왕복을 수행하므로 그 순간에는 rerun이 발생한다. editor recovery가 dialog와 현재 draft를 복원하는 것이 의도된 계약이다.
- 매수·매도 기록의 거래일 종가 자동 조회는 이번 변경 범위가 아니며 기존 동작을 유지한다.
