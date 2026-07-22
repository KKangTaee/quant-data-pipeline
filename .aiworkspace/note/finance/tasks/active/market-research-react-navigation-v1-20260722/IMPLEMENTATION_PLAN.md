# Market Research React Navigation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Market Research Streamlit/custom-HTML header and native family/view widgets with one responsive React component while preserving Python-owned canonical view, URL, session, fallback, and lazy-render contracts.

**Architecture:** `app/web/overview/navigation.py` remains the navigation state owner and builds a versioned presentation payload. A new wrapper declares `app/web/streamlit_components/market_research_navigation/component_static`, and React emits only validated `select_view` events. The existing Streamlit header and controls remain a build-missing fallback; module renderers and data paths do not change.

**Tech Stack:** Python 3.12, Streamlit 1.57 custom components, React 18, TypeScript 5.7, Vite 6, Vitest 4, Testing Library, scoped CSS, pytest, Codex in-app Browser QA.

## Global Constraints

- Preserve `/overview`, `overview_tab`, legacy slug normalization, query > widget > session precedence, and all seven canonical view identifiers.
- Keep Python as the only owner of canonical view validation, session state, query params, and renderer dispatch.
- The component may emit only `{event: {id: "select_view", view, nonce}}`; it must not fetch providers, read DB, write persistence, or choose module data.
- Keep the current Streamlit header and family/view controls as a build-missing fallback.
- Use `RESEARCH WORKSPACE`, `Market Research`, and `Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.` exactly.
- Desktop and 760px show family descriptions; at 420px descriptions remain accessible but visually hidden, families are 3 columns, and views are 2 columns without horizontal overflow.
- Selected state uses blue-gray surface, weight, and an indicator; destructive/red tone and color-only selection are prohibited.
- Do not add drawer, sticky navigation, watchlist, recent/saved research, module-body changes, or data/service changes.
- Commit canonical `component_static`; do not stage `node_modules`, QA screenshots, registry JSONL, run history, research bundles, or unrelated dirty files.

## File Structure

- Create `app/web/overview/market_research_navigation_react_component.py`: build availability, declaration, and render wrapper.
- Create `app/web/streamlit_components/market_research_navigation/`: TypeScript/React source, Vitest tests, Vite config, package metadata, and canonical static distribution.
- Modify `app/web/overview/navigation.py`: family descriptions, pure payload builder, pure event resolver, React-first selector, existing fallback extraction.
- Modify `app/web/overview/page.py`: render the current HTML header only when the React bundle is unavailable.
- Modify `tests/test_market_research_navigation.py`: Python payload, event, wrapper availability, React-first/fallback, and page ownership contracts.
- Modify the active task docs and minimal durable finance docs only during closeout.

---

### Task 1: Python Payload, Event Resolver, And Component Wrapper

**Files:**
- Create: `app/web/overview/market_research_navigation_react_component.py`
- Modify: `app/web/overview/navigation.py`
- Test: `tests/test_market_research_navigation.py`

**Interfaces:**
- Produces: `build_market_research_navigation_payload(active_view: object) -> dict[str, object]`.
- Produces: `resolve_market_research_navigation_event(current_view: object, component_value: object) -> str`.
- Produces: `market_research_navigation_react_component_available(build_dir: Path | None = None) -> bool`.
- Produces: `render_market_research_navigation(payload: dict[str, Any], *, key: str = "market_research_navigation") -> dict[str, Any] | None`.

- [ ] **Step 1: Write failing Python contract tests**

Add imports and these tests to `tests/test_market_research_navigation.py`:

