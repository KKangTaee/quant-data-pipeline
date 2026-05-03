# Phase 34 Final Portfolio Selection Decision Pack Plan

## 이 문서는 무엇인가

Phase 34에서 만들 `Final Portfolio Selection Decision Pack`의 목적, 범위, 작업 단위를 정리하는 계획 문서다.

## 목적

- Phase 31~33에서 쌓은 portfolio risk, robustness / stress, paper tracking 근거를 한 화면에서 읽는다.
- 저장된 `Paper Portfolio Tracking Ledger` record를 최종 선정 검토 입력으로 사용한다.
- 후보나 proposal을 `선정`, `보류`, `거절`, `재검토` 중 어디에 둘지 명시적으로 판단하는 decision pack을 만든다.

## 쉽게 말하면

Phase 34는 "이제 이 포트폴리오를 실전 후보로 골라도 되는가?"를 묻는 단계다.

다만 이 단계도 broker 주문이나 자동매매가 아니다.
실제 돈을 넣기 직전, 백테스트 / 검증 / paper tracking / 사람의 판단을 모아서
최종 실전 후보로 선정할지, 더 볼지, 거절할지를 기록하는 단계다.

## 왜 필요한가

- Phase 33까지는 paper tracking 시작 조건과 관찰 기록을 남겼지만, 최종 선정 decision은 아직 없다.
- paper ledger가 `READY_FOR_FINAL_SELECTION_REVIEW`로 읽혀도, 그것은 "검토 가능"이지 자동 선정이 아니다.
- 최종 후보를 고를 때는 성과 숫자뿐 아니라 blocker, stress gap, paper tracking 상태, operator note를 같이 봐야 한다.
- live approval / 주문 지시와 최종 후보 선정 기록을 분리해야 위험한 오해를 줄일 수 있다.

## 이 phase가 끝나면 좋은 점

- 사용자는 저장된 paper ledger record를 기반으로 최종 실전 후보 검토 화면을 열 수 있다.
- 최종 선정 / 보류 / 거절 / 재검토 판단이 어떤 근거로 내려졌는지 남는다.
- Phase 35는 선정 이후 리밸런싱, 중단, 축소, 재검토 운영 기준을 이어받을 수 있다.

## 이 phase에서 다루는 대상

- `Backtest > Portfolio Proposal`의 저장된 Paper Tracking Ledger review surface
- `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`
- current candidate registry row
- Portfolio Proposal registry row
- Phase 31 validation snapshot
- Phase 32 robustness / stress snapshot
- Phase 33 paper ledger row와 `phase34_handoff`
- 새 final selection decision 저장소
  - 예상 위치: `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`

## 현재 구현 우선순위

1. Final decision 계약과 저장소 경계 정의
   - 쉽게 말하면: 최종 선정 판단 한 줄에 무엇을 저장할지 먼저 정한다.
   - 왜 먼저 하는가: 선정 / 보류 / 거절은 가장 중요한 operator decision이므로 저장 계약이 흔들리면 UI와 운영 가이드가 모두 흔들린다.
   - 기대 효과: final decision이 live approval이나 주문 지시와 섞이지 않는다.
2. Decision evidence pack 계산 기준 추가
   - 쉽게 말하면: paper ledger, validation, stress, blocker, operator note를 한 묶음으로 읽는다.
   - 왜 필요한가: 최종 판단은 CAGR / MDD 하나만 보고 내리면 안 된다.
   - 기대 효과: 사용자가 "왜 선정했는가 / 왜 보류했는가"를 재현할 수 있다.
3. Final decision UI 추가
   - 쉽게 말하면: 저장된 paper ledger record를 고르고, 선정 / 보류 / 거절 / 재검토 route를 선택한다.
   - 왜 필요한가: 최종 판단은 사람이 명시적으로 해야 하며 자동 저장되면 안 된다.
   - 기대 효과: Phase 34가 실제로 사용 가능한 검토 화면이 된다.
4. Saved final decision review와 Phase 35 handoff
   - 쉽게 말하면: 저장한 최종 판단을 다시 열어 보고, 선정 이후 운영 가이드로 넘긴다.
   - 왜 필요한가: 최종 후보 선정 이후에도 리밸런싱, 중단, 축소, 재검토 기준이 필요하다.
   - 기대 효과: Phase 35가 읽을 수 있는 운영 입력이 생긴다.

## 이 문서에서 자주 쓰는 용어

- `Final Portfolio Selection Decision Pack`: 최종 실전 후보로 선정할지, 보류할지, 거절할지, 재검토할지 판단하는 근거 묶음이다.
- `Final Decision`: 사람이 명시적으로 남기는 최종 검토 판단이다. live approval이나 주문 지시가 아니다.
- `Decision Evidence`: 백테스트 성과, validation, robustness / stress, paper tracking, operator note를 합친 판단 근거다.
- `Phase 35 Handoff`: 선정 이후 운영 기준 phase로 넘길 준비 상태다.

## 이번 phase의 운영 원칙

- live approval, broker order, 자동매매는 만들지 않는다.
- 최종 decision은 사용자가 명시적으로 저장할 때만 append-only로 남긴다.
- paper ledger record를 자동으로 최종 선정으로 승격하지 않는다.
- `선정`도 "실전 후보 선정"이지 "주문 실행"이 아니다.
- 보류 / 거절 / 재검토도 정상적인 결과로 취급한다.
- Phase 35 운영 기준은 이번 phase에서 완성하지 않고 handoff만 남긴다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업. Final decision 계약과 저장소 경계 정의

- final decision row에 필요한 필드를 정한다.
- source paper ledger, source candidate / proposal, decision route, evidence snapshot, operator reason을 분리한다.
- live approval / order instruction과의 경계를 문서와 helper 기준으로 고정한다.

### 두 번째 작업. Decision evidence pack 계산 기준 추가

- 저장된 paper ledger row를 읽어 최종 검토 가능 상태를 계산한다.
- Phase31 / Phase32 / Phase33 근거를 한 묶음으로 요약한다.
- blocker와 missing evidence를 다음 행동으로 읽히게 만든다.

### 세 번째 작업. Final decision UI 추가

- `Backtest > Portfolio Proposal` 또는 관련 review surface에서 final decision pack을 연다.
- 사용자가 `select`, `hold`, `reject`, `re_review` 중 하나를 명시적으로 고르게 한다.
- 저장 전 preview와 blocker 안내를 제공한다.

### 네 번째 작업. Saved final decision review와 Phase 35 handoff 정리

- 저장된 final decision record를 다시 읽는 surface를 만든다.
- Phase35 `Post-Selection Operating Guide`가 읽을 route와 next action을 남긴다.

## 다음에 확인할 것

- final decision 저장소 이름과 row schema가 기존 registry들과 섞이지 않는지 확인한다.
- `선정`이라는 단어가 live approval / 주문 지시로 오해되지 않는지 확인한다.
- 단일 후보와 proposal 모두 final decision input으로 자연스럽게 읽히는지 확인한다.

## 한 줄 정리

Phase 34는 검증과 paper tracking을 통과한 후보나 proposal을 최종 실전 후보로 선정 / 보류 / 거절 / 재검토하는 decision pack을 만드는 단계다.
