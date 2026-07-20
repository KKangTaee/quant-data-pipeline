# Status

Status: Phase 4 Complete
Last Updated: 2026-07-20

## Roadmap

- [x] 1차 현행 감사
- [x] 2차 A안 설계 승인
- [x] 3차 data/read-model hardening
- [x] 4차 React one-shell implementation
- [ ] 5차 sector conditional outlook와 closeout

## Current Step

`MarketMoversDecisionWorkbench`가 ranking, sector/industry current flow, bellwether Top 3, quick research와 가격·재무·뉴스·공시 상세를 하나의 selected state로 연결한다. 전체 roadmap은 `4/5차`이며 다음은 별도 승인 범위인 5차 sector conditional outlook/OOS publication gate다.

## Completion Evidence

- React-first 경로는 legacy Streamlit ranking/breadth/research를 중복 렌더링하지 않는다.
- 재무 탭은 `보고 주기`, `재무 영역`, `재무 Factor`를 독립 제어하며 단일 factor chart/readout을 유지한다.
- 실제 989px component 폭에서 ranking/breadth는 약 `604/373px` 2열이며, 693px·353px에서는 1열과 horizontal overflow 0을 확인했다.
- generated QA screenshot은 `market-movers-react-one-shell-v1-desktop-qa.png`이며 commit하지 않는다.
