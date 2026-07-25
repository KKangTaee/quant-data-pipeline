# Master Merge Resolution 2026-07-25 Risks

## Closed

- generated Vite asset의 ours/theirs 해시를 임의 선택하는 위험은 source 재빌드 방침으로
  제거했다.
- common ResearchHeader와 manual freshness action의 merged source build 및
  1280·420px actual QA를 통과했다.
- unmerged path와 conflict marker가 없고 run history·registry·QA 이미지가 staged
  merge 범위에서 제외됐음을 확인했다.

## Accepted

- repository-wide 전체 suite는 기존 비관련 baseline failure가 알려져 있어 실행하지
  않았다. 충돌 및 incoming ownership 영역의 focused Python `456`개와 React `11`개,
  TypeScript/build/compile/Browser QA를 통합 기준으로 사용한다.
