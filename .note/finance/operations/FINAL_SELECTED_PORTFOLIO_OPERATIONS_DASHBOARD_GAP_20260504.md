# Final-Selected Portfolio Operations Dashboard Gap

## 목적

이 문서는 Phase 35 이후, 현재 finance Backtest workflow가 `실전 후보 포트폴리오 선정`까지 도달한 뒤 무엇을 더 만들어야 완성형 퀀트 운용 플랫폼에 가까워지는지 정리한다.

핵심 결론은 다음과 같다.

- 현재 시스템은 사용자가 전략을 백테스트하고, 검증하고, 최종적으로 실전 후보 포트폴리오를 선정하는 최소 흐름까지는 도달했다.
- 하지만 아직 선정 이후의 운용, 모니터링, 리밸런싱, 알림, 성과 추적은 별도 제품 영역으로 남아 있다.
- 다음으로 가장 우선순위가 높은 기능은 `최종 선정 포트폴리오 운영 대시보드`다.

## 현재 도달 지점

현재 사용자-facing workflow는 아래 단계로 읽는다.

```text
전략 실행
-> Real-Money 검증
-> Compare / 후보 비교
-> Candidate Review
-> Portfolio Proposal
-> Final Review
-> 최종 판단 완료
```

이 흐름의 목적은 `이 전략 또는 포트폴리오 조합을 실전 후보로 볼 수 있는가`를 판단하는 것이다.

Final Review에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장된 포트폴리오는 실전 후보로 선정된 상태로 볼 수 있다. 다만 이것은 live approval, broker order, 자동매매 실행을 뜻하지 않는다.

## 완성형 운용 플랫폼까지 남은 기능

| 축 | 필요한 기능 | 왜 필요한가 |
|---|---|---|
| 최종 선정 포트폴리오 운영 대시보드 | Final Review에서 선정된 포트폴리오 목록, 상태, 비중, 다음 확인일, 주요 trigger를 한 화면에서 확인 | 후보 선정 결과가 실제 운용 관리 대상으로 이어지려면 별도 home이 필요하다 |
| Paper / Live Monitoring | paper 추적, 가격 업데이트, 목표 비중 대비 현재 비중, 드리프트 확인 | 선정 이후에도 전략이 계속 유효한지 관찰해야 한다 |
| Rebalance Engine | 목표 비중과 현재 비중 차이, 리밸런싱 필요 여부, 매수 / 매도 후보 계산 | 실전 운용에서는 선정보다 반복적인 비중 관리가 중요하다 |
| Risk / Alert Framework | MDD, 변동성, 상관, 집중도, stop / re-review 기준, 경고 상태 | 포트폴리오가 위험 기준을 벗어나면 즉시 재검토해야 한다 |
| Performance Attribution | 수익률을 전략, 종목, factor, benchmark 대비로 분해 | 왜 성과가 좋거나 나쁜지 알아야 전략 유지 여부를 판단할 수 있다 |
| Execution / Order Workflow | 주문 전 체크리스트, 예상 체결 금액, broker export, 수동 주문 기록 | 자동매매 전이라도 실제 주문 실행을 체계화해야 한다 |
| Governance / Versioning | 전략 버전, 데이터 버전, 검증 결과, 승인 / 변경 이력 | 나중에 왜 이 포트폴리오가 선택되었는지 재현 가능해야 한다 |

## 가장 먼저 만들 필요가 큰 기능

### 최종 선정 포트폴리오 운영 대시보드

사용자 판단상, 다음 단계에서 꼭 만들어야 할 1순위 기능이다.

이 대시보드는 Final Review에서 끝난 판단 결과를 실제 운용 관리 화면으로 넘겨 주는 역할을 한다.

쉽게 말하면:

- Final Review는 `이 포트폴리오를 실전 후보로 선정할지`를 결정한다.
- 운영 대시보드는 `선정된 포트폴리오를 지금 어떻게 보고 있고, 다음에 무엇을 해야 하는지`를 보여준다.

## Phase 36 후보

추천 phase 이름:

```text
Phase 36. Final-Selected Portfolio Monitoring & Rebalance Operations
```

### 목적

Final Review에서 선정된 포트폴리오를 한 화면에서 관리하고, paper / live 전 운영 상태를 추적할 수 있는 최소 운영 대시보드를 만든다.

### 첫 범위

- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에서 최종 선정 records 읽기
- `SELECT_FOR_PRACTICAL_PORTFOLIO` 포트폴리오를 운영 대상 목록으로 표시
- 구성 전략 / ticker / target weight 요약
- 현재 상태 label 표시
  - `normal`
  - `watch`
  - `rebalance_needed`
  - `re_review_needed`
  - `blocked`
- 다음 확인일 / 다음 행동 표시
- 목표 비중 합계와 구성 누락 여부 확인
- paper tracking ledger 또는 final decision record와 연결된 근거 표시

### 후속 범위

- 현재 가격 기반 current weight 계산
- target vs current weight drift 계산
- 리밸런싱 필요 여부 자동 판단
- 리밸런싱 주문 초안 생성
- risk trigger / alert 표시
- 성과 attribution과 benchmark 비교

### 이번 phase에서 제외할 것

- 자동 주문 실행
- broker API live trading
- 세금 최적화
- 실제 투자금 자동 배분
- 법적 투자 권유 문구

## 우선순위 제안

1. 최종 선정 포트폴리오 운영 대시보드
2. Paper / live 가격 모니터링
3. 목표 비중 대비 current weight / drift 계산
4. 리밸런싱 필요 여부와 주문 초안
5. risk limit / alert / stop 기준
6. 성과 attribution
7. execution / broker 연동
8. governance / reporting

## 정리

현재 시스템은 `실전 후보를 찾는 최소 workflow`까지는 도달했다.

다음 핵심은 후보 선정 화면을 더 늘리는 것이 아니라, 선정된 포트폴리오를 실제로 계속 볼 수 있는 운영 화면을 만드는 것이다.

따라서 Phase 36을 연다면 `최종 선정 포트폴리오 운영 대시보드`를 첫 목표로 두는 것이 가장 합리적이다.
