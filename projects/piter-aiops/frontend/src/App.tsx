import { useState, useRef, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { askQuestion, triageAlert, uploadDocument } from "@/lib/api";
import { useBootstrap } from "@/context/bootstrap";
import { useDemoTour } from "@/context/demo-tour";
import { useWorkflowSession } from "@/context/workflow-session";
import { AppTopBar } from "@/components/AppTopBar";
import { DemoDashboard } from "@/components/DemoDashboard";
import { CitationList, FormattedAnswer } from "@/components/FormattedAnswer";
import { EnrichmentPanel } from "@/components/EnrichmentPanel";
import {
  StepPipeline,
  WORKFLOW_PIPELINE_ORDER,
  WORKFLOW_PIPELINE_STEPS,
} from "@/components/StepPipeline";
import { delay, rankSimilarAlerts, alertImpactDollars, alertSavedMinutes } from "@/lib/workflow-utils";
import type { Citation, RagAnswer, WorkflowAlert, WorkflowTriagePayload } from "@/types/rag";
import {
  FileText,
  Database,
  Server,
  Container,
  Cloud,
  Globe,
  MessageSquare,
  Trash2,
  CheckCircle2,
  ArrowRight,
  Lightbulb,
  Target,
  Layers,
  Terminal,
  X,
  Play,
  Loader2,
  AlertTriangle,
  Sparkles,
  Scissors,
  Search,
  Bell,
  ShieldCheck,
  ArrowUpRight,
  TrendingDown,
  Activity,
  Upload,
} from "lucide-react";
// ---------- Data ----------

type Step = {
  n: number;
  title: string;
  plain: string; // non-technical explanation
  tech: string; // technical detail
  icon: React.ComponentType<{ className?: string }>;
  color: string; // semantic token name
};

const STEPS: Step[] = [
  {
    n: 1,
    title: "Collect Runbooks & Incident History",
    plain:
      "I gather the team's runbooks, past alert tickets, post-mortems and on-call notes — the knowledge that today only lives in people's heads or scattered wiki pages.",
    tech: "PDF / MD / TXT / JSON alert exports uploaded to an S3 bucket that the Knowledge Base reads from.",
    icon: FileText,
    color: "ingest",
  },
  {
    n: 2,
    title: "Build the Bedrock Knowledge Base",
    plain:
      "Amazon Bedrock indexes everything so when an on-call engineer asks a question about an alert, the system knows exactly where to look.",
    tech: "Bedrock Knowledge Base + vector store. Data source synced from S3; embeddings indexed for retrieval.",
    icon: Database,
    color: "rag",
  },
  {
    n: 3,
    title: "Flask Triage UI (with boto3)",
    plain:
      "A simple web console: paste an alert or ask a question, get back a grounded answer with the source runbook, plus suggested next steps.",
    tech: "Python Flask app; boto3 calls bedrock-agent-runtime RetrieveAndGenerate; UI shows answer + citations + latency.",
    icon: Server,
    color: "interface",
  },
  {
    n: 4,
    title: "Containerize with Docker",
    plain:
      "I wrap the app into a container so it runs identically on a laptop, a staging box or production — no setup surprises.",
    tech: "Dockerfile with python:3.11-slim base, requirements.txt, EXPOSE 5000, CMD gunicorn/flask run.",
    icon: Container,
    color: "tools",
  },
  {
    n: 5,
    title: "Deploy to EC2",
    plain:
      "A small Linux VM on AWS hosts the container so the whole on-call team can reach it from a browser.",
    tech: "EC2 instance (Amazon Linux), Docker installed, image pulled/copied, container run with port 80→5000 exposed via security group.",
    icon: Cloud,
    color: "agent",
  },
  {
    n: 6,
    title: "Public URL & Demo",
    plain:
      "Anyone on the team opens the URL during an incident, asks a question, and gets the answer plus the source — in seconds.",
    tech: "Access via EC2 public IPv4 / DNS. Screenshots captured for KB, sync, EC2, container, and a real alert Q&A.",
    icon: Globe,
    color: "resolution",
  },
  {
    n: 7,
    title: "Cleanup",
    plain:
      "When the demo is done, I delete the AWS resources so nothing keeps costing money.",
    tech: "Terminate EC2, delete KB + data source, empty/delete S3 bucket, remove IAM roles created for the demo.",
    icon: Trash2,
    color: "ingest",
  },
];

// ---------- Page ----------

function AppShell() {
  const { sessionTotals, triageCount, lastTriageAt } = useWorkflowSession();

  return (
    <main className="min-h-screen overflow-x-hidden text-foreground">
      <AppTopBar
        totalSavedDollars={sessionTotals.dollars}
        totalSavedMin={sessionTotals.minutes}
        triageCount={triageCount}
        lastTriageAt={lastTriageAt}
      />
      <Hero />
      <Problem />
      <MvpWorkflow />
      <DemoDashboard />
      <Architecture />
      <LiveKnowledgeBase />
      <DocumentUpload />
      <Flow />
      <Stack />
      <Deliverables />
      <Footer />
    </main>
  );
}

export default function App() {
  const { loading, error } = useBootstrap();

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center text-muted-foreground">
        <Loader2 className="size-6 animate-spin mr-2" />
        Loading PITER AiOps…
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-md rounded-lg border border-border bg-card p-4 text-sm">
          <div className="font-medium text-[var(--destructive)]">Could not load app</div>
          <p className="mt-2 text-muted-foreground">{error}</p>
        </div>
      </main>
    );
  }

  return <AppShell />;
}

