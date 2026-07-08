# Risks

- 행 선택은 아직 Streamlit selectbox 기반이다. 표 row click 기반 drawer는 별도 frontend capability가 필요하다.
- Metadata fetch 버튼은 기존 service boundary를 유지하지만, 사용자가 눌러야만 실행된다.
- 원천 detail table은 expander 안으로 낮췄으므로 첫 화면에서 raw table이 바로 보이지 않는다.
