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
