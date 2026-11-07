import { MAX_MESSAGE_CHARS } from "./contractApi";
import type { ChatTurn } from "./useContractReview";

type ContractChatProps = {
  turns: ChatTurn[];
  message: string;
  sending: boolean;
  error: string;
  onMessageChange: (value: string) => void;
  onSend: (value: string) => void;
  onUseDraft: (draft: string) => void;
};

export function ContractChat({
  turns, message, sending, error, onMessageChange, onSend, onUseDraft,
}: ContractChatProps) {
  return (
    <section className="results" aria-labelledby="chat-title">
      <div className="section-heading">
        <h2 id="chat-title">Spør om kontrakten</h2>
      </div>
      {turns.length === 0 && (
        <div className="form-actions">
          <button type="button" className="button-quiet" disabled={sending}
            onClick={() => onMessageChange("Forklar et vilkår jeg bør se nærmere på.")}>
            Forklar et vilkår
          </button>
          <button type="button" className="button-quiet" disabled={sending}
            onClick={() => onMessageChange("Hjelp meg å skrive et svar til kunden.")}>
            Hjelp meg å svare
          </button>
        </div>
      )}
      <div role="log" aria-label="Samtale">
        {turns.map(({ question, response }, index) => (
          <article key={index} className="finding">
            <p><strong>Du</strong> {question}</p>
            <p className="explanation">{response.answer}</p>
            {response.mode === "mock" && <span className="mode">Eksempelmodus</span>}
            {response.sources.map((source, sourceIndex) => (
              <div className="quote" key={sourceIndex}>
                <p className="quote-source">{source.document === "offer" ? "Tilbud" : "Kontrakt"}</p>
                <blockquote>{source.quote}</blockquote>
              </div>
            ))}
            {response.draft !== null && (
              <>
                <div className="field">
                  <label htmlFor={`draft-${index}`}>Forslag til svar</label>
                  <textarea id={`draft-${index}`} readOnly value={response.draft} />
                </div>
                <button type="button" className="button" onClick={() => {
                  if (response.draft !== null) onUseDraft(response.draft);
                }}>
                  Bruk i utkast
                </button>
              </>
            )}
          </article>
        ))}
      </div>
      <form onSubmit={(event) => {
        event.preventDefault();
        onSend(message);
      }}>
        <div className="field">
          <label htmlFor="chat-message">Melding</label>
          <textarea
            id="chat-message"
            value={message}
            maxLength={MAX_MESSAGE_CHARS}
            readOnly={sending}
            onChange={(event) => onMessageChange(event.target.value)}
          />
        </div>
        <div className="form-actions">
          <button className="button" disabled={sending || !message.trim()}>
            {sending ? "Sender …" : "Send"}
          </button>
        </div>
      </form>
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}
