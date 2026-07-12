# Notes

- 원인은 viewport 자체보다 `.fr-invest-report__review-impact > div` selector가 direct child trace list까지 2열로 만드는 cascade 충돌이다.
- Python read model과 trace payload에는 변경이 필요하지 않다.
- compact QA에서 `Universe / listing evidence`, `Survivorship / delisting control`처럼 긴 audit 문자열도 형제 카드와 동일한 전체 폭을 유지했다.
- 680px에서는 관측 / 판단 근거 label과 value가 한 열로 쌓이고 detail tab도 한 열로 전환된다.
