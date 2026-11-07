import { useEffect, useRef, useState } from "react";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/schibsted-grotesk/wght.css";
import "@fontsource/ibm-plex-serif/latin-400.css";
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

function App() {
  const [view, setView] = useState<View>(currentView);
  const isFirstRender = useRef(true);

  useEffect(() => {
    function handleHashChange() {
      const next = currentView();
      if (next === view) return;
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
    window.scrollTo(0, 0);
    document.querySelector<HTMLElement>(`[data-view="${view}"] h1`)?.focus();
  }, [view]);

  // Both views stay mounted so pasted text and findings survive moving between them.
  return (
    <>
      <div data-view="landing" hidden={view !== "landing"}>
        <Landing toolHref={TOOL_HASH} />
      </div>
      <div data-view="tool" hidden={view !== "tool"}>
        <Tool />
      </div>
      <footer className="site-footer wrap">
        Prototype fra Oslo Sprint. Bruk fiktive dokumenter. Verktøyet gir ikke juridisk rådgivning, så les alltid hele
        kontrakten selv.
      </footer>
    </>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
