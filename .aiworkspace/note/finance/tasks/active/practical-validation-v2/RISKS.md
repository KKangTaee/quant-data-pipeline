# RISKS - Practical Validation V2

Status: Active
Last Updated: 2026-05-12

## P1 - Provider coverage is still partial

일부 ETF issuer / endpoint는 아직 완전 자동 수집을 보장하지 않는다.
P2 closeout 기준은 완전한 전 ETF 지원이 아니라, 부족 데이터를 명확히 표시하는 것이다.

## P1 - Stress coverage can remain REVIEW

현재 stress window 중 일부는 candidate period / curve granularity / runtime replay 한계 때문에 REVIEW로 남을 수 있다.
이 상태는 pass가 아니라 Final Review에서 확인해야 하는 trigger다.

## P2 - Source origin confusion

official row와 DB bridge row를 병합하면 PASS가 가능하지만, 사용자가 모든 값이 official source라고 오해하면 안 된다.
UI와 compact evidence에는 `official + db_bridge` 같은 origin이 유지되어야 한다.
