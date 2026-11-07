import { useEffect, useRef, useState } from "react";
import {
  ANALYSIS_ERROR,
  FOLLOW_UP_ERROR,
  MAX_DOCUMENT_CHARS,
  MAX_MESSAGE_CHARS,
  requestAnalysis,
  requestFollowUp,
  type Analysis,
  type ChatMessage,
  type Finding,
  type FollowUp,
} from "./contractApi";

export function isSelectable(finding: Finding) {
  return finding.status !== "samsvarer" && Boolean(finding.suggested_change);
}

export type ChatTurn = { question: string; response: FollowUp };

function recentMessages(turns: ChatTurn[], question: string): ChatMessage[] {
  const messages: ChatMessage[] = turns.slice(-3).flatMap(({ question, response }) => [
    { role: "user", content: question },
    {
      role: "assistant",
      content: (response.draft ? `${response.answer}\n\n${response.draft}` : response.answer)
        .slice(0, MAX_MESSAGE_CHARS),
    },
  ]);
  messages.push({ role: "user", content: question });
  return messages.slice(-6);
}

export function useContractReview() {
  const [offer, setOffer] = useState("");
  const [contract, setContract] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [chatError, setChatError] = useState("");
  const [acceptedDraft, setAcceptedDraft] = useState<string | null>(null);
  const analysisRequest = useRef<AbortController | null>(null);
  const chatRequest = useRef<AbortController | null>(null);

  useEffect(() => () => {
    analysisRequest.current?.abort();
    chatRequest.current?.abort();
  }, []);

  const documents = { offer_text: offer.trim() || null, contract_text: contract.trim() };
  const canAnalyze = documents.contract_text.length > 0 &&
    documents.contract_text.length <= MAX_DOCUMENT_CHARS &&
    (documents.offer_text?.length ?? 0) <= MAX_DOCUMENT_CHARS;
  const suggestions = (analysis?.findings ?? []).flatMap((finding) =>
    selected.includes(finding.id) && finding.suggested_change ? [finding.suggested_change] : [],
  );
  const reply = acceptedDraft ?? (suggestions.length
    ? ["Hei,", ...suggestions, "Vennlig hilsen"].join("\n\n")
    : null);

  function clearResults() {
    analysisRequest.current?.abort();
    chatRequest.current?.abort();
    analysisRequest.current = null;
    chatRequest.current = null;
    setAnalysis(null);
    setSelected([]);
    setLoading(false);
    setError("");
    setTurns([]);
    setMessage("");
    setSending(false);
    setChatError("");
    setAcceptedDraft(null);
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
  }

  async function analyze() {
    if (!canAnalyze || analysisRequest.current) return;
    clearResults();
    const controller = new AbortController();
    analysisRequest.current = controller;
    setLoading(true);
    try {
      const result = await requestAnalysis(documents, controller.signal);
      if (!controller.signal.aborted) setAnalysis(result);
    } catch (cause) {
      if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : ANALYSIS_ERROR);
    } finally {
      if (!controller.signal.aborted) {
        analysisRequest.current = null;
        setLoading(false);
      }
    }
  }

  async function sendMessage(text: string) {
    const question = text.trim();
    if (!analysis || chatRequest.current || !question || question.length > MAX_MESSAGE_CHARS) return;
    const controller = new AbortController();
    chatRequest.current = controller;
    setSending(true);
    setChatError("");
    setMessage(question);
    try {
      const response = await requestFollowUp({
        ...documents,
        findings: analysis.findings,
        messages: recentMessages(turns, question),
        current_draft: reply?.slice(0, 4_000) ?? null,
      }, controller.signal);
      if (!controller.signal.aborted) {
        setTurns((current) => [...current, { question, response }]);
        setMessage("");
      }
    } catch (cause) {
      if (!controller.signal.aborted) setChatError(cause instanceof Error ? cause.message : FOLLOW_UP_ERROR);
    } finally {
      if (!controller.signal.aborted) {
        chatRequest.current = null;
        setSending(false);
      }
    }
  }

  return {
    offer, contract, analysis, selected, loading, error, turns, message, sending, chatError, reply, acceptedDraft,
    canAnalyze, analyze, changeOffer, changeContract, toggleFinding, sendMessage, setMessage, setAcceptedDraft,
  };
}
