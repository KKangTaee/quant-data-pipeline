# Master Merge Resolution Notes

- merge base 이후 current branch는 경제 사이클 v3 관측·전환·freshness를, master는
  inflation-policy 5/5 기능 복구와 Risk-On Momentum productionization을 추가했다.
- registry JSONL의 unstaged 수정과 run history/QA 이미지/run artifact는 사용자 또는
  local 소유 변경으로 판단해 건드리지 않는다.
- `economic_cycle_snapshot`의 제품 의미는 v3 observed-state 계약이 우선하며 기존
  probability JSON은 shadow/legacy 호환으로만 유지한다.
- inflation-policy artifact/snapshot은 경제 사이클 결과를 입력이나 fallback으로 쓰지 않는다.
- Risk-On Momentum은 master의 완료된 productionization이 current truth다. purpose catalog,
  Level1 maturity와 settings summary를 `production / 운영 전략`으로 일치시켰다.
- 경제 사이클 React는 v3를 기본 탭으로 유지하고, 물가·정책 payload가 있을 때만 독립
  `물가·정책 경로` 탭을 노출한다. Python이 payload 합성과 command validation/write를 소유한다.
- broad `tests/test_service_contracts.py`의 18 failures는 이번 충돌 파일과 무관한 기존
  Final Review/Practical Validation source-text, Sentiment/Futures baseline drift다.
- 공용 `fred_vintages` writer는 경제 사이클처럼 release metadata를 제공하지 않는
  호출이 기존 non-null `released_at`을 지우지 않도록 `COALESCE` UPSERT를 사용한다.
- Risk-On Quick은 의도적으로 macro-off 비교 실행을 생략하므로 빈 DataFrame 계약을
  반환하고, Practical Validation은 `Risk-On Momentum 5D` 표시명을 runtime key로 정규화한다.
