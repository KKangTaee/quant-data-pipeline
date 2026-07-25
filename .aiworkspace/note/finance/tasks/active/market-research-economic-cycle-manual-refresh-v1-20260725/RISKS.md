# Risks

Last Updated: 2026-07-25

## Remaining Risks

- 사용자가 대화에 제공한 API key는 chat history에 노출되었으므로 설정 완료 후 rotation이
  권장된다.
- weekday target은 미국 공휴일을 구분하지 않는다. provider에 신규 release가 없어도 PIT
  cutoff 날짜로 materialize될 수 있다는 의미를 UI가 과장하지 않아야 한다.
- actual refresh는 앞으로도 provider/network 및 17-series 응답 상태에 의존한다.
- broad service contract의 18개 기존 Backtest/AAII/Futures failure는 이 task 범위 밖의
  baseline drift로 남아 있다.
- repository-wide UI/engine boundary check는 기존
  `app/services/backtest_workflow_shell.py -> app.web.backtest_workflow_routes` import
  1건으로 실패한다. 이 task의 변경 파일에는 해당 역방향 import가 없다.

## Mitigations

- secret-aware local write와 tracked diff scan을 수행한다.
- `override=False`, last-good preservation, persisted postcondition을 tests로 고정한다.
- monthly history count/checksum을 actual refresh 전후 비교한다.
- generated artifact와 unrelated files를 stage하지 않는다.
- tracked `.gitignore`와 shared local exclude를 함께 적용했고 세 worktree `.env`가 모두
  ignored인지 확인했다.
- actual refresh에서 monthly history checksum과 target business key를 확인했다.
