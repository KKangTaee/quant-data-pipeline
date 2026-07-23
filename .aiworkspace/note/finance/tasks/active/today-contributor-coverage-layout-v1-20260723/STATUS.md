# Today Contributor Coverage / Review Layout V1 Status

Status: Complete
Roadmap: 2/2 stages complete
Last Updated: 2026-07-23

## Completed

- User screenshot and actual default portfolio payload were inspected.
- Confirmed that SOXX and QQQ are computable but removed by the top-2/bottom-2 projection policy.
- Confirmed that review-row spacing is caused by nested CSS grid stretch.
- User approved full contributor cards ordered by absolute impact and compact top-aligned review rows.
- `IMPLEMENTATION_PLAN.md`에 Python contributor completeness, React coverage/layout, Browser QA/docs의 3개 TDD task를 작성했다.
- Python EOD/live projection이 계산 가능한 모든 기여 값을 보존하고 절대 기여액 내림차순, 동률 symbol 오름차순으로 정렬한다. 0은 `neutral`이며 누락값은 0으로 만들지 않는다.
- React와 HTML fallback에 `전체 N개 · 영향 큰 순` 또는 `기여 계산 N/M개 · 영향 큰 순` coverage copy를 적용했다.
- `우선 확인`은 동일 높이 우측 패널 안에서도 상단 정렬되고 행 간격은 8px로 고정된다.
- Python 93개, React 19개, typecheck, production build, py_compile을 통과했다.
- actual default portfolio에서 AMD, TEM, RKLB, SOXX, QQQ 전체 5개 순서와 review 3행의 8px 간격을 확인했다. 1280/760/420 top·iframe overflow는 모두 0이고 browser console error도 0이었다.

## Scope Boundary

- DB schema, 수익률·기여 계산식, provider 수집, 장중 refresh cadence, Today fragment/rerun 경계는 변경하지 않았다.
- 생성 QA 이미지는 `today-contributor-coverage-layout-v1-qa.png`이며 커밋하지 않는다.
