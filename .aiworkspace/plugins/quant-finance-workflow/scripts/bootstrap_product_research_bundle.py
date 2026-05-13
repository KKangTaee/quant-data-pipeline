#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from textwrap import dedent


# scripts live under .aiworkspace/plugins/quant-finance-workflow/scripts.
REPO_ROOT = Path(__file__).resolve().parents[4]
FINANCE_NOTE_DIR = REPO_ROOT / ".aiworkspace" / "note" / "finance"
RESEARCHES_DIR = FINANCE_NOTE_DIR / "researches"
ACTIVE_RESEARCH_DIR = RESEARCHES_DIR / "active"

REQUIRED_FILES = [
    "RESEARCH_PLAN.md",
    "CURRENT_PROJECT_AUDIT.md",
    "BENCHMARKS.md",
    "UI_PATTERNS.md",
    "FEATURE_CANDIDATES.md",
    "RECOMMENDATION.md",
    "SOURCES.md",
    "RISKS.md",
]


def _slugify(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return re.sub(r"-+", "-", token) or "product-research"


def _validate_research_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise argparse.ArgumentTypeError(
            "research id must use only letters, numbers, dot, underscore, or hyphen"
        )
    return value


def _research_id(title: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    return f"{date.today():%Y-%m}-{_slugify(title)}"


def _research_plan(title: str, focus: str) -> str:
    return dedent(
        f"""\
        # {title} Research Plan

        ## Why This Work Exists

        {focus}

        ## Research Questions

        | Question | Decision this supports |
        | --- | --- |
        | What exists in the current finance project? | Identify real product strengths, gaps, and constraints. |
        | What do comparable products or patterns show? | Separate durable patterns from copied features. |
        | Which opportunities are worth considering? | Build a narrow, evidence-backed candidate list. |
        | What should happen next? | Distinguish immediate build candidates from roadmap options and parking-lot ideas. |

        ## Scope

        Include:

        - current finance project audit
        - comparable product, service, framework, or workflow benchmarks
        - recurring UI/workflow/data/evidence patterns
        - feature candidates and recommendation

        Exclude:

        - direct implementation
        - roadmap changes without human approval
        - live trading, broker order, or auto rebalance unless the product boundary changes

        ## Method

        1. Audit local product structure and workflow.
        2. Research current external benchmarks from primary sources.
        3. Extract reusable patterns and conflicts with project boundaries.
        4. Score feature candidates by impact, effort, risk, confidence, and fit.
        5. Write a recommendation with immediate, next, later, and parking-lot scope.

        ## Outputs

        | File | Role |
        | --- | --- |
        | `CURRENT_PROJECT_AUDIT.md` | Current finance product facts, strengths, weaknesses, boundaries. |
        | `BENCHMARKS.md` | External benchmark notes with evidence labels. |
        | `UI_PATTERNS.md` | Recurring workflow and interface patterns. |
        | `FEATURE_CANDIDATES.md` | Candidate features and prioritization. |
        | `RECOMMENDATION.md` | Final recommendation and handoff. |
        | `SOURCES.md` | Local and web sources with access dates. |
        | `RISKS.md` | Open questions, evidence limits, and follow-up risks. |
        """
    )


def _audit(title: str) -> str:
    return dedent(
        f"""\
        # Current Project Audit

        ## Snapshot

        Summarize the current finance project state relevant to `{title}`.

        ## Local Evidence

        | Area | Local source | What it proves |
        | --- | --- | --- |
        | Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | TBD |
        | Roadmap | `.aiworkspace/note/finance/docs/ROADMAP.md` | TBD |
        | Project map | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | TBD |

        ## Surface Classification

        | Surface | User-facing / internal / mixed | Notes |
        | --- | --- | --- |
        | TBD | TBD | TBD |

        ## Strengths

        - TBD

        ## Weaknesses

        - TBD

        ## Product Boundaries

        - Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
        - Do not turn research output into roadmap commitment without user approval.

        ## Audit Conclusion

        TBD
        """
    )


def _benchmarks() -> str:
    return dedent(
        """\
        # Benchmarks

        Evidence labels:

        - `Observed`: official UI/docs directly show the pattern.
        - `Documented`: official docs or repository describe the pattern.
        - `Claimed`: product page or marketing copy claims the pattern.
        - `Inferred`: synthesis from multiple supported facts.
        - `Unknown`: evidence is missing or unclear.

        ## Benchmark Matrix

        | Product / Service | Category | Evidence | Relevant pattern |
        | --- | --- | --- | --- |
        | TBD | TBD | Unknown | TBD |

        ## Key Findings

        ### 1. TBD

        - TBD

        ## Benchmark-Informed Gaps

        | Gap | Source pattern | Finance implication |
        | --- | --- | --- |
        | TBD | TBD | TBD |
        """
    )


def _ui_patterns() -> str:
    return dedent(
        """\
        # UI And Workflow Patterns

        ## Product Goal

        TBD

        ## Pattern 1. TBD

        - TBD

        ## Pattern 2. TBD

        - TBD

        ## Pattern 3. TBD

        - TBD

        ## Pattern Conflicts With Current Boundaries

        | Pattern | Conflict | Handling |
        | --- | --- | --- |
        | TBD | TBD | TBD |
        """
    )


def _feature_candidates() -> str:
    return dedent(
        """\
        # Feature Candidates

        Scoring: 1 low, 5 high.

        | Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
        | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
        | P0 | TBD | 0 | 0 | 0 | 0 | 0 | TBD |

        ## P0. TBD

        Goal:

        - TBD

        Evidence:

        - Audit: TBD
        - Benchmark: TBD

        Dependencies:

        - TBD

        Success criteria:

        - TBD

        ## Parking Lot

        - TBD
        """
    )


def _recommendation() -> str:
    return dedent(
        """\
        # Recommendation

        ## One-Line Recommendation

        TBD

        ## Why This Direction

        TBD

        ## Recommended 1st Build Scope

        ### Step 1. TBD

        - TBD

        ## Recommended Next Phase After 1st Build

        | Phase | Output | Why |
        | --- | --- | --- |
        | TBD | TBD | TBD |

        ## What Not To Do Yet

        - TBD

        ## Decision Rules

        Proceed when:

        - TBD

        ## Final Recommendation

        TBD
        """
    )


def _sources() -> str:
    return dedent(
        f"""\
        # Sources

        Access date: {date.today():%Y-%m-%d}

        Evidence labels:

        - `Observed`: official UI/docs directly show the pattern.
        - `Documented`: official docs or repository describe the pattern.
        - `Claimed`: product page or marketing copy claims the pattern.
        - `Inferred`: synthesis from multiple supported facts.
        - `Unknown`: evidence is missing or unclear.

        ## Local Sources

        | Source | Evidence | Notes |
        | --- | --- | --- |
        | TBD | Unknown | TBD |

        ## Web Sources

        | Source | Evidence | Notes |
        | --- | --- | --- |
        | TBD | Unknown | TBD |

        ## Source Notes

        - Prefer current, official, primary sources.
        - Treat product marketing pages as feature-pattern evidence, not verified technical capability.
        """
    )


def _risks() -> str:
    return dedent(
        """\
        # Risks

        ## Product Risks

        | Risk | Impact | Mitigation |
        | --- | --- | --- |
        | Research output is mistaken for approved roadmap | High | Keep recommendation as evidence until user approval. |

        ## Technical Risks

        | Risk | Impact | Mitigation |
        | --- | --- | --- |
        | TBD | TBD | TBD |

        ## Research Gaps

        | Gap | Why it matters | Follow-up |
        | --- | --- | --- |
        | TBD | TBD | TBD |
        """
    )


def _templates(title: str, focus: str) -> dict[str, str]:
    return {
        "RESEARCH_PLAN.md": _research_plan(title, focus),
        "CURRENT_PROJECT_AUDIT.md": _audit(title),
        "BENCHMARKS.md": _benchmarks(),
        "UI_PATTERNS.md": _ui_patterns(),
        "FEATURE_CANDIDATES.md": _feature_candidates(),
        "RECOMMENDATION.md": _recommendation(),
        "SOURCES.md": _sources(),
        "RISKS.md": _risks(),
    }


def _write(path: Path, content: str, *, force: bool) -> str:
    if path.exists() and not force:
        return f"skip: {path} already exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"write: {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a finance product research bundle.")
    parser.add_argument("--title", required=True, help="Human-readable research title.")
    parser.add_argument("--focus", default="", help="One or two sentences explaining why this research exists.")
    parser.add_argument("--research-id", type=_validate_research_id, help="Folder name under researches/active.")
    parser.add_argument("--force", action="store_true", help="Overwrite files if they already exist.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned files without writing.")
    args = parser.parse_args()

    focus = args.focus.strip() or "TBD"
    rid = _research_id(args.title, args.research_id)
    target_dir = ACTIVE_RESEARCH_DIR / rid
    templates = _templates(args.title, focus)

    if args.dry_run:
        print(f"research_id: {rid}")
        for name in REQUIRED_FILES:
            print(target_dir / name)
        print("reminder: add the bundle to .aiworkspace/note/finance/researches/README.md")
        return 0

    for name in REQUIRED_FILES:
        print(_write(target_dir / name, templates[name], force=args.force))
    print("reminder: add the bundle to .aiworkspace/note/finance/researches/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
