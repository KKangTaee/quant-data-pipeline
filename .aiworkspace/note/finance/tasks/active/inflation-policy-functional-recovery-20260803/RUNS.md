# Inflation Policy Functional Recovery Runs

## 2026-08-03 Baseline

- `.venv/bin/python -m pytest <inflation-policy 관련 17개 파일> -q`
  - 결과: `190 passed`, 기존 edgar deprecation warning 3건
- `npm test -- --run` in `economic_cycle_workbench`
  - 결과: React `11 passed`
- actual Browser reverse click
  - 결과: `datetime is not JSON serializable`로 component render crash 재현

## 2026-08-03 Recovery Stage 1

- reverse datetime regression RED: raw `datetime` assertion 실패 확인
- component publication regression RED: overall `LIMITED`가 READY inflation까지 숨김 확인
- 수정 후 집중 Python `191 passed`, React `12 passed`, production build 성공
- actual DB reverse command transport: JSON 직렬화 성공, joint path 미존재로 정상
  `NOT_AVAILABLE`
- 기존 서버 Browser 재확인에서 legacy raw session result가 final payload에 붙는 추가
  crash를 재현하고 final transport-edge RED 테스트를 추가했다.
- 최신 코드 전용 `localhost:8502` actual Browser에서 역산 click 후
  `선택한 snapshot과 정확히 일치하는 검증 artifact가 없습니다.`가 정상 표시됐고
  error log 0건을 확인했다.

## 2026-08-03 Recovery Stage 2

- SPF collector/schema/loader RED→GREEN: 12 passed
- 실제 Philadelphia Fed workbook 수집: 1,560 rows, latest survey `2026Q2`, 각 horizon
  10 bins와 약 100% 합계 확인
- direct Q4 target audit에서 inconsistent base-vintage 음수값 재현 후 single-vintage
  target regression 추가
- 실제 Q4 validation: 31 origins, 8 target years, model/SPF weight 0.5/0.5,
  CRPS 0.3613 < prior-year baseline 0.7823, official SPF 0.4217, calibration 0.0484
- 집중 Python suite: 70 passed, 기존 edgar deprecation warning 3건
- React: 13 passed, production Vite build 성공
- actual materialization `2026-08-03T03:15:00Z --persist`: snapshot overall `LIMITED`,
  inflation `READY`, policy `LIMITED`, next release scenarios 5 rows
- actual Browser `localhost:8502`: 5상태/threshold/0.1~0.5 민감도 표시 확인
  - QA: `inflation-policy-core-pce-q4-ready-qa.png`
