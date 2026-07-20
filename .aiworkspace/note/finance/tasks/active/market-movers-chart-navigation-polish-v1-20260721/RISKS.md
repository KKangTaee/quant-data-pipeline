# Risks

Last Updated: 2026-07-21

- pointer drag와 hover는 pointer capture 및 active-point 계산을 함께 사용하며 자동 source/build contract는 통과했다.
- point당 최소 폭과 label format은 구현됐으나 실제 39/40개 분기의 시각 겹침은 Browser QA가 남아 있다.
- Streamlit iframe 내부 overflow가 바깥 페이지 세로 스크롤을 방해하지 않는지 좁은 화면에서 확인해야 한다.
- Browser localhost URL policy가 DOM 접근을 차단해 actual hover/drag/screenshot 증거를 만들지 못했다.
