# Master Merge Resolution Risks

- 저장소 전체 pytest의 기존 Streamlit singleton order-dependency는 이번 통합 범위와
  분리된 공통 QA debt다. Risk-On과 Analysis Workspace를 한 process에 묶으면 9건이
  실패하지만 독립 process에서는 29건과 33건이 모두 통과한다.
- broad service contract에는 current source와 맞지 않는 Final Review/Practical Validation
  source-text assertion, Sentiment/Futures fixture baseline 등 18개 기존 실패가 남아 있다.
- workbench npm audit은 moderate 1건, high 1건을 보고한다. 자동 major fix는 이번
  merge-resolution 범위를 벗어나 적용하지 않았다.
- actual desktop Browser QA는 완료했다. 별도 responsive breakpoint QA는 이번 충돌 해결의
  필수 gap으로 보지 않는다.
