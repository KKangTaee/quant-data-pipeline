# Today Live Island Rerun Isolation V1 Risks

## Residual Risks

- shell/island iframe 높이와 반응형 간격은 desktop·760·420px actual QA에서 overflow 0으로 닫았다.
- 실제 OPEN 시간에만 확인 가능한 provider completion timing은 deterministic 계약으로 검증했으며 실측 gap은 남아 있다.
- OPEN portfolio fragment의 매우 짧은 Streamlit running indicator까지 완전히 제거하려면 별도 API/push architecture가 필요하지만 이번 범위에는 포함하지 않는다.
