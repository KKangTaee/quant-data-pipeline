# Portfolio Monitoring Item Builder UX Fix V1 Risks

## Closed Risks

1. Streamlit iframe position
   - iframe 축소는 전체 workbench를 자르므로 사용하지 않는다. auto measurement로 본문 높이를 보존하고 drawer panel만 560px로 제한해 footer 가시성을 확인했다.
2. Catalog recovery input
   - recovery payload는 Python과 React 양쪽에서 enum/field whitelist를 적용하며 persistence command로 사용하지 않는다.
3. Entry readiness timing
   - blur lookup 제거로 exact effective-date 확인은 add command까지 지연된다. review는 `등록 시 확정`을 표시하고 backend blocker가 권위를 유지한다.
4. Recovery replay
   - Streamlit가 같은 recovery object를 새 identity로 전달해도 stable content key가 이미 소비된 snapshot 재적용을 막는다. 새 drawer command id는 새 recovery로 구분된다.
