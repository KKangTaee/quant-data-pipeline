# Phase 36 Final Selected Portfolio Monitoring And Rebalance Operations Plan

## 이 문서는 무엇인가

이 문서는 Phase36에서 `최종 선정 포트폴리오 운영 대시보드`를 어떻게 열고, 어디까지 구현할지 정리하는 계획 문서다.

Phase36은 Final Review 뒤에 또 다른 판단 저장 단계를 추가하는 phase가 아니다.
Final Review에서 이미 선정된 포트폴리오를 운영자가 다시 찾아보고, 현재 어떤 상태로 봐야 하는지 확인하는 Operations 화면을 만드는 phase다.

## 목적

- Final Review에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 포트폴리오를 한 화면에서 확인한다.
- 구성 전략 / ticker / target weight / benchmark / evidence / next action을 운영 관점으로 읽는다.
- live approval, broker order, 자동매매가 아니라는 실행 경계를 계속 고정한다.
- drift 결과를 Final Review review trigger와 함께 읽되, alert 저장이나 주문 지시로 오해되지 않게 한다.

## 쉽게 말하면

Final Review는 `이 포트폴리오를 실전 후보로 볼 것인가`를 결정한다.

Phase36 대시보드는 그 결정을 다시 저장하지 않고,
`선정된 포트폴리오를 지금 어디서 보고, 다음에 무엇을 확인해야 하는가`를 보여준다.

## 왜 필요한가

Phase35까지의 workflow는 아래처럼 최종 판단까지 닫혔다.

```text
Portfolio Proposal -> Final Review -> 최종 판단 완료
```

하지만 최종 판단이 끝나도 운영 관점에서는 아직 질문이 남는다.

- 선정된 포트폴리오가 몇 개인가
- 각 포트폴리오는 어떤 component와 target weight를 갖는가
- 어떤 benchmark와 evidence를 기준으로 선정됐는가
- 다음 확인일 / 다음 행동 / 관찰 trigger는 무엇인가
- 실제 승인 / 주문은 여전히 비활성화되어 있는가

이 질문을 Final Review 안에 계속 추가하면 Final Review가 다시 과도하게 커진다.
따라서 Phase36은 `Operations > Selected Portfolio Dashboard`라는 별도 운영 화면으로 분리한다.

## 이 phase가 끝나면 좋은 점

- 사용자는 최종 선정 포트폴리오를 Backtest workflow가 아니라 Operations에서 다시 찾을 수 있다.
- Final Review가 마지막 판단 단계라는 Phase35 경계가 유지된다.
- 선정된 포트폴리오의 target allocation, evidence, next action을 한 화면에서 읽을 수 있다.
- 이후 account holding 자동 연결, risk alert, rebalance review phase로 넘어갈 기준 surface가 생긴다.
- drift가 커졌을 때 어떤 review trigger를 같이 확인해야 하는지 read-only로 볼 수 있다.

## 이 phase에서 다루는 대상

직접 다루는 대상:

- `Operations > Selected Portfolio Dashboard`
- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
- Final Review selected decision row
- selected component / target weight / benchmark / evidence / paper observation snapshot
- dashboard status label
- drift alert / review trigger preview

직접 다루지 않는 대상:

- 새 final decision 저장소
- 새 candidate / proposal registry 저장
- 실제 계좌 보유 수량 자동 연결
- 주문 초안 생성
- alert registry 저장
- broker API
- 자동매매
- 실제 투자금 자동 배분

## 현재 구현 우선순위

