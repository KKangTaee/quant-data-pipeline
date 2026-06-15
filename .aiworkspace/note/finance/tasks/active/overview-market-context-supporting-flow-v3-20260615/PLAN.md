# Overview Market Context Supporting Flow V3

Status: Active
Date: 2026-06-15
Worktree: `sub-dev`

## 이걸 하는 이유?

1차는 Market Context를 큰 카드에서 분리했고, 2차는 `오늘의 시장 맥락`을 2~3문장형으로 정리했다. 하지만 하단 `해석할 때 같이 볼 변수`, `과거 유사 맥락 참고`, `자료 기준 / 출처 상태`는 아직 같은 무게로 이어져서 사용자가 시장 해석인지, 참고인지, 자료 근거인지 헷갈릴 수 있다.

이번 3차는 하단 보조영역을 `다음 맥락 체크`, `참고: 과거 유사 맥락`, `근거: 자료 기준 / 출처 상태`로 재정의해 읽기 흐름을 정리한다.

## Scope

- `해석할 때 같이 볼 변수`를 `다음 맥락 체크`로 재구성한다.
- Data Health / 자료 상태를 시장 변수 row에서 제거하고, 상단 status / 근거 영역으로 낮춘다.
- 과거 유사 맥락은 참고 섹션으로 낮추고 자료 부족 시 시각적 무게를 줄인다.
- 자료 기준 / 출처 상태는 evidence/footer 성격이 드러나도록 제목과 설명을 정리한다.
- 서비스 / UI 계약 테스트와 Browser QA를 갱신한다.

## Out Of Scope

- 새 provider, DB schema, registry / saved JSONL write.
- Overview render 중 external fetch.
- 예측 모델, 매수/매도 신호, validation gate, Final Review decision, monitoring signal.
- 복잡한 drill-in interaction 또는 dashboard editor.

## Completion Criteria

- 화면에 `해석할 때 같이 볼 변수`가 더 이상 나오지 않는다.
- `다음 맥락 체크`는 이벤트 / 심리 / 매크로 확인 같은 관찰 지점만 표시한다.
- `자료 상태 주의점`은 main next-context row가 아니다.
- 과거 유사 맥락과 출처 상태는 각각 `참고`, `근거` 성격으로 표시된다.
- focused unittest, py_compile, diff check, Browser QA가 완료된다.
