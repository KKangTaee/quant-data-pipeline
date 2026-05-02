# Phase 30 Portfolio Proposal Draft UI Fourth Work Unit

## 이 문서는 무엇인가

Phase 30의 네 번째 작업 단위 기록이다.
Portfolio Proposal 계약을 실제 Backtest UI에서 확인하고 저장할 수 있도록,
`Backtest > Portfolio Proposal` panel과 append-only proposal registry helper를 추가했다.

## 쉽게 말하면

이제 current candidate 여러 개를 골라
"왜 이 후보들을 하나의 포트폴리오 제안 초안으로 묶는가"를 화면에서 작성할 수 있다.

다만 이 화면은 투자 승인, 실전 주문, 자동 포트폴리오 최적화 화면이 아니다.
후보 묶음의 목적, 역할, 비중, 다음 검토 행동을 남기는 초안 저장 화면이다.

## 왜 필요한가

Phase 29까지는 좋은 백테스트 결과를 후보로 읽고,
Candidate Review Note와 Current Candidate Registry에 남기는 흐름이 생겼다.

하지만 최종 목표는 단일 후보 목록이 아니라,
사용자가 실제로 검토할 수 있는 포트폴리오 구성안과 가이드를 제시하는 것이다.

Portfolio Proposal UI는 그 중간 단계다.
후보 여러 개를 그냥 합치는 것이 아니라,
각 후보의 역할과 target weight, weight reason, Real-Money / Pre-Live 상태,
저장 전 blocker를 함께 보게 한다.

## 바뀐 코드

새 파일:

- `app/web/runtime/portfolio_proposal.py`

이 파일이 담당하는 것:

- `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` path constant
- `PORTFOLIO_PROPOSAL_SCHEMA_VERSION`
- proposal row append helper
- 최신 proposal row load helper

변경된 파일:

- `app/web/pages/backtest.py`
  - `Backtest` panel option에 `Portfolio Proposal`을 추가했다.
  - `Create Proposal Draft` tab에서 current candidate를 여러 개 선택하고 proposal 초안을 만든다.
  - `Proposal Registry` tab에서 저장된 proposal row를 확인한다.
- `app/web/runtime/__init__.py`
  - portfolio proposal helper와 registry path constant를 public runtime boundary로 export한다.

## UI 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> current candidate 여러 개 선택
  -> proposal objective / type / status 입력
  -> 후보별 proposal role / target weight / weight reason 입력
  -> 저장 전 blocker 확인
  -> Portfolio Proposal JSON Preview 확인
  -> Save Portfolio Proposal Draft
  -> PORTFOLIO_PROPOSAL_REGISTRY.jsonl append
  -> Proposal Registry tab에서 inspect
```

## 저장되는 핵심 정보

- `proposal_id`
- `proposal_status`
- `proposal_type`
- `objective`
- `candidate_refs`
- `construction`
- `risk_constraints`
- `evidence_snapshot`
- `open_blockers`
- `operator_decision`

`candidate_refs`에는 current candidate registry id, strategy family, candidate role,
proposal role, target weight, weight reason, Real-Money 상태, Pre-Live 상태를 함께 남긴다.

## 저장 전 blocker

현재 UI는 아래 조건을 저장 전 blocker로 본다.

- 선택된 current candidate가 없음
- target weight 합계가 100%가 아님
- Pre-Live 상태가 `reject`인 후보에 active weight가 있음
- Real-Money deployment가 `blocked`인 후보를 `core_anchor`로 두려 함

이 blocker들은 live approval gate가 아니라,
초안 저장 전에 최소한의 일관성을 지키기 위한 안전장치다.

## 의도적으로 바꾸지 않은 것

- 실제 주문 실행
- live trading approval
- 자동 비중 최적화
- correlation / covariance 기반 optimizer
- saved portfolio replay 계약
- current candidate registry row schema
- pre-live registry row schema
- Candidate Review UI
- Pre-Live Review UI

## 검증 기준

- `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py`
- `.venv/bin/python` import smoke:
  - `load_portfolio_proposals`
  - `append_portfolio_proposal`
  - `PORTFOLIO_PROPOSAL_REGISTRY_FILE`
- `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`

## 현재 판단

Phase 30은 이제 Portfolio Proposal 계약을 문서로만 둔 상태에서 한 단계 더 나아가,
초안 작성과 registry append가 가능한 상태가 되었다.

아직 남은 작업은 proposal을 더 풍부하게 평가하는 monitoring surface와,
Candidate Review / Pre-Live / History / Saved Portfolio의 추가 `backtest.py` 모듈 분리다.
