# Inflation Policy Workbench Plan

State: complete
Last Updated: 2026-08-02

## 이걸 하는 이유?

사용자가 반복해서 수행하는 `Core PCE 경로 -> FOMC 정책 경로 -> 10년물 동적
저항선`의 순방향 판단과 `목표 금리 구간 -> 필요한 정책·물가 경로`의 역산을 한
화면에서 수행할 수 있게 한다. 기존 경제 사이클 확률은 입력·보조값·fallback으로
사용하지 않는다.

## Scope

- DB에 저장된 inflation-policy snapshot의 독립 read model
- 자동 저항 기준과 사용자 저장 기준 조회·구분
- 사용자 기준 저장과 검증된 joint path만 사용하는 bounded reverse command
- `경기 국면 | 물가·정책 경로` 내부 선택기와 React workbench
- `LIMITED | NOT_AVAILABLE | FAILED` 공개 경계, 근거·신선도·과거 기준 표시
- Python/React 자동 검증, 실제 DB smoke, desktop/mobile Browser QA

## Out Of Scope

- 기존 경제 사이클 결과·확률·artifact 재사용
- 주식시장 숫자 스트레스 구현(4차)
- 침체 확률 구현(5차)
- provider 직접 호출, UI 확률 계산, 자동 매매 판단

## Execution

상세 RED/GREEN 단계와 파일 계약은
`docs/superpowers/plans/2026-08-02-inflation-policy-workbench-implementation.md`를
따른다. 코드 대조에서 누락이 확인된 resistance definition·exact artifact loader를
동일 DB-only 경계 안에서 먼저 추가한다.

## Completion

- 독립 service/command/transport tests 통과
- React test/typecheck/build 통과
- actual DB가 `LIMITED/NOT_AVAILABLE`을 승격 없이 표시
- desktop/420px에서 overflow·console error 없이 workflow 확인
- QA screenshot과 task/phase/doc sync 완료
