# Phase 30 Portfolio Proposal Pre-Live Feedback Sixth Work Unit

## 이 문서는 무엇인가

Phase 30의 여섯 번째 작업 단위 기록이다.
저장된 Portfolio Proposal draft를 현재 Pre-Live registry 상태와 비교하는
`Pre-Live Feedback` surface를 추가했다.

## 쉽게 말하면

proposal을 저장한 뒤에도 후보의 Pre-Live 상태는 바뀔 수 있다.

이번 작업은 proposal 저장 당시 snapshot과
현재 `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`의 active record를 비교해서,
어떤 후보가 paper tracking 중인지,
어떤 후보의 상태가 proposal 저장 당시와 달라졌는지,
review date가 지났는지,
active weight를 둔 후보가 hold / reject / re-review 상태인지 확인하게 만든다.

이 화면은 proposal을 자동 수정하지 않는다.
상태를 바꾸려면 `Backtest > Pre-Live Review`에서 별도 record를 저장해야 한다.

## 왜 필요한가

Portfolio Proposal은 한 번 저장하고 끝나는 문서가 아니다.
후보별 Pre-Live 운영 상태가 바뀌면 proposal 해석도 같이 다시 봐야 한다.

최종 목표인 실전 포트폴리오 / 가이드 제시로 가려면,
proposal이 현재 paper / pre-live 관찰 상태와 어긋나지 않는지 확인하는 surface가 필요하다.

## 바뀐 코드

변경된 파일:

- `app/web/pages/backtest.py`

추가된 것:

- `Backtest > Portfolio Proposal > Pre-Live Feedback` tab
- proposal별 Pre-Live feedback summary table
- proposal component별 saved Pre-Live snapshot vs current Pre-Live status 비교
- status drift 표시
- review overdue 표시
- tracking cadence / next action 표시
- feedback gap readout

## UI 흐름

```text
PORTFOLIO_PROPOSAL_REGISTRY.jsonl
  + PRE_LIVE_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> Pre-Live Feedback
  -> proposal 선택
  -> saved pre-live snapshot과 current pre-live status 비교
  -> status drift / overdue review / feedback gap 확인
```

## Feedback Gap 기준

현재 UI는 아래를 feedback gap으로 표시한다.

- proposal component에 연결된 active Pre-Live record가 없음
- proposal 저장 당시 Pre-Live snapshot과 현재 Pre-Live 상태가 다름
- 현재 Pre-Live 상태가 `hold`, `reject`, `re_review`인데 target weight가 0보다 큼
- 현재 Pre-Live review date가 지남

이 기준은 live approval gate가 아니다.
proposal을 다시 읽을 때 놓치기 쉬운 운영 피드백을 보여주는 보조 정보다.

## 의도적으로 바꾸지 않은 것

- proposal row 자동 수정
- pre-live registry 자동 수정
- current candidate registry 자동 수정
- paper tracking 성과 자동 계산
- live readiness approval
- broker / order integration
- portfolio optimizer

## 검증 기준

- `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py`
- `.venv/bin/python` Pre-Live feedback helper smoke
- `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`

## 현재 판단

Phase 30은 이제 proposal draft 작성 / 저장 / monitoring review에 더해,
proposal과 현재 Pre-Live 운영 상태를 비교하는 feedback surface까지 갖췄다.

아직 남은 것은 paper tracking 성과 자체를 proposal에 반영하는 더 깊은 feedback loop와,
Candidate Review / Pre-Live / History / Saved Portfolio의 추가 `backtest.py` 모듈 분리다.
