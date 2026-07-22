# Risks

- upstream enum을 사용자 문구로 바꾸면 registry/test/Gate contract가 깨질 수 있으므로 raw identity를 보존한다.
- 신규 상태가 추가될 때 first-read에 raw enum이 재노출되지 않도록 안전한 fallback 문구를 둔다.
- 한글 문구가 길어질 수 있으므로 desktop과 좁은 폭 카드 줄바꿈을 actual Browser에서 확인한다.
