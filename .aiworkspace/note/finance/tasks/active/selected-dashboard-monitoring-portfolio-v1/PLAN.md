# Selected Dashboard Monitoring Portfolio V1

## Goal

`Operations > Selected Portfolio Dashboard`를 Final Review 통과 후보를 담아 관찰하는 사용자 모니터링 포트폴리오 작업장으로 개편한다.

## 이걸 하는 이유?

현재 Selected Dashboard는 Final Review selected row를 바로 하나의 dashboard 대상으로 보여준다. 사용자는 실제 투자 후보를 여러 개의 개인 모니터링 포트폴리오로 나누고, 각 포트폴리오에 Final Review 통과 후보를 하나씩 담은 뒤 가상 시작일 / 종료일 / 초기자산 기준으로 성과와 drift를 추적하고 싶어 한다.

## Scope

- 새 dashboard 전용 saved JSONL에 사용자 모니터링 포트폴리오를 저장한다.
- 사용자는 포트폴리오 이름을 입력해 생성하고, 선택하고, 삭제할 수 있다.
- Final Review `SELECT_FOR_PRACTICAL_PORTFOLIO` 통과 후보를 포트폴리오에 하나씩 추가한다.
- 같은 포트폴리오 안에서 같은 selected decision은 중복 추가하지 않는다.
- 각 전략에 대해 가상 시작일 / 종료일 / 초기자산으로 monitoring scenario를 실행한다.
- 현재 가치, 누적 수익률, CAGR, MDD, benchmark 대비 성과, drift / 리밸런싱 검토 필요 여부, review signal을 표시한다.
- Live / Deployment Readiness는 마지막 optional preflight로 낮춘다.

## Out Of Scope

- live approval, broker order, account sync, auto rebalance.
- Final Review selected row 재작성.
- provider 직접 fetch 또는 DB schema 변경.
- monitoring log 자동 저장.
- 기존 saved mix 파일 의미 변경.
