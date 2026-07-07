# Practical Validation Flow4 Action Steps V3 Notes

- 문제 원인: `resolution_guide.next_action`이 non-PASS row의 action들을 slash-joined string으로 만들고, Flow 4 UI가 이를 문단으로 그대로 렌더링했다.
- 결정: `next_action`은 compatibility summary로 유지하되, visible Flow 4 `해결 방법`은 `action_steps` list를 우선한다.
- 구성 원칙: row별 `Next Action`이 있으면 가장 구체적인 사용자 action으로 우선 노출하고, 기준별 기본 action guide는 보강 / 재검증 같은 후속 단계로 붙인다.
- Data Coverage는 provider gap 보강과 DB price ingestion, Flow 2 재검증이 한 흐름 안에서 보여야 한다.
