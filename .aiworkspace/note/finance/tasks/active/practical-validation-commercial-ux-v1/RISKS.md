# Risks

## 2026-05-30

- Streamlit custom CSS는 theme별 색상 대비가 흔들릴 수 있어 Browser QA로 dark theme 가독성을 확인해야 한다.
- Evidence board를 접힘 / 탭 구조로 낮춰도 raw evidence 접근성은 유지해야 한다.
- 현재 구현은 Streamlit HTML/CSS helper 기반이므로 완전한 design system은 아니다. 다만 raw table 우선 노출을 줄이고 gate / action 판단 우선순위를 높이는 1차 상용 UX pass로 본다.
- 2차 shell은 dark workbench 톤을 강하게 적용하므로 light theme에서 대비를 다시 확인해야 할 수 있다. 이번 QA는 현재 local theme 기준으로 수행한다.

## 2026-05-31

- 현재 Portfolio Validation closeout 기준으로 치명적 미해결 risk는 없다.
- 남은 UX risk는 Streamlit 기반 shell의 theme / viewport 다양성이다. 다음에 다시 손볼 때는 desktop / mobile viewport별 step surface와 tab overflow를 한 번 더 보면 된다.
- 저장-only row와 Final Review 후보 노출 분리는 구현 / 문서 모두 맞췄지만, 향후 waiver 또는 수동 override가 생기면 `Gate 통과 후보만 Final Review source picker에 노출` 원칙을 다시 검토해야 한다.
