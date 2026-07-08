# Design

## 문제 이해

Flow 4의 기존 구조는 카테고리와 기준 상세를 잘 보여주지만, 상태 의미가 기술 status 중심이다. 사용자는 다음 네 가지를 구분해야 한다.

- 통과: Final Review로 넘겨도 되는 기준
- 보강 후 재검증 필요: 데이터 / 근거 / 실행 gap을 해결해야 하는 기준
- Final Review 판단 필요: 자동 차단은 아니지만 최종 판단에서 확인할 기준
- 실전 사용 어려움: 현재 상태로는 포트폴리오 사용이 성립하기 어려운 차단 기준

## 구현 방향

1. `backtest_practical_validation_modules._check_status`
   - `Current=REVIEW`이면 `REVIEW`로 유지한다.
   - `Current=NEEDS_INPUT`이면 `NEEDS_INPUT`, `Current=NOT_RUN`이면 `NOT_RUN`, `BLOCK`이면 `BLOCKED`.

2. `backtest_practical_validation_workspace`
   - criteria card에 `outcome_key / outcome_label / outcome_detail`을 추가한다.
   - summary에 `criteria_repair_count`, `criteria_not_practical_count`를 추가한다.
   - overall outcome summary를 만들어 Flow 4 상단에서 바로 읽게 한다.

3. `backtest_practical_validation/page.py`
   - Flow 4 metric 문구를 기술 상태가 아니라 사용자 행동 기준으로 바꾼다.
   - group summary에 `Final Review 판단` 목록을 함께 노출한다.

## 비범위

- gate threshold 전면 재설계
- registry / saved JSONL rewrite
- provider ingestion 또는 DB schema 변경
- Final Review selected-route 저장 정책 변경
