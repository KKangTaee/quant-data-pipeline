# Risks

## Resolved / Watch

- 새 React 보드가 실행 UI처럼 보이면 React가 수집 실행을 소유하는 것으로 오해될 수 있다. 1차에서는 실행 버튼을 만들지 않고 기존 Python 수집 버튼을 유지했다.
- `no_action`을 과하게 표시하면 Final Review / Monitoring 판단 항목을 PV 메인 UI에 다시 반복할 수 있다. Browser QA에서 발견한 Final Review preview card는 module id와 label token exclusion으로 제거했다.
- Browser QA는 Flow 2 replay 이후 Flow 4가 보여야 하므로 재현 시간이 든다. 이번 QA는 local Streamlit replay 후 스크린샷으로 확인했다.
