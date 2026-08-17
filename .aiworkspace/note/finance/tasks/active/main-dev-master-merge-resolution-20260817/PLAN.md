# Main-dev Master Merge Resolution Plan

State: complete
Last Updated: 2026-08-17

## 이걸 하는 이유?

`codex/main-dev`의 경제 사이클 current baseline과 `master`의 Futures Macro·Sentiment
변경을 어느 한쪽도 잃지 않고 하나의 검증 가능한 기준선으로 통합하기 위해서다.

## Roadmap

1. 병합 상태, 충돌 파일과 제외할 local artifact를 식별한다.
2. base / current / incoming 의도와 canonical 문서 역할을 대조해 수동 조정한다.
3. 충돌 해소 결과와 전체 staged diff를 검토하고 영역별 자동 검증을 실행한다.
4. actual Browser QA가 필요한 화면을 확인하고 coherent merge commit으로 닫는다.

## Scope

- finance 문서 충돌 5개와 integrated state pointer
- master에서 들어온 Futures Macro·Sentiment code / test / React bundle
- current branch의 경제 사이클 code / docs baseline 보존 확인
- registry, run history, QA 이미지와 generated artifact 제외

## Completion Criteria

- unresolved conflict와 conflict marker 0건
- 경제 사이클·Futures Macro·Sentiment의 distinct behavior와 safety boundary 보존
- focused Python / React / diff 검증 통과
- 필요한 actual Browser QA와 merge commit 완료

## Completion

- 전체 roadmap `4/4` 완료
- 후속 범위는 broad service-contract baseline 18 failures를 소유하는 별도 task뿐이다.
