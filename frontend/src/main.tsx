import { useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

type Finding = {
  id: string;
  category: "leveranse" | "betaling" | "ekstraarbeid" | "ansvar";
  status: "samsvarer" | "avvik" | "må_avklares";
  explanation: string;
  offer_quote: string | null;
  contract_quote: string | null;
  suggested_change: string | null;
};

type Analysis = { mode: "mock" | "live"; findings: Finding[] };

const statusLabels: Record<Finding["status"], string> = {
  samsvarer: "Samsvarer",
  avvik: "Avvik",
  må_avklares: "Må avklares",
};

function App() {
  const [offer, setOffer] = useState("");
  const [contract, setContract] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAnalysis(null);
    setSelected([]);

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ offer_text: offer, contract_text: contract }),
      });
      if (!response.ok) {
        const detail: unknown = (await response.json().catch(() => null))?.detail;
        throw new Error(typeof detail === "string" ? detail : "Analysen kunne ikke gjennomføres.");
      }
      setAnalysis(await response.json());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Noe gikk galt.");
    } finally {
      setLoading(false);
    }
  }

  const suggestions = (analysis?.findings ?? []).flatMap((finding) =>
    selected.includes(finding.id) && finding.suggested_change ? [finding.suggested_change] : [],
  );

  return (
    <main>
      <h1>Kontraktsstøtte</h1>
      <p>Sammenlign kundens kontrakt med tilbudet du sendte.</p>
      <form onSubmit={analyze}>
        <fieldset disabled={loading}>
          <label htmlFor="offer">Tilbud</label>
          <textarea id="offer" required value={offer} onChange={(event) => setOffer(event.target.value)} />
          <label htmlFor="contract">Kontrakt</label>
          <textarea id="contract" required value={contract} onChange={(event) => setContract(event.target.value)} />
          <button disabled={!offer.trim() || !contract.trim()}>
            {loading ? "Analyserer …" : "Analyser"}
          </button>
        </fieldset>
      </form>
      {error && <p role="alert">{error}</p>}
      {analysis && (
        <section aria-label="Resultater">
          <h2>Funn</h2>
          {analysis.mode === "mock" && <p>Eksempelmodus. Funnene viser et fiktivt dokumentpar.</p>}
          {analysis.findings.length === 0 && <p>Ingen funn å vise.</p>}
          {analysis.findings.map((finding) => (
            <article key={finding.id}>
              <h3>{statusLabels[finding.status]} · {finding.category}</h3>
              <p>{finding.explanation}</p>
              {finding.offer_quote && <p><strong>Tilbud:</strong> {finding.offer_quote}</p>}
              {finding.contract_quote && <p><strong>Kontrakt:</strong> {finding.contract_quote}</p>}
              {finding.suggested_change && (
                <label className="choice">
                  <input
                    type="checkbox"
                    checked={selected.includes(finding.id)}
                    onChange={(event) => setSelected((current) =>
                      event.target.checked
                        ? [...current, finding.id]
                        : current.filter((id) => id !== finding.id),
                    )}
                  />
                  {finding.suggested_change}
                </label>
              )}
            </article>
          ))}
          {suggestions.length > 0 && (
            <>
              <label htmlFor="draft">Svarutkast til kunden</label>
              <textarea id="draft" readOnly value={["Hei,", ...suggestions, "Vennlig hilsen"].join("\n\n")} />
            </>
          )}
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
