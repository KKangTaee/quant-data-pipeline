# Risks

- upstream enum을 사용자 문구로 바꾸면 registry/test/Gate contract가 깨질 수 있으므로 raw identity를 보존한다.
- 신규 상태가 추가될 때 first-read에 raw enum이 재노출되지 않도록 안전한 fallback 문구를 둔다.
- 한글 문구가 길어질 수 있으므로 desktop과 좁은 폭 카드 줄바꿈을 actual Browser에서 확인한다.
- 신규 status는 raw enum 대신 generic fallback으로 표시되므로, 의미가 확정되면 명시적 mapping과 contract test를 함께 추가해야 한다.
- Streamlit custom component 초기 frame-height warning 1건은 framework lifecycle 경고로 남아 있으며 이번 presentation 변경과 무관하다.
