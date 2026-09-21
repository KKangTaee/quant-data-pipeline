# 실행 검증

2026-09-21 KST

- TDD: condition_results/previous_window/time_context 새 계약 24개 RED → 관련 windows와 43개 GREEN.
- reload 제거/fallback RED: 3 failed / 2 passed → UI 변경 후 56개 통과.
- 이전 동일 anchor·잘못된 이전 범위·비교 불가 0% 방지 회귀 추가 → 60개 통과. 첫 동일 anchor 테스트 fixture가 보합→상승임을 확인해 0.5%→1% 데이터로 바로잡음.
- `uv run --frozen --inexact --with pytest python -m pytest tests/test_futures*.py tests/test_overview_futures_macro*.py -q`: 204 passed, 15 subtests passed, 3 dependency deprecation warnings.
- 독립 리뷰 P2: divergent/one_flat 범주가 같아도 자산 방향이 바뀐 3사례가 UNCHANGED. 3 RED 확인 → 방향 비교 추가 → reading/condition/fallback 44 passed.
- React: npm ci, tsc --noEmit, npm run build 통과. 소스 prettier 정렬 후 tracked production bundle 재빌드.
- 실제 DB: 모든 가용 현재/이전 수익률을 endpoints의 100*(end/start−1)로 독립 재계산, 자체 달러를 고정 5개 통화 역평균으로 재계산하여 일치 확인.
- 실제 관측 예: 09-21 22:15 KST 마감대비 ES +0.6483%, NQ +1.0271%, ZN +0.2216%, 달러 +0.0754%; 직전 60분 ES −0.0354%, NQ −0.0967%, ZN −0.1178%, 달러 +0.0227%. 전자는 주가 상승/거시 혼합, 후자는 주가 하락/부담 동반으로 표시. 이후 실제값은 갱신에 따라 변함.
- Browser QA 8502: 최신 데이터 반영 7.853초, 버튼 복구/관측 21:55→22:15, 2구간 전환, prior 20:15→21:15 증거 펼침, reload 버튼 0개 확인.
- 반응형 1440/900/420px: iframe 가로 overflow 없음. 420px에서 가격 2열/확인 결과 1열. 실제 화면 screenshot 직접 확인.
- 캡처: main repo .playwright-mcp/futures-guided-desktop.png / futures-guided-mobile.png (generated, commit 제외).
- 브라우저 공통 shell의 기존 relative _stcore 404/경고는 선물 컴포넌트와 별도. 신규 컴포넌트 렌더 오류는 발견하지 못함.
- 최종 회귀(리뷰 수정 후): 207 passed + 15 subtests passed, 18.30초. Python compile, TypeScript tsc, production build, diff check 통과.
- Ruff 전체 정책에는 기존 broad-exception/timezone modernization 등의 경고가 있어 일괄 수정하지 않음. 변경 파일 import/F 오류 정리 및 `ruff check --select I,F` 통과.
- 리뷰 재확인: 자산별 방향 반전 3사례 CHANGED와 설명 확인, 추가 문제 없음, 코드 병합 가능 판정.
- 900px도 가로 overflow 없음(iframe 729=scrollWidth). 경기국면 이동이 economic-cycle URL을 설정함을 확인.
