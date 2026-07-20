# Overview Sentiment CNN Endpoint Label Design

Date: 2026-07-20
Status: Approved by user request

## Problem

The CNN chart renders `37.1 · 공포` directly beside the final point. When the last few observations are close together, this text covers the line and makes the most recent path harder to read. The same value, state, and date already appear in the chart header.

## Approved Design

- Remove only the always-visible SVG text beside the CNN final point.
- Keep the circular final-point marker so the series endpoint remains visible.
- Keep the chart-header latest state, value, and date.
- Keep hover guide, point, and tooltip behavior unchanged.
- Do not change AAII charts, chart dimensions, data, colors, or aligned-period behavior.

This avoids duplicated information and prevents a responsive label-placement problem rather than moving the collision to another part of the graph.

## Verification

- A React source contract must fail while the endpoint text expression exists.
- The focused contract and the full Overview React contract class must pass after removal.
- The production component build and static distribution must succeed.

