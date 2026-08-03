# Inflation Policy Yield Path Status

State: active

## Current Position

- actual DB/Browser 재감사 기준 전체 5차 중 2차 Core PCE까지 완료, 3~4차 functional
  recovery active, 5차 독립 침체 위험 모델 pending
- 현재 단위: reverse command JSON/component별 publication gate와 Core PCE Q4/Q4
  production validation 완료 후 FOMC history/policy/joint path 복구 진행
- 사용자 승인: 순방향/역산 개념과 UI 시안 확인 완료
- 1차 actual source gate: 필수 source/series gap 0, `materialization_allowed=true`
- 독립성 gate: 기존 경제 사이클 결과·확률·artifact·snapshot 재사용 없음
- 실제 2026-08-03 replay: Core PCE 1개월 및 Q4/Q4 artifact `READY`, 물가 component
  `READY`; 통합 snapshot은 policy/joint/equity가 남아 `LIMITED`
- 동적 10년물 기준: 당시 active 4.58~4.65%, next overhead 4.67%; 4.7 고정 상수 없음
- 연말 Q4/Q4 5상태·3개 threshold·5개 다음 발표 민감도는 실제 DB snapshot으로 공개;
  정책·저항 event probability는 `LIMITED`, reverse·equity·침체는 actual input/validation
  gate 때문에 `NOT_AVAILABLE`
- Market Research 안의 `경기 국면 | 물가·정책 경로` 선택기, 순방향·역산·USER 기준
  저장·근거 disclosure가 DB-only read/command 경계로 연결됨
- 4차는 `index = next-year forward EPS × forward multiple`, measured EPS revision과
  사용자 AI uplift 분리, arbitrary user target과 비인과 조건부 연관 disclosure를 구현함
- Philadelphia Fed SPF 1,560개 확률 bin을 적재하고 2018~2025 독립 Q4 target 8개로
  선형 pool을 검증했다. CRPS 0.3613으로 prior-Q4 0.7823과 SPF-only 0.4217을 앞섰다.
- actual DB에 official EPS vintage가 0건이므로 Shiller를 대체 사용하지 않고 equity
  확률을 숨김
- 4차 correctness gate: complete workbook vintage, origin별 rate revision, 공개시각 label,
  세 baseline+coverage, snapshot별 live scenario context, 별도 `joint_macro_paths`, 장 마감
  cutoff, path-order 불변 paired residual과 필수 scenario input 완전성을 고정
- 기존 4차 Browser QA는 unavailable 화면과 layout만 확인해 actual 결과 동작 완료 근거로
  사용하지 않는다.

## Next

3차 policy/joint path·4차 PIT forward EPS를 actual production 경로에 연결한다.
5차 침체 모델은 이 복구 뒤 별도 episode/OOS gate로 구현하며 기존 경제
사이클 확률을 재사용하지 않는다.
