# Today Live Island Rerun Isolation V1 Risks

## Open Risks

- Streamlit component를 shell/island로 나누면 iframe 높이와 반응형 간격이 달라질 수 있어 desktop·760·420px actual QA가 필요하다.
- 실제 OPEN 시간에만 확인 가능한 provider completion timing은 deterministic fixture로 먼저 검증하고 실측 gap을 별도로 남겨야 한다.
- OPEN portfolio fragment의 매우 짧은 Streamlit running indicator까지 완전히 제거하려면 별도 API/push architecture가 필요하지만 이번 범위에는 포함하지 않는다.
