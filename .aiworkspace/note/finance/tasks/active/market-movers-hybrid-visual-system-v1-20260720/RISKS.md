# Risks

- 시각 변경 중 기존 selected-state event 또는 payload schema를 건드리면 기능 회귀가 발생할 수 있다.
- component iframe 실제 폭이 브라우저 viewport보다 좁으므로 900px breakpoint를 실제 element width에서 검증해야 한다.
- decoration을 과도하게 추가하면 시장맥락의 읽는 흐름 대신 카드 모음으로 돌아갈 수 있다.
- purple/teal decorative accent 제거가 positive/negative semantic 구분을 약화시키지 않도록 값 색상은 유지한다.
- generated `.superpowers/` mockup과 기존 QA image, registry/saved/run-history 변경은 commit 대상이 아니다.
