# Phase 29 Review Note To Registry Draft Fourth Work Unit

## 이 문서는 무엇인가

`Candidate Review Note` 중 실제 후보로 남길 만한 것을
`CURRENT_CANDIDATE_REGISTRY.jsonl` row 초안으로 변환하는 네 번째 작업 단위를 정리한다.

## 쉽게 말하면

검토 노트를 저장한 뒤에도 끝이 아니다.
그 노트를 보고 "이건 후보 목록에 남겨도 되겠다"는 판단이 들 때만
명시적으로 current candidate registry에 추가할 수 있게 만든 단계다.

## 왜 필요한가

- Candidate Review Note는 판단 메모라서 후보 목록에 자동으로 보이지 않는다.
- 하지만 어떤 review note는 실제로 near-miss, scenario, current candidate 후보로 남길 필요가 있다.
- 이 과정을 채팅이나 수동 JSON 편집으로만 처리하면 실수하기 쉽다.

그래서 UI에서 registry row 초안을 먼저 보여주고,
사용자가 확인한 뒤에만 append하도록 만들었다.

## 이 작업이 끝나면 좋은 점

- review note를 후보 registry로 올릴 때 필요한 필수 값이 화면에서 보인다.
- 저장 전에 registry row JSON을 확인할 수 있다.
- `Reject For Now` note는 기본적으로 registry 저장 버튼이 비활성화되어
  거절한 초안이 후보 목록에 섞이는 일을 줄인다.

## 구현한 것

1. `Candidate Review > Review Notes`에서 저장된 review note를 선택한다.
2. 선택한 note 아래에 `Prepare Current Candidate Registry Row` 영역을 추가했다.
3. `Registry ID`, `Record Type`, `Strategy Family`, `Strategy Name`, `Candidate Role`, `Title`, `Registry Notes`를 확인 / 수정할 수 있게 했다.
4. `Current Candidate Registry Row JSON Preview`로 저장 전 row를 확인하게 했다.
5. `Append To Current Candidate Registry` 버튼을 눌러야만 `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`에 append된다.

## 중요한 경계

- 이 기능은 투자 추천이 아니다.
- 이 기능은 live trading 승인도 아니다.
- registry에 append해도 Pre-Live나 live 단계가 자동으로 열리지 않는다.
- `Candidate Review Note`를 후보 목록으로 남길 때 쓰는 명시적 기록 단계다.

## 확인할 위치

- `Backtest > Candidate Review > Review Notes`
- `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`
- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`

## 다음에 남은 것

- 사용자가 Phase 29 QA에서 registry draft / append 흐름이 충분히 명확한지 확인한다.
- QA가 끝나면 Phase 29 closeout 또는 Phase 30 portfolio proposal handoff로 넘어간다.
