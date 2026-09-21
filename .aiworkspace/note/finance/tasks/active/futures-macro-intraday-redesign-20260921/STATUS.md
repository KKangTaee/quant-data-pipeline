# 선물 매크로 장중 변화 개편 상태

State: complete
Date: 2026-09-21

- 사용자 승인 1~5차 전체 완료, 5/5. 잔여 개발 차수 없음.
- 구현 branch: `codex/futures-macro-intraday`; 시작 commit `8ce476e5b`. 로컬 master에 fast-forward 통합 후 기존 8501 앱에서 제공.
- 소유 범위: 선물 매크로 탭과 필요한 수집/관측 경계. 경기국면·물가정책 화면/계산, Today/Monitoring의 일별 current 의미 보존.
- 검증: 관련 회귀 194 passed + 2 subtests, 유지 service 계약 35 passed, TypeScript/production build, 실제 DB/provider/Browser QA.
- 독립 리뷰 P2 두 건(휴장 중 stale 복구, 보조 자산 기준점 보강) 수정·회귀 완료.
- 실제 갱신 6.846초. 현재 read/compute/write 3회 0.447/0.439/0.437초. 전체 속도는 공급사 응답과 보강 필요량에 따라 변동.
- 기존 master에서도 실패하는 thermometer 계약 3개는 남아 있으며 RISKS/RUNS에 명시.
- 다음 진입: 실제 선물 매크로 화면, 이 task RUNS.md/DESIGN.md. 장중 과거 확률은 이번 범위 밖의 별도 요청 사항.
