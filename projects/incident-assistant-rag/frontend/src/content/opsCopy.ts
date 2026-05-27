/** Centralized UI copy for IncidentIQ (frontend only). */

export const PRODUCT_TAGLINE =
  "Ask operational questions, retrieve runbooks, validate sources, and reduce incident triage time.";

export const NO_KB_MATCH_MESSAGE =
  "No reliable knowledge-base match found. Add a relevant SOP, runbook, postmortem, alert explanation, or ownership document and re-index.";

export const SUPPORTED_FILE_TYPES = ["MD", "TXT", "CSV", "PDF", "DOCX"] as const;

export type QuestionGroup = {
  id: string;
  label: string;
  questions: readonly string[];
};

export const CHAT_QUESTION_GROUPS: readonly QuestionGroup[] = [
  {
    id: "triage",
    label: "Triage",
    questions: [
      "What should I check when users cannot log in after deployment?",
      "How should I investigate database locks?",
    ],
  },
  {
    id: "escalation",
    label: "Escalation",
    questions: ["When should I escalate a production login outage to the backend team?"],
  },
  {
    id: "ownership",
    label: "Ownership",
    questions: ["Which team owns payment service latency incidents?"],
  },
  {
    id: "priority",
    label: "Priority",
    questions: ["What is the best restaurant in Tokyo?"],
  },
  {
    id: "runbooks",
    label: "Runbooks",
    questions: ["What should I do if payment requests are slow and users report timeout?"],
  },
];

export const DEMO_INCIDENT_SCENARIOS = [
  "Many users cannot log in after the latest production deployment on auth-service.",
  "Payment requests are timing out for a subset of users in production.",
] as const;

export type CapabilityItem = {
  title: string;
  description: string;
  tag: string;
};

/** Product capabilities (static explainer cards, not live metrics). */
export const PRODUCT_CAPABILITIES: readonly CapabilityItem[] = [
  {
    tag: "Grounded answers",
    title: "Context-only responses",
    description: "The model answers from retrieved chunks only. Weak or missing matches trigger a refusal—not general knowledge.",
  },
  {
    tag: "FAISS retrieval",
    title: "Semantic search",
    description: "Questions are embedded and matched against runbook chunks stored in a local FAISS index with score filtering.",
  },
  {
    tag: "Incident reasoning",
    title: "Structured triage",
    description: "Incident Analysis produces severity, checks, escalation, and gaps aligned to NOC workflows.",
  },
  {
    tag: "Source transparency",
    title: "Evidence visible",
    description: "Every grounded answer shows filenames, similarity scores, and chunk excerpts for auditability.",
  },
];

export type WorkspaceModule = {
  id: string;
  title: string;
  summary: string;
  action: string;
};

export const WORKSPACE_MODULES: readonly WorkspaceModule[] = [
  {
    id: "chat",
    title: "RAG Chat",
    summary: "Operational Q&A with retrieved runbook context, confidence, and source excerpts.",
    action: "Open RAG Chat",
  },
  {
    id: "incident",
    title: "Incident Analysis",
    summary: "Structured triage report: severity, checks, escalation, and evidence from the knowledge base.",
    action: "Open incident analysis",
  },
  {
    id: "knowledge",
    title: "Knowledge Base",
    summary: "Index sample or uploaded documents into FAISS before querying.",
    action: "Manage knowledge base",
  },
  {
    id: "trust",
    title: "Evaluation & trust",
    summary: "Five scripted eval questions including irrelevant queries; UI surfaces Context · No match when retrieval fails.",
    action: "See README eval section",
  },
];

export const KB_PIPELINE_STEPS = [
  { step: "1", label: "Upload or sample docs", detail: "Course corpus or user uploads" },
  { step: "2", label: "Clean & chunk", detail: "700 chars, 120 overlap" },
  { step: "3", label: "Embed", detail: "text-embedding-3-small" },
  { step: "4", label: "FAISS index", detail: "Local IndexFlatIP store" },
  { step: "5", label: "Grounded Q&A", detail: "Chat & incident analysis" },
] as const;
