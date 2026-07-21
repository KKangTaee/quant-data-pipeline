# Portfolio Monitoring Reference Help Removal V1 Risks

- 패널만 제거하고 contextual catalog row를 남기면 dead configuration과 drift test가 남으므로 함께 제거한다.
- contextual row를 제거하면서 canonical Reference item까지 지우면 정보가 사라지므로 세 item과 destination을 명시적으로 보존한다.
- 다른 surface의 contextual help 적정성은 별도 UX audit 범위이며 이번 변경에 포함하지 않는다.
- 위 두 구현 위험은 ownership contract와 actual deep-link QA로 닫았다.
- 남은 범위 밖 위험: 다른 6개 surface의 contextual panel 필요성은 이번 task에서 평가하지 않았다.
