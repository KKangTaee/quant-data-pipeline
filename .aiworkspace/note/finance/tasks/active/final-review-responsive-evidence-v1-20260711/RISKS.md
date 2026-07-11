# Risks

- 해소: compact 900px과 mobile 680px에서 CSS pixel 기준 가로 overflow 0을 확인했다.
- 해소: 공백이 적은 lifecycle evidence에 `overflow-wrap: anywhere`와 `word-break: break-word`를 함께 적용했다.
- 잔여: 실제 browser zoom은 OS / 브라우저 렌더링 비율에 따라 글자 rasterization이 달라질 수 있으나, layout 기준 viewport resize와 wrapping 계약은 검증했다.
