# Phase 35 Test Checklist

## 현재 상태

이 checklist는 아직 QA 대상이 아니다.

현재 Phase 35는 `active / not_ready_for_qa` 상태이며,
구현이 완료되면 이 파일을 실제 manual QA 항목으로 다시 작성한다.

## QA가 열릴 때 확인할 예정인 큰 영역

- `Backtest > Final Review` 또는 Phase35 operating guide surface에서 selected final review record를 읽을 수 있는지
- `SELECT_FOR_PRACTICAL_PORTFOLIO`가 아닌 final review record는 운영 guide 대상에서 제외되는지
- 리밸런싱 / 중단 / 축소 / 재검토 기준이 사용자가 이해할 수 있게 보이는지
- operating guide가 live approval / order instruction과 분리되어 보이는지
- 저장 또는 기록이 필요하다면 append-only이고 기존 final decision registry를 덮어쓰지 않는지

## 한 줄 판단 기준

Phase 35 QA는 구현 완료 후,
**최종 선정 후보가 주문이 아니라 운영 가능한 기준표로 바뀌었는지**를 확인하는 방향으로 작성한다.
