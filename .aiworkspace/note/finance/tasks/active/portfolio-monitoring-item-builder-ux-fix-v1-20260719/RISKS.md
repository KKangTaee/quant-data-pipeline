# Portfolio Monitoring Item Builder UX Fix V1 Risks

## Closed Risks

1. Streamlit iframe position
   - drawer frame is embedded below the Streamlit app header, so 560px is intentionally smaller than the 720px QA viewport. Browser QA에서 footer 가시성을 확인했다.
2. Catalog recovery input
   - recovery payload는 Python과 React 양쪽에서 enum/field whitelist를 적용하며 persistence command로 사용하지 않는다.
3. Entry readiness timing
   - blur lookup 제거로 exact effective-date 확인은 add command까지 지연된다. review는 `등록 시 확정`을 표시하고 backend blocker가 권위를 유지한다.
