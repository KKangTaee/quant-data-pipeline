# Notes

- 현재 criteria summary card에는 module id와 설명은 있지만 observed value / threshold / as-of가 없다.
- 같은 validation payload의 module별 audit row에는 Current / Evidence가 남아 있어 read model adapter로 일부 복구할 수 있다.
- Target / as-of가 실제로 없는 row는 값을 추정하지 않고 trace type으로 한계를 표시한다.
- Decision Cockpit의 policy/read model은 저장 route 계산에 필요하므로 UI 제거와 service 삭제를 구분한다.
- 최신 Distinct Strategy validation의 REVIEW 9개는 adapter 적용 후 `derived 8 / qualitative 1 / missing contract 0`으로 분류됐다.
- audit Target이 없는 경우 Evidence / Expected Check를 `판단 근거`로 표시하고 수치 threshold로 오해시키지 않는다.
- 다음 실험은 적용 가능한 패턴 중 salience 상위 3개만 표시하고 `바꿀 것 / 같게 둘 것 / 확인할 것`을 제공한다.
- 다음 실험은 설정 아이디어이며 자동 실행, 점수 변경, strategy variant 저장을 하지 않는다.
- Decision Cockpit의 read model은 권장 route / gate / blocker 계산에 계속 사용하고 standalone visible section만 제거했다.
- 최종 판단은 상태, 권장 판단, route 선택, 판단 사유, 저장 CTA를 한 section에 두며 기술 checklist와 ID는 접힌 상세로 내렸다.
