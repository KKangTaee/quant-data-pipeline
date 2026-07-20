# Portfolio Monitoring Position Events V1 Runs

- 2026-07-20: finance docs INDEX/ROADMAP/PROJECT_MAP, Portfolio Monitoring architecture/data/flow contracts, recent task status와 git history를 확인했다.
- 2026-07-20: command enum/handlers, item schema/repository, direct-security valuation, Streamlit bridge, React item detail/builder를 조사했다.
- 2026-07-20: current implementation에 post-registration quantity edit와 buy/sell ledger가 없고 add/end/reopen만 있음을 확인했다.
- 2026-07-20: 사용자와 3차 roadmap, append-only event ledger, actual execution price, external-flow semantics, direct-stock-only UX와 검증 기준을 승인했다.
- 2026-07-20: design self-review에서 same-day revision order를 root-stable `event_order`로 고정하고, split-first 순서, sell net proceeds, daily Modified Dietz `0.5` flow timing과 invalid denominator 처리를 명시했다. Placeholder와 scope contradiction은 남기지 않았다.
- 2026-07-20: written design review를 반영해 execution price 빈 입력 계약을 DB exact-date close 자동 입력으로 바꿨다. 사용자는 override할 수 있고 거래일 변경 시 새 close로 reset하며 reference close와 source provenance를 저장한다.
- 2026-07-20: approved spec을 8개 TDD task / 4 checkpoint implementation plan으로 전환했다. schema/domain/command/valuation/read model/page/React/QA-doc 경계, exact commands, commit units와 isolated Browser QA를 명시하고 spec coverage·placeholder·type consistency를 self-review했다.
- 2026-07-20: schema/repository, immutable projection, command, cashflow valuation, workspace-v2 read model, exact-close page bridge와 React position ledger를 Tasks 1-7 단위로 구현하고 각각 focused unittest/typecheck/build를 통과했다.
- 2026-07-20: `.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -q` 결과 `137 tests OK`를 확인했다.
- 2026-07-20: React `npm test -- --run` 결과 `29 tests passed`, `npm run typecheck`, `npm run build`를 통과하고 canonical `component_static`을 갱신했다.
- 2026-07-20: 운영 schema 사전 확인은 group/item/command `1/2/5`, position event table 없음이었다. `MySQLMonitoringRepository.ensure_schema()` 적용 후 기존 count `1/2/5` 유지, `monitoring_security_position_event=0`을 확인했다.
- 2026-07-20: registries/saved JSONL 4개 checksum은 schema 적용 전후 동일했다. QA는 임시 Streamlit fixture를 사용해 운영 event row와 사용자 setup을 수정하지 않았다.
- 2026-07-20: actual `Operations > Portfolio Monitoring` read-only smoke에서 기존 그룹 1개·항목 2개와 workspace-v2를 확인하고 browser warning/error 0을 확인했다.
- 2026-07-20: isolated Browser QA에서 최초 수량 `30→32`, 추가매수 `5주 @ $163.50` manual override, 일부매도 `4주 @ $164` DB-close default와 출금 `$656`, replace의 superseded revision, voided audit row를 확인했다.
- 2026-07-20: 종가 기본값 rerun reset을 Browser QA에서 발견하고 stable recovery key로 수정했다. 수정 뒤 `$164` auto-fill, default/manual provenance와 저장 활성화를 재검증했다.
- 2026-07-20: responsive QA는 component client/scroll width가 900px viewport에서 `704/704`, 420px viewport에서 `377/377`로 horizontal overflow 0이었다. 420px dialog는 iframe width 377을 채우고 action/fields를 유지했다.
- 2026-07-20: QA screenshot은 `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/portfolio-monitoring-position-events-v1-qa.png`에 생성했고 stage하지 않았다.
