# Inflation Policy Yield Path Status

State: complete

## Current Position

- actual DB/Browser 재감사 기준 전체 5차 기능 복구 완료
- 현재 단위: reverse command JSON/component gate, Core PCE Q4/Q4, FOMC history,
  policy/joint rate path와 PIT forward EPS/equity production validation 완료 후 독립 침체 복구
- 사용자 승인: 순방향/역산 개념과 UI 시안 확인 완료
- 1차 actual source gate: 필수 source/series gap 0, `materialization_allowed=true`
- 독립성 gate: 기존 경제 사이클 결과·확률·artifact·snapshot 재사용 없음
- 실제 2026-08-03 replay: Core PCE 1개월/Q4/Q4, policy, joint rate, equity와 독립
  recession artifact `READY`; 6개 component와 통합 snapshot 모두 `READY`
- 동적 10년물 기준: active 4.58~4.65%, next overhead 4.79%; 4.7 고정 상수 없음
- 연말 Q4/Q4 5상태·3개 threshold·5개 다음 발표 민감도, 정책·저항 event probability,
  reverse·equity·12개월 침체 확률은 모두 각자의 actual validation을 통과해 공개
- Market Research 안의 `경기 국면 | 물가·정책 경로` 선택기, 순방향·역산·USER 기준
  저장·근거 disclosure가 DB-only read/command 경계로 연결됨
- 4차는 `index = next-year forward EPS × forward multiple`, measured EPS revision과
  사용자 AI uplift 분리, arbitrary user target과 비인과 조건부 연관 disclosure를 구현함
- Philadelphia Fed SPF 1,560개 확률 bin을 적재하고 2018~2025 독립 Q4 target 8개로
  선형 pool을 검증했다. CRPS 0.3613으로 prior-Q4 0.7823과 SPF-only 0.4217을 앞섰다.
- 공식 FOMC rate decision 86건·SEP 40개 release를 적재하고 December 동시결과 누수를
  제외해 다음 회의 78개, 연말 22개 evaluation origin에서 정책 baseline을 앞섰다.
  completed rate episode 110개와 resistance event 57개에서 검증한
  2,000개 공동 경로를 저장했고 4.79% 도달 역산 84.5%/1,690개 경로를 Browser에서 확인했다.
- FactSet Earnings Insight의 두 CY 라벨 검증 annual bottom-up EPS 80 release/160 rows를
  적재했다. 금리 PIT clock 수정 뒤 nested chronological ridge를 적용해 77 completed
  origin의 MAE 6.0751%가 best baseline 7.6929%보다 낮고 OOS 80% interval coverage
  0.875로 equity가 `READY`다.
- 독립 침체 모델은 138 completed origins/86 OOS folds/2 episodes에서 Brier 0.146934가
  base-rate 0.157162보다 낮고 calibration 0.024324로 `READY`다. 현재 확률은
  23.1484%, `WATCH/관찰`이며 기존 경제 사이클 결과를 사용하지 않는다.
- actual equity command는 사용자 6,400 조건을 동일 snapshot/artifact로 계산해
  `6,400 이하 2.6%`(exact 2.5719%)와 EPS×multiple 분해를 Browser에 표시한다.
- 4차 correctness gate: complete workbook vintage, origin별 rate revision, 공개시각 label,
  세 baseline+coverage, snapshot별 live scenario context, 별도 `joint_macro_paths`, 장 마감
  cutoff, path-order 불변 paired residual과 필수 scenario input 완전성을 고정
- 기존 4차 Browser QA는 unavailable 화면과 layout만 확인해 actual 결과 동작 완료 근거로
  사용하지 않는다.

## Next

phase 종료. 동일 refresh/materialization 경로의 정기 갱신과 검증 지표 drift만 운영한다.
