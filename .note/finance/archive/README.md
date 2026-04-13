# Finance Archive Notes

## 목적

이 폴더는 root 로그를 가볍게 유지하기 위해
한 시점의 전체 로그를 안전하게 보관해 두는 archive 위치다.

이번 first-pass 압축에서는:

- 기존 root `WORK_PROGRESS.md`
- 기존 root `QUESTION_AND_ANALYSIS_LOG.md`

를 그대로 이 폴더로 옮기고,
root에는 현재 active context만 남긴 concise 버전을 다시 만들었다.

## 현재 archive 파일

- `WORK_PROGRESS_ARCHIVE_20260413.md`
  - 2026-04-13 시점까지 누적된 full work log
- `QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md`
  - 2026-04-13 시점까지 누적된 full question/analysis log

## 읽는 순서

1. 먼저 root `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`를 본다
2. 과거 세부 히스토리가 필요할 때만 이 archive를 연다

## 왜 이렇게 두는가

- root 로그가 너무 커지면 다음 작업에서 context를 다시 잡는 속도가 느려진다
- 반대로 세부 히스토리를 지우면 과거 판단 근거를 잃는다

그래서 현재는:

- root = current active context
- archive = full historical detail

구조로 유지한다.
