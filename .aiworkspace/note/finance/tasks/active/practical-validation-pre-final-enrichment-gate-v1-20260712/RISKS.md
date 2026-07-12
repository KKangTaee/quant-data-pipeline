# Risks

- provider 일시 장애가 Final Review 승격을 영구 차단하지 않도록 실패 상태와 source mapping 한계를 구분해야 한다.
- 수집 성공만으로 저장 validation이나 Final Review report를 최신으로 간주하면 안 된다.
- legacy saved validation의 audit history를 재작성하거나 삭제하지 않는다.

## Closeout

- 위 위험은 Gate / read-only recovery / explicit rerun 계약으로 방어했다.
- provider 장애 시 재시도 횟수, backoff, 운영자 override는 이번 v1 범위가 아니며 별도 정책이 필요하다.
- 기간 밖 stress, 미구현 검증, historical survivorship source, 세금·계좌 판단은 자동 수집으로 해결되지 않는 잔여 제한이다.
