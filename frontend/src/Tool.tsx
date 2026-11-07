import {
  AssistantRuntimeProvider, MessagePrimitive, ThreadPrimitive, useAuiState, useExternalStoreRuntime,
  type ThreadMessageLike,
} from "@assistant-ui/react";
import { createContext, useContext, useRef, useState, type DragEvent, type FormEvent } from "react";
import { MAX_DOCUMENT_CHARS, MAX_MESSAGE_CHARS } from "./contractApi";
import { extractPdfText } from "./pdfText";
import { useContractChat, type ChatEntry } from "./useContractChat";
import "./chat.css";

const starterQuestions = [
  { label: "Gjennomgå en kontrakt", message: "Jeg vil gjennomgå en kundekontrakt." },
  { label: "Sammenlign med tilbudet", message: "Jeg vil sammenligne kundens kontrakt med tilbudet mitt." },
  { label: "Hjelp meg å svare kunden", message: "Hjelp meg å skrive et svar til kunden om kontrakten." },
];

const statusLabels = {
  risiko: "Risiko", avvik: "Avvik", må_avklares: "Må avklares", samsvarer: "Samsvarer",
};

const ChatEntries = createContext<ChatEntry[]>([]);

function ChatMessage() {
  const id = useAuiState((state) => state.message.id);
  const entry = useContext(ChatEntries).find((item) => item.id === id);
  const [copyStatus, setCopyStatus] = useState("");
  const draftRef = useRef<HTMLPreElement>(null);
  if (!entry) return null;
  const { draft } = entry;

  async function copyDraft() {
    if (!draft) return;
    try {
      await navigator.clipboard.writeText(draft);
      setCopyStatus("Utkast kopiert.");
    } catch {
      const selection = window.getSelection();
      if (draftRef.current && selection) {
        const range = document.createRange();
        range.selectNodeContents(draftRef.current);
        selection.removeAllRanges();
        selection.addRange(range);
      }
      setCopyStatus("Kopier teksten manuelt.");
    }
  }

  return (
    <MessagePrimitive.Root className={`chat-message chat-message-${entry.role}`}>
      <div className="chat-bubble">
        {entry.files?.length ? <ul className="chat-files">{entry.files.map((file, index) =>
          <li key={index}>{file}</li>,
        )}</ul> : null}
        {entry.content && <div className="chat-text"><MessagePrimitive.Parts /></div>}
        {entry.mode === "mock" && <span className="mode">Eksempelmodus</span>}
        {entry.findings?.length === 0 && <p>Jeg fant ingen vesentlige punkter i teksten jeg gjennomgikk.</p>}
        {entry.findings?.map((finding) => (
          <details className="chat-finding" key={finding.id} open={finding.status !== "samsvarer"}>
            <summary>{statusLabels[finding.status]} · {finding.category}</summary>
            <p>{finding.explanation}</p>
            {finding.contract_quote && <blockquote><strong>Kontrakt</strong> {finding.contract_quote}</blockquote>}
            {finding.offer_quote && <blockquote><strong>Tilbud</strong> {finding.offer_quote}</blockquote>}
            {finding.suggested_change && <p>{finding.suggested_change}</p>}
          </details>
        ))}
        {entry.sources?.map((source, index) => (
          <blockquote key={index}><strong>{source.document === "contract" ? "Kontrakt" : "Tilbud"}</strong> {source.quote}</blockquote>
        ))}
        {draft && (
          <div className="chat-draft">
            <strong>Utkast</strong>
            <pre ref={draftRef}>{draft}</pre>
            <button type="button" className="button-quiet" onClick={copyDraft}>Kopier utkast</button>
            <span role="status">{copyStatus}</span>
          </div>
        )}
      </div>
    </MessagePrimitive.Root>
  );
}

function convertMessage(entry: ChatEntry): ThreadMessageLike {
  return { id: entry.id, role: entry.role, content: [{ type: "text", text: entry.content }] };
}