```python
from app.web.overview.navigation import (
    build_market_research_navigation_payload,
    resolve_market_research_navigation_event,
)


def test_market_research_react_payload_covers_all_families_and_views():
    payload = build_market_research_navigation_payload("sp500")

    assert payload["schema_version"] == "market_research_navigation_v1"
    assert payload["active_family"] == "index-valuation"
    assert payload["active_view"] == "sp500"
    assert [row["id"] for row in payload["families"]] == [
        "market-environment",
        "index-valuation",
        "stock-research",
    ]
    assert [
        view["id"]
        for family in payload["families"]
        for view in family["views"]
    ] == list(MARKET_RESEARCH_VIEW_OPTIONS)


def test_market_research_react_event_accepts_only_canonical_view_selection():
    assert resolve_market_research_navigation_event(
        "economic-cycle",
        {"event": {"id": "select_view", "view": "us-stock", "nonce": 1}},
    ) == "us-stock"
    assert resolve_market_research_navigation_event(
        "economic-cycle",
        {"event": {"id": "select_view", "view": "broken", "nonce": 2}},
    ) == "economic-cycle"
    assert resolve_market_research_navigation_event(
        "economic-cycle",
        {"event": {"id": "other", "view": "sp500", "nonce": 3}},
    ) == "economic-cycle"
    assert resolve_market_research_navigation_event("economic-cycle", None) == "economic-cycle"


def test_market_research_react_wrapper_requires_static_index(tmp_path):
    from app.web.overview.market_research_navigation_react_component import (
        market_research_navigation_react_component_available,
    )

    assert not market_research_navigation_react_component_available(tmp_path)
    (tmp_path / "index.html").write_text("<!doctype html>", encoding="utf-8")
    assert market_research_navigation_react_component_available(tmp_path)
```

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k 'react_payload or react_event or react_wrapper'
```

Expected: collection fails because the new builder, resolver, and wrapper module do not exist.

- [ ] **Step 3: Add family descriptions and pure Python contracts**

Add to `app/web/overview/navigation.py` after `MARKET_RESEARCH_FAMILY_LABELS`:

```python
MARKET_RESEARCH_FAMILY_DESCRIPTIONS = {
    "market-environment": "경제·매크로·심리·일정",
    "index-valuation": "대표지수 멀티플과 실적",
    "stock-research": "변동 종목과 개별 기업",
}
```

Add after `market_research_default_view_for_family`:

```python
def build_market_research_navigation_payload(active_view: object) -> dict[str, object]:
    """Build the presentation-only React navigation payload."""
    canonical = normalize_market_research_view(active_view)
    families = []
    for family in MARKET_RESEARCH_FAMILY_OPTIONS:
        families.append(
            {
                "id": family,
                "label": MARKET_RESEARCH_FAMILY_LABELS[family],
                "description": MARKET_RESEARCH_FAMILY_DESCRIPTIONS[family],
                "views": [
                    {"id": view, "label": MARKET_RESEARCH_VIEW_LABELS[view]}
                    for view in market_research_views_for_family(family)
                ],
            }
        )
    return {
        "schema_version": "market_research_navigation_v1",
        "eyebrow": "RESEARCH WORKSPACE",
        "title": "Market Research",
        "description": "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.",
        "active_family": market_research_family_for_view(canonical),
        "active_view": canonical,
        "families": families,
    }


def resolve_market_research_navigation_event(
    current_view: object,
    component_value: object,
) -> str:
    """Accept only a canonical React navigation selection event."""
    canonical = normalize_market_research_view(current_view)
    if not isinstance(component_value, dict):
        return canonical
    event = component_value.get("event")
    if not isinstance(event, dict) or event.get("id") != "select_view":
        return canonical
    candidate = str(event.get("view") or "").strip().lower()
    return candidate if candidate in MARKET_RESEARCH_VIEW_OPTIONS else canonical
```

- [ ] **Step 4: Add the complete Streamlit component wrapper**

Create `app/web/overview/market_research_navigation_react_component.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


MARKET_RESEARCH_NAVIGATION_COMPONENT_NAME = "market_research_navigation"
MARKET_RESEARCH_NAVIGATION_COMPONENT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "streamlit_components"
    / "market_research_navigation"
)
MARKET_RESEARCH_NAVIGATION_BUILD_DIR = (
    MARKET_RESEARCH_NAVIGATION_COMPONENT_ROOT / "component_static"
)

