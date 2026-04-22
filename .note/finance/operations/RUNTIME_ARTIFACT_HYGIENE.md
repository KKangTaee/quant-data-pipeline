# Runtime Artifact And Session Hygiene

## 목적

이 문서는 finance 작업 중 계속 쌓이는 runtime artifact와 session 산출물을
어떻게 해석하고 다뤄야 하는지 정리한 운영 문서다.

## 왜 필요한가

현재 프로젝트는 backtest와 UI 실행이 많아서 아래 파일이 계속 쌓인다.

- `BACKTEST_RUN_HISTORY.jsonl`
- `WEB_APP_RUN_HISTORY.jsonl`
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
- current candidate registry (`CURRENT_CANDIDATE_REGISTRY.jsonl`)
- candidate review notes (`CANDIDATE_REVIEW_NOTES.jsonl`)
- pre-live candidate registry (`PRE_LIVE_CANDIDATE_REGISTRY.jsonl`)

### runtime artifact

기본적으로 commit 대상이 아닌 파일:

- backtest run history jsonl
- web app run history jsonl
- saved portfolio runtime jsonl
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

- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`
- `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`

## 지금 프로젝트에서 특히 조심할 것

- `.note/finance/BACKTEST_RUN_HISTORY.jsonl`
- `.note/finance/WEB_APP_RUN_HISTORY.jsonl`

이 두 파일은 현재 이미 tracked history 역할도 일부 겸하고 있어서
즉시 구조를 바꾸기보다,
이번 단계에서는:

- artifact라는 해석을 분명히 하고
- 새 clutter를 `.gitignore`로 더 막는 방향이 안전하다

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
