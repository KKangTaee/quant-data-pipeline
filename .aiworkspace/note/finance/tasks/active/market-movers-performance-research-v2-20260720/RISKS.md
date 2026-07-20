# Risks

- React local selection과 Python selected research가 일시적으로 다를 수 있으므로 stale research를 다른 symbol에 표시하면 안 된다.
- group context lazy event가 control rerun과 충돌하면 반복 rerun이 생길 수 있다.
- monthly market-date aggregation query는 index/access path를 별도 최적화하지 않으면 사용자가 월간을 처음 열 때 여전히 느릴 수 있다.
- 뉴스 provider metadata는 불완전하고 session-only이므로 원인 판정으로 표현하면 안 된다.
- financial 40-point bar chart는 좁은 폭에서 label/hover density가 높아질 수 있다.
- ResizeObserver callback loop를 막기 위해 height 변화가 있을 때만 Streamlit frame update를 보내야 한다.
- registry/saved/run-history와 기존 QA image는 사용자/local artifact이므로 stage하지 않는다.
- actual Browser에서 selected research mismatch, repeat rerun, frame-height 잘림, console error는 재현되지 않았다.
- monthly breadth 첫 요청은 기존 market-date aggregation query 비용 때문에 daily보다 여전히 느릴 수 있으며, DB index/query 최적화는 별도 data-performance task가 필요하다.
- external news/SEC metadata는 session-only 보조 링크이며 원인 판정·본문 수집·durable persistence로 확장하지 않았다.
- explicit data refresh는 session projection과 600초 cached DB read model을 함께 비운다. 단순 화면 새로고침은 cache를 다시 읽되 마지막 수동 데이터 갱신 시각을 바꾸지 않는다.
