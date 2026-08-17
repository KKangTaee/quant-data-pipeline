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
    return () => {
      observer.disconnect();
      window.clearTimeout(timer);
    };
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
        <div className="mr-navigation__heading">
          <span>{payload.eyebrow}</span>
          <h1>{payload.title}</h1>
        </div>
        <p>{payload.description}</p>
      </header>
      <nav className="mr-navigation__families" aria-label="리서치 목적">
        {payload.families.map((family) => (
          <button
            type="button"
            key={family.id}
            aria-label={`${family.label}: ${family.description}`}
            aria-pressed={family.id === activeFamily.id}
            onClick={() => {
              if (family.id !== activeFamily.id) emit(family.views[0]?.id ?? "");
            }}
          >
            <strong>{family.label}</strong>
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
