# Legacy Phase Backtest Reports

Status: Migration Pending
Last Verified: 2026-05-12

이 폴더는 기존 `.note/finance/backtest_reports/phase*/` 문서를 1차로 안전 이동한 위치다.

여기 있는 문서는 최종 보관 구조가 아니다. 후속 migration에서 아래 중 하나로 처리한다.

- `runs/YYYY/`로 이동
- `candidates/point_in_time/`로 승격
- `validation/`으로 이동
- `strategies/` hub/log에 흡수
- 중복이면 삭제

## 2차 처리 결과

`phase23`, `phase24`는 개발 검증 report 성격이 분명해서 `validation/`으로 이동했다.

- `phase23` quarterly contract smoke validation -> `validation/runtime/`
- `phase24` Global Relative Strength core runtime smoke -> `validation/runtime/`
- `phase24` Global Relative Strength UI replay smoke -> `validation/ui_replay/`

## Remaining Legacy Folders

- `phase13/`
- `phase14/`
- `phase15/`
- `phase16/`
- `phase17/`
- `phase18/`
- `phase21/`
- `phase22/`
