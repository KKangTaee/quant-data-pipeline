# Risks

- collection result status schema가 collector마다 다를 수 있으므로 summary normalizer는 알려진 status를 보수적으로 분류해야 한다.
- progress를 별도 Streamlit panel로 복원하면 one-shell이 다시 분리되므로 read model과 React surface에 통합한다.
- 자동 replay는 명시적 수집/검증 경계와 부분 실패 해석을 흐리므로 이번 범위에서 제외한다.
- actual provider 재수집은 외부 state와 run history를 변경하므로 fixture/in-memory lifecycle QA를 우선하고 실제 수집은 사용자가 이미 만든 state를 읽는 범위로 제한한다.
- 실제 collector 조합별 장시간/부분 실패 UX는 사용자 실행 시 추가 관찰할 수 있지만, summary normalizer와 partial Browser fixture로 전체 성공 오표시는 방지했다.
- branch 전체 `test_service_contracts.py`에는 current one-shell 이전 static contract를 포함한 18개 실패가 있어 전체 suite green은 아니다. 이번 변경 소유 테스트, 핵심 서비스 계약, compile/build/Browser QA는 green이다.
