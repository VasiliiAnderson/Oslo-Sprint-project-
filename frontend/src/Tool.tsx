import { useRef, useState, type FormEvent } from "react";

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

type CopyState = "idle" | "copied" | "failed";

const MAX_CHARS = 20_000;
const MAX_DETAIL_CHARS = 200;
const ANALYSIS_ERROR = "Analysen kunne ikke gjennomføres. Prøv igjen.";
const CONNECTION_ERROR = "Fikk ikke kontakt med tjenesten. Prøv igjen.";

const statusLabels: Record<Finding["status"], string> = {
  samsvarer: "Samsvarer",
  avvik: "Avvik",
  må_avklares: "Må avklares",
};

const statusClasses: Record<Finding["status"], string> = {
  samsvarer: "status-samsvarer",
  avvik: "status-avvik",
  må_avklares: "status-avklares",
};

const categoryLabels: Record<Finding["category"], string> = {
  leveranse: "Leveranse",
  betaling: "Betaling",
  ekstraarbeid: "Ekstraarbeid",
  ansvar: "Ansvar",
};

function isSelectable(finding: Finding) {
  return finding.status !== "samsvarer" && Boolean(finding.suggested_change);
}

function isAcceptedLength(text: string) {
  const length = text.trim().length;
  return length > 0 && length <= MAX_CHARS;
}

function formatCount(count: number) {
  return count.toLocaleString("nb-NO");
}

async function requestAnalysis(offer: string, contract: string): Promise<Analysis> {
  let response: Response;
  try {
    response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ offer_text: offer, contract_text: contract }),
    });
  } catch {
    throw new Error(CONNECTION_ERROR);
  }

  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = (body as { detail?: unknown } | null)?.detail;
    const isShortText = typeof detail === "string" && detail.trim() && detail.length <= MAX_DETAIL_CHARS;
    throw new Error(isShortText ? detail : ANALYSIS_ERROR);
  }
  if (!Array.isArray((body as Analysis | null)?.findings)) {
    throw new Error(ANALYSIS_ERROR);
  }
  return body as Analysis;
}

type DocumentFieldProps = {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
};

function DocumentField({ id, label, value, onChange }: DocumentFieldProps) {
  const length = value.trim().length;
  const tooLong = length > MAX_CHARS;
  const hintId = `${id}-hint`;

  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <textarea
        id={id}
        value={value}
        aria-describedby={hintId}
        aria-invalid={tooLong}
        onChange={(event) => onChange(event.target.value)}
      />
      <p id={hintId} className={tooLong ? "hint hint-error" : "hint"}>
        {formatCount(length)} av {formatCount(MAX_CHARS)} tegn
        {tooLong && ". Kort ned teksten for å analysere."}
      </p>
    </div>
  );
}

type FindingCardProps = {
  finding: Finding;
  selected: boolean;
  onToggle: (checked: boolean) => void;
};

function FindingCard({ finding, selected, onToggle }: FindingCardProps) {
  return (
    <article className={`finding ${statusClasses[finding.status]}`}>
      <h3>
        <span className="status">{statusLabels[finding.status]}</span>
        <span className="category">{categoryLabels[finding.category]}</span>
      </h3>
      <p className="explanation">{finding.explanation}</p>
      {(finding.offer_quote || finding.contract_quote) && (
        <div className="columns">
          {finding.offer_quote && (
            <div className="quote quote-offer">
              <p className="quote-source">Tilbud</p>
              <blockquote>{finding.offer_quote}</blockquote>
            </div>
          )}
          {finding.contract_quote && (
            <div className="quote quote-contract">
              <p className="quote-source">Kontrakt</p>
              <blockquote>{finding.contract_quote}</blockquote>
            </div>
          )}
        </div>
      )}
      {isSelectable(finding) && (
        <label className="choice">
          <input type="checkbox" checked={selected} onChange={(event) => onToggle(event.target.checked)} />
          <span>
            <span className="choice-title">Ta med i svaret</span>
            {finding.suggested_change}
          </span>
        </label>
      )}
    </article>
  );
}

