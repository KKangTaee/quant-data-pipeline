# Portfolio Monitoring Diagnosis Grouping / Scroll V1 Notes

- current root dedup은 exact `root_id`만 합치므로 pairwise correlation과 per-item drawdown 의미 중복을 제거하지 못한다.
- 원본 fact/history는 보존하고 user-facing display projection만 grouping한다.
- desktop 내부 scroll과 mobile natural page scroll을 분리한다.
