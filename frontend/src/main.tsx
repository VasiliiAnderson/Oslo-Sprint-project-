import { useEffect, useRef, useState } from "react";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import "./style.css";
import { Landing } from "./Landing";
import { Tool } from "./Tool";

type View = "landing" | "tool";

const TOOL_HASH = "#/sjekk";

const titles: Record<View, string> = {
  landing: "Kontraktsstøtte",
  tool: "Sjekk kontrakten – Kontraktsstøtte",
};

function currentView(): View {
  return window.location.hash === TOOL_HASH ? "tool" : "landing";
}

function Menu({ view }: { view: View }) {
  return (
    <header className="menu">
      <nav className="menu-inner wrap" aria-label="Hovedmeny">
        <a className="brand" href="#/">Kontraktsstøtte</a>
        <div className="menu-links">
          <a className="menu-link" href="#/" aria-current={view === "landing" ? "page" : undefined}>Forside</a>
          <a className="menu-link" href="#eksempel">Se et eksempel</a>
          <a className="button menu-cta" href={TOOL_HASH} aria-current={view === "tool" ? "page" : undefined}>
            Sjekk kontrakten
          </a>
        </div>
      </nav>
    </header>
  );
}

function App() {
  const [view, setView] = useState<View>(currentView);
  const isFirstRender = useRef(true);

  useEffect(() => {
    function handleHashChange() {
      const next = currentView();
      if (next === view) {
        if (window.location.hash === "#/") window.scrollTo({ top: 0 });
        return;
      }
      const update = () => flushSync(() => setView(next));
      if (document.startViewTransition) document.startViewTransition(update);
      else update();
    }
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, [view]);

  useEffect(() => {
    document.title = titles[view];
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const anchor = window.location.hash.startsWith("#/") ? null : document.querySelector(window.location.hash || "#none");
    if (anchor) anchor.scrollIntoView({ behavior: "instant" });
    else window.scrollTo({ top: 0, behavior: "instant" });
    document.querySelector<HTMLElement>(`[data-view="${view}"] h1`)?.focus({ preventScroll: true });
  }, [view]);

  // Both views stay mounted so pasted text and findings survive moving between them.
  return (
    <>
      <Menu view={view} />
      <div data-view="landing" hidden={view !== "landing"}>
        <Landing toolHref={TOOL_HASH} />
      </div>
      <div data-view="tool" hidden={view !== "tool"}>
        <Tool />
      </div>
      <footer className="site-footer">
        <div className="wrap">
          Konsept for ferdig løsning. Prototypen sammenligner foreløpig tilbud og kontrakt. Bruk fiktive dokumenter.
          Verktøyet gir ikke juridisk rådgivning.
        </div>
      </footer>
    </>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
