# Notes

- 원인은 `backtest_final_review_decision_brief.py`가 `proof_status`를 `display_value`와 `threshold_or_comparator`에 그대로 넣는 것이다.
- `backtest_realism_audit.py`의 상태 생성과 Gate 판정은 이번 범위에서 변경하지 않는다.
- React에서 문자열을 추측 변환하지 않고 Python-owned read model이 사용자 문구를 제공한다.
- known `proof_status` 9개를 명시적으로 매핑하고 unknown 상태는 `유동성 근거 상태 확인 필요`로 fail-safe 표시한다.
- `measured_value`는 raw enum을 유지하고 `display_value`와 `threshold_or_comparator`만 사용자 문구를 사용한다.
- current GTAA actual 화면의 상태는 `weak_source_or_proxy_liquidity_evidence`이며 `공식 자료가 부족하거나 일부 대체 지표를 사용함`으로 표시된다.
