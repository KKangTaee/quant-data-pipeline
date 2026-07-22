# Risks

- Result Workspace service의 순수 read-model 경계를 유지하려면 DB-aware refresh plan은 web adapter에서 만들고 JSON-ready model만 주입해야 한다.
- Portfolio Mix는 component별 requested end와 current mix requested end를 혼동하면 과수집 또는 부족 판정이 생길 수 있다.
- 현재 보유 종목만 최신화하면 GTAA ranking Universe가 오래된 채 남아 결과 재현성이 깨진다.
- 가격 수집 성공을 백테스트 성공으로 오인하면 안 된다. 새 실행 전까지 old result와 Level2 handoff는 차단 상태여야 한다.
- provider/source gap은 반복 refresh로 해결되지 않을 수 있으므로 retry loop를 차단하고 별도 원인 안내가 필요하다.
- current worktree에는 사용자 registry, saved setup, run history, generated screenshots가 있으므로 설계·구현 커밋에서 명시적으로 제외한다.