// ---------- Sections ----------

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="absolute inset-0 grid-bg opacity-30" aria-hidden />
      <div className="relative mx-auto max-w-6xl px-6 py-20 md:py-28">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl"
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-xs text-muted-foreground">
            <Lightbulb className="size-3.5 text-[var(--tools)]" />
            From Alert to Resolution, Faster.
          </span>
          <h1 className="mt-5 text-4xl md:text-6xl font-semibold tracking-tight">
            <span className="text-[var(--tools)]">PITER AiOps</span>
            <br />
            AI-Powered Incident Operations
          </h1>
          <p className="mt-3 text-sm md:text-base text-muted-foreground">
            Priority. Investigation. Triage. Escalation. Resolution.
          </p>
          <p className="mt-4 text-base md:text-lg text-muted-foreground leading-relaxed">
            Production incidents cost enterprise teams money, engineering time, customer trust,
            and reputation. PITER AiOps applies a structured five-stage incident-response framework
            to help operations teams prioritize, investigate, triage, escalate, and resolve
            incidents faster — with RAG, tools, and guided workflows.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="#priority-center"
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition"
            >
              Run the PITER workflow <ArrowRight className="size-4" />
            </a>
            <a
              href="#architecture"
              className="inline-flex items-center gap-2 rounded-md border border-border bg-card/60 px-4 py-2 text-sm font-medium hover:bg-card transition"
            >
              See the architecture
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Problem() {
  const items = [
    {
      icon: Target,
      title: "Business impact",
      body:
        "Unstructured incident response inflates MTTR, burns engineer hours, and amplifies revenue and reputational risk. Alert fatigue makes P1 signals harder to spot in the noise.",
    },
    {
      icon: Lightbulb,
      title: "PITER framework",
      body:
        "PITER combines the five golden pillars of effective incident response: Priority, Investigation, Triage, Escalation, and Resolution — each stage enriched with knowledge-base evidence and operational tools.",
    },
    {
      icon: Layers,
      title: "Why it matters",
      body:
        "Lower MTTR, less tribal knowledge, faster onboarding for new on-call. Same RAG pattern companies like Amdocs use for internal support and SRE assistants.",
    },
  ];
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
          What I'm solving
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {items.map((it) => (
            <div
              key={it.title}
              className="glass rounded-xl p-5"
            >
              <it.icon className="size-5 text-[var(--tools)]" />
              <h3 className="mt-3 font-medium">{it.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                {it.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

type BlockKey = "documents" | "kb" | "flask" | "docker" | "ec2" | "public";

type BlockDemo = {
  key: BlockKey;
  label: string;
  sub: string;
  color: string;
  icon: React.ComponentType<{ className?: string }>;
  summary: string;
  call: { lang: string; title: string; code: string };
  result: { title: string; lines: string[] };
  plan: string[];
};

const BLOCKS: Record<BlockKey, BlockDemo> = {
  documents: {
    key: "documents",
    label: "Documents",
    sub: "PDF / TXT / DOCX",
    color: "ingest",
    icon: FileText,
    summary:
      "Runbooks, alert exports and post-mortems. Uploaded to an S3 bucket that the Knowledge Base reads from.",
    call: {
      lang: "bash",
      title: "Upload to S3",
      code: `aws s3 cp ./knowledge_base/ s3://piter-aiops-kb/ \\
  --recursive --exclude "*.DS_Store"`,
    },
    result: {
      title: "Upload report",
      lines: [
        "upload: knowledge_base/runbooks/postgres-cpu.md       →  s3://piter-aiops-kb/runbooks/postgres-cpu.md",
        "upload: knowledge_base/incidents/postmortem_2024_07.md  →  s3://piter-aiops-kb/incidents/postmortem_2024_07.md",
        "upload: knowledge_base/policies/alert-reference.md    →  s3://piter-aiops-kb/policies/alert-reference.md",
        "37 objects uploaded · 18.4 MB total",
      ],
    },
    plan: [
      "Confirm all files reach S3",
      "Trigger a Knowledge Base sync",
      "Wait for ingestion to finish",
    ],
  },
  kb: {
    key: "kb",
    label: "Bedrock KB",
    sub: "S3 + Vector index",
    color: "rag",
    icon: Database,
    summary:
      "Amazon Bedrock chunks runbooks and incidents, embeds them, and stores them in a vector index for retrieval.",
    call: {
      lang: "python",
      title: "boto3 · RetrieveAndGenerate",
      code: `client = boto3.client("bedrock-agent-runtime")
resp = client.retrieve_and_generate(
  input={"text": "Postgres CPU is 95% on prod-db-1. What do I do?"},
  retrieveAndGenerateConfiguration={
    "type": "KNOWLEDGE_BASE",
    "knowledgeBaseConfiguration": {
      "knowledgeBaseId": "KB-ABC123",
      "modelArn": "anthropic.claude-3-haiku-...",
    },
  },
)`,
    },
    result: {
      title: "Retrieved citations",
      lines: [
        "runbook_db_cpu.md          · chunk 3  · score 0.93",
        "postmortem_2024_07.pdf     · chunk 9  · score 0.81",
        'answer: "Check long-running queries via pg_stat_activity, then..."',
      ],
    },
    plan: [
      "Return answer text to Flask",
      "Attach source runbooks to the response",
      "Log query for SRE analytics",
    ],
  },
  flask: {
    key: "flask",
    label: "Flask + boto3",
    sub: "Alert → Answer",
    color: "interface",
    icon: Server,
    summary:
      "A small Python web server. Renders the triage console, takes the alert/question, calls Bedrock, returns the answer.",
    call: {
      lang: "http",
      title: "Browser → Flask",
      code: `POST /ask  HTTP/1.1
Content-Type: application/json

{ "question": "Postgres CPU 95% on prod-db-1 — runbook?" }`,
    },
    result: {
      title: "Flask response",
      lines: [
        "200 OK · 412 ms",
        '{ "answer": "Inspect pg_stat_activity, kill long queries...",',
        '  "sources": ["runbook_db_cpu.md", "postmortem_2024_07.pdf"] }',
      ],
    },
    plan: [
      "Render answer in the UI",
      "Show source filenames under the answer",
      "Keep the input ready for the next question",
    ],
  },
  docker: {
    key: "docker",
    label: "Docker",
    sub: "Portable image",
    color: "tools",
    icon: Container,
    summary:
      "Packages Flask + Python deps + config into a single image that runs the same anywhere.",
    call: {
      lang: "bash",
      title: "Build & run locally",
      code: `docker build -t piter-aiops:1.0 .
docker run -p 5000:5000 \\
  -e AWS_REGION=us-east-1 \\
  -e KB_ID=KB-ABC123 \\
  piter-aiops:1.0`,
    },
    result: {
      title: "Container status",
      lines: [
        "Successfully built sha256:9f3a…",
        "Successfully tagged piter-aiops:1.0",
        "Container started · listening on 0.0.0.0:5000",
      ],
    },
    plan: [
      "Push image to a registry (or copy to EC2)",
      "Provision the EC2 instance",
      "Run the same image in production",
    ],
  },
  ec2: {
    key: "ec2",
    label: "EC2 Instance",
    sub: "Runs the container",
    color: "agent",
    icon: Cloud,
    summary:
      "A small Linux virtual machine on AWS that hosts the Docker container and exposes a port.",
    call: {
      lang: "bash",
      title: "On the EC2 host",
      code: `ssh ec2-user@<public-ip>
sudo yum install -y docker && sudo service docker start
docker load -i piter-aiops.tar
docker run -d -p 80:5000 \\
  --restart unless-stopped piter-aiops:1.0`,
    },
    result: {
      title: "Host check",
      lines: [
        "CONTAINER ID   IMAGE             STATUS         PORTS",
        "a91c2f5e8b1d   piter-aiops:1.0  Up 12 seconds  0.0.0.0:80->5000/tcp",
        "Security group: inbound 80/tcp from 0.0.0.0/0  ✓",
      ],
    },
    plan: [
      "Verify the public URL responds",
      "Capture proof screenshots",
      "Schedule cleanup after the demo",
    ],
  },
  public: {
    key: "public",
    label: "Public URL",
    sub: "On-call team uses it",
    color: "resolution",
    icon: Globe,
    summary:
      "The live, shareable endpoint that on-call engineers (and reviewers) open during an incident.",
    call: {
      lang: "bash",
      title: "Smoke test",
      code: `curl -s http://ec2-1-2-3-4.compute.amazonaws.com/ask \\
  -H "Content-Type: application/json" \\
  -d '{"question":"Postgres CPU 95% on prod-db-1 — runbook?"}'`,
    },
    result: {
      title: "Live answer",
      lines: [
        '{ "answer": "Inspect pg_stat_activity, kill long queries...",',
        '  "sources": ["runbook_db_cpu.md", "postmortem_2024_07.pdf"],',
        '  "latency_ms": 480 }',
      ],
    },
    plan: [
      "Share the URL with the on-call team",
      "Collect a real alert Q&A screenshot",
      "Run cleanup: terminate EC2, delete KB + S3",
    ],
  },
};

const FLOW: BlockKey[] = ["documents", "kb", "flask", "docker", "ec2", "public"];
const ARROW_LABELS = ["upload", "retrieve", "serve", "ship", "deploy"];

function Architecture() {
  const { architectureBlock, setArchitectureBlock } = useDemoTour();
  const active = architectureBlock;
  const block = BLOCKS[active];

  return (
    <section id="architecture" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
          Interactive architecture
        </h2>
        <p className="mt-2 text-muted-foreground max-w-2xl">
          Click any block to see an example tool call, the live response, and
          the resolution plan that follows.
        </p>

        <div className="mt-10 glass rounded-2xl p-6 md:p-8">
          <div className="flex flex-wrap items-stretch gap-3 md:gap-2 md:flex-nowrap">
            {FLOW.map((key, i) => (
              <div key={key} className="contents md:flex md:items-stretch md:flex-1">
                <ArchBlock
                  block={BLOCKS[key]}
                  active={active === key}
                  onClick={() => setArchitectureBlock(key)}
                />
                {i < FLOW.length - 1 && <Arrow label={ARROW_LABELS[i]} />}
              </div>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={active}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              className="mt-8 rounded-xl border border-border bg-background/60 p-5 md:p-6"
            >
              <DetailPanel block={block} onClose={() => setArchitectureBlock("kb")} />
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}

function ArchBlock({
  block,
  active,
  onClick,
}: {
  block: BlockDemo;
  active: boolean;
  onClick: () => void;
}) {
  const Icon = block.icon;
  return (
    <motion.button
      type="button"
      onClick={onClick}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      aria-pressed={active}
      className="flex-1 min-w-[140px] rounded-xl border border-border bg-card/60 p-4 text-center cursor-pointer transition-colors hover:bg-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      style={{
        boxShadow: active
          ? `0 0 0 2px var(--${block.color}), 0 12px 36px -14px var(--${block.color})`
          : `0 0 0 1px var(--${block.color}), 0 10px 30px -16px var(--${block.color})`,
        opacity: active ? 1 : 0.9,
      }}
    >
      <div className="mx-auto w-fit" style={{ color: `var(--${block.color})` }}>
        <Icon className="size-6" />
      </div>
      <div className="mt-2 text-sm font-medium">{block.label}</div>
      <div className="text-xs text-muted-foreground">{block.sub}</div>
    </motion.button>
  );
}

function Arrow({ label }: { label: string }) {
  return (
    <div className="hidden md:flex flex-col items-center justify-center px-1 text-muted-foreground">
      <ArrowRight className="size-5" />
      <span className="mt-1 text-[10px] uppercase tracking-wider">{label}</span>
    </div>
  );
}

function DetailPanel({
  block,
  onClose,
}: {
  block: BlockDemo;
  onClose: () => void;
}) {
  const Icon = block.icon;
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div
            className="flex size-9 items-center justify-center rounded-md"
            style={{
              backgroundColor: `color-mix(in oklab, var(--${block.color}) 22%, transparent)`,
              color: `var(--${block.color})`,
            }}
          >
            <Icon className="size-5" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">
              Live demo
            </div>
            <h3 className="text-lg font-medium">{block.label}</h3>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Reset selection"
          className="rounded-md p-1.5 text-muted-foreground hover:bg-card hover:text-foreground transition-colors"
        >
          <X className="size-4" />
        </button>
      </div>

      <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
        {block.summary}
      </p>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <CodeCard
          title={block.call.title}
          lang={block.call.lang}
          code={block.call.code}
          color={block.color}
        />
        <div className="rounded-lg border border-border bg-card/60 p-4">
          <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
            <Terminal className="size-3.5" />
            {block.result.title}
          </div>
          <pre className="mt-3 whitespace-pre-wrap break-words font-mono text-xs leading-relaxed text-foreground/90">
            {block.result.lines.join("\n")}
          </pre>
        </div>
      </div>

      <div className="mt-5 rounded-lg border border-border bg-card/60 p-4">
        <div className="text-xs uppercase tracking-wider text-muted-foreground">
          Resolution plan
        </div>
        <ol className="mt-3 space-y-2">
          {block.plan.map((step, i) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              <span
                className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold"
                style={{
                  backgroundColor: `color-mix(in oklab, var(--${block.color}) 25%, transparent)`,
                  color: `var(--${block.color})`,
                }}
              >
                {i + 1}
              </span>
              <span className="text-foreground/90">{step}</span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}

function CodeCard({
  title,
  lang,
  code,
  color,
}: {
  title: string;
  lang: string;
  code: string;
  color: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-background/80 overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="text-xs font-medium">{title}</span>
        <span
          className="rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider"
          style={{
            backgroundColor: `color-mix(in oklab, var(--${color}) 22%, transparent)`,
            color: `var(--${color})`,
          }}
        >
          {lang}
        </span>
      </div>
      <pre className="max-w-full overflow-x-auto p-3 font-mono text-xs leading-relaxed text-foreground/90">
        {code}
      </pre>
    </div>
  );
}

function Flow() {
  return (
    <section id="flow" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
          How it works, step by step
        </h2>
        <p className="mt-2 text-muted-foreground max-w-2xl">
          Each step has a <em>plain-English</em> version for non-technical
          reviewers and a <em>technical</em> note for engineers.
        </p>

        <ol className="mt-10 space-y-4">
          {STEPS.map((s, i) => (
            <motion.li
              key={s.n}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.04 }}
              className="glass rounded-xl p-5 md:p-6"
            >
              <div className="flex items-start gap-4">
                <div
                  className="flex size-10 shrink-0 items-center justify-center rounded-lg"
                  style={{
                    backgroundColor: `color-mix(in oklab, var(--${s.color}) 20%, transparent)`,
                    color: `var(--${s.color})`,
                  }}
                >
                  <s.icon className="size-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Step {s.n}</span>
                  </div>
                  <h3 className="mt-1 text-lg font-medium">{s.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                    {s.plain}
                  </p>
                  <div className="mt-3 rounded-md border border-border bg-background/60 p-3 text-xs text-muted-foreground">
                    <span className="font-medium text-foreground">Technical: </span>
                    {s.tech}
                  </div>
                </div>
              </div>
            </motion.li>
          ))}
        </ol>
      </div>
    </section>
  );
}

function Stack() {
  const stack = [
    { name: "Amazon Bedrock", role: "Knowledge Base + LLM" },
    { name: "Amazon S3", role: "Document storage / data source" },
    { name: "Python + Flask", role: "Web app & routing" },
    { name: "boto3", role: "AWS SDK from Python" },
    { name: "Docker", role: "Containerization" },
    { name: "Amazon EC2", role: "Public hosting" },
  ];
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
          Tech stack
        </h2>
        <div className="mt-8 grid gap-3 sm:grid-cols-2 md:grid-cols-3">
          {stack.map((s) => (
            <div
              key={s.name}
              className="flex items-center justify-between rounded-lg border border-border bg-card/60 px-4 py-3"
            >
              <span className="text-sm font-medium">{s.name}</span>
              <span className="text-xs text-muted-foreground">{s.role}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Deliverables() {
  const items = [
    "Bedrock Knowledge Base screenshot + successful sync",
    "Flask app running locally and in the browser",
    "Dockerfile + image built and running as a container",
    "EC2 instance details + publicly accessible URL",
    "Real question → real answer example",
    "Cleanup note: all AWS resources deleted",
  ];
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
          What I'll submit
        </h2>
        <ul className="mt-8 grid gap-3 md:grid-cols-2">
          {items.map((t) => (
            <li
              key={t}
              className="flex items-start gap-3 rounded-lg border border-border bg-card/60 px-4 py-3"
            >
              <CheckCircle2 className="size-5 shrink-0 text-[var(--resolution)]" />
              <span className="text-sm">{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="mx-auto max-w-6xl px-6 py-10 text-center text-xs text-muted-foreground">
      <MessageSquare className="mx-auto size-4 opacity-70" />
      <p className="mt-2">
        Mid-project presentation · Built to be understood by both technical and
        non-technical reviewers.
      </p>
    </footer>
  );
}

// ---------- MVP Workflow ----------

type AlertSeverity = "P1" | "P2" | "P3";

function severityColor(s: string): string {
  if (s === "P1") return "destructive";
  if (s === "P2") return "tools";
  return "rag";
}

function decisionMeta(d: string | undefined) {
  if (d === "auto-resolve")
    return { label: "Auto-resolve", color: "resolution", icon: ShieldCheck };
  if (d === "tier1-resolve")
    return { label: "Resolve at Tier-1", color: "interface", icon: CheckCircle2 };
  return { label: "Escalate (prepared)", color: "destructive", icon: ArrowUpRight };
}

function MvpWorkflow() {
  const { alerts } = useBootstrap();
  const {
    resolved,
    markResolved: markResolvedSession,
    sessionTotals,
    recordTriageComplete,
  } = useWorkflowSession();
  const [activeId, setActiveId] = useState<string>("");
  const [stage, setStage] = useState<
    | "idle"
    | "priority"
    | "investigation"
    | "triage"
    | "escalation"
    | "resolution"
    | "done"
  >("idle");
  const [triageData, setTriageData] = useState<WorkflowTriagePayload | null>(null);
  const [triageError, setTriageError] = useState<string | null>(null);
  const [bedrockSessionId, setBedrockSessionId] = useState<string | null>(null);
  const [followUpQuestion, setFollowUpQuestion] = useState("");
  const [followUpBusy, setFollowUpBusy] = useState(false);
  const [followUpError, setFollowUpError] = useState<string | null>(null);

  const effectiveId = activeId || alerts[0]?.id || "";
  const alert = alerts.find((a) => a.id === effectiveId) ?? alerts[0];

  if (!alert) {
    return null;
  }

  async function submitFollowUp() {
    const q = followUpQuestion.trim();
    if (!q || !bedrockSessionId) return;
    setFollowUpBusy(true);
    setFollowUpError(null);
    try {
      const answer = await askQuestion(q, bedrockSessionId);
      setTriageData((prev) =>
        prev
          ? {
              ...prev,
              result: {
                ...prev.result!,
                answer: answer.answer,
                answer_sections: answer.answer_sections,
                citations: answer.citations,
                grounded: answer.grounded,
                session_id: answer.session_id ?? bedrockSessionId,
                latency_ms: answer.latency_ms,
                matched_runbook: answer.matched_runbook ?? prev.result?.matched_runbook,
              },
              session_id: answer.session_id ?? bedrockSessionId,
            }
          : prev,
      );
      if (answer.session_id) setBedrockSessionId(answer.session_id);
      setFollowUpQuestion("");
    } catch (err) {
      setFollowUpError(err instanceof Error ? err.message : "Follow-up failed");
    } finally {
      setFollowUpBusy(false);
    }
  }

  async function triage() {
    setTriageError(null);
    setTriageData(null);
    setFollowUpError(null);
    setStage("priority");
    try {
      const payload = await triageAlert(alert.id, undefined, bedrockSessionId);
      setTriageData(payload);
      if (payload.session_id) setBedrockSessionId(payload.session_id);
      for (const s of [
        "priority",
        "investigation",
        "triage",
        "escalation",
        "resolution",
        "done",
      ] as const) {
        setStage(s);
        await delay(400);
      }
      recordTriageComplete(alert.id);
    } catch (err) {
      setTriageError(err instanceof Error ? err.message : "Triage failed");
      setStage("idle");
    }
  }

  const displayRunbook =
    triageData?.matched_runbook ?? triageData?.result?.matched_runbook ?? alert.matchedRunbook;
  const displayQuestion = triageData?.question ?? alert.question;
  const effectiveDecision =
    triageData?.effective_decision ?? alert.decision ?? "escalate";
  const effectiveReason =
    triageData?.effective_reason ?? alert.decisionReason ?? "";
  const dMeta = decisionMeta(effectiveDecision);

  const citations = triageData?.result?.citations ?? [];
  const similarAlerts = rankSimilarAlerts(alerts, alert, 2);

  const triageImpactDollars =
    triageData?.impact_avoided ?? alertImpactDollars(alert);
  const triageSavedMin = triageData?.saved_min ?? alertSavedMinutes(alert);

  function markResolved() {
    markResolvedSession(alert.id);
  }

  const totalSavedMin = sessionTotals.minutes;
  const totalSavedImpact = sessionTotals.dollars;

  const DIcon = dMeta.icon;

  return (
    <section id="priority-center" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--tools)]">
          <Activity className="size-3.5" />
          PITER workflow
        </div>
        <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
          Priority → Investigation → Triage → Escalation → Resolution
        </h2>
        <p className="mt-2 text-muted-foreground max-w-3xl">
          Incoming alerts are classified P1–P4, enriched with logs, deployments, runbooks,
          and history, then guided through triage, escalation, and resolution — reducing
          MTTR and protecting revenue.
        </p>

        <div className="mt-8 grid gap-4 lg:grid-cols-[320px,1fr]">
          {/* Alert console */}
          <div className="rounded-xl border border-border bg-card/60 p-3">
            <div className="flex items-center justify-between px-2 py-1.5 text-xs uppercase tracking-wider text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Bell className="size-3.5" />
                Priority Center · incoming alerts
              </span>
              <span>{alerts.length}</span>
            </div>
            <ul className="mt-1 space-y-2">
              {alerts.map((a) => {
                const isActive = a.id === activeId;
                const isResolved = resolved.has(a.id);
                const sc = severityColor(a.severity);
                return (
                  <li key={a.id}>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveId(a.id);
                        setStage("idle");
                        setTriageData(null);
                        setTriageError(null);
                        setBedrockSessionId(null);
                        setFollowUpQuestion("");
                        setFollowUpError(null);
                      }}
                      className="w-full text-left rounded-lg border border-border bg-background/60 p-3 cursor-pointer transition-colors hover:bg-background"
                      style={{
                        boxShadow: isActive
                          ? `inset 0 0 0 1px var(--${sc})`
                          : undefined,
                      }}
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span
                          className="rounded px-1.5 py-0.5 font-semibold"
                          style={{
                            backgroundColor: `color-mix(in oklab, var(--${sc}) 22%, transparent)`,
                            color: `var(--${sc})`,
                          }}
                        >
                          {a.severity}
                        </span>
                        <span className="text-muted-foreground">{a.firedAt}</span>
                      </div>
                      <div className="mt-1.5 text-sm font-medium leading-snug">
                        {a.title}
                      </div>
                      <div className="mt-1 flex items-center justify-between text-[11px] text-muted-foreground">
                        <span>{a.service}</span>
                        {isResolved && (
                          <span className="flex items-center gap-1 text-[var(--resolution)]">
                            <CheckCircle2 className="size-3" />
                            resolved
                          </span>
                        )}
                      </div>
                    </button>
                  </li>
                );
              })}
            </ul>

            <div className="mt-4 rounded-lg border border-border bg-background/60 p-3">
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                Business impact saved
              </div>
              <div className="mt-1 flex items-baseline gap-2">
                <TrendingDown className="size-4 text-[var(--resolution)]" />
                <span className="text-2xl font-semibold text-[var(--resolution)]">
                  ~ ${totalSavedImpact.toLocaleString()}
                </span>
              </div>
              <div className="text-[11px] text-muted-foreground">
                {totalSavedMin} min of MTTR avoided this session
              </div>
              {sessionTotals.triagedCount > 0 && (
                <div className="mt-1 text-[11px] text-[var(--resolution)]">
                  {sessionTotals.triagedCount} alert
                  {sessionTotals.triagedCount === 1 ? "" : "s"} triaged with assistant guidance
                </div>
              )}
              <div className="mt-2 text-[10px] text-muted-foreground/80">
                Demo estimate — not actual financial impact.
              </div>
            </div>
          </div>

          {/* Investigation + triage workspace */}
          <div id="investigation" className="rounded-xl border border-border bg-card/60 p-5 scroll-mt-24">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
                  Alert {alert.id} · {alert.source}
                </div>
                <h3 className="mt-1 text-lg font-medium">{alert.title}</h3>
                <div className="text-xs text-muted-foreground">{alert.service}</div>
              </div>
              <button
                type="button"
                onClick={triage}
                disabled={stage !== "idle" && stage !== "done"}
                className="inline-flex items-center gap-2 rounded-md bg-primary px-3.5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-60 transition"
              >
                {stage !== "idle" && stage !== "done" ? (
                  <>
                    <Loader2 className="size-4 animate-spin" /> Triaging…
                  </>
                ) : (
                  <>
                    <Play className="size-4" /> Run PITER workflow
                  </>
                )}
              </button>
            </div>

            <div className="mt-4">
              <StepPipeline
                stage={stage}
                steps={WORKFLOW_PIPELINE_STEPS}
                order={WORKFLOW_PIPELINE_ORDER}
              />
            </div>

            {triageError && (
              <div className="mt-4 rounded-lg border border-border bg-[color-mix(in_oklab,var(--destructive)_12%,transparent)] p-3 text-sm text-[var(--destructive)]">
                {triageError}
              </div>
            )}

            <AnimatePresence>
              {(stage === "investigation" ||
                stage === "triage" ||
                stage === "escalation" ||
                stage === "resolution" ||
                stage === "done") && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-5 rounded-lg border border-border bg-background/60 p-4"
                >
                  <div id="triage-plan" className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground scroll-mt-24">
                    <Database className="size-3.5 text-[var(--rag)]" />
                    Investigation &amp; Triage Plan
                  </div>
                  <div className="mt-2 text-sm">
                    <span className="text-muted-foreground">Question sent: </span>
                    <span className="font-mono text-xs">"{displayQuestion}"</span>
                  </div>
                  <div className="mt-1 text-sm">
                    <span className="text-muted-foreground">Top runbook: </span>
                    <span className="font-medium">{displayRunbook ?? "—"}</span>
                  </div>
                  {triageData?.result && (
                    <div className="mt-3">
                      <FormattedAnswer
                        answer={triageData.result.answer}
                        sections={triageData.result.answer_sections}
                        grounded={triageData.result.grounded}
                      />
                    </div>
                  )}

                  {citations.length > 0 && (
                    <div className="mt-4">
                      <CitationList citations={citations.slice(0, 4)} title="Retrieved citations" />
                    </div>
                  )}

                  <EnrichmentPanel
                    enrichment={triageData?.enrichment}
                    ownerTeam={triageData?.owner_team}
                    similarIncidents={triageData?.similar_incidents}
                    externalStatus={triageData?.external_status}
                  />

                  {similarAlerts.length > 0 && (
                    <div id="incident-history" className="mt-4 scroll-mt-24">
                      <div className="text-xs uppercase tracking-wider text-muted-foreground">
                        Incident History · similar open alerts
                      </div>
                      <ul className="mt-2 space-y-2">
                        {similarAlerts.map((a) => (
                          <li
                            key={a.id}
                            className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border bg-card/60 px-3 py-2 text-sm"
                          >
                            <div>
                              <span className="font-medium">{a.title}</span>
                              <span className="ml-2 text-xs text-muted-foreground">
                                {a.severity} · {a.service}
                              </span>
                            </div>
                            <button
                              type="button"
                              className="text-xs text-[var(--interface)] hover:underline"
                              onClick={() => {
                                setActiveId(a.id);
                                setStage("idle");
                                setTriageData(null);
                                setTriageError(null);
                              }}
                            >
                              Open in console
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {(stage === "escalation" || stage === "resolution" || stage === "done") && (
                <motion.div
                  id="escalation"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 rounded-lg border border-border bg-background/60 p-4 scroll-mt-24"
                  style={{
                    boxShadow: `inset 0 0 0 1px color-mix(in oklab, var(--${dMeta.color}) 40%, transparent)`,
                  }}
                >
                  <div className="flex items-center gap-2">
                    <DIcon
                      className="size-4"
                      style={{ color: `var(--${dMeta.color})` }}
                    />
                    <span
                      className="text-sm font-semibold"
                      style={{ color: `var(--${dMeta.color})` }}
                    >
                      Escalation Hub · {dMeta.label}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                    {effectiveReason}
                  </p>

                  {stage === "done" && (
                    <div className="mt-3 rounded-lg border border-border bg-[color-mix(in_oklab,var(--resolution)_12%,transparent)] px-3 py-2 text-sm">
                      Expected MTTR reduction:{" "}
                      <span className="font-semibold text-[var(--resolution)]">
                        ~ ${triageImpactDollars.toLocaleString()}
                      </span>{" "}
                      /{" "}
                      <span className="font-semibold text-[var(--resolution)]">
                        {triageSavedMin} min
                      </span>{" "}
                      (demo estimate). Counted when you run triage once per alert.
                    </div>
                  )}

                  <div className="mt-3 grid gap-2 sm:grid-cols-2 text-xs">
                    <div className="rounded border border-border bg-card/60 px-2.5 py-1.5">
                      <div className="text-muted-foreground">Severity</div>
                      <div className="font-mono">{alert.severity}</div>
                    </div>
                    <div className="rounded border border-border bg-card/60 px-2.5 py-1.5">
                      <div className="text-muted-foreground">Demo impact if resolved</div>
                      <div className="font-mono text-[var(--resolution)]">
                        ${alertImpactDollars(alert).toLocaleString()} / {alertSavedMinutes(alert)} min
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div id="resolution" className="scroll-mt-24">
            {stage === "done" && !resolved.has(alert.id) && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                type="button"
                onClick={markResolved}
                className="mt-4 inline-flex items-center gap-2 rounded-md border border-border bg-card px-3.5 py-2 text-sm hover:bg-background transition"
              >
                <CheckCircle2 className="size-4 text-[var(--resolution)]" />
                Resolution Tracker · mark incident resolved
              </motion.button>
            )}
            </div>
            {resolved.has(alert.id) && (
              <div className="mt-4 text-xs text-[var(--resolution)] flex items-center gap-1.5">
                <CheckCircle2 className="size-3.5" />
                Resolved · impact already counted from triage
              </div>
            )}

            {stage === "done" && bedrockSessionId && (
              <div className="mt-4 rounded-lg border border-border bg-background/60 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted-foreground">
                  <span className="flex items-center gap-1.5 uppercase tracking-wider">
                    <MessageSquare className="size-3.5" />
                    Follow-up (same session)
                  </span>
                  <span
                    className="font-mono truncate max-w-[220px]"
                    title={bedrockSessionId}
                  >
                    session {bedrockSessionId.slice(0, 8)}…
                  </span>
                </div>
                <div className="mt-2 flex gap-2">
                  <input
                    type="text"
                    value={followUpQuestion}
                    onChange={(e) => setFollowUpQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !followUpBusy) void submitFollowUp();
                    }}
                    placeholder='e.g. "Who do I escalate to?" or "Show me the SQL again"'
                    className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm"
                    disabled={followUpBusy}
                  />
                  <button
                    type="button"
                    onClick={() => void submitFollowUp()}
                    disabled={followUpBusy || !followUpQuestion.trim()}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-2 text-sm hover:bg-background disabled:opacity-50"
                  >
                    {followUpBusy ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <MessageSquare className="size-4" />
                    )}
                    Ask
                  </button>
                </div>
                {followUpError && (
                  <p className="mt-2 text-xs text-[var(--destructive)]">{followUpError}</p>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-4">
          {[
            { icon: Bell, label: "Catch", body: "Alert lands in the console" },
            { icon: Search, label: "Triage", body: "KB matches runbook + history" },
            { icon: Sparkles, label: "Suggest", body: "Concrete next-step actions" },
            {
              icon: ShieldCheck,
              label: "Decide",
              body: "Resolve at Tier-1 or escalate — before impact grows",
            },
          ].map((s) => (
            <div
              key={s.label}
              className="rounded-lg border border-border bg-card/60 p-3"
            >
              <s.icon className="size-4 text-[var(--tools)]" />
              <div className="mt-2 text-sm font-medium">{s.label}</div>
              <div className="text-xs text-muted-foreground">{s.body}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------- Document upload ----------

function DocumentUpload() {
  const { data } = useBootstrap();
  const [file, setFile] = useState<File | null>(null);
  const [syncKb, setSyncKb] = useState(data?.sync_kb_default ?? false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const bucket = data?.s3_bucket || "…";
  const prefix = data?.s3_prefix || "";
  const allowedTypes = data?.allowed_types ?? [".md", ".txt", ".csv", ".docx", ".pdf"];
  const allowed = allowedTypes.join(", ");
  const maxMb = data?.max_upload_mb ?? 5;
  const maxBytes = maxMb * 1024 * 1024;

  const validateFile = useCallback(
    (candidate: File): string | null => {
      const ext = candidate.name.includes(".")
        ? `.${candidate.name.split(".").pop()?.toLowerCase()}`
        : "";
      if (!allowedTypes.some((t) => t.toLowerCase() === ext)) {
        return `Invalid file type. Allowed: ${allowed}`;
      }
      if (candidate.size > maxBytes) {
        return `File exceeds ${maxMb} MB limit (${(candidate.size / (1024 * 1024)).toFixed(1)} MB).`;
      }
      if (candidate.size === 0) {
        return "File is empty.";
      }
      return null;
    },
    [allowed, allowedTypes, maxBytes, maxMb],
  );

  const selectFile = useCallback(
    (candidate: File | null) => {
      setMessage(null);
      if (!candidate) {
        setFile(null);
        setError(null);
        return;
      }
      const validationError = validateFile(candidate);
      if (validationError) {
        setFile(null);
        setError(validationError);
        return;
      }
      setFile(candidate);
      setError(null);
    },
    [validateFile],
  );

  function onDragOver(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }

  function onDragLeave(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) selectFile(dropped);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Choose a file to upload.");
      return;
    }
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await uploadDocument(file, syncKb);
      const base = `Uploaded ${result.filename ?? file.name} → ${result.s3_uri ?? result.s3_key ?? "S3"}`;
      if (result.sync_warning || result.partial) {
        setMessage(`${base} · ${result.sync_warning ?? result.message ?? "KB sync pending"}`);
      } else {
        setMessage(`${base}${result.sync_started ? " · KB sync started" : ""}`);
      }
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section id="document-upload" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--ingest)]">
          <Upload className="size-3.5" />
          Knowledge Base — manage corpus
        </div>
        <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
          Upload runbook documents
        </h2>
        <p className="mt-2 text-muted-foreground max-w-3xl">
          Add MD, TXT, CSV, DOCX, or PDF to{" "}
          <code className="text-xs">
            s3://{bucket}/{prefix}/
          </code>
          . Optionally sync the Bedrock Knowledge Base after upload.
        </p>

        <form
          onSubmit={onSubmit}
          className="mt-8 rounded-xl border border-border bg-card/60 p-5 space-y-4"
        >
          <div>
            <label className="text-xs uppercase tracking-wider text-muted-foreground">
              Document file
            </label>
            <div
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  fileInputRef.current?.click();
                }
              }}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              className={`mt-2 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-4 py-8 text-center transition ${
                dragActive
                  ? "border-[var(--ingest)] bg-[color-mix(in_oklab,var(--ingest)_12%,transparent)]"
                  : "border-border bg-background/40 hover:border-muted-foreground/50"
              }`}
            >
              <Upload className="size-6 text-muted-foreground" />
              <p className="mt-2 text-sm font-medium">
                {dragActive ? "Drop file here" : "Drag & drop or click to browse"}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Max {maxMb} MB · {allowed}
              </p>
              {file && (
                <p className="mt-3 text-xs text-[var(--resolution)]">
                  Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept={allowedTypes.join(",")}
              className="sr-only"
              onChange={(e) => selectFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={syncKb}
              onChange={(e) => setSyncKb(e.target.checked)}
            />
            Sync to Knowledge Base after upload
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={busy || !file}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-60"
            >
              {busy ? <Loader2 className="size-4 animate-spin" /> : <Upload className="size-4" />}
              Upload document
            </button>
          </div>
        </form>

        <div className="mt-4 rounded-lg border border-border bg-background/60 p-3 text-xs text-muted-foreground" aria-live="polite">
          {error && <p className="text-[var(--destructive)]">{error}</p>}
          {message && <p className="text-[var(--resolution)]">{message}</p>}
        </div>
      </div>
    </section>
  );
}

// ---------- Live Knowledge Base ----------

function LiveKnowledgeBase() {
  const { data } = useBootstrap();
  const examples = data?.examples ?? [];
  const exampleGroups = data?.example_groups ?? {};
  const maxLen = data?.max_len ?? 500;
  const modelLabel = data?.model_label ?? "Bedrock";
  const kbId = data?.kb_id ?? "";

  const [question, setQuestion] = useState(examples[0] ?? "");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [result, setResult] = useState<RagAnswer | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const answer = await askQuestion(question, sessionId);
      setResult(answer);
      if (answer.session_id) setSessionId(answer.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  function newConversation() {
    setSessionId(null);
    setResult(null);
    setError(null);
  }

  return (
    <section id="live-kb" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--tools)]">
          <Sparkles className="size-3.5" />
          Live Knowledge Base
        </div>
        <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
          Try the PITER Knowledge Base in real time
        </h2>
        <p className="mt-2 text-muted-foreground max-w-2xl">
          Ask incident questions against indexed runbooks and alert history. Responses are
          grounded in your corpus with citations — powered by {modelLabel}
          {kbId ? ` · KB ${kbId}` : ""}.
        </p>

        <div className="mt-8 rounded-xl border border-border bg-card/60 p-4 flex flex-col max-w-3xl">
          <label
            htmlFor="live-kb-question"
            className="text-xs uppercase tracking-wider text-muted-foreground"
          >
            Question (max {maxLen} chars)
          </label>
          <textarea
            id="live-kb-question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            maxLength={maxLen}
            aria-label="Incident knowledge base question"
            className="mt-2 h-24 w-full resize-none rounded-md border border-border bg-background/80 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {Object.keys(exampleGroups).length > 0 ? (
            <div className="mt-3 space-y-3">
              {Object.entries(exampleGroups).map(([label, questions]) => (
                <div key={label}>
                  <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5">
                    {label}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {questions.map((q) => (
                      <button
                        key={q}
                        type="button"
                        onClick={() => setQuestion(q)}
                        className="rounded-full border border-border bg-background/60 px-3 py-1 text-xs text-muted-foreground hover:bg-card hover:text-foreground transition-colors"
                      >
                        {q.length > 48 ? `${q.slice(0, 48)}…` : q}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-3 flex flex-wrap gap-2">
              {examples.slice(0, 6).map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => setQuestion(q)}
                  className="rounded-full border border-border bg-background/60 px-3 py-1 text-xs text-muted-foreground hover:bg-card hover:text-foreground transition-colors"
                >
                  {q.length > 48 ? `${q.slice(0, 48)}…` : q}
                </button>
              ))}
            </div>
          )}
          <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={run}
            disabled={busy}
            aria-busy={busy}
            aria-label={busy ? "Querying knowledge base" : "Ask knowledge base"}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-60 transition"
          >
            {busy ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Querying Bedrock…
              </>
            ) : (
              <>
                <Play className="size-4" />
                Ask Knowledge Base
              </>
            )}
          </button>
          {sessionId && (
            <button
              type="button"
              onClick={newConversation}
              className="text-xs text-muted-foreground hover:text-foreground underline-offset-2 hover:underline"
            >
              New conversation
            </button>
          )}
          </div>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-4 flex items-start gap-2 rounded-lg border border-border bg-[color-mix(in_oklab,var(--destructive)_15%,transparent)] p-3 text-sm max-w-3xl"
              role="alert"
            >
              <AlertTriangle className="size-4 mt-0.5 text-[var(--destructive)]" />
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-6 grid gap-4 max-w-4xl"
              aria-live="polite"
            >
              <Stat
                label="Latency"
                value={`${result.latency_ms} ms`}
                color="resolution"
              />
              <div className="rounded-xl border border-border bg-background/60 p-5">
                <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
                  <Sparkles className="size-3.5 text-[var(--tools)]" />
                  Answer
                  {!result.grounded && (
                    <span className="ml-2 rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider bg-[color-mix(in_oklab,var(--destructive)_20%,transparent)] text-[var(--destructive)]">
                      Low confidence
                    </span>
                  )}
                </div>
                <div className="mt-3">
                  <FormattedAnswer
                    answer={result.answer}
                    sections={result.answer_sections}
                    grounded={result.grounded}
                  />
                </div>
              </div>
              {result.citations.length > 0 && (
                <CitationList citations={result.citations} />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}

const KB_PIPELINE_STEPS = [
  { key: "chunk", label: "Chunk", icon: Scissors, color: "ingest" },
  { key: "retrieve", label: "Retrieve", icon: Search, color: "rag" },
  { key: "generate", label: "Generate", icon: Sparkles, color: "agent" },
  { key: "done", label: "Answer", icon: CheckCircle2, color: "resolution" },
] as const;

const KB_PIPELINE_ORDER = ["idle", "chunk", "retrieve", "generate", "done"] as const;

function PipelineStages({
  stage,
}: {
  stage: "idle" | "chunk" | "retrieve" | "generate" | "done";
}) {
  return (
    <StepPipeline
      stage={stage}
      steps={[...KB_PIPELINE_STEPS]}
      order={KB_PIPELINE_ORDER}
    />
  );
}

function Stat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div
      className="rounded-xl border border-border bg-card/60 p-4"
      style={{ boxShadow: `inset 0 0 0 1px color-mix(in oklab, var(--${color}) 35%, transparent)` }}
    >
      <div className="text-xs uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div
        className="mt-1 text-2xl font-semibold"
        style={{ color: `var(--${color})` }}
      >
        {value}
      </div>
    </div>
  );
}
