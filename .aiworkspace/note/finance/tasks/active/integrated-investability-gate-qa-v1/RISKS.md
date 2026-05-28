# Risks

- Integrated gate contract가 너무 좁으면 개별 audit 연결은 통과해도 조합 상태에서 selected-route가 잘못 열릴 수 있다.
- Older validation rows without newer audit payloads may still require revalidation before selection.
- 이 QA는 gate 조합을 고정하지만, historical universe / delisting source 자체를 수집하지는 않는다.