export function Tool() {
  const [offer, setOffer] = useState("");
  const [contract, setContract] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyState, setCopyState] = useState<CopyState>("idle");
  const replyRef = useRef<HTMLTextAreaElement>(null);

  const canAnalyze = isAcceptedLength(offer) && isAcceptedLength(contract);
  const findings = analysis?.findings ?? [];
  const suggestions = findings.flatMap((finding) =>
    isSelectable(finding) && selected.includes(finding.id) ? [finding.suggested_change as string] : [],
  );
  const reply = ["Hei,", ...suggestions, "Vennlig hilsen"].join("\n\n");

  function clearResults() {
    setAnalysis(null);
    setSelected([]);
    setError("");
    setCopyState("idle");
  }

  function changeOffer(value: string) {
    setOffer(value);
    clearResults();
  }

  function changeContract(value: string) {
    setContract(value);
    clearResults();
  }

  function toggleFinding(id: string, checked: boolean) {
    setSelected((current) => (checked ? [...current, id] : current.filter((item) => item !== id)));
    setCopyState("idle");
  }

  async function analyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canAnalyze || loading) return;
    setLoading(true);
    clearResults();

    try {
      setAnalysis(await requestAnalysis(offer, contract));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : ANALYSIS_ERROR);
    } finally {
      setLoading(false);
    }
  }

  async function copyReply() {
    try {
      await navigator.clipboard.writeText(reply);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
      replyRef.current?.select();
    }
  }

  return (
    <main>
      <header className="tool-bar">
        <div className="wrap">
          <a className="brand" href="#/">Kontraktsstøtte</a>
        </div>
      </header>

      <div className="wrap">
        <div className="tool-intro">
          <h1 className="tool-title" tabIndex={-1}>Sjekk kontrakten</h1>
          <p>Sammenlign kundens kontrakt med tilbudet du sendte.</p>
        </div>

        <form onSubmit={analyze}>
          <fieldset disabled={loading}>
            <div className="columns documents">
              <DocumentField id="offer" label="Tilbud" value={offer} onChange={changeOffer} />
              <DocumentField id="contract" label="Kundens kontrakt" value={contract} onChange={changeContract} />
            </div>
            <div className="form-actions">
              <button className="button" disabled={!canAnalyze}>
                {loading ? "Analyserer …" : "Analyser"}
              </button>
            </div>
          </fieldset>
        </form>

        {error && <p className="error" role="alert">{error}</p>}

        {analysis && (
          <section className="results" aria-labelledby="findings-title">
            <div className="section-heading">
              <h2 id="findings-title">Funn</h2>
              {analysis.mode === "mock" && <span className="mode">Eksempelmodus</span>}
            </div>
            {analysis.mode === "mock" && (
              <p className="note">Funnene er et fast eksempel og er ikke basert på tekstene du limte inn.</p>
            )}
            {findings.length === 0 && <p className="note">Ingen funn å vise</p>}
            {findings.map((finding) => (
              <FindingCard
                key={finding.id}
                finding={finding}
                selected={selected.includes(finding.id)}
                onToggle={(checked) => toggleFinding(finding.id, checked)}
              />
            ))}

            {findings.some(isSelectable) && suggestions.length === 0 && (
              <p className="note">Velg minst ett punkt for å lage et svar til kunden.</p>
            )}

            {suggestions.length > 0 && (
              <div className="reply">
                <div className="reply-intro">
                  <label htmlFor="reply">Svar til kunden</label>
                  <p>Bare punktene du har valgt er med.</p>
                  <button type="button" className="button button-pad" onClick={copyReply}>Kopier svar</button>
                  <p role="status" className={copyState === "failed" ? "reply-status reply-status-failed" : "reply-status"}>
                    {copyState === "copied" && "Svaret er kopiert."}
                    {copyState === "failed" && "Kopieringen virket ikke. Teksten er markert, så du kan kopiere den selv."}
                  </p>
                </div>
                <textarea id="reply" ref={replyRef} readOnly value={reply} />
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
