# 조사

09:14:50 실행은 QQQ/SOXX 2026-08-24, 나머지 6개는 2026-08-05였다. 09:15:08 실행은 QQQ/SOXX만 09-18로 갱신됐다. 모든 6개 ETF의 profile_status는 active였다.

strict_factor freshness classifier의 30일 초과 heuristic이 refresh service에서 수집 불가로 취급된 것이 원인이다. provider의 실제 미제공을 확인한 판단이 아니었다.

실제 수집 시 6개 모두 provider 응답 정상, 186개 일봉이 저장됐다. 따라서 이번 문제는 upstream 제공 불능이 아닌 age-only 추정에 의한 사전 제외였음이 운영 실행으로도 확인됐다.
