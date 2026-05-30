import React, { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  Sparkles,
  Database,
  Search,
  MessageSquare,
  ShieldCheck,
  Server,
  Brain,
  GitBranch,
  Boxes,
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  Cpu,
  Code2,
  Layers,
  Activity,
  Terminal,
  ChevronRight,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const sections = {
  architecture: {
    title: "System Architecture",
    subtitle: "Full-stack RAG application for incident analysis",
    icon: Layers,
    color: "from-slate-900 to-slate-700",
    details:
      "IncidentIQ connects a React frontend to a FastAPI backend. The backend handles document ingestion, embeddings, FAISS retrieval, grounded prompting, OpenAI generation, and optional Supabase metadata/history storage.",
  },
  ingestion: {
    title: "Knowledge Ingestion",
    subtitle: "Documents become searchable operational knowledge",
    icon: Upload,
    color: "from-blue-900 to-blue-700",
    details:
      "The system supports MD, TXT, CSV, PDF, and DOCX files. Each document is loaded, cleaned, split into overlapping chunks, embedded with OpenAI, and stored in FAISS with metadata.",
  },
  rag: {
    title: "RAG Chat Pipeline",
    subtitle: "Grounded answers with sources and confidence",
    icon: MessageSquare,
    color: "from-violet-900 to-violet-700",
    details:
      "User questions are embedded, matched against FAISS, converted into a grounded prompt, and answered by OpenAI. The response includes sources, chunk scores, confidence, and no-context behavior.",
  },
  incident: {
    title: "Incident Reasoning",
    subtitle: "Structured analysis for production incidents",
    icon: AlertTriangle,
    color: "from-amber-900 to-amber-700",
    details:
      "Incident descriptions are analyzed with severity estimation, relevant runbook retrieval, structured prompting, JSON validation, fallback handling, next actions, escalation guidance, and source-backed confidence.",
  },
  api: {
    title: "API Layer",
    subtitle: "FastAPI endpoints for app features",
    icon: Server,
    color: "from-emerald-900 to-emerald-700",
    details:
      "The backend exposes health, upload, document indexing, uploaded document listing, RAG chat, and incident analysis endpoints under /api.",
  },
  infrastructure: {
    title: "Infrastructure",
    subtitle: "Local Dockerized deployment",
    icon: Boxes,
    color: "from-cyan-900 to-cyan-700",
    details:
      "The app runs locally with Docker Compose. The frontend is served through Nginx on localhost:3000, while FastAPI runs on localhost:8000 with Swagger available at /docs.",
  },
  testing: {
    title: "Testing & Evaluation",
    subtitle: "Reliability, validation, and build checks",
    icon: CheckCircle2,
    color: "from-green-900 to-green-700",
    details:
      "Backend tests are run with Pytest, expected to pass 81 tests. Evaluation questions live in evaluation/test_questions.json, and the frontend build runs TypeScript checks before Vite build.",
  },
  security: {
    title: "Security Practices",
    subtitle: "Secrets and generated files stay protected",
    icon: ShieldCheck,
    color: "from-rose-900 to-rose-700",
    details:
      "API keys stay in backend .env files ignored by Git. The frontend never receives secret keys. Uploads are renamed with UUIDs, and generated FAISS/embedding files are not committed.",
  },
};

const mainFlow = [
  { id: "user", label: "User", icon: Activity, section: "architecture" },
  { id: "frontend", label: "React Frontend", icon: Code2, section: "architecture" },
  { id: "backend", label: "FastAPI Backend", icon: Server, section: "api" },
  { id: "ingestion", label: "Document Pipeline", icon: Upload, section: "ingestion" },
  { id: "faiss", label: "FAISS Vector Store", icon: Database, section: "rag" },
  { id: "retriever", label: "Retriever", icon: Search, section: "rag" },
  { id: "prompt", label: "Prompt Builder", icon: FileText, section: "rag" },
  { id: "openai", label: "OpenAI Generator", icon: Brain, section: "rag" },
  { id: "answer", label: "Answer + Sources", icon: Sparkles, section: "rag" },
];

const ragSteps = [
  "User asks a question",
  "Question is embedded",
  "FAISS retrieves relevant chunks",
  "Backend builds grounded prompt",
  "OpenAI generates answer",
  "Frontend shows answer, sources, scores, and confidence",
];

const incidentSteps = [
  "Incident description is submitted",
  "Severity is estimated",
  "Relevant runbooks are retrieved from FAISS",
  "Structured incident prompt is built",
  "JSON analysis is generated",
  "Response is validated or fallback is used",
  "Severity, causes, checks, missing info, next action, escalation, sources, and confidence are returned",
];

const endpoints = [
  ["GET", "/api/health", "Backend health check"],
  ["POST", "/api/upload", "Upload document"],
  ["GET", "/api/documents/samples", "List sample documents"],
  ["POST", "/api/documents/index-samples", "Index sample documents"],
  ["GET", "/api/documents/uploaded", "List uploaded documents"],
  ["POST", "/api/documents/index-uploaded", "Index uploaded documents"],
  ["POST", "/api/chat", "Ask a RAG question"],
  ["POST", "/api/incident/analyze", "Analyze an incident"],
];

const techStack = [
  { title: "Backend", items: ["Python", "FastAPI", "Pydantic", "OpenAI API", "FAISS", "Pytest"] },
  { title: "Frontend", items: ["React", "TypeScript", "Vite", "Nginx"] },
  { title: "Database", items: ["Supabase Postgres", "Metadata", "History", "Optional mode"] },
  { title: "Infrastructure", items: ["Docker", "Docker Compose", "Localhost", "Swagger"] },
];

const edgeCases = [
  "Empty upload file",
  "Unsupported file type",
  "Missing file extension",
  "Large file validation",
  "Empty CSV",
  "Unreadable PDF",
  "PDF with no extractable text",
  "Empty DOCX",
  "Empty question",
  "Invalid top_k",
  "Missing FAISS index",
  "Low-confidence retrieval",
  "Irrelevant questions",
  "Bad JSON from LLM",
  "Database unavailable",
  "Supabase disabled mode",
  "Embedding dimension mismatch",
  "FAISS metadata mismatch",
];

function FlowNode({ node, active, onClick }) {
  const Icon = node.icon;
  return (
    <button
      onClick={() => onClick(node.section)}
      className={`group relative min-w-[150px] rounded-2xl border p-4 text-left shadow-sm transition-all duration-300 ${
        active ? "border-slate-900 bg-white shadow-xl scale-[1.03]" : "border-slate-200 bg-white/80 hover:bg-white hover:shadow-lg"
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`rounded-xl p-2 ${active ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-700 group-hover:bg-slate-900 group-hover:text-white"}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <div className="text-sm font-bold text-slate-900">{node.label}</div>
          <div className="text-xs text-slate-500">Click to explore</div>
        </div>
      </div>
    </button>
  );
}

function SectionCard({ section }) {
  const Icon = section.icon;
  return (
    <motion.div
      key={section.title}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.25 }}
    >
      <Card className="overflow-hidden rounded-3xl border-0 shadow-xl">
        <div className={`bg-gradient-to-br ${section.color} p-6 text-white`}>
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="mb-3 inline-flex rounded-2xl bg-white/15 p-3 backdrop-blur">
                <Icon className="h-7 w-7" />
              </div>
              <h2 className="text-2xl font-black tracking-tight">{section.title}</h2>
              <p className="mt-1 text-sm text-white/80">{section.subtitle}</p>
            </div>
            <Sparkles className="h-6 w-6 text-white/70" />
          </div>
        </div>
        <CardContent className="p-6">
          <p className="text-sm leading-7 text-slate-700">{section.details}</p>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function StepList({ title, steps, icon: Icon }) {
  return (
    <Card className="rounded-3xl border-slate-200 bg-white/85 shadow-sm backdrop-blur">
      <CardContent className="p-5">
        <div className="mb-4 flex items-center gap-2">
          <div className="rounded-xl bg-slate-900 p-2 text-white">
            <Icon className="h-4 w-4" />
          </div>
          <h3 className="font-bold text-slate-900">{title}</h3>
        </div>
        <div className="space-y-3">
          {steps.map((step, index) => (
            <div key={step} className="flex gap-3">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-700">
                {index + 1}
              </div>
              <div className="pt-1 text-sm text-slate-700">{step}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function IncidentIQInteractiveDiagram() {
  const [activeKey, setActiveKey] = useState("architecture");
  const activeSection = sections[activeKey];

  const selectedNodes = useMemo(
    () => mainFlow.filter((node) => node.section === activeKey).map((node) => node.id),
    [activeKey]
  );

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#eef2ff,transparent_34%),linear-gradient(135deg,#f8fafc,#eef2f7)] p-4 text-slate-900 md:p-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="overflow-hidden rounded-[2rem] bg-slate-950 shadow-2xl"
        >
          <div className="grid gap-8 p-7 text-white md:grid-cols-[1.2fr_0.8fr] md:p-10">
            <div>
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white/80 backdrop-blur">
                <Activity className="h-4 w-4" />
                IncidentIQ Architecture Diagram
              </div>
              <h1 className="text-4xl font-black tracking-tight md:text-6xl">
                Professional Interactive RAG System Map
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-8 text-white/75">
                A visual walkthrough of the IncidentIQ full-stack Retrieval-Augmented Generation application: frontend, backend, ingestion, FAISS search, OpenAI generation, incident reasoning, testing, Docker deployment, and security.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                {Object.entries(sections).map(([key, section]) => {
                  const Icon = section.icon;
                  return (
                    <Button
                      key={key}
                      onClick={() => setActiveKey(key)}
                      className={`rounded-full px-4 py-2 text-sm transition-all ${
                        activeKey === key
                          ? "bg-white text-slate-950 hover:bg-white"
                          : "bg-white/10 text-white hover:bg-white/20"
                      }`}
                    >
                      <Icon className="mr-2 h-4 w-4" />
                      {section.title}
                    </Button>
                  );
                })}
              </div>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-white/90">
                <PlayCircle className="h-4 w-4" />
                Recommended Demo Flow
              </div>
              <div className="space-y-3 text-sm text-white/75">
                {[
                  "Open localhost:3000",
                  "Index sample documents",
                  "Ask a login failure RAG question",
                  "Review sources and confidence",
                  "Analyze a production auth incident",
                  "Confirm severity, checks, escalation, and next action",
                ].map((item, index) => (
                  <div key={item} className="flex items-center gap-3 rounded-2xl bg-white/5 p-3">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-xs font-black text-slate-950">
                      {index + 1}
                    </span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
          <Card className="rounded-[2rem] border-slate-200 bg-white/75 p-4 shadow-xl backdrop-blur">
            <CardContent className="p-2 md:p-4">
              <div className="mb-5 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-xl font-black text-slate-900">End-to-End System Flow</h2>
                  <p className="text-sm text-slate-500">Click any node to focus the explanation panel.</p>
                </div>
                <GitBranch className="h-6 w-6 text-slate-400" />
              </div>

              <div className="overflow-x-auto pb-3">
                <div className="flex min-w-max items-center gap-3">
                  {mainFlow.map((node, index) => (
                    <React.Fragment key={node.id}>
                      <FlowNode
                        node={node}
                        active={selectedNodes.includes(node.id)}
                        onClick={setActiveKey}
                      />
                      {index < mainFlow.length - 1 && (
                        <ChevronRight className="h-6 w-6 shrink-0 text-slate-300" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {techStack.map((group) => (
                  <Card key={group.title} className="rounded-3xl border-slate-200 bg-slate-50 shadow-none">
                    <CardContent className="p-5">
                      <h3 className="mb-3 font-black text-slate-900">{group.title}</h3>
                      <div className="flex flex-wrap gap-2">
                        {group.items.map((item) => (
                          <span key={item} className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-600 shadow-sm">
                            {item}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          <AnimatePresence mode="wait">
            <SectionCard section={activeSection} />
          </AnimatePresence>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <StepList title="RAG Chat Pipeline" steps={ragSteps} icon={MessageSquare} />
          <StepList title="Incident Reasoning Pipeline" steps={incidentSteps} icon={AlertTriangle} />
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
          <Card className="rounded-[2rem] border-slate-200 bg-white/85 shadow-xl backdrop-blur">
            <CardContent className="p-6">
              <div className="mb-5 flex items-center gap-2">
                <div className="rounded-xl bg-slate-900 p-2 text-white">
                  <Terminal className="h-4 w-4" />
                </div>
                <h2 className="text-xl font-black text-slate-900">API Endpoints</h2>
              </div>
              <div className="overflow-hidden rounded-2xl border border-slate-200">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="p-3">Method</th>
                      <th className="p-3">Endpoint</th>
                      <th className="p-3">Purpose</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white">
                    {endpoints.map(([method, endpoint, desc]) => (
                      <tr key={endpoint} className="hover:bg-slate-50">
                        <td className="p-3">
                          <span className={`rounded-full px-2 py-1 text-xs font-black ${method === "GET" ? "bg-blue-50 text-blue-700" : "bg-emerald-50 text-emerald-700"}`}>
                            {method}
                          </span>
                        </td>
                        <td className="p-3 font-mono text-xs font-bold text-slate-800">{endpoint}</td>
                        <td className="p-3 text-slate-600">{desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-[2rem] border-slate-200 bg-white/85 shadow-xl backdrop-blur">
            <CardContent className="p-6">
              <div className="mb-5 flex items-center gap-2">
                <div className="rounded-xl bg-slate-900 p-2 text-white">
                  <Cpu className="h-4 w-4" />
                </div>
                <h2 className="text-xl font-black text-slate-900">Quality & Edge Cases</h2>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {edgeCases.map((item) => (
                  <div key={item} className="flex items-start gap-2 rounded-2xl bg-slate-50 p-3 text-sm text-slate-700">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-slate-500" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="rounded-[2rem] border-slate-200 bg-white/85 shadow-xl backdrop-blur">
          <CardContent className="grid gap-6 p-6 md:grid-cols-3">
            <div className="rounded-3xl bg-slate-950 p-5 text-white">
              <ShieldCheck className="mb-4 h-8 w-8 text-white/80" />
              <h3 className="font-black">Security</h3>
              <p className="mt-2 text-sm leading-6 text-white/70">
                Backend-only secrets, ignored .env files, UUID upload names, and generated FAISS files excluded from Git.
              </p>
            </div>
            <div className="rounded-3xl bg-slate-100 p-5">
              <Database className="mb-4 h-8 w-8 text-slate-700" />
              <h3 className="font-black text-slate-900">Optional Supabase</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                DATABASE_ENABLED can remain false locally, then be enabled after running the schema in Supabase SQL Editor.
              </p>
            </div>
            <div className="rounded-3xl bg-slate-100 p-5">
              <Boxes className="mb-4 h-8 w-8 text-slate-700" />
              <h3 className="font-black text-slate-900">Docker Demo</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Docker Compose builds and runs the frontend, backend, and local app access through localhost ports.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
