# Risks

Last Updated: 2026-07-21

- pointer drag와 hover가 같은 gesture를 공유하므로 drag 임계치와 pointer capture가 필요하다.
- 많은 X축 label이 다시 겹치지 않도록 point당 최소 폭과 label format을 함께 검증한다.
- Streamlit iframe 내부 overflow가 바깥 페이지 세로 스크롤을 방해하지 않는지 좁은 화면에서 확인한다.
