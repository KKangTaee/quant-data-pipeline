# Phase 36 Test Checklist

## 목적

이 checklist는 Phase36의 `Operations > Selected Portfolio Dashboard`가 제대로 열렸는지 확인하는 manual QA 문서다.

이번 checklist는 Final Review selected row를 운영 대시보드에서 올바르게 읽고,
선정 당시 contract를 사용자가 지정한 최신 기간으로 재검증할 수 있는지 확인한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 완료된 뒤 Phase36 closeout 또는 Phase37 방향을 결정한다.
- 이 대시보드는 live approval, broker order, 자동매매가 아니다.

## 1. Operations navigation 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard`
- 체크 항목:
  - [ ] Operations navigation에 `Selected Portfolio Dashboard`가 보이는지
  - [ ] 화면 제목이 `Selected Portfolio Dashboard`로 보이는지
  - [ ] 설명 문구가 선정 포트폴리오를 최신 기간으로 재검증하는 대시보드라고 설명하는지
  - [ ] `Backtest > Final Review`가 아닌 Operations 화면으로 분리되어 있는지

## 2. 데이터 기준 / empty state 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard`
- 체크 항목:
  - [ ] source path가 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`로 보이는지
  - [ ] selected filter가 `SELECT_FOR_PRACTICAL_PORTFOLIO` 기준으로 설명되는지
  - [ ] final decision file이 없거나 selected row가 없을 때 오류 대신 안내 문구가 보이는지
  - [ ] performance recheck / drift check가 새 registry를 저장한다고 설명하지 않는지

## 3. 최종 선정 포트폴리오 목록 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard > 운영 대상 목록`
- 체크 항목:
  - [ ] Final Review에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장한 row만 운영 대상으로 표시되는지
  - [ ] table에 status, decision id, source, title, component 수, target weight, benchmark, evidence route / score가 보이는지
  - [ ] status filter, source type filter, benchmark filter가 동작하는지
  - [ ] `normal`, `watch`, `rebalance_needed`, `re_review_needed`, `blocked` status 의미가 화면에서 읽히는지

## 4. Snapshot / Performance Recheck 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard > 상세 확인 > Snapshot / Performance Recheck`
- 체크 항목:
  - [ ] 선택한 portfolio의 source type / source id / decision id가 보이는지
  - [ ] 원래 검증 시작일 / 종료일, baseline CAGR / MDD가 보이는지
  - [ ] `Recheck start`, `Recheck end`, `Virtual capital` 입력이 보이는지
  - [ ] `Recheck end` 기본값이 DB latest market date로 잡히는지
  - [ ] `Run Recheck`를 누르면 selected component contract replay가 실행되는지
  - [ ] portfolio value, total return, CAGR, MDD, benchmark spread가 보이는지
  - [ ] 원래 baseline과 recheck 결과의 CAGR / MDD 변화가 비교되는지
  - [ ] component contribution, strongest periods, weakest periods가 보이는지
  - [ ] 재검증 결과가 live approval이나 주문 지시로 표현되지 않는지

## 5. Allocation / Operator Context 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard > Allocation / Operator Context`
- 체크 항목:
  - [ ] target allocation table에 component title, role, target weight, family, benchmark가 보이는지
  - [ ] operator reason / constraints / next action이 JSON이 아니라 문장으로 보이는지
  - [ ] paper observation review cadence와 trigger가 JSON이 아니라 목록 / 문장으로 보이는지
  - [ ] evidence checks는 접힘 영역에서 Final Review evidence / Validation / Robustness / Paper Observation check로 보이는지

## 6. 실행 경계 / Audit 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard > 실행 경계`
- 체크 항목:
  - [ ] `Live Approval` button이 disabled인지
  - [ ] `Broker Order` button이 disabled인지
  - [ ] `Auto Rebalance` button이 disabled인지
  - [ ] dashboard가 실제 주문, broker API, 자동매매를 만들지 않는다고 설명하는지
  - [ ] Final Review 원본 JSON은 기본 화면에 바로 노출되지 않고 `Audit / Developer Details` 접힘 영역에 있는지

## 7. Allocation Check / Drift Check 확인

- 확인 위치:
  - `Operations > Selected Portfolio Dashboard > Allocation Check: 실제 보유 상태 / drift 점검`
- 체크 항목:
  - [ ] drift check가 기본 화면이 아니라 고급 접힘 영역에 있는지
  - [ ] `현재 보유 상태 입력 방식`에서 현재 보유 평가금액, 보유 수량과 가격, 이미 계산한 현재 비중 입력을 선택할 수 있는지
  - [ ] 현재 보유 평가금액 입력에서는 component별 current value와 `Unassigned cash / outside value`가 current weight로 변환되는지
  - [ ] 보유 수량과 가격 입력에서는 holding symbol, shares, current price가 current value / current weight로 변환되는지
  - [ ] 이미 계산한 현재 비중 입력에서는 component별 현재 비중 입력란이 target weight 기본값으로 보이는지
  - [ ] `Load latest close`가 DB 조회 실패 시 화면 오류 대신 warning으로 남는지
  - [ ] `Rebalance threshold`, `Watch threshold`, `Total tolerance`를 조정할 수 있는지
  - [ ] 현재 비중 합계가 100% 근처가 아니면 `DRIFT_INPUT_INCOMPLETE` 계열 안내가 보이는지
  - [ ] target 대비 drift가 watch threshold 이상이면 관찰 필요로 읽히는지
  - [ ] target 대비 drift가 rebalance threshold 이상이면 `REBALANCE_NEEDED` / 리밸런싱 검토 필요로 읽히는지
  - [ ] drift 결과가 주문 지시가 아니라 read-only 검토 신호로 설명되는지
  - [ ] `Drift Alert / Review Trigger Preview`가 drift 결과를 운영 경고 / 관찰 / 리밸런싱 검토 / 입력 확인으로 다시 보여주는지
  - [ ] Final Review에 남긴 review trigger가 alert preview table에 같이 표시되는지
  - [ ] alert preview가 alert registry 저장이나 주문 지시를 만들지 않는다고 설명되는지

## 8. 문서 확인

- 확인 문서:
  - `.note/finance/phases/phase36/PHASE36_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase36/PHASE36_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase36/PHASE36_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase36이 Final Review 이후 새 판단 저장 단계가 아니라 Operations dashboard로 설명되는지
  - [ ] Performance Recheck가 selected component contract를 사용자가 지정한 기간으로 replay하는 핵심 기능으로 설명되는지
  - [ ] current weight / current value / shares x price 기반 drift check와 alert preview는 고급 보조 기능으로, DB latest close는 입력 보조 기능이며 account holding 자동 연결 / alert persistence는 후속 phase로 설명되는지
  - [ ] live approval / broker order / 자동매매가 out of scope로 남아 있는지
  - [ ] 새 page와 helper 파일이 code analysis 문서에 등록되어 있는지

## 완료 판단

위 항목이 통과하면,
**사용자는 Final Review에서 선정한 포트폴리오를 Operations에서 다시 찾고, 최신 기간으로 재검증하며, target allocation과 evidence를 확인할 수 있는 상태**로 본다.

다만 이것은 broker order, 자동매매, live approval, 수익 보장이 아니다.
