# Final Review Confirmed Review Flow V1 Design

## 현재 경계

- Python `backtest_evidence_read_model`이 score, gate, Level2 REVIEW disposition, save / Monitoring handoff를 만든다.
- Streamlit `backtest_final_review/page.py`가 후보 선택, 확정 session state, section render 순서를 소유한다.
- React investment report는 전달받은 payload를 표시만 한다.

## 구현 방향

- 후보 identity는 validation id와 source identity를 우선하는 stable key helper로 만든다. selectbox option은 key이고 `format_func`만 label을 표시한다.
- 확정 후보 key를 별도 session state에 저장한다. 현재 selector key와 확정 key가 다르면 downstream 판단 surface를 렌더링하지 않는다.
- 확정 시점에도 새 validation / provider / persistence 작업은 수행하지 않고 이미 만들어 둔 candidate context를 선택해 report read model만 조합한다.
- Level2 REVIEW service payload에 사용자 행동 결과를 명시하고 React와 fallback이 같은 다섯 역할 순서로 표시한다.
