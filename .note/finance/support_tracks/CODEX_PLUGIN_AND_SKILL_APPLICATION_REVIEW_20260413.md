# Codex Plugin And Skill Application Review

## 목적

이 문서는 `quant-data-pipeline`에서
Codex CLI plugin과 repo-local skill을 도입하면
실제로 작업 효율이 좋아질지 검토한 결과를 정리한 문서다.

## 공식 기준 요약

OpenAI Codex 안내 기준으로:

- plugin은 reusable workflow의 **installable distribution unit**이다
- skill은 reusable workflow의 **authoring format**에 가깝다
- plugin은 skill, optional app integration, MCP config를 함께 묶을 수 있다

공식 참고:

- OpenAI Help Center
  - `Using Codex with your ChatGPT plan`
  - plugins 설명 구간
  - https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan.pdf

## 현재 프로젝트에 plugin이 맞는 이유

이 프로젝트에는 반복되는 workflow가 분명하다.

예를 들면:

- bounded backtest refinement
- phase report / strategy hub / one-pager / backtest log 동기화
- current candidate summary 유지
- runtime artifact hygiene 확인

즉 매번 완전히 새로 판단하기보다
같은 순서를 반복하는 작업이 많다.

이런 경우에는:

- 단순 문서만 두는 것보다
- repo-local skill로 workflow를 적어 두고
- plugin으로 installable 형태로 묶는 편이
  future Codex session과 팀 공유에 유리하다

## 현재 판단

### skill만으로 충분한 부분

- repo 구조 다시 읽기
- current candidate anchor 확인
- bounded search 범위 정하기
- 결과 문서 동기화 순서 기억하기

이런 것은 skill이 잘 맞는다.

### plugin까지 가면 좋은 부분

- repo-local skill을 반복 설치/활성화하기 쉽게 만들기
- 향후 cleanup/checklist script를 함께 묶기
- 향후 MCP or app integration을 같은 패키지에 묶기

즉:

- 당장은 skill이 핵심이고
- plugin은 그 skill을 팀/프로젝트 단위로 배포하는 포장재에 가깝다

## 이번에 만든 초안

repo-local draft plugin:

- `plugins/quant-finance-workflow`

repo-local draft skill:

- `plugins/quant-finance-workflow/skills/finance-backtest-candidate-refinement`

repo-local first practical script:

- `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - current git diff를 기준으로
    - phase docs
    - strategy hub / one-pager / backtest log
    - root concise logs
    - generated artifacts
    상태를 한 번에 점검하는 checklist runner

Phase 21 practical baseline:

- `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`
  - 새 phase 문서를 template 기준으로 한 번에 여는 automation script
- `plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py`
  - current strongest candidate와 near-miss를 machine-readable registry로 남기고 다시 읽는 persistence helper
- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - current candidate automation baseline을 위한 append-only registry

이 초안은:

- 지금 프로젝트의 backtest refinement 흐름을 재사용 가능한 skill로 묶고
- 향후 Codex plugin으로 실험할 수 있게 repo-local scaffold를 만든 상태다
- 그리고 첫 practical script까지 붙여서
  단순 scaffold가 아니라 실제 workflow에 바로 써볼 수 있는 상태가 됐다

## 이 프로젝트에서 plugin이 특히 효과적일 수 있는 이유

1. 전략 refinement가 반복된다
2. 결과 문서화 규칙이 많다
3. `Value / Quality / Quality + Value` current anchor가 자주 바뀐다
4. phase 문서와 strategy 문서를 같이 맞춰야 한다

즉 한 번의 search보다
반복 refinement cycle을 잘 패키징하는 것이 더 중요하다.

## 지금 당장 기대할 수 있는 효과

- 다음 세션에서 current candidate와 문서 동기화 순서를 더 빨리 다시 잡을 수 있음
- Codex가 “어디부터 읽어야 하는지”를 덜 헤맴
- future team workflow로 공유하기 쉬움

## 아직 plugin보다 문서가 더 중요한 부분

아직은 아래가 더 중요하다.

- current candidate summary 유지
- root log 압축 유지
- strategy hub / one-pager / backtest log 일관성 유지

즉 plugin은 좋은 가속 장치이지만,
현재 후보와 문서 구조가 정리돼 있어야 효과가 크다.

## 권장 다음 단계

1. draft skill 내용을 프로젝트 workflow에 맞게 채우기
2. 이 script를 실제 refinement closeout에서 몇 번 써보며 false positive/negative를 줄이기
3. plugin manifest는 local test에 필요한 수준까지 점진적으로 채우기
4. 실제로 몇 턴 써본 뒤 team-facing plugin으로 넓힐지 판단