export function Tool() {
  const chat = useContractChat();
  const [message, setMessage] = useState("");
  const [pasting, setPasting] = useState(false);
  const [pastedText, setPastedText] = useState("");
  const [reading, setReading] = useState(false);
  const [fileError, setFileError] = useState("");
  const uploadRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const entries = chat.pending ? [...chat.entries, chat.pending] : chat.entries;
  const busy = Boolean(chat.pending) || reading;
  const canSend = !busy && Boolean(message.trim() || chat.attachments.length);
  const runtime = useExternalStoreRuntime({
    messages: entries, convertMessage, isRunning: Boolean(chat.pending),
    onNew: async (entry) => {
      await sendMessage(entry.content.flatMap((part) => part.type === "text" ? [part.text] : []).join("\n"));
    },
  });

  async function addFiles(files: FileList) {
    if (busy || !files.length) return;
    if (files.length + chat.attachments.length > 2) {
      setFileError("Du kan legge ved opptil to dokumenter om gangen.");
      return;
    }
    setReading(true);
    setFileError("");
    try {
      const documents = await Promise.all(Array.from(files, async (file) => {
        const { text } = await extractPdfText(file);
        if (text.length > MAX_DOCUMENT_CHARS) throw new Error(`«${file.name}» er for langt. Lim inn et kortere utdrag.`);
        return { name: file.name, text };
      }));
      chat.setAttachments((current) => [...current, ...documents]);
    } catch (cause) {
      setFileError(cause instanceof Error ? cause.message : "Kunne ikke lese vedlegget.");
    } finally {
      setReading(false);
    }
  }

  function addPastedText() {
    const text = pastedText.trim();
    if (!text || text.length > MAX_DOCUMENT_CHARS || chat.attachments.length >= 2) return;
    chat.setAttachments((current) => [...current, { name: `Innlimt dokument ${current.length + 1}`, text }]);
    setPastedText("");
    setPasting(false);
    setFileError("");
    inputRef.current?.focus();
  }

  function dropFiles(event: DragEvent) {
    if (!event.dataTransfer.types.includes("Files")) return;
    event.preventDefault();
    void addFiles(event.dataTransfer.files);
  }

  async function sendMessage(text: string) {
    if (busy || (!text.trim() && !chat.attachments.length)) return;
    setMessage("");
    if (!(await chat.send(text))) setMessage(text);
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(message);
  }

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <ChatEntries.Provider value={entries}>
        <ThreadPrimitive.Root className={entries.length ? "chat-workspace" : "chat-workspace chat-workspace-empty"} onDragOver={(event) => {
          if (event.dataTransfer.types.includes("Files")) event.preventDefault();
        }} onDrop={dropFiles}>
          <header className="chat-header">
            <h1 tabIndex={-1}>Kontraktschat</h1>
            {(chat.entries.length > 0 || chat.attachments.length > 0) && (
              <button type="button" className="button-quiet" disabled={busy} onClick={() => {
                chat.reset();
                setMessage("");
                setPastedText("");
                setPasting(false);
                setFileError("");
                inputRef.current?.focus();
              }}>Ny samtale</button>
            )}
          </header>
          <ThreadPrimitive.Viewport className="chat-viewport">
            {entries.length === 0 && (
              <div className="chat-welcome">
                <h2>Hva trenger du hjelp med?</h2>
                <p>Spør om en kontrakt, eller legg ved dokumentene dine.</p>
                <div className="chat-suggestions">
                  {starterQuestions.map(({ label, message }) => (
                    <button key={label} type="button" disabled={busy} onClick={() => {
                      inputRef.current?.focus();
                      void sendMessage(message);
                    }}>{label}</button>
                  ))}
                </div>
              </div>
            )}
            <div className="chat-thread" role="log" aria-label="Samtale">
              <ThreadPrimitive.Messages components={{ UserMessage: ChatMessage, AssistantMessage: ChatMessage }} />
              {(reading || chat.pending) && <p className="chat-working" role="status">
                {reading ? "Leser vedlegg …" : "Jobber med svaret …"}
              </p>}
            </div>
          </ThreadPrimitive.Viewport>
          <form className="chat-composer" onSubmit={submit}>
            {(chat.documents.contract || chat.documents.offer) && <p className="chat-active">
              {chat.documents.contract && <>Kontrakt: {chat.documents.contract.name} </>}
              {chat.documents.offer && <>Tilbud: {chat.documents.offer.name}</>}
            </p>}
            {chat.attachments.length > 0 && <ul className="chat-files">
              {chat.attachments.map(({ name }, index) => <li key={index}>
                {name} <button type="button" aria-label={`Fjern ${name}`} disabled={busy}
                  onClick={() => chat.setAttachments((files) => files.filter((_, i) => i !== index))}>×</button>
              </li>)}
            </ul>}
            {pasting && <div className="chat-paste">
              <label htmlFor="document-paste">Lim inn dokumenttekst</label>
              <textarea id="document-paste" value={pastedText} maxLength={MAX_DOCUMENT_CHARS} disabled={busy}
                onChange={(event) => setPastedText(event.target.value)} />
              <button type="button" className="button-quiet" disabled={busy || !pastedText.trim() || chat.attachments.length >= 2}
                onClick={addPastedText}>Legg ved tekst</button>
            </div>}
            <textarea ref={inputRef} aria-label="Melding" placeholder="Spør om kontrakten …" value={message}
              rows={2} maxLength={MAX_MESSAGE_CHARS} readOnly={busy} onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }} />
            <div className="chat-composer-actions">
              <input ref={uploadRef} type="file" aria-label="PDF-vedlegg" accept="application/pdf,.pdf" multiple hidden
                onChange={(event) => {
                  if (event.target.files) void addFiles(event.target.files);
                  event.target.value = "";
                }} />
              <button type="button" className="button-quiet" disabled={busy}
                onClick={() => uploadRef.current?.click()}>{reading ? "Leser PDF …" : "+ Legg ved PDF"}</button>
              <button type="button" className="button-quiet" disabled={busy}
                aria-expanded={pasting} onClick={() => setPasting(!pasting)}>Lim inn dokument</button>
              <button className="button" disabled={!canSend}>Send</button>
            </div>
            {(fileError || chat.error) && <p className="error" role="alert">{fileError || chat.error}</p>}
          </form>
        </ThreadPrimitive.Root>
      </ChatEntries.Provider>
    </AssistantRuntimeProvider>
  );
}
