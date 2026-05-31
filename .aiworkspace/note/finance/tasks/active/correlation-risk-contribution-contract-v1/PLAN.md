# Correlation / Risk Contribution Contract V1 Plan

Status: Complete
Created: 2026-05-29

## Goal

Phase 11의 11-3으로 existing component return correlation / risk contribution evidence를 read-only audit contract로 분리한다.

이걸 하는 이유?

- 목표 비중과 holdings overlap이 괜찮아 보여도 실제 성과 변동은 특정 component나 같은 risk source에 몰릴 수 있다.
- 기존 Practical Validation diagnostic의 correlation / risk contribution proxy와 Robustness Lab의 drop-one dependency를 Final Review에서 같은 의미로 읽게 한다.
- component return matrix가 없거나 proxy-only이면 실전 판단에서 `PASS`처럼 보이지 않게 한다.

## Scope

- `app/services/backtest_risk_contribution_audit.py` 추가
- Practical Validation result에 `risk_contribution_audit`와 display rows 연결
- Practical Validation / Final Review 화면에서 audit summary 표시
- Final Review decision snapshot / evidence rows에 audit payload 보존
- focused service contract tests 추가

## Out Of Scope

- covariance / marginal contribution full model
- raw return matrix / covariance artifact 저장
- selected-route gate policy enforcement
- 신규 strategy runtime perturbation
- user memo / preset / comment persistence
- broker order / live approval / auto rebalance

## Completion Criteria

- computed component return matrix가 있을 때 correlation / risk contribution rows를 표시한다.
- component return matrix가 없으면 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- high correlation, concentrated risk contribution, drop-one dependency를 `REVIEW`로 고정한다.
- raw return matrix나 covariance artifact를 저장하지 않는다.

## Completion Result

- `risk_contribution_audit_v1` is implemented as a read-only service contract.
- Practical Validation and Final Review show the same compact risk contribution rows.
- Final Review snapshots and evidence rows preserve the audit without adding new persistence surfaces.
