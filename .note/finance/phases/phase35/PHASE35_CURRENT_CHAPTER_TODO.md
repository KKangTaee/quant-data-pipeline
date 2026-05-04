# Phase 35 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 35의 목표는 별도 후속 가이드 탭을 추가하는 것이 아니라,
Backtest workflow를 아래처럼 단순하고 이해 가능한 마지막 단계로 정리하는 것이다.

```text
Portfolio Proposal -> Final Review -> 최종 판단 완료
```

Final Review에서 사용자가 확인해야 하는 최종 상태는 아래 네 가지다.

- 투자 가능 후보
- 내용 부족 / 관찰 필요
- 투자하면 안 됨
- 재검토 필요

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 35 전체 목표 | Final Review를 현재 workflow의 마지막 active panel로 고정 | `implementation_complete` |
| 첫 번째 작업 | Final Review 종료 상태 계약 정리 | `completed` |
| 두 번째 작업 | 별도 후속 가이드 workflow 제거 | `completed` |
| 세 번째 작업 | Final Review UI의 최종 판단 완료 표시 보강 | `completed` |
| 네 번째 작업 | 문서 / QA checklist 동기화 | `completed` |

## 완료한 내용

- `Backtest` workflow navigation에서 별도 후속 가이드 panel을 제거했다.
- `app/web/backtest_post_selection_guide.py`와 helper module을 제거했다.
- `Backtest > Final Review`가 현재 후보 선정 workflow의 마지막 active panel이 되게 했다.
- saved final decision review에서 `투자 가능성`과 `Final Review Status`를 확인할 수 있게 했다.
- 기존 저장 row에 남아 있는 legacy `phase35_handoff` 문구가 UI에 그대로 보이지 않도록 Final Review status 표시를 현재 기준으로 변환한다.
- `Final Review`의 보조 action은 `Live Approval / Order` disabled 상태로 남겨 실행 경계를 유지했다.
- `phase35_handoff` field는 과거 row 호환을 위해 읽을 수 있지만, 사용자-facing으로는 final review completion status로 해석한다.

## 중요한 경계

- Phase35는 새 registry를 만들지 않는다.
- Phase35는 별도 저장 버튼을 추가하지 않는다.
- Final Review의 final decision registry가 최종 판단 원본이다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO`도 live approval, broker order, 자동매매가 아니다.
- 실제 투자 금액 결정, 주문 실행, broker API 연결은 별도 phase가 필요하다.

## 현재 판단

Phase 35는 implementation_complete / manual_qa_pending 상태다.
이제 사용자가 `PHASE35_TEST_CHECKLIST.md`를 기준으로 manual QA를 진행하면 된다.
