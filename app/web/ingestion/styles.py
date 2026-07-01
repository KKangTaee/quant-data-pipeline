"""Responsive CSS for Workspace > Ingestion."""

from __future__ import annotations

import streamlit as st


def install_ingestion_responsive_styles() -> None:
    st.markdown(
        """
        <style>
          .ingestion-meta-list {
            display: grid;
            gap: 0.5rem;
            margin: 0.35rem 0 0.65rem;
          }
          .ingestion-meta-row {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            gap: 0.35rem 0.45rem;
            min-width: 0;
          }
          .ingestion-meta-label {
            color: #7a7f8c;
            font-size: 0.9rem;
            font-weight: 700;
            line-height: 1.35;
            white-space: nowrap;
          }
          .ingestion-pill {
            background: rgba(125, 130, 150, 0.12);
            border: 1px solid rgba(49, 51, 63, 0.08);
            border-radius: 0.4rem;
            color: #246b3f;
            display: inline-block;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.8rem;
            line-height: 1.35;
            max-width: 100%;
            overflow-wrap: anywhere;
            padding: 0.12rem 0.36rem;
            word-break: break-word;
          }
          .ingestion-text-value {
            color: inherit;
            display: inline-block;
            line-height: 1.35;
            max-width: 100%;
            overflow-wrap: anywhere;
            word-break: keep-all;
          }
          .ingestion-text-value + .ingestion-text-value::before {
            color: #8b909b;
            content: " · ";
          }
          .ingestion-stat-grid {
            display: grid;
            gap: 0.65rem;
            grid-template-columns: repeat(auto-fit, minmax(7.5rem, 1fr));
            margin: 0.75rem 0 0.95rem;
          }
          .ingestion-stat-card {
            background: rgba(125, 130, 150, 0.08);
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 0.5rem;
            min-width: 0;
            padding: 0.72rem 0.82rem;
          }
          .ingestion-stat-card.status-success {
            background: #eaf8ef;
            border-color: rgba(34, 139, 73, 0.22);
          }
          .ingestion-stat-card.status-success .ingestion-stat-value,
          .ingestion-stat-card.status-success .ingestion-stat-label {
            color: #14783f;
          }
          .ingestion-stat-card.status-partial_success {
            background: #fff7e6;
            border-color: rgba(184, 121, 0, 0.22);
          }
          .ingestion-stat-card.status-partial_success .ingestion-stat-value,
          .ingestion-stat-card.status-partial_success .ingestion-stat-label {
            color: #8a5a00;
          }
          .ingestion-stat-card.status-failed {
            background: #fff0f0;
            border-color: rgba(210, 56, 56, 0.22);
          }
          .ingestion-stat-card.status-failed .ingestion-stat-value,
          .ingestion-stat-card.status-failed .ingestion-stat-label {
            color: #9f2626;
          }
          .ingestion-stat-label {
            color: #6f7480;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.25;
            overflow-wrap: anywhere;
          }
          .ingestion-stat-value {
            color: inherit;
            font-size: clamp(1.55rem, 4.5vw, 2.35rem);
            font-weight: 760;
            letter-spacing: 0;
            line-height: 1.08;
            margin-top: 0.32rem;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .ingestion-meta-grid {
            display: grid;
            gap: 0.65rem;
            grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
            margin: 0.35rem 0 0.75rem;
          }
          .ingestion-meta-card {
            background: rgba(125, 130, 150, 0.08);
            border: 1px solid rgba(49, 51, 63, 0.09);
            border-radius: 0.5rem;
            min-width: 0;
            padding: 0.62rem 0.72rem;
          }
          .ingestion-meta-card-label {
            color: #6f7480;
            font-size: 0.76rem;
            font-weight: 700;
            line-height: 1.2;
          }
          .ingestion-meta-card-value {
            color: inherit;
            font-size: 1rem;
            font-weight: 650;
            line-height: 1.3;
            margin-top: 0.26rem;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .ingestion-select-caption {
            color: inherit;
            font-size: 0.9rem;
            line-height: 1.35;
            margin: -0.25rem 0 0.45rem;
            overflow-wrap: anywhere;
          }
          .ingestion-workflow-grid {
            display: grid;
            gap: 0.75rem;
            grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
            margin: 0.85rem 0 1.1rem;
          }
          .ingestion-workflow-card {
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 0.5rem;
            min-width: 0;
            padding: 0.78rem 0.86rem;
          }
          .ingestion-workflow-step {
            color: #6f7480;
            font-size: 0.75rem;
            font-weight: 800;
            line-height: 1.2;
            text-transform: uppercase;
          }
          .ingestion-workflow-title {
            font-size: 0.98rem;
            font-weight: 760;
            line-height: 1.25;
            margin-top: 0.18rem;
          }
          .ingestion-workflow-body {
            color: #6f7480;
            font-size: 0.84rem;
            line-height: 1.4;
            margin-top: 0.28rem;
            overflow-wrap: anywhere;
          }
          .ingestion-contract-panel,
          .ingestion-callout {
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 0.5rem;
            margin: 0.7rem 0 0.9rem;
            padding: 0.8rem 0.9rem;
          }
          .ingestion-callout.warning {
            background: #fff7e6;
            border-color: rgba(184, 121, 0, 0.24);
          }
          .ingestion-callout.danger {
            background: #fff0f0;
            border-color: rgba(210, 56, 56, 0.24);
          }
          .ingestion-callout.info {
            background: rgba(41, 111, 214, 0.08);
            border-color: rgba(41, 111, 214, 0.18);
          }
          .ingestion-callout.success {
            background: #eaf8ef;
            border-color: rgba(34, 139, 73, 0.22);
          }
          .ingestion-callout-title,
          .ingestion-contract-title {
            font-size: 0.95rem;
            font-weight: 800;
            line-height: 1.25;
          }
          .ingestion-callout-body {
            font-size: 0.9rem;
            line-height: 1.45;
            margin-top: 0.32rem;
            overflow-wrap: anywhere;
          }
          .ingestion-contract-grid {
            display: grid;
            gap: 0.52rem;
            grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
            margin-top: 0.62rem;
          }
          .ingestion-contract-item {
            min-width: 0;
          }
          .ingestion-contract-label {
            color: #6f7480;
            font-size: 0.74rem;
            font-weight: 800;
            line-height: 1.2;
          }
          .ingestion-contract-value {
            font-size: 0.94rem;
            font-weight: 650;
            line-height: 1.32;
            margin-top: 0.18rem;
            overflow-wrap: anywhere;
          }
          .ingestion-contract-note {
            color: #6f7480;
            font-size: 0.83rem;
            line-height: 1.4;
            margin-top: 0.62rem;
            overflow-wrap: anywhere;
          }
          @media (max-width: 760px) {
            div[data-testid="column"] {
              flex: 1 1 100% !important;
              max-width: 100% !important;
              min-width: 0 !important;
              width: 100% !important;
            }
            .ingestion-stat-grid {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .ingestion-meta-grid {
              grid-template-columns: minmax(0, 1fr);
            }
            .ingestion-workflow-grid,
            .ingestion-contract-grid {
              grid-template-columns: minmax(0, 1fr);
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
