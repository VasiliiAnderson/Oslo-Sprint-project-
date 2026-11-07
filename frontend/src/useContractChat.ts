import { useRef, useState } from "react";
import {
  FOLLOW_UP_ERROR, MAX_MESSAGE_CHARS, requestAnalysis, requestChatContext, requestFollowUp,
  type Analysis, type Attachment, type ChatMessage, type FollowUp, type Mode,
} from "./contractApi";

export type ChatEntry = ChatMessage & {
  id: string;
  files?: string[];
  mode?: Mode;
  findings?: Analysis["findings"];
  sources?: FollowUp["sources"];
  draft?: string | null;
};

type ActiveDocuments = { contract?: Attachment; offer?: Attachment };

function chatHistory(entries: ChatEntry[], question: string): ChatMessage[] {
  return [
    ...entries.filter((entry) => entry.content.trim()).slice(-5).map(({ role, content }) => ({
      role, content: content.slice(0, MAX_MESSAGE_CHARS),
    })),
    { role: "user", content: question },
  ];
}

export function useContractChat() {
  const [entries, setEntries] = useState<ChatEntry[]>([]);
  const [pending, setPending] = useState<ChatEntry | null>(null);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [documents, setDocuments] = useState<ActiveDocuments>({});
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [waitingQuestion, setWaitingQuestion] = useState("");
  const [error, setError] = useState("");
  const request = useRef<AbortController | null>(null);

  async function send(text: string) {
    const question = text.trim();
    if (request.current || (!question && !attachments.length) || question.length > MAX_MESSAGE_CHARS) return false;
    const controller = new AbortController();
    request.current = controller;
    const signal = controller.signal;
    const user: ChatEntry = {
      id: crypto.randomUUID(), role: "user", content: question, files: attachments.map(({ name }) => name),
    };
    const response: ChatEntry = { id: crypto.randomUUID(), role: "assistant", content: "" };
    setPending(user);
    setError("");
    try {
      let next = documents;
      let history = entries;
      let nextAnalysis = analysis;
      const context = attachments.length || !documents.contract
        ? await requestChatContext(attachments, question ? chatHistory(entries, question) : [], signal)
        : null;
      if (context) {
        response.mode = context.mode;
        const contracts = attachments.filter((_, index) => context.roles[index] === "contract");
        const offers = attachments.filter((_, index) => context.roles[index] === "offer");
        if (context.roles.includes("unclear") || contracts.length > 1 || offers.length > 1) {
          response.content = contracts.length > 1 || offers.length > 1
            ? "Jeg fant flere dokumenter av samme type. Fjern det du ikke vil bruke, og send vedlegget på nytt."
            : context.answer;
          setEntries([...entries, user, response]);
          if (question) setWaitingQuestion(question);
          return true;
        }
        const replacing = Boolean(documents.contract && contracts[0] && documents.contract.text !== contracts[0].text);
        if (replacing) {
          history = [];
          next = {};
          nextAnalysis = null;
        }
        next = { contract: contracts[0] ?? next.contract, offer: offers[0] ?? next.offer };
      }

      if (!next.contract) {
        response.content = context?.answer ?? "Legg ved kontrakten, så ser jeg nærmere på det.";
        if (context?.needs_contract && question) setWaitingQuestion(question);
        else if (question) setWaitingQuestion("");
      } else {
        const payload = { contract_text: next.contract.text, offer_text: next.offer?.text ?? null };
        const prompt = question || (history === entries ? waitingQuestion : "");
        if (!nextAnalysis || attachments.length) {
          nextAnalysis = await requestAnalysis(payload, signal);
          response.mode = nextAnalysis.mode;
          response.findings = nextAnalysis.findings;
        }
        if (prompt) {
          const latestDraft = [...history].reverse().find((entry) => entry.draft)?.draft ?? null;
          const reply = await requestFollowUp({
            ...payload, findings: nextAnalysis.findings,
            messages: chatHistory(history, prompt), current_draft: latestDraft,
          }, signal);
          response.mode = reply.mode;
          response.content = reply.answer;
          response.sources = reply.sources;
          response.draft = reply.draft;
        } else {
          response.content = next.offer ? "Jeg har sammenlignet kontrakten med tilbudet." : "Jeg har gjennomgått kontrakten.";
        }
        setWaitingQuestion("");
      }
      setDocuments(next);
      setAnalysis(nextAnalysis);
      setEntries([...history, user, response]);
      setAttachments([]);
      return true;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : FOLLOW_UP_ERROR);
      return false;
    } finally {
      request.current = null;
      setPending(null);
    }
  }

  function reset() {
    if (request.current) return;
    setEntries([]);
    setAttachments([]);
    setDocuments({});
    setAnalysis(null);
    setWaitingQuestion("");
    setError("");
  }

  return { entries, pending, attachments, setAttachments, documents, send, reset, error };
}