_market_research_navigation_component = None


def market_research_navigation_react_component_available(
    build_dir: Path | None = None,
) -> bool:
    target = Path(build_dir) if build_dir is not None else MARKET_RESEARCH_NAVIGATION_BUILD_DIR
    return (target / "index.html").exists()


def _declare_market_research_navigation_component():
    global _market_research_navigation_component
    if not market_research_navigation_react_component_available():
        return None
    if _market_research_navigation_component is None:
        _market_research_navigation_component = components.declare_component(
            MARKET_RESEARCH_NAVIGATION_COMPONENT_NAME,
            path=str(MARKET_RESEARCH_NAVIGATION_BUILD_DIR),
        )
    return _market_research_navigation_component


def render_market_research_navigation(
    payload: dict[str, Any],
    *,
    key: str = "market_research_navigation",
) -> dict[str, Any] | None:
    component = _declare_market_research_navigation_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None


__all__ = [
    "MARKET_RESEARCH_NAVIGATION_BUILD_DIR",
    "market_research_navigation_react_component_available",
    "render_market_research_navigation",
]
```

- [ ] **Step 5: Run GREEN and commit Task 1**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k 'react_payload or react_event or react_wrapper'
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/market_research_navigation_react_component.py
git diff --check
git add app/web/overview/navigation.py app/web/overview/market_research_navigation_react_component.py tests/test_market_research_navigation.py
git commit -m "기능: Market Research React 탐색 계약 추가"
```

Expected: the three new contracts pass and compile/diff checks exit 0.

---

### Task 2: Responsive React Header And Navigation Component

**Files:**
- Create: `app/web/streamlit_components/market_research_navigation/index.html`
- Create: `app/web/streamlit_components/market_research_navigation/package.json`
- Create: `app/web/streamlit_components/market_research_navigation/package-lock.json`
- Create: `app/web/streamlit_components/market_research_navigation/tsconfig.json`
- Create: `app/web/streamlit_components/market_research_navigation/vite.config.ts`
- Create: `app/web/streamlit_components/market_research_navigation/src/contracts.ts`
- Create: `app/web/streamlit_components/market_research_navigation/src/main.tsx`
- Create: `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.tsx`
- Create: `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.test.tsx`
- Create: `app/web/streamlit_components/market_research_navigation/src/style.css`
- Generate: `app/web/streamlit_components/market_research_navigation/component_static/`

**Interfaces:**
- Consumes: the `market_research_navigation_v1` payload from Task 1.
- Emits: `{event: {id: "select_view", view: string, nonce: number}}`.
- Exports: named `MarketResearchNavigation` for Vitest and connected default export for Streamlit.

- [ ] **Step 1: Create package/test scaffolding only**

Create `package.json`:

```json
{
  "name": "market-research-navigation-component",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vite build --outDir component_static",
    "test": "vitest run",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "streamlit-component-lib": "^2.0.0",
    "typescript": "^5.7.3",
    "vite": "^6.0.7"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.9.1",
    "@testing-library/react": "^16.3.2",
    "@testing-library/user-event": "^14.6.1",
    "@types/react": "^18.3.31",
    "@types/react-dom": "^18.3.7",
    "jsdom": "^29.1.1",
    "vitest": "^4.1.10"
  }
}
```

Create `vite.config.ts`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "./",
  plugins: [react()],
  build: { sourcemap: false },
  test: { environment: "jsdom" },
});
```

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": []
}
```

Create `index.html`:

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Market Research Navigation</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Run `npm install` inside the component directory to create the exact lockfile. Do not stage `node_modules`.

- [ ] **Step 2: Write failing React behavior tests**

Create `src/MarketResearchNavigation.test.tsx`:

