# Risks

- latest-common row를 strategy signal 또는 rebalance row로 잘못 사용하면 look-ahead 또는 가짜 rebalance가 생길 수 있다. valuation date와 signal date를 분리해야 한다.
- 모든 REVIEW를 blocker로 바꾸면 historical source 미구현 때문에 후보 workflow가 영구 정지할 수 있다.
- accepted limit를 너무 쉽게 허용하면 중요한 evidence gap을 사용자 확인 문구로 우회할 수 있다. applicability와 criticality가 Gate를 먼저 결정해야 한다.
- root issue dedup 과정에서 서로 다른 원인을 과도하게 합치면 필요한 근거를 숨길 수 있다. derived check는 보존한다.
- 고정 감점을 제거한 뒤 기존 종합 점수와 UI copy가 어긋날 수 있다. score contract migration test가 필요하다.
- 현재 registry 변경은 사용자 실행 결과다. implementation / doc commit에서 stage하거나 재작성하지 않는다.
- historical universe / delisting source 신규 수집은 이 task의 구현 범위가 아니다. dynamic universe는 근거가 없으면 defer/block해야 한다.
