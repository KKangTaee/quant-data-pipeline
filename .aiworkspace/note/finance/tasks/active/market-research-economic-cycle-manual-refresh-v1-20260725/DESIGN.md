# Design

Status: Approved
Last Updated: 2026-07-25

## Approved Direction

브라우저 진입은 DB read만 수행한다. 저장된 월중 계산일이 최신 계산 가능 평일보다
뒤처졌을 때 compact 안내와 `최신 데이터로 다시 계산` action을 제공한다. 사용자가
클릭해야 기존 17-series incremental collection과 nowcast materialization이 실행된다.

## Boundaries

- `.env`는 worktree-local이며 `override=False`로 읽는다.
- React는 event만 보내고 Python action wrapper가 job을 실행한다.
- 성공은 job return뿐 아니라 persisted target snapshot postcondition까지 필요하다.
- 실패 시 last-good monthly/intramonth snapshot을 유지한다.
- background scheduler와 raw diagnostic panel은 범위 밖이다.

## Detailed Spec

`docs/superpowers/specs/2026-07-25-economic-cycle-manual-refresh-design.md`
