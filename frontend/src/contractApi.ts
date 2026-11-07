export type Finding = {
  id: string;
  category: "leveranse" | "betaling" | "ekstraarbeid" | "ansvar";
  status: "samsvarer" | "avvik" | "risiko" | "må_avklares";
  explanation: string;
  offer_quote: string | null;
  contract_quote: string | null;
  suggested_change: string | null;
};

type Mode = "mock" | "live";
export type Analysis = { mode: Mode; findings: Finding[] };
export type ChatMessage = { role: "user" | "assistant"; content: string };
export type FollowUp = {
  mode: Mode;
  answer: string;
  sources: { document: "offer" | "contract"; quote: string }[];
  draft: string | null;
};
type Documents = { offer_text: string | null; contract_text: string };
type FollowUpRequest = Documents & {
  findings: Finding[];
  messages: ChatMessage[];
  current_draft: string | null;
};

export const MAX_DOCUMENT_CHARS = 20_000;
export const MAX_MESSAGE_CHARS = 2_000;
export const ANALYSIS_ERROR = "Analysen kunne ikke gjennomføres. Prøv igjen.";
export const FOLLOW_UP_ERROR = "Meldingen kunne ikke besvares. Prøv igjen.";

async function post(path: string, payload: Documents, fallback: string, signal: AbortSignal) {
  let response: Response;
  try {
    response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal,
    });
  } catch {
    throw new Error("Fikk ikke kontakt med tjenesten. Prøv igjen.");
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail: unknown = body?.detail;
    throw new Error(typeof detail === "string" && detail.trim() && detail.length <= 200 ? detail : fallback);
  }
  if (body?.mode !== "mock" && body?.mode !== "live") throw new Error(fallback);
  return body;
}

export async function requestAnalysis(documents: Documents, signal: AbortSignal): Promise<Analysis> {
  const body = await post("/analyze", documents, ANALYSIS_ERROR, signal);
  if (!Array.isArray(body.findings)) throw new Error(ANALYSIS_ERROR);
  return body;
}

export async function requestFollowUp(payload: FollowUpRequest, signal: AbortSignal): Promise<FollowUp> {
  const body = await post("/follow-up", payload, FOLLOW_UP_ERROR, signal);
  if (typeof body.answer !== "string" || !Array.isArray(body.sources) ||
      (body.draft !== null && typeof body.draft !== "string")) {
    throw new Error(FOLLOW_UP_ERROR);
  }
  return body;
}
