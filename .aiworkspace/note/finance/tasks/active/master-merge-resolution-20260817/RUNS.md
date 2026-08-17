# Master Merge Resolution Runs

- 2026-08-17: merge metadata, 단일 unresolved `ROADMAP.md`, base/ours/theirs와 양쪽 task 상태를 확인했다.
- 2026-08-17: Sentiment 3차 관측 변화와 Futures Macro 재가격화·비예측 경계를 함께 보존해 충돌을 수동 조정했다.
- 2026-08-17: final React root와 durable docs를 대조해 이전 예측 gate 표시 문구를 현재 primary UI 계약으로 정렬했다.
- 2026-08-17: 현재 worktree `.venv`에는 pytest/pip가 없어 incoming을 만든 sibling `sub-dev`
  runtime으로 현재 source를 검증했다. Futures Macro 12개 test file은 `157 passed`,
  `15 subtests passed`, dependency deprecation warning 3건이었다.
- 2026-08-17: 변경 service-contract 5개 중 일봉 collector를 마지막 호출로 가정한 1건이
  5분봉 추가 호출 때문에 실패했다. interval=`1d` call을 명시적으로 고른 뒤 `5 passed`를 확인했다.
- 2026-08-17: 네 Python module compile과 `npm ci --offline` 기반 React production build
  180 modules가 통과했고 기존 static asset hash와 동일하게 재생성됐다.
- 2026-08-17: current worktree를 8517에서 실행해 Futures Macro 재가격화·1D/5D/20D,
  예측 gate 부재, Sentiment 1W/1M, Watch guide 부재를 확인했다. 두 component 모두
  clientWidth=scrollWidth=1109, console warning/error 0이었다.
- 2026-08-17: conflict marker, unresolved index, diff whitespace와 protected artifact staging을
  최종 확인했다. Browser screenshot은 generated artifact로 남기고 stage하지 않았다.
