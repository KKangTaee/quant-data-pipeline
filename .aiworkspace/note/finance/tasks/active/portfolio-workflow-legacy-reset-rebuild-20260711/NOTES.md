# Notes

- 2026-07-11: 사용자의 `수집`은 provider 수집이 아니라 동일 포트폴리오를 1차 → 2차 → 3차로 다시 올리는 의미로 확인됐다.
- 구형 Practical Validation rows는 schema version 5이지만 `practical_validation_workspace`와 module `review_role`이 없어 Final Review fallback에서 REVIEW 10개가 모두 `final_decision_input`으로 보였다.
- 재구성은 display migration이 아니라 현재 workflow의 새 실행 결과를 만드는 방식으로 진행한다.
- 재구성 범위는 기존 Final Review 판단 6개 전체로 확정했다. 구형 단일 GRS 4개는 final decision에 보존된 replay contract를 사용하고, weighted mix 2개는 selection source의 original prefill contract를 사용했다.
- 동일 후보 의미를 유지하기 위해 stored-period replay를 사용했다. 새 판단 row는 schema v3이며 `monitoring_candidate=true`, live approval / order instruction은 계속 false다.
- 기존 `SAVED_PORTFOLIOS.jsonl` 2개 setup은 현재 6개 selected-route chain과 별개인 legacy reusable setup이므로 요청에 따라 활성 위치에서 제거했다.
- 롤백 사본은 `/tmp/quant-data-pipeline-backtest-dev-portfolio-reset-20260711T094422/`에 checksum manifest와 함께 남겼다.
