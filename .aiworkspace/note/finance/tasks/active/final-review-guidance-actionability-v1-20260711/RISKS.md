# Risks

- 오래된 evidence payload는 신규 구조 필드가 없으므로 기존 row/metric을 안전하게 정규화해야 한다.
- 모든 패턴에 직접 scenario 결과가 있는 것은 아니므로 추론과 관측 근거를 명확히 구분해야 한다.
- Browser QA는 로컬 앱 기동 및 in-app Browser 접근 가능 여부에 따라 제한될 수 있다.

## Closeout

- 기존 payload 호환은 named adapter fallback과 focused contract test로 확인했다.
- 직접 scenario 근거가 없는 rate / duration 등은 `추가 검증 필요`로 제한해 단정하지 않는다.
- Browser QA는 현재 worktree 전용 8502 포트에서 완료했다. 별도 worktree의 8501 프로세스는 변경하지 않았다.
