# Risks

- React/fallback 제목 계층 drift는 payload/source 계약 테스트로 보호한다.
- 일반 desktop iframe 폭에서 status badge와 제목이 겹치지 않음을 Browser QA로 확인했다. 극단적으로 좁은 embedded width는 기존 responsive rule 범위에 남는다.
- 전체 Overview 묶음의 unrelated Sentiment source assertion 1건은 이 task에서 수정하지 않았다.
