# Design

Status: Active
Last Updated: 2026-07-10

## Problem

The current Final Review investment report uses bordered cards at almost every level: outer report, facts, decision summary, evidence list, interpretation, scorecard, handoff, improvement, and Level2 review. This makes the page feel like boxes inside boxes and gives first-read summary items the same visual weight as lower-level diagnostics.

## Direction

- The report body should look like one document, not a dashboard made of repeated cards.
- The top hero owns the main decision and score.
- Candidate metadata becomes a chip-like strip, not four cards.
- Decision summary becomes two columns: `왜 후보인가` and `무엇을 확인해야 하나`.
- Strengths and watch items become row lists with Korean labels.
- Detailed scorecard / Level2 / handoff / improvement / review disposition move into disclosure sections below the first-read surface.

## Boundary

React remains display-only. It receives the existing Python report payload and chooses which fields are visible first. The service read model, scorecard semantics, route decision, save readiness, Monitoring handoff, provider/DB fetch, registry, saved JSONL, and run history are not changed.
