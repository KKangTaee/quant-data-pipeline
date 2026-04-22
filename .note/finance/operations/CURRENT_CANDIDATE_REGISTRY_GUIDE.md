# Current Candidate Registry Guide

## 이 문서는 무엇인가
- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` 파일이 무엇인지, 왜 만들었는지, 어떻게 쓰는지 설명하는 안내 문서다.

## 목적
- current candidate와 near-miss를 사람이 읽는 Markdown 문서만이 아니라,
  기계가 다시 읽을 수 있는 형태로도 남긴다.
- 이후 automation, plugin workflow, scenario persistence가 같은 후보를 더 안정적으로 다시 참조할 수 있게 만든다.

## 쉽게 말하면
- 지금까지는 current candidate가 주로 Markdown 문서에 있었다.
- 이제는 같은 후보를 JSONL 파일에도 같이 남겨서,
  script나 plugin이 "현재 anchor가 무엇인지"를 더 쉽게 다시 읽을 수 있게 만든다.

## 왜 필요한가
- strongest candidate, lower-MDD near-miss, cleaner alternative는 자주 다시 참조된다.
- 그런데 이 정보가 문서에만 있으면:
  - script가 쓰기 어렵고
  - plugin workflow에서 재사용하기 어렵고
  - future automation에서 source-of-truth가 흐려질 수 있다.
- 그래서 사람용 요약 문서와 별도로,
  machine-readable registry를 같이 두는 것이 자연스럽다.

## 파일 위치
- registry:
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
- human-facing summary:
  - `.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`

## 역할 분리
- `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
  - 사람이 읽는 front door 문서
- `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - script, automation, plugin이 읽는 machine-readable persistence

## 현재 UI 연결
- `Backtest > Candidate Review`
  - 이 registry의 active 후보를 검토 보드로 보여준다.
  - 후보별 role, review stage, why it exists, suggested next step을 확인한다.
  - 선택한 후보를 `Pre-Live Review`로 넘길 수 있다.
- `Backtest > Compare & Portfolio Builder > Current Candidate Re-entry`
  - 이 registry의 후보 묶음을 compare form으로 다시 채운다.
- 즉 현재 strongest candidate와 near-miss는 문서에서만 다시 찾는 것이 아니라,
  candidate review, compare, Pre-Live Review workflow로 이어지는 source-of-truth로 사용된다.
- 다만 이 registry row 자체가 live trading 승인이나 최종 투자 추천은 아니다.

## 후보 검토 초안과의 차이
- `Candidate Intake Draft`
  - `Latest Backtest Run` 또는 `History` 결과를 후보처럼 검토해보는 임시 초안이다.
  - registry에 자동 저장되지 않는다.
- `Candidate Review Note`
  - `Candidate Intake Draft`를 본 뒤 운영자가 남기는 판단 메모다.
  - `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`에 저장된다.
  - 이 역시 current candidate registry 자동 등록은 아니다.
- `Review Note -> Current Candidate Registry Draft`
  - 저장된 review note 중 후보 목록에 남길 만한 것을 registry row 초안으로 바꾸는 단계다.
  - `Append To Current Candidate Registry`를 눌러야만 이 파일에 append된다.
- `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - 사람이 후보로 남기기로 판단한 뒤 기록되는 durable 후보 저장소다.

즉 좋은 결과가 나왔다면 먼저 Candidate Intake Draft로 읽고,
필요하면 Candidate Review Note로 판단을 남긴 뒤,
후보로 남길 근거가 충분할 때 registry row 또는 관련 report로 정리하는 흐름이 안전하다.

## 기본 사용 방법

### 1. 현재 seed 상태 확인
```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
```

### 2. 특정 후보 상세 확인
```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py show value_current_anchor_top14_psr
```

### 3. registry 무결성 확인
```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
```

### 4. 새 registry row 추가
```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py append --json-file path/to/row.json
```

## 현재 기준 record 예시
- `current_candidate`
  - 지금 다시 봐야 하는 strongest practical point
- `near_miss`
  - MDD는 더 좋지만 gate가 약해진 후보
- `scenario`
  - cleaner alternative나 future revisit 후보

## 한 줄 정리
- current candidate registry는 **사람이 읽는 current candidate summary를, script와 plugin도 다시 읽을 수 있게 만든 JSONL 기반 persistence layer**다.
