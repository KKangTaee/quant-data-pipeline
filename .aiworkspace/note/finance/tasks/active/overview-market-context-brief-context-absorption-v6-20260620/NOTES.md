# Notes

## Decision

`이벤트 일정`과 `자료 기준`은 전체 Market Context 신뢰도를 평가하는 독립 축이 아니다. 가격 움직임 / 섹터 확산 자체를 낮추기보다는, 이벤트 원인 해석 또는 장중 Futures/Macro 해석 범위를 제한하는 보조 정보다.

따라서 별도 `브리프 신뢰도` 섹션으로 보여주지 않고, 실제 시장맥락 결론으로 흡수한다.

## UX Interpretation

- `오늘의 시장 브리프`: 오늘 가격 움직임, 확산/집중, Futures/Macro 배경, 이벤트 배경을 결론 중심으로 보여준다.
- `이벤트 배경`: 가까운 이벤트나 추정 일정이 오늘 움직임의 직접 원인으로 볼 만큼 강한지 요약한다.
- `Futures/Macro 배경`: Futures 자료 제한이 있으면 장중 macro 설명을 보류한다.
- `근거: 자료 기준 / 출처 상태`: 왜 보류/제한인지에 대한 source / freshness / 보강 위치를 접힌 근거로 남긴다.

## Compatibility

`context_findings` / `next_checks`는 이전 task와 테스트 호환을 위해 payload에 남긴다. 기본 UI가 이를 action checklist나 별도 findings rail로 다시 표시하면 이번 V6 결정과 충돌한다.
