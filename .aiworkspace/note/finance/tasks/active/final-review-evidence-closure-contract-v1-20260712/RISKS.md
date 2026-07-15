# Risks

- latest-common row를 strategy signal 또는 rebalance row로 잘못 사용하면 look-ahead 또는 가짜 rebalance가 생길 수 있다. valuation date와 signal date를 분리해야 한다.
- 모든 REVIEW를 blocker로 바꾸면 historical source 미구현 때문에 후보 workflow가 영구 정지할 수 있다.
- accepted limit를 너무 쉽게 허용하면 중요한 evidence gap을 사용자 확인 문구로 우회할 수 있다. applicability와 criticality가 Gate를 먼저 결정해야 한다.
- root issue dedup 과정에서 서로 다른 원인을 과도하게 합치면 필요한 근거를 숨길 수 있다. derived check는 보존한다.
- 고정 감점을 제거한 뒤 기존 종합 점수와 UI copy가 어긋날 수 있다. score contract migration test가 필요하다.
- 현재 registry 변경은 사용자 실행 결과다. implementation / doc commit에서 stage하거나 재작성하지 않는다.
- historical universe / delisting source 신규 수집은 이 task의 구현 범위가 아니다. dynamic universe는 근거가 없으면 defer/block해야 한다.

## Closeout Residuals

- dynamic historical universe는 PIT membership / delisting provider가 없으므로 의도대로 `engineering_required + critical`에서 멈춘다.
- weighted portfolio의 component별 마지막 날짜는 다를 수 있다. portfolio 월간 결과와 GRS의 `latest_common_price_date / last_complete_rebalance_date / latest_valuation_date`를 혼동하지 않아야 한다.
- 과거 validation row는 새 closure payload가 없어서 legacy read adapter로 계속 읽는다. 기존 JSONL row는 rewrite하지 않았다.
- score effect를 만들 새 measurement adapter는 observed / threshold / comparison / target dimension / explicit effect를 모두 저장해야 한다. 정성 REVIEW에는 숫자 감점을 다시 도입하지 않는다.

## Follow-up UX Residual

- Flow 3의 accepted-limit 개수는 Final Review로 넘길 판단 입력 수이지 이미 수용이 완료됐다는 뜻이 아니다. 상세 항목과 terminal state는 Final Review에서 확인하고 종결해야 한다.

## Decision Workspace Continuation

- 시작 기준선의 Practical Validation boundary test 2개는 기능 회귀가 아니라 `source=source` 인자 추가를 반영하지 못한 source-string drift다. 3차에서 Final Review boundary contract를 교체할 때 함께 정리하고 전체 suite에서 재확인한다.
- candidate/benchmark는 interpolation 없이 exact common date만 사용한다. 비동기 월말 series가 2점 미만으로 줄면 상대성과를 만들지 않고 `unmeasured`로 남긴다.
- cost application proof가 없는 stored curve는 net 성과로 승격하지 않는다. 이 gap은 disclosure에 남고 cost 관측값은 강점/약점으로 분류하지 않는다.
- React candidate/decision intent는 presentation event일 뿐이다. source eligibility, route capability, duplicate decision ID, append는 계속 Python에서 재검증해야 한다.
- Browser QA는 저장 버튼 활성화까지만 확인했다. 실제 append는 4차 snapshot/persistence contract test와 기존 registry writer regression으로 검증하고 사용자 registry에는 QA row를 쓰지 않는다.

## Decision Workspace Closeout Residuals

- current GRS stored row는 structured `review_trigger_details`가 없어 Monitoring 변화 조건이 `미측정`으로 보일 수 있다. prose trigger를 임의 구조화하지 않으며, 향후 validation producer가 measurement / comparator / cadence / action을 명시해야 한다.
- missing benchmark는 interpolation이나 provider fetch로 메우지 않고 unmeasured lane과 source gap으로 남는다.
- dynamic historical universe / delisting source는 여전히 범위 밖이다. 해당 근거가 필요한 후보를 snapshot 존재만으로 selected-route에 올릴 수 없다.
- Browser QA는 protected registry mutation을 수행하지 않았다. append-only writer의 실제 UI 저장은 격리된 disposable registry가 준비된 경우에만 추가 검증한다.
