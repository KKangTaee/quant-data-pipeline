# Runtime Artifact And Session Hygiene

## 목적

이 문서는 finance 작업 중 계속 쌓이는 runtime artifact와 session 산출물을
어떻게 해석하고 다뤄야 하는지 정리한 운영 문서다.

## 왜 필요한가

현재 프로젝트는 backtest와 UI 실행이 많아서 아래 파일이 계속 쌓인다.

- `run_history/BACKTEST_RUN_HISTORY.jsonl`
- `run_history/WEB_APP_RUN_HISTORY.jsonl`
- `backtest_artifacts/`
- `run_artifacts/`
- `_tmp_*.csv`
- daily failure CSV
- notebook scratch 파일

이런 파일은 코드나 전략 문서와 달리
실행 상태를 기록하는 산출물이라,
문맥을 빠르게 다시 잡는 데는 도움이 적고
git 상태를 지저분하게 만들기 쉽다.

## 구분 기준

### durable 문서

계속 유지하고 인덱싱할 문서:

- phase 문서
- strategy hub
- one-pager
- strategy backtest log
- current candidate summary
- glossary / roadmap / index
- current candidate registry (`registries/CURRENT_CANDIDATE_REGISTRY.jsonl`)
- candidate review notes (`registries/CANDIDATE_REVIEW_NOTES.jsonl`)
- pre-live candidate registry (`registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`)
- portfolio proposal registry (`registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`)
- paper portfolio tracking ledger (`registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`)
- final portfolio selection decisions (`registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`)

### runtime artifact

기본적으로 commit 대상이 아닌 파일:

- `run_history/` 아래 backtest / web app run history jsonl
- `saved/` 아래 saved portfolio setup jsonl
- `backtest_artifacts/`
- `run_artifacts/`
- 임시 csv / failure csv
- notebook scratch
- `.DS_Store`

## 현재 권장 원칙

1. 결과를 남기고 싶으면 artifact가 아니라 Markdown report에 남긴다
2. 다시 볼 가치가 있는 결과는 strategy backtest log에 append한다
3. runtime file은 기본적으로 generated state로 취급한다
4. commit 전에는 `git status`에서 artifact가 섞이지 않았는지 먼저 본다

단, 아래 파일은 generated artifact가 아니라
의도적으로 유지하는 durable registry로 본다.

- `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl`
- `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`
- `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`
- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`

## 지금 프로젝트에서 특히 조심할 것

- `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`
- `.note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl`
- `.note/finance/saved/SAVED_PORTFOLIOS.jsonl`

이 파일들은 `run_history/`와 `saved/`로 모아 둔다.
필요할 때 로컬 상태 확인에는 사용하지만,
중요한 전략 판단은 별도 Markdown report나 registry row로 요약한다.

## 운영 체크

새로운 refinement work unit을 끝낼 때는:

1. phase 문서가 갱신됐는지
2. strategy hub / one-pager / backtest log가 맞는지
3. root concise logs가 필요하면 갱신됐는지
4. git에 runtime artifact만 남아 있는지

를 같이 본다.

가능하면 이 점검은 아래 helper로 먼저 확인한다.

```bash
python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

현재 운영 기준으로는 Codex가 아래 시점에 이 스크립트를 우선적으로 돌리는 것이 권장된다.

1. refinement 결과를 문서에 반영한 직후
2. commit 직전
3. phase closeout 직전
