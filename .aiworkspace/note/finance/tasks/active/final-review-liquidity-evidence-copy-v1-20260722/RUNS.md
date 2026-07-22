# Runs

- 첨부 이미지에서 `weak_source_or_proxy_liquidity_evidence`와 비교 기준 `official_fresh_capacity_evidence`의 first-read 노출을 확인했다.
- `rg`로 상태 생성 owner가 `app/services/backtest_realism_audit.py`, Level3 표시 owner가 `app/services/backtest_final_review_decision_brief.py`임을 확인했다.
- baseline Decision Brief `35 passed`, subtests 7개 통과.
- RED: label helper 부재와 기존 `유동성·capacity 근거` raw enum 표시로 신규 2개 test가 예상대로 실패했다.
- GREEN: 신규 2개 test와 상태별 subtest 9개 통과, Decision Brief 전체 `37 passed`, subtests 16개 통과.
- linked regression: Decision Brief + Final Review visual contract `45 passed`, refactor boundary `3 passed`.
- actual GTAA Level3: 제목·현황·설명·기준 한글 표시, raw enum first-read 미노출, 760px card `329/329`, page `760/760`, 1280px card `342/342`, page `1280/1280` scroll width 일치.
- console error 0. Streamlit framework가 component ready 전 frame height를 보낸 초기 경고 1건은 렌더링 이후 재발하지 않았고 앱 코드 오류는 아니다.
- QA screenshot은 `final-review-liquidity-evidence-copy-v1-qa.png` generated artifact로 남기고 stage하지 않는다.
