# Phase 30 Registry IO Helper Refactor Third Work Unit

## 이 문서는 무엇인가

Phase 30의 세 번째 작업 단위 기록이다.
Portfolio Proposal UI / persistence를 만들기 전에,
`app/web/pages/backtest.py` 안에 있던 registry JSONL 읽기 / append helper를
작은 runtime module로 분리했다.

## 쉽게 말하면

이번 작업은 화면을 바꾸거나 새 기능을 추가한 것이 아니다.

Candidate Review, Current Candidate Registry, Pre-Live Review가 함께 쓰는
파일 읽기 / 저장 helper만 먼저 밖으로 빼서,
나중에 Portfolio Proposal도 같은 방식의 저장소를 붙이기 쉽게 만든 작업이다.

## 왜 필요한가

- `backtest.py`는 16k lines 이상으로 커져 있고, UI rendering과 JSONL persistence helper가 섞여 있었다.
- Portfolio Proposal 구현이 들어오면 registry / candidate / pre-live 저장 helper를 다시 쓰거나 비슷한 코드를 만들 가능성이 높다.
- 먼저 작고 안전한 I/O helper부터 분리하면, 후속 UI 구현 때 `backtest.py`가 더 커지는 것을 줄일 수 있다.
- 이번 작업은 behavior change가 아니라 ownership boundary를 만드는 refactor다.

## 바뀐 코드

새 파일:

- `app/web/runtime/candidate_registry.py`

이 파일이 담당하는 것:

- `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl` 최신 active 후보 읽기
- current candidate registry row append
- `.note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl` active review note 읽기
- candidate review note append
- `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 최신 active pre-live row 읽기
- pre-live candidate registry row append

변경된 파일:

- `app/web/pages/backtest.py`
  - 기존 내부 helper 구현을 제거하고 runtime helper를 import해서 사용한다.
  - Streamlit panel, session state key, button flow, display behavior는 바꾸지 않는다.
- `app/web/runtime/__init__.py`
  - 새 helper와 registry path constants를 public runtime boundary로 export한다.

## 의도적으로 바꾸지 않은 것

- Candidate Review UI
- Pre-Live Review UI
- Compare prefill behavior
- Current candidate registry row schema
- Candidate review note schema
- Pre-Live registry row schema
- JSONL file paths
- append-only semantics
- Streamlit session state key

## 검증 기준

- `python3 -m py_compile app/web/runtime/candidate_registry.py app/web/runtime/__init__.py app/web/pages/backtest.py`
- `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate`
- `.venv/bin/python` import smoke:
  - `load_current_candidate_registry_latest`
  - `load_pre_live_candidate_registry_latest`
  - `load_candidate_review_notes`

## 현재 판단

이번 작업은 `backtest.py` 전체 리팩토링이 아니다.
첫 번째 실제 코드 분리로 registry JSONL I/O helper만 분리했다.

다음 리팩토링 후보는 둘 중 하나가 자연스럽다.

1. Candidate Review display / draft helper 일부 분리
2. Pre-Live Review display / draft helper 일부 분리

다만 Portfolio Proposal UI를 먼저 구현해야 한다면,
이번에 분리한 `candidate_registry.py`를 재사용해 저장소 helper 패턴을 맞춘다.

후속 상태:

- 네 번째 작업에서 Portfolio Proposal UI / persistence를 먼저 구현했다.
- proposal 전용 JSONL helper는 `app/web/runtime/portfolio_proposal.py`로 분리했다.
- Candidate Review / Pre-Live display module 분리는 여전히 후속 리팩토링 후보로 남아 있다.
