# Risks

- finding_kind가 raw status와 별도 truth source가 되면 분류 drift가 생길 수 있다. closure resolution class와 audit applicability를 입력으로만 사용하고 UI에서 재계산하지 않는다.
- accepted limit를 지나치게 넓게 허용하면 중요한 evidence gap을 Final Review 판단으로 우회할 수 있다. criticality와 applicability가 먼저 Gate를 결정해야 한다.
- current two-component React surface를 즉시 삭제하면 legacy source contract와 fallback 회귀가 커질 수 있다. active render를 먼저 교체하고 물리 삭제는 usage audit 후 결정한다.
- source / profile / replay intent를 React에 노출해도 Python session과 current validation id를 재검증하지 않으면 stale action이 실행될 수 있다.
- single component 100%와 underlying holdings concentration을 구분하지 않으면 포트폴리오 성격을 잘못 설명할 수 있다.
- 긴 raw evidence를 one-shell에 다시 모두 넣으면 Final Review 개편 전과 같은 card / guide 과잉으로 돌아갈 수 있다.
- 실제 PASS audit row를 모두 first-read 카드로 펼치면 다시 정보 과잉이 될 수 있다. first-read verified card는 최대 8개로 제한하고 전체 row는 disclosure에서 확인한다.
- structured measurement가 없는 prose를 `measured_caution`으로 해석하면 숫자를 발명하게 된다. observation과 threshold / comparator가 모두 있는 경우만 해당 finding_kind를 만든다.
- React build와 Python payload schema를 함께 변경한 뒤 장기 실행 Streamlit process가 stale module / bundle을 들 수 있으므로 Browser QA 전 재기동이 필요하다.
- protected registry와 run history는 사용자 실사용 결과다. 구현 / QA / docs commit에서 stage하거나 rewrite하지 않는다.
