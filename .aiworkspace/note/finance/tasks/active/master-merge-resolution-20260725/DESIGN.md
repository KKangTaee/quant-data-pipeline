# Master Merge Resolution 2026-07-25 Design

## Conflict Ownership

- Root handoff logs: 서로 다른 완료 milestone을 최신순으로 모두 보존한다.
- `docs/INDEX.md`: Header System을 최신 Market Research UX로 두고 Editorial Navigation을
  previous로 내리며 Economic Cycle·Sentiment·data 완료 포인터를 함께 유지한다.
- `docs/ROADMAP.md`: Institutional Holdings와 Economic Cycle/data track 완료 기록을 모두
  유지한다.
- `docs/PROJECT_MAP.md`: 공통 ResearchHeader 소유권과 Economic Cycle/S&P freshness service
  소유권을 같은 canonical row 집합에 합친다.
- `overview_actions.py`: Futures Macro 일봉 확정과 Economic Cycle snapshot loader import를
  모두 유지한다.
- Economic Cycle workbench: TypeScript/React source와 유효한 freshness responsive CSS를
  합친 뒤 Vite가 production asset 이름과 `index.html` 참조를 다시 소유하게 한다.

## Resolution Rules

- 문서는 conflict hunk 순서가 아니라 역할과 최신순 읽기 흐름으로 합친다.
- 현재 DOM에 없는 legacy `.cycle-hero` selector는 보존하지 않는다.
- generated bundle은 ours/theirs 해시 중 하나를 임의 선택하지 않고 merged source build로
  재생성한다.
- untracked run history·registry 변경·QA 이미지는 stage하지 않는다.

## Verification Direction

- conflict marker, unmerged index, `git diff --check`
- `overview_actions.py` compile/import 계약과 관련 focused tests
- Economic Cycle TypeScript production build 및 필요한 focused service/UI contract tests
- staged file 목록과 generated/local artifact 제외 여부
