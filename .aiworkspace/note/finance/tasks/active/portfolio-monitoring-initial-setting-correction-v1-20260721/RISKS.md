# Portfolio Monitoring Initial Setting Correction V1 Risks

- 시작일만 바꾸고 entry close/history load 범위를 그대로 두면 최초 투자금과 가치곡선이 잘못된다.
- group timeline이 원본 item date를 계속 읽으면 개별 lane과 그룹 KPI가 불일치한다.
- 새 시작일보다 이른 기존 buy/sell을 허용하면 음의 시간 순서가 생긴다.
- 기존 initial correction row의 optional date가 비어 있는 경우 원본 item fallback이 필요하다.
- existing table에 additive column 적용이 실제 운영 DB에서도 idempotent한지 schema migration 검증이 필요하다.
