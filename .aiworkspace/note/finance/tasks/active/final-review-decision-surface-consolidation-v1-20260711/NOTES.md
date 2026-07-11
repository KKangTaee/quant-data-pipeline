# Notes

- 현재 criteria summary card에는 module id와 설명은 있지만 observed value / threshold / as-of가 없다.
- 같은 validation payload의 module별 audit row에는 Current / Evidence가 남아 있어 read model adapter로 일부 복구할 수 있다.
- Target / as-of가 실제로 없는 row는 값을 추정하지 않고 trace type으로 한계를 표시한다.
- Decision Cockpit의 policy/read model은 저장 route 계산에 필요하므로 UI 제거와 service 삭제를 구분한다.
