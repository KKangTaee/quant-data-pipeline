# Phase 35 Next Phase Preparation

## 현재 상태

- Phase 35 progress: `implementation_complete`
- Phase 35 validation: `manual_qa_pending`

Phase 35는 사용자 QA 대기 상태다.
QA가 완료되면 실전 후보 포트폴리오 선정과 운영 전 지침 확인까지의 기본 흐름은 닫을 수 있다.

## Phase35가 끝나면 갖춰지는 것

- `Backtest > Final Review`에서 최종 선정 / 보류 / 거절 / 재검토 판단을 기록한다.
- `Backtest > Post-Selection Guide`에서 final decision을 다시 읽어 투자 가능 후보 / 투자하면 안 됨 / 내용 부족 / 재검토 필요를 확인한다.
- selected final decision의 component, target weight, evidence, 리밸런싱 / 축소 / 중단 / 재검토 기준을 확인한다.
- Phase35는 추가 registry를 저장하지 않는다.
- live approval, broker order, 자동매매는 여전히 out of scope다.

## 다음 phase 후보

Phase35 QA가 완료된 뒤에는 아래 중 하나를 선택하는 것이 자연스럽다.

### 후보 A. Portfolio Monitoring / Paper-Live Tracking

- 선정된 포트폴리오 후보를 실제 기간별 성과 관찰 화면으로 추적한다.
- 실제 투자 전 paper/live monitoring chart, benchmark comparison, trigger breach를 본다.
- Phase35의 운영 전 기준을 실제 관찰 데이터와 연결한다.

### 후보 B. Live Approval Boundary

- 사용자가 실제 투자 승인 전 확인해야 할 최종 체크리스트를 만든다.
- 주문 실행은 하지 않되, 투자 금액, 계좌 제약, 실행 위험, tax/cost checklist를 확인한다.
- live approval과 broker order의 경계를 문서와 UI에서 명확히 나눈다.

### 후보 C. Portfolio Construction Quality Upgrade

- 후보 조합의 correlation, turnover, capacity, concentration, cost estimate를 더 정량화한다.
- 현재 Phase31~35의 validation / final guide를 더 강하게 만든다.

## 권장 방향

Phase35 manual QA가 끝나면 바로 주문 / 자동매매로 가기보다,
먼저 `Portfolio Monitoring / Paper-Live Tracking`을 검토하는 것이 좋다.

이유:

- 사용자가 이미 최종 후보와 운영 전 기준을 확인할 수 있게 되었으므로, 다음 병목은 "실제로 지켜보면 어떤가"다.
- live approval 전에 paper/live tracking 기간을 거치면 과최적화나 데이터 문제를 더 잘 발견할 수 있다.
- broker order를 만들기 전에 monitoring과 trigger breach 체계가 있어야 한다.

## 명확한 out of scope

다음 phase를 열더라도 아래는 별도 승인 없이는 만들지 않는다.

- 실제 주문 생성
- broker API 연결
- 자동매매
- 수익 보장 표현
- 사용자의 투자 금액을 자동 결정하는 기능

## QA gate

Phase35는 아래가 확인되면 closeout 가능하다.

- Post-Selection Guide가 추가 저장 없이 Final Review record를 읽는지
- 투자 가능 / 투자하면 안 됨 / 내용 부족 / 재검토 필요가 명확히 보이는지
- `FINAL_INVESTMENT_GUIDE_READY`가 정상 조건에서 보이는지
- live approval / order disabled 경계가 유지되는지
- 문서가 "실전 후보 포트폴리오 선정 + 운영 전 지침 확인"까지 갖춘 상태로 읽히는지
