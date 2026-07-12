# Design

- 투자 검토서 React에 Python이 만든 `decision_action` display model을 전달한다.
- React는 route 선택, 판단 사유 입력, submit intent만 맡는다.
- Python은 route guide, save evaluation, 자동 Decision ID, constraints / next action template, append를 계속 소유한다.
- Decision ID와 storage path는 사용자 화면에 노출하지 않는다.
- Practical Validation / robustness / investability raw detail은 이전 stage와 report audit trace에 남기고 Appendix shell은 제거한다.
- selected decision 운영 확인은 Operations > Portfolio Monitoring이 소유한다. non-select row는 append-only audit data로 보존한다.
