# Risks

## 2026-05-30

- Streamlit custom CSS는 theme별 색상 대비가 흔들릴 수 있어 Browser QA로 dark theme 가독성을 확인해야 한다.
- Evidence board를 접힘 / 탭 구조로 낮춰도 raw evidence 접근성은 유지해야 한다.
- 현재 구현은 Streamlit HTML/CSS helper 기반이므로 완전한 design system은 아니다. 다만 raw table 우선 노출을 줄이고 gate / action 판단 우선순위를 높이는 1차 상용 UX pass로 본다.
