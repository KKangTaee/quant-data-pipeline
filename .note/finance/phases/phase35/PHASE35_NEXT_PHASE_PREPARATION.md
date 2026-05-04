# Phase 35 Next Phase Preparation

## 현재 상태

- Phase 35 progress: `implementation_complete`
- Phase 35 validation: `manual_qa_pending`

Phase35는 사용자 QA 대기 상태다.
QA가 완료되면 기본 후보 선정 workflow는 아래 단계까지 닫힌다.

```text
Portfolio Proposal -> Final Review -> 최종 판단 완료
```

## Phase35가 끝나면 갖춰지는 것

- `Backtest > Final Review`에서 단일 후보 또는 saved proposal을 최종 검토한다.
- validation, robustness, paper observation 기준을 한 화면에서 확인한다.
- 최종 선정 / 보류 / 거절 / 재검토 판단을 final decision registry에 남긴다.
- 저장된 final decision review에서 투자 가능 / 내용 부족 / 투자하면 안 됨 / 재검토 필요를 확인한다.
- 별도 후속 가이드 panel이나 추가 registry는 없다.
- live approval, broker order, 자동매매는 여전히 out of scope다.

## 다음 phase 후보

Phase35 QA가 완료된 뒤에는 아래 중 하나를 선택하는 것이 자연스럽다.

### 후보 A. Portfolio Monitoring / Paper-Live Tracking

- 최종 선정 후보를 실제 기간별 성과 관찰 화면으로 추적한다.
- benchmark comparison, trigger breach, review cadence를 운영 화면과 연결한다.

### 후보 B. Live Approval Boundary

- 주문 실행은 하지 않되, 실제 투자 전 승인 체크리스트를 만든다.
- 투자 금액, 계좌 제약, 실행 위험, 세금 / 비용 확인을 사람이 점검하게 한다.

### 후보 C. Portfolio Construction Quality Upgrade

- 후보 조합의 correlation, turnover, capacity, concentration, cost estimate를 더 정량화한다.
- 현재 validation / final review의 근거 품질을 높인다.

## 권장 방향

Phase35 manual QA가 끝나면 바로 주문 / 자동매매로 가기보다,
먼저 `Portfolio Monitoring / Paper-Live Tracking`을 검토하는 것이 좋다.

이유:

- 최종 후보를 골랐더라도, 실제 기간 관찰과 trigger breach 확인이 있어야 한다.
- live approval 전에 paper/live tracking 기간을 거치면 과최적화나 데이터 문제를 더 잘 발견할 수 있다.
- broker order를 만들기 전에 monitoring 체계가 있어야 한다.

## 명확한 out of scope

다음 phase를 열더라도 아래는 별도 승인 없이는 만들지 않는다.

- 실제 주문 생성
- broker API 연결
- 자동매매
- 수익 보장 표현
- 사용자의 투자 금액을 자동 결정하는 기능

## QA gate

Phase35는 아래가 확인되면 closeout 가능하다.

- Backtest workflow navigation이 Final Review에서 끝나는지
- 별도 후속 가이드 panel이 보이지 않는지
- Final Review saved decision에서 투자 가능 / 내용 부족 / 투자하면 안 됨 / 재검토 필요가 보이는지
- `Live Approval / Order` disabled 경계가 유지되는지
- 문서가 `Portfolio Proposal -> Final Review -> 최종 판단 완료`로 읽히는지
