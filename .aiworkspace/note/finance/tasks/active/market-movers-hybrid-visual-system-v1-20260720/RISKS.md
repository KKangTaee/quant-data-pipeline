# Risks

- 시각 변경 중 기존 selected-state event 또는 payload schema를 건드리면 기능 회귀가 발생할 수 있다.
- component iframe 실제 폭이 브라우저 viewport보다 좁으므로 900px breakpoint를 실제 element width에서 검증해야 한다.
- decoration을 과도하게 추가하면 시장맥락의 읽는 흐름 대신 카드 모음으로 돌아갈 수 있다.
- purple/teal decorative accent 제거가 positive/negative semantic 구분을 약화시키지 않도록 값 색상은 유지한다.
- generated `.superpowers/` mockup과 기존 QA image, registry/saved/run-history 변경은 commit 대상이 아니다.
- actual Browser는 nested iframe의 하단 element click 좌표를 잘못 보정해 상세 조사 버튼 클릭 자동화가 안정적이지 않았다. 해당 UI의 DOM/accessibility/state contract와 기존 one-shell actual QA는 통과했지만, 브라우저 런타임이 개선되면 actual click 재확인이 좋다.
- first uncached Market Movers load는 약 40초가 걸릴 수 있다. 이번 presentation-only task에서는 service/DB 성능을 변경하지 않았다.
- sector conditional outlook과 industry outlook은 이번 visual task 범위가 아니다. historical episode/OOS publication gate 없이 예측 수치를 추가하면 안 된다.
