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
- `FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`
  - 예전 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 긴 `3-3. 상세 구현 메모` 원문 archive

## 읽는 순서

1. 먼저 root `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`를 본다
2. 현재 finance 시스템 구조는 root `FINANCE_COMPREHENSIVE_ANALYSIS.md`를 본다
3. 과거 세부 히스토리나 legacy 구현 메모가 필요할 때만 이 archive를 연다

## 왜 이렇게 두는가

- root 로그가 너무 커지면 다음 작업에서 context를 다시 잡는 속도가 느려진다
- 반대로 세부 히스토리를 지우면 과거 판단 근거를 잃는다

그래서 현재는:

- root = current active context
- archive = full historical detail

구조로 유지한다.

`FINANCE_COMPREHENSIVE_ANALYSIS.md`는 이제 high-level current-state map으로 관리하므로,
긴 legacy 구현 메모는 root 문서에 직접 두지 않고 archive에서 보존한다.
