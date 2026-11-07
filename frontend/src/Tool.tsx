import { useEffect, useRef, useState, type DragEvent, type FormEvent } from "react";
import { extractPdfText, PdfReadError } from "./pdfText";

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
  disabled: boolean;
  onChange: (value: string) => void;
  onReadingChange: (reading: boolean) => void;
};

function hasFiles(event: DragEvent) {
  return event.dataTransfer.types.includes("Files");
}

function DocumentField({ id, label, value, disabled, onChange, onReadingChange }: DocumentFieldProps) {
  const [reading, setReading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [fileNote, setFileNote] = useState("");
  const [fileError, setFileError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const length = value.trim().length;
  const tooLong = length > MAX_CHARS;
  const hintId = `${id}-hint`;

  async function readFile(file: File) {
    if (reading || disabled) return;
    setReading(true);
    onReadingChange(true);
    setFileNote("");
    setFileError("");
    try {
      const { text, pages } = await extractPdfText(file);
      onChange(text);
      const pageLabel = pages === 1 ? "1 side" : `${pages} sider`;
      setFileNote(`Hentet fra ${file.name} (${pageLabel}). Sjekk at teksten stemmer.`);
    } catch (error) {
      setFileError(error instanceof PdfReadError ? error.message : "Kunne ikke lese PDF-filen.");
    } finally {
      setReading(false);
      onReadingChange(false);
    }
  }

  function handleDrop(event: DragEvent) {
    if (!hasFiles(event)) return;
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) void readFile(file);
  }

  return (
    <div
      className={dragging ? "field field-dragging" : "field"}
      onDragOver={(event) => {
        if (!hasFiles(event)) return;
        event.preventDefault();
        setDragging(!disabled && !reading);
      }}
      onDragLeave={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setDragging(false);
      }}
      onDrop={handleDrop}
    >
      <div className="field-head">
        <label htmlFor={id}>{label}</label>
        <button
          type="button"
          className="button-quiet"
          disabled={reading}
          aria-label={`Last opp PDF for ${label.toLowerCase()}`}
          onClick={() => fileInputRef.current?.click()}
        >
          {reading ? "Leser PDF …" : "Last opp PDF"}
        </button>
        <input
          ref={fileInputRef}
          id={`${id}-file`}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];
            event.target.value = "";
            if (file) void readFile(file);
          }}
        />
      </div>
      <textarea
        id={id}
        value={value}
        readOnly={reading}
        placeholder="Lim inn teksten, eller slipp en PDF her"
        aria-describedby={hintId}
        aria-invalid={tooLong}
        onChange={(event) => {
          setFileNote("");
          setFileError("");
          onChange(event.target.value);
        }}
      />
      {fileError && <p className="hint hint-error" role="alert">{fileError}</p>}
      {fileNote && <p className="hint" role="status">{fileNote}</p>}
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
  const [offerReading, setOfferReading] = useState(false);
  const [contractReading, setContractReading] = useState(false);
  const replyRef = useRef<HTMLTextAreaElement>(null);

  // A file dropped beside the fields would otherwise open in the tab and lose the pasted text.
  useEffect(() => {
    function ignoreFileDrop(event: globalThis.DragEvent) {
      if (event.dataTransfer?.types.includes("Files")) event.preventDefault();
    }
    window.addEventListener("dragover", ignoreFileDrop);
    window.addEventListener("drop", ignoreFileDrop);
    return () => {
      window.removeEventListener("dragover", ignoreFileDrop);
      window.removeEventListener("drop", ignoreFileDrop);
    };
  }, []);

  const canAnalyze = isAcceptedLength(offer) && isAcceptedLength(contract) && !offerReading && !contractReading;
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
      <div className="tool-intro navy">
        <div className="wrap">
          <h1 className="tool-title" tabIndex={-1}>Sjekk kontrakten</h1>
          <p>Legg inn tilbudet og kundens kontrakt, og se hva som er endret.</p>
        </div>
      </div>

      <div className="wrap tool-body">
        <form onSubmit={analyze}>
          <fieldset disabled={loading}>
            <div className="columns documents">
              <DocumentField
                id="offer"
                label="Tilbud"
                value={offer}
                disabled={loading}
                onChange={changeOffer}
                onReadingChange={setOfferReading}
              />
              <DocumentField
                id="contract"
                label="Kundens kontrakt"
                value={contract}
                disabled={loading}
                onChange={changeContract}
                onReadingChange={setContractReading}
              />
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
              <p className="note">Funnene er et fast eksempel og er ikke basert på dokumentene du la inn.</p>
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
