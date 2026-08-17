# Main-dev Master Merge Resolution Design

State: complete
Last Updated: 2026-08-17

## Resolution Policy

- current branch의 confirmed RTDSM state·unrestricted transition 계약을 현재 경제 사이클
  기준선으로 유지한다.
- incoming master의 Futures Macro 장중 closed-5m 관측, 재가격화 해석과 Sentiment 1W·1M
  실제 관측 변화는 독립 surface behavior로 보존한다.
- root log는 양쪽 완료 기록을 시간순으로 합치고 상세 검증은 이 task에 둔다.
- Roadmap과 state manifest는 chronology가 아니라 integrated current truth를 기록한다.
- registry JSONL, run history, QA 이미지와 run artifact는 merge commit에 포함하지 않는다.