```tsx
import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ComponentProps } from "streamlit-component-lib";

const streamlitMocks = vi.hoisted(() => ({
  setComponentValue: vi.fn(),
  setFrameHeight: vi.fn(),
}));

vi.mock("streamlit-component-lib", () => ({
  Streamlit: streamlitMocks,
  withStreamlitConnection: <T,>(component: T) => component,
}));

import { MarketResearchNavigation } from "./MarketResearchNavigation";
import type { MarketResearchNavigationPayload } from "./contracts";

const payload: MarketResearchNavigationPayload = {
  schema_version: "market_research_navigation_v1",
  eyebrow: "RESEARCH WORKSPACE",
  title: "Market Research",
  description: "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.",
  active_family: "market-environment",
  active_view: "economic-cycle",
  families: [
    { id: "market-environment", label: "시장 환경", description: "경제·매크로·심리·일정", views: [
      { id: "economic-cycle", label: "경제 사이클" },
      { id: "futures-macro", label: "선물 매크로" },
      { id: "sentiment", label: "심리" },
      { id: "events", label: "일정" },
    ] },
    { id: "index-valuation", label: "지수 가치평가", description: "대표지수 멀티플과 실적", views: [
      { id: "sp500", label: "S&P 500" },
    ] },
    { id: "stock-research", label: "종목 리서치", description: "변동 종목과 개별 기업", views: [
      { id: "market-movers", label: "변동 종목" },
      { id: "us-stock", label: "개별 종목" },
    ] },
  ],
};

function props(value?: MarketResearchNavigationPayload): ComponentProps {
  return { args: value ? { payload: value } : {}, width: 1280 } as ComponentProps;
}

afterEach(cleanup);

describe("MarketResearchNavigation", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders one accessible heading and selected family/view states", () => {
    render(<MarketResearchNavigation {...props(payload)} />);
    expect(screen.getByRole("heading", { name: "Market Research", level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /시장 환경/ })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "경제 사이클" })).toHaveAttribute("aria-current", "page");
  });

  it("emits the target family default view once", async () => {
    const user = userEvent.setup();
    render(<MarketResearchNavigation {...props(payload)} />);
    await user.click(screen.getByRole("button", { name: /지수 가치평가/ }));
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledTimes(1);
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledWith({
      event: { id: "select_view", view: "sp500", nonce: expect.any(Number) },
    });
  });

  it("emits a local view and ignores the already active view", async () => {
    const user = userEvent.setup();
    render(<MarketResearchNavigation {...props(payload)} />);
    await user.click(screen.getByRole("button", { name: /시장 환경/ }));
    await user.click(screen.getByRole("button", { name: "선물 매크로" }));
    await user.click(screen.getByRole("button", { name: "경제 사이클" }));
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledTimes(1);
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledWith({
      event: { id: "select_view", view: "futures-macro", nonce: expect.any(Number) },
    });
  });

  it("shows a bounded empty state without a payload", () => {
    render(<MarketResearchNavigation {...props()} />);
    expect(screen.getByText("Market Research 탐색을 불러오지 못했습니다.")).toBeInTheDocument();
    expect(streamlitMocks.setComponentValue).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 3: Run React RED**

Run:

```bash
npm test
```

Expected: FAIL because `contracts.ts` and `MarketResearchNavigation.tsx` do not exist.

- [ ] **Step 4: Implement contracts and the React component**

Create `src/contracts.ts`:

```ts
export type MarketResearchView = { id: string; label: string };
export type MarketResearchFamily = {
  id: string;
  label: string;
  description: string;
  views: MarketResearchView[];
};
export type MarketResearchNavigationPayload = {
  schema_version: "market_research_navigation_v1";
  eyebrow: string;
  title: string;
  description: string;
  active_family: string;
  active_view: string;
  families: MarketResearchFamily[];
};
```

Create `src/MarketResearchNavigation.tsx`:

```tsx
import { useEffect, useRef } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import type { MarketResearchNavigationPayload } from "./contracts";
import "./style.css";

type Props = Omit<ComponentProps, "args"> & {
  args: { payload?: MarketResearchNavigationPayload };
};