1. 최종 선정 row read model
   - 쉽게 말하면: Final Review 기록 중 선정된 row만 운영 대상으로 바꿔 읽는다.
   - 왜 먼저 하는가: 대시보드는 새 저장소가 아니라 기존 최종 판단 기록을 읽어야 하기 때문이다.
   - 기대 효과: source-of-truth가 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` 하나로 유지된다.

2. Operations dashboard UI
   - 쉽게 말하면: 선정 포트폴리오 목록, 상태, target allocation, evidence, next action을 보여준다.
   - 왜 필요한가: Final Review 안에서 운영 화면까지 확장하면 workflow 경계가 다시 흐려진다.
   - 기대 효과: Final Review는 판단, Operations는 선정 이후 관찰이라는 역할 분리가 생긴다.

3. 문서 / QA 동기화
   - 쉽게 말하면: Phase36이 새 저장 단계가 아니라 read-only 운영 대시보드라는 점을 문서에 고정한다.
   - 왜 필요한가: 이후 phase에서 drift / rebalance / alert를 추가할 때 범위가 흔들리지 않게 하기 위해서다.
   - 기대 효과: Phase37 이후 작업이 자연스럽게 이어진다.

## 이 문서에서 자주 쓰는 용어

- 최종 선정 포트폴리오
  - Final Review에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장된 포트폴리오 또는 단일 후보다.
- 운영 대시보드
  - 선정 이후 상태, target allocation, evidence, next action을 읽는 화면이다.
- drift
  - 목표 비중과 현재 비중의 차이다. Phase36에서는 현재 비중 직접 입력, 현재 평가금액 입력, 수량 x 현재가 입력으로 read-only 계산한다.
- read-only dashboard
  - 기존 기록을 읽어서 보여주지만 새 판단 row나 주문 row를 저장하지 않는 화면이다.

## 이번 phase의 운영 원칙

- Final Review는 마지막 판단 단계로 유지한다.
- Phase36은 `Operations` 영역의 운영 화면으로 둔다.
- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`은 새로 만드는 파일이 아니라 Final Review가 이미 쓰는 최종 판단 원본이다.
- dashboard는 이 파일을 읽기만 한다.
- `rebalance_needed` status enum은 운영 row 상태와 상세 drift check 결과를 구분해서 쓴다.
- DB latest close 조회는 수량 x 현재가 입력을 돕는 보조값이며, 실제 계좌 보유 수량 자동 연결은 만들지 않는다.
- Drift Alert / Review Trigger Preview는 read-only 해석이며, alert row를 저장하지 않는다.
- live approval, broker order, 자동매매는 disabled 경계로 유지한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업. 최종 선정 포트폴리오 대시보드 first pass

- 무엇을 바꾸는가:
  - Final Review selected decision row를 dashboard row로 변환한다.
  - `Operations > Selected Portfolio Dashboard`를 추가한다.
  - status summary, filterable table, selected row detail, target allocation, evidence checks, disabled execution boundary를 표시한다.
- 왜 필요한가:
  - 최종 선정 후에도 사용자가 선정 결과를 운영 관점으로 다시 찾아볼 수 있어야 한다.
- 끝나면 좋아지는 점:
  - Final Review 이후 첫 운영 home이 생긴다.

### 두 번째 작업. price / holding 기반 drift 준비

- 무엇을 바꾸는가:
  - current weight 직접 입력 외에 current value와 shares x price 입력 계약을 추가한다.
  - shares x price 입력에서는 선택적으로 DB latest close를 불러와 현재가 입력을 보조한다.
- 왜 필요한가:
  - target weight만으로는 `rebalance_needed`를 자동 판단할 수 없다.
- 끝나면 좋아지는 점:
  - 실제 계좌 연결 없이도 평가금액이나 보유 수량 가정으로 current weight / drift를 확인할 수 있다.

### 세 번째 작업. drift alert / review trigger preview

- 무엇을 바꾸는가:
  - drift 결과를 운영 경고 없음 / 관찰 경고 / 리밸런싱 검토 경고 / 입력 확인 경고로 다시 읽는다.
  - Final Review에 남은 review trigger를 drift 결과 옆에서 확인한다.
- 왜 필요한가:
  - drift가 커졌을 때 단순 숫자만 보면 다음 행동이 불명확할 수 있다.
- 끝나면 좋아지는 점:
  - 사용자는 주문 없이도 어떤 component와 trigger를 다시 봐야 하는지 운영 관점으로 확인할 수 있다.

## 다음에 확인할 것

- Final Review에서 실제 selected row가 저장된 뒤 dashboard table과 detail이 기대대로 보이는지 확인한다.
- selected row가 없을 때 empty state가 자연스럽게 보이는지 확인한다.
- status 계산이 과하게 낙관적이지 않은지 확인한다.
- account holding 자동 연결과 risk alert를 다음 phase에서 어디까지 다룰지 결정한다.
- Phase36 alert preview를 저장 가능한 alert / review workflow로 확장할지 결정한다.

## 한 줄 정리

Phase36은 최종 선정 포트폴리오를 새로 판단하는 단계가 아니라, Final Review selected row를 운영 대시보드에서 읽고 관리하기 시작하는 phase다.
