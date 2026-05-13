# NOTES - Product Research Plugin Stage 5

## Stage 5 Direction

이번 단계는 "리서치 결과를 더 쓰는 것"이 아니라 "리서치 workflow를 plugin source 안에 넣는 것"이다.

이번까지 확인된 반복 패턴:

1. active research bundle을 만든다.
2. `CURRENT_PROJECT_AUDIT.md`로 현행 제품 구조와 약점을 정리한다.
3. `BENCHMARKS.md`, `UI_PATTERNS.md`, `SOURCES.md`로 외부 근거와 패턴을 모은다.
4. `FEATURE_CANDIDATES.md`, `RECOMMENDATION.md`, `RISKS.md`로 후보와 추천 범위를 좁힌다.
5. research output은 승인된 개발 계획이 아니며, 구현은 별도 task/phase 승인 후 진행한다.

## Stage 5 Design Choice

별도 product research plugin 분리는 아직 이르다.

현재는 다음 이유로 기존 `quant-finance-workflow` plugin 내부에 둔다.

- product research output이 finance docs, reports, runtime/code boundary와 강하게 연결되어 있다.
- 아직 research-to-roadmap / research-to-phase handoff가 더 반복 검증되지 않았다.
- helper script와 orchestration skill을 먼저 안정화하면 나중에 별도 plugin으로 분리하기 쉽다.

## Helper Script Scope

`bootstrap_product_research_bundle.py`:

- research id와 title을 받아 required file skeleton을 만든다.
- 실제 외부 리서치나 web browsing은 하지 않는다.
- `researches/README.md` 갱신은 자동으로 강제하지 않고, 검증 script에서 누락 여부를 알려준다.

`check_product_research_bundle.py`:

- active research bundle의 required files, basic sections, source date, README listing을 확인한다.
- 추천안 자체의 품질을 판단하지 않고, output contract 누락만 잡는다.

## Follow-Up Candidates

- research result를 user-approved phase/task plan으로 넘기는 `research-to-phase` workflow
- accepted recommendation만 `docs/ROADMAP.md`에 승격하는 doc-sync rule
- product research plugin 분리 여부 판단