export function MarketResearchNavigation({ args, width, theme }: Props) {
  const payload = args.payload;
  const rootRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const resize = () => Streamlit.setFrameHeight();
    resize();
    window.requestAnimationFrame(resize);
    const timer = window.setTimeout(resize, 160);
    if (!rootRef.current || typeof ResizeObserver === "undefined") {
      return () => window.clearTimeout(timer);
    }
    const observer = new ResizeObserver(resize);
    observer.observe(rootRef.current);
    return () => { observer.disconnect(); window.clearTimeout(timer); };
  }, [payload, width]);

  if (!payload) {
    return <div className="mr-navigation-empty">Market Research 탐색을 불러오지 못했습니다.</div>;
  }

  const activeFamily = payload.families.find((row) => row.id === payload.active_family)
    ?? payload.families[0];
  const emit = (view: string) => {
    if (!view || view === payload.active_view) return;
    Streamlit.setComponentValue({ event: { id: "select_view", view, nonce: Date.now() } });
  };

  return (
    <main
      ref={rootRef}
      className={`mr-navigation ${theme?.base === "dark" ? "is-dark" : "is-light"}`}
    >
      <header className="mr-navigation__header">
        <span>{payload.eyebrow}</span>
        <h1>{payload.title}</h1>
        <p>{payload.description}</p>
      </header>
      <nav className="mr-navigation__families" aria-label="리서치 목적">
        {payload.families.map((family) => (
          <button
            type="button"
            key={family.id}
            aria-pressed={family.id === activeFamily.id}
            onClick={() => {
              if (family.id !== activeFamily.id) emit(family.views[0]?.id ?? "");
            }}
          >
            <strong>{family.label}</strong>
            <span>{family.description}</span>
          </button>
        ))}
      </nav>
      <nav className="mr-navigation__views" aria-label="세부 리서치">
        {activeFamily.views.map((view) => (
          <button
            type="button"
            key={view.id}
            aria-current={view.id === payload.active_view ? "page" : undefined}
            onClick={() => emit(view.id)}
          >
            {view.label}
          </button>
        ))}
      </nav>
    </main>
  );
}

