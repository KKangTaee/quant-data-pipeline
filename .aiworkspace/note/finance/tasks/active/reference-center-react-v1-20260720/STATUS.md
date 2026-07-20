# Reference Center React V1 Status

Status: Completed
Date: 2026-07-20

## Progress

- Guides와 Glossary를 상단 `Reference` 단일 진입점으로 통합했다.
- Streamlit-free 24-item curated catalog, stable item ID, destination allowlist, current-surface/legacy-label drift guard를 추가했다.
- React Search-first Hybrid 화면에 4개 scope filter, 6개 journey, ranked search, local detail/related navigation, desktop drawer와 mobile sheet를 구현했다.
- `/reference?item=<id>` deep link, invalid-link fallback, owner surface 이동, 7개 current surface contextual help를 연결했다.
- legacy Guides/Glossary renderer와 catalog/test를 제거하고 내부 durable `docs/GLOSSARY.md`는 보존했다.
- focused Python 28개를 포함한 combined Python regression 102개, React 15개, typecheck/build/compile/diff check와 actual responsive Browser QA를 통과했다.
- PC 상세 패널 follow-up에서 고정 760px frame 때문에 낮은 화면 하단이 밀리고 긴 화면은 채우지 못하는 회귀를 수정했다. frame은 임의 상한 없이 parent viewport의 실제 사용 가능 높이로 계산하고 resize에 동기화하며, 본문 scroll과 항상 보이는 destination footer를 분리했다.

## Roadmap State

- Overall implementation roadmap: `4/4차`
- 1차: canonical catalog / routing contract 완료
- 2차: React search / detail workbench와 Streamlit bridge 완료
- 3차: single navigation / contextual deep link 완료
- 4차: legacy removal / documentation / desktop·900px·420px Browser QA 완료

## Completion Boundary

- Reference는 읽기 전용 설명 surface이며 provider, DB, registry, saved setup, validation 판정, log/run-history UI를 소유하지 않는다.
- 사용자-facing catalog는 내부 `GLOSSARY.md`를 runtime에 자동 파싱하지 않는다.
- 초기 QA와 PC follow-up screenshot은 generated artifact `reference-center-react-v1-qa.png`, `reference-center-pc-bottom-fix-qa.png`, `reference-center-tall-pc-viewport-qa.png`로 남겼고 commit 대상에서 제외했다.

## Next Action

새 제품 surface나 사용자 용어가 추가될 때 `app/services/reference_center.py`의 curated item과 contextual help referential-integrity test를 함께 갱신한다.
