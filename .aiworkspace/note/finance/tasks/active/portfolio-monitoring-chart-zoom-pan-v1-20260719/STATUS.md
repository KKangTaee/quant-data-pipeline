# Status

- Current: 선택 차트의 desktop 목록 35% / 상세 65%와 축 11px 가독성 후속 구현 및 자동 회귀 완료, 실제 Browser interaction/layout QA 대기
- Roadmap: 2/3차 완료, 3차 자동 검증·문서 정렬 완료 / Browser QA 미완료
- Delivered:
  - 1차: inclusive viewport, cursor anchor zoom, minimum 15-session clamp, horizontal pan pure helper TDD
  - 2차: wheel zoom, 4px drag pan, `− / + / 전체 보기`, range label, pointer-capture recovery와 mobile controls
  - 3차 일부: Python 102개, React 24개, typecheck/build, static distribution과 durable 문서 정렬
  - 가독성 후속: desktop `35:65`, 목록 최소 280px, 선택 차트 Y축·VOL·X축 11px/700
- Commits: `79cb9b75`, `b824a98d`, `a23c57d4`, `4804f5de`
- Next: 정책상 허용된 in-app Browser에서 desktop/900px/420px layout·wheel/drag/reset·overflow QA
