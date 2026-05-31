# Ingestion Console UX / Data Quality V1 Plan

Status: Active
Created: 2026-06-01

## Goal

`Workspace > Ingestion`을 사용자가 이해하기 쉬운 수집 운영 콘솔로 정리한다.

1차 범위는 기존 수집 자유도, 특히 사용자가 원하는 심볼 / 기간 / 소스 / 범위를 직접 정하는 형식을 유지하면서,
job 의미, 저장 위치, downstream 사용처, 데이터 품질 한계를 더 명확하게 보여주는 것이다.

## 이걸 하는 이유?

Ingestion은 Backtest / Practical Validation / Overview가 필요한 DB-backed 데이터를 채우는 핵심 입구다.
하지만 현재 화면은 영어 job 이름과 초창기 운영 설명이 많아, 사용자가 무엇을 수집하는지와 수집 데이터가 검증에 충분한지 판단하기 어렵다.
이 작업은 수집 기능을 더 안전하고 이해 가능한 사용자 흐름으로 바꾸기 위한 첫 단계다.

## Scope

- Ingestion UI 섹션 / 탭 / 카드 언어를 한글 목적형으로 정리한다.
- 각 주요 job에 목적, 저장 테이블, 사용 위치, 품질 주의사항을 표시한다.
- 결과 summary에서 내부 job id보다 사용자-facing job 이름과 다음 액션을 먼저 보여준다.
- 이미 구현되어 있으나 화면에 노출되지 않은 lifecycle evidence job을 Ingestion에서 실행할 수 있게 한다.
- 기존 수집 입력 형식인 심볼 / 기간 / 소스 / 옵션 선택은 유지한다.

## Out Of Scope

- DB schema 변경
- 새 외부 provider connector 추가
- provider raw response 저장 정책 변경
- Backtest / Practical Validation scoring 정책 변경
- live approval, broker order, auto rebalance

## Stop Condition

- `Workspace > Ingestion`에서 핵심 수집 job들이 한글 목적명과 품질 안내를 갖는다.
- lifecycle 보강 job이 UI dispatch와 화면에 연결된다.
- compile 검증과 가능한 Browser QA를 완료한다.
- task 문서, root handoff log, 필요한 durable docs가 정렬된다.