export default withStreamlitConnection(MarketResearchNavigation);
```

Create `src/main.tsx`:

```tsx
import React from "react";
import { createRoot } from "react-dom/client";
import MarketResearchNavigation from "./MarketResearchNavigation";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <MarketResearchNavigation />
  </React.StrictMode>,
);
```

- [ ] **Step 5: Implement the complete responsive CSS**

Create `src/style.css` with these exact layout contracts:

```css
:root { background: transparent; font-family: Inter, Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-synthesis: none; }
* { box-sizing: border-box; }
html, body, #root { width: 100%; min-height: 100%; margin: 0; }
body { overflow-x: hidden; background: transparent; }
button { font: inherit; }
.mr-navigation {
  --ink: #1d3042; --muted: #6c7e8e; --line: #dce5eb; --soft: #f5f8fa;
  display: grid; width: 100%; gap: 16px; padding: 2px 2px 14px; color: var(--ink); overflow-x: hidden;
}
.mr-navigation.is-dark { --ink: #f4f7fa; --muted: #a5b0bb; --line: #2c333c; --soft: #15191f; }
.mr-navigation__header { display: grid; max-width: 760px; gap: 7px; padding: 4px 0 2px; }
.mr-navigation__header span { color: #6d8799; font-size: 10px; font-weight: 900; letter-spacing: .14em; }
.mr-navigation__header h1 { margin: 0; font-size: clamp(38px, 4.4vw, 55px); line-height: 1.03; letter-spacing: -.05em; }
.mr-navigation__header p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
.mr-navigation__families { display: grid; width: min(100%, 820px); grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.mr-navigation__families button { position: relative; display: grid; min-width: 0; gap: 4px; padding: 12px 14px; border: 1px solid transparent; border-radius: 13px; color: var(--muted); background: transparent; text-align: left; cursor: pointer; transition: 160ms ease; }
.mr-navigation__families button::after { position: absolute; right: 14px; bottom: 9px; left: 14px; height: 2px; border-radius: 2px; background: transparent; content: ""; }
.mr-navigation__families button:hover { color: var(--ink); background: color-mix(in srgb, #7394ac 8%, transparent); }
.mr-navigation__families button[aria-pressed="true"] { border-color: color-mix(in srgb, #7597ae 26%, transparent); color: var(--ink); background: color-mix(in srgb, #7597ae 13%, var(--soft)); }
.mr-navigation__families button[aria-pressed="true"]::after { background: #718ca0; }
.mr-navigation__families strong { font-size: 13px; }
.mr-navigation__families span { overflow: hidden; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.mr-navigation__views { display: flex; width: min(100%, 820px); flex-wrap: wrap; gap: 7px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 15px; background: color-mix(in srgb, #7597ae 7%, transparent); }
.mr-navigation__views button { min-height: 34px; padding: 7px 12px; border: 1px solid transparent; border-radius: 999px; color: var(--muted); background: transparent; cursor: pointer; transition: 150ms ease; }
.mr-navigation__views button:hover { color: var(--ink); background: color-mix(in srgb, #7597ae 10%, transparent); }
.mr-navigation__views button[aria-current="page"] { border-color: color-mix(in srgb, #7597ae 34%, transparent); color: var(--ink); background: color-mix(in srgb, #7597ae 18%, var(--soft)); font-weight: 800; }
.mr-navigation button:focus-visible { outline: 2px solid #7aa6c4; outline-offset: 2px; }
@media (max-width: 760px) { .mr-navigation { gap: 13px; } .mr-navigation__families button { padding-inline: 10px; } }
@media (max-width: 480px) {
  .mr-navigation { gap: 12px; padding-bottom: 10px; }
  .mr-navigation__header h1 { font-size: clamp(34px, 11vw, 44px); }
  .mr-navigation__header p { font-size: 12px; }
  .mr-navigation__families { gap: 5px; }
  .mr-navigation__families button { min-height: 52px; place-content: center; padding: 9px 5px 12px; text-align: center; }
  .mr-navigation__families span { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
  .mr-navigation__families button::after { right: 10px; bottom: 7px; left: 10px; }
  .mr-navigation__views { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; }
  .mr-navigation__views button { width: 100%; }
  .mr-navigation__views button:only-child { grid-column: 1 / -1; }
}
@media (prefers-reduced-motion: reduce) { .mr-navigation button { transition: none; } }
```

- [ ] **Step 6: Run React GREEN, typecheck, and build**

Run in `app/web/streamlit_components/market_research_navigation`:

```bash
npm test
npm run typecheck
npm run build
```

Expected: 4 tests pass, typecheck exits 0, and `component_static/index.html` plus hashed JS/CSS assets are generated.

- [ ] **Step 7: Commit Task 2**

Run:

```bash
git diff --check
git add \
  app/web/streamlit_components/market_research_navigation/index.html \
  app/web/streamlit_components/market_research_navigation/package.json \
  app/web/streamlit_components/market_research_navigation/package-lock.json \
  app/web/streamlit_components/market_research_navigation/tsconfig.json \
  app/web/streamlit_components/market_research_navigation/vite.config.ts \
  app/web/streamlit_components/market_research_navigation/src \
  app/web/streamlit_components/market_research_navigation/component_static
git commit -m "기능: Market Research React 상단 컴포넌트 구현"
```

Before committing, confirm `git status --short` does not stage `node_modules`.

---

### Task 3: React-First Integration, Fallback, Actual QA, And Closeout

**Files:**
- Modify: `app/web/overview/navigation.py`
- Modify: `app/web/overview/page.py`
- Modify: `tests/test_market_research_navigation.py`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-react-navigation-v1-20260722/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/docs/{INDEX,ROADMAP,PROJECT_MAP}.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/{WORK_PROGRESS,QUESTION_AND_ANALYSIS_LOG}.md`
- Generate unstaged: `market-research-react-navigation-qa.png`

**Interfaces:**
- Consumes: Task 1 payload/resolver/wrapper and Task 2 static bundle.
- Preserves: `_render_market_research_selector() -> str` and `_render_selected_market_research_view(...) -> str`.

- [ ] **Step 1: Write failing React-first/fallback integration tests**

Add to `tests/test_market_research_navigation.py`:

```python
def test_market_research_selector_prefers_react_and_keeps_streamlit_fallback():
    source = Path("app/web/overview/navigation.py").read_text(encoding="utf-8")
    body = source[source.index("def _render_market_research_selector"):]
    body = body[: body.index("def _render_selected_market_research_view")]

    assert "market_research_navigation_react_component_available()" in body
    assert "build_market_research_navigation_payload(current_view)" in body
    assert "render_market_research_navigation(" in body
    assert "resolve_market_research_navigation_event(" in body
    assert "_render_market_research_streamlit_fallback(" in body
    assert body.index("render_market_research_navigation(") < body.index("_render_market_research_streamlit_fallback(")


def test_market_research_page_renders_streamlit_header_only_for_fallback():
    source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
    body = source[source.index("def render_overview_dashboard"):]

    assert "market_research_navigation_react_component_available()" in body
    assert "if not market_research_navigation_react_component_available():" in body
    assert "_market_research_header_html()" in body
    assert body.index("if not market_research_navigation_react_component_available():") < body.index("_render_market_research_selector()")
```

- [ ] **Step 2: Run integration RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py -q -k 'prefers_react or header_only_for_fallback'
```

Expected: both tests fail because the selector still renders only Streamlit and the page always renders the HTML header.

- [ ] **Step 3: Extract the existing Streamlit fallback unchanged**

Move the current Streamlit presentation into this complete helper:

```python
def _render_market_research_streamlit_fallback(
    current_view: str,
    current_family: str,
) -> str:
    """Render the native controls only when the React bundle is unavailable."""
    st.markdown(_market_research_navigation_css(), unsafe_allow_html=True)

    family_options: dict[str, object] = {}
    if MARKET_RESEARCH_FAMILY_WIDGET_KEY not in st.session_state:
        family_options["default"] = current_family
    selected_family = st.segmented_control(
        "리서치 목적",
        options=list(MARKET_RESEARCH_FAMILY_OPTIONS),
        format_func=lambda value: MARKET_RESEARCH_FAMILY_LABELS[str(value)],
        key=MARKET_RESEARCH_FAMILY_WIDGET_KEY,
        label_visibility="collapsed",
        width="content",
        **family_options,
    ) or current_family

    family_label, family_views = market_research_local_navigation_context(
        selected_family
    )
    selected_view = (
        current_view
        if current_view in family_views
        else market_research_default_view_for_family(selected_family)
    )
    if st.session_state.get(MARKET_RESEARCH_VIEW_WIDGET_KEY) not in family_views:
        st.session_state.pop(MARKET_RESEARCH_VIEW_WIDGET_KEY, None)
    view_options: dict[str, object] = {}
    if MARKET_RESEARCH_VIEW_WIDGET_KEY not in st.session_state:
        view_options["default"] = selected_view

    with st.container(
        key=MARKET_RESEARCH_LOCAL_NAV_KEY,
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="center",
        gap="small",
    ):
        st.markdown(
            '<div class="mr-market-research-local-label">'
            "<span>선택한 리서치</span>"
            f"<strong>{escape(family_label)}</strong>"
            "</div>",
            unsafe_allow_html=True,
        )
        selected_view = st.pills(
            "세부 리서치",
            options=list(family_views),
            format_func=lambda value: MARKET_RESEARCH_VIEW_LABELS[str(value)],
            selection_mode="single",
            required=True,
            key=MARKET_RESEARCH_VIEW_WIDGET_KEY,
            label_visibility="collapsed",
            width="content",
            **view_options,
        ) or selected_view
    return str(selected_view)
```

Do not change its widget keys, family defaults, CSS, labels, or view result.

- [ ] **Step 4: Add the React-first branch**

Import the wrapper functions and change the selector after current view/family resolution:

```python
    if market_research_navigation_react_component_available():
        component_value = render_market_research_navigation(
            build_market_research_navigation_payload(current_view),
            key="market_research_navigation",
        )
        selected_view = resolve_market_research_navigation_event(
            current_view,
            component_value,
        )
    else:
        selected_view = _render_market_research_streamlit_fallback(
            current_view,
            current_family,
        )
    return _store_market_research_view(str(selected_view))
```

Add the new public/pure names to `__all__`.

- [ ] **Step 5: Make the page header fallback-only**

Import `market_research_navigation_react_component_available` in `page.py` and wrap the current CSS/header block exactly:

```python
    if not market_research_navigation_react_component_available():
        st.markdown(_market_research_page_css(), unsafe_allow_html=True)
        with st.container(key="market_research_page_header"):
            st.markdown(_market_research_header_html(), unsafe_allow_html=True)
```

Do not change the renderer map.

- [ ] **Step 6: Run automated regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py tests/test_today_home.py -q
.venv/bin/python -m py_compile app/web/overview/page.py app/web/overview/navigation.py app/web/overview/market_research_navigation_react_component.py
npm test --prefix app/web/streamlit_components/market_research_navigation
npm run typecheck --prefix app/web/streamlit_components/market_research_navigation
npm run build --prefix app/web/streamlit_components/market_research_navigation
git diff --check
```

Expected: all scoped Python/React tests pass and compile/typecheck/build/diff checks exit 0.

- [ ] **Step 7: Perform actual Browser QA**

Run Streamlit on a free localhost port and use the Codex in-app Browser.

Verify at 1280×900, 760×900, and 420×900:

- exactly one `Market Research` h1 appears
- iframe height hugs the React surface without clipping or a large blank tail
- active family has `aria-pressed=true`; active view has `aria-current=page`
- family clicks resolve to `economic-cycle`, `sp500`, and `market-movers`
- all seven view clicks update `overview_tab` to their canonical slug and lazy-render the expected module
- reload preserves the selected URL view
- 420px has three family columns, two view columns, hidden visual descriptions, visible focus outline, and document/main overflow 0
- no console error is introduced by the component

Save one final desktop screenshot as `market-research-react-navigation-qa.png` and leave it unstaged.

- [ ] **Step 8: Apply `finance-doc-sync` closeout**

Record exact automated counts, Browser QA dimensions/states, fallback verification, and any known unrelated full-suite baseline in task docs. Update only the minimal durable Market Research entries in `INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`, `flows/README.md`, `WORK_PROGRESS.md`, and `QUESTION_AND_ANALYSIS_LOG.md`.

Set `STATUS.md` to `Status: Complete` and `Roadmap: 3/3 complete`. Mark sticky/drawer/module-body work as deferred, not incomplete.

- [ ] **Step 9: Run final verification and commit**

Apply `superpowers:verification-before-completion`, rerun the complete scoped command set from Step 6, inspect `git status --short`, and confirm only pre-existing user artifacts plus the new unstaged QA screenshot remain.

Commit implementation integration and docs as coherent units:

```bash
git add app/web/overview/navigation.py app/web/overview/page.py tests/test_market_research_navigation.py
git commit -m "기능: Market Research React 상단 연결"

git add .aiworkspace/note/finance/tasks/active/market-research-react-navigation-v1-20260722 \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/flows/README.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Market Research React 상단 완료 기록"
```

Do not stage `market-research-react-navigation-qa.png`.

## Self-Review Result

- Spec coverage: full React header, three families, seven views, Python state ownership, event allowlist, fallback, theme, 1280/760/420 responsiveness, accessibility, static distribution, actual Browser QA, and docs sync are covered by Tasks 1-3.
- Placeholder scan: passed; every code-changing step contains an exact contract, code body, command, and expected result.
- Type consistency: `market_research_navigation_v1`, `select_view`, `active_family`, `active_view`, `families[].views[]`, Python wrapper names, and React TypeScript contracts match across all tasks.
