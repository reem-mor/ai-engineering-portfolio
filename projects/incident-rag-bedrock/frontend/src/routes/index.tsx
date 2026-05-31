import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { AnimatePresence, motion } from "framer-motion";
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
  Clock,
  TrendingDown,
  Activity,
} from "lucide-react";
import { askKb } from "@/lib/rag.functions";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Topic RAG App — Bedrock + Flask + Docker + EC2" },
      {
        name: "description",
        content:
          "A simple end-to-end AI web app: your documents become a Bedrock Knowledge Base, queried by a Flask app, packaged with Docker, and deployed on EC2.",
      },
      { property: "og:title", content: "Topic RAG App — Mid-Project Architecture" },
      {
        property: "og:description",
        content:
          "Documents → Bedrock Knowledge Base → Flask + boto3 → Docker → EC2 → Public URL. Explained for technical and non-technical reviewers.",
      },
    ],
  }),
  component: Page,
});

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

function Page() {
  return (
    <main className="min-h-screen text-foreground">
      <Hero />
      <Problem />
      <MvpWorkflow />
      <Architecture />
      <DemoMode />
      <Flow />
      <Stack />
      <Deliverables />
      <Footer />
    </main>
  );
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
            Mid-project · Incident triage RAG
          </span>
          <h1 className="mt-5 text-4xl md:text-6xl font-semibold tracking-tight">
            AI-assisted <span className="text-[var(--tools)]">Incident Triage</span>
            <br />
            powered by a Knowledge Base.
          </h1>
          <p className="mt-5 text-base md:text-lg text-muted-foreground leading-relaxed">
            When an alert fires, on-call engineers waste minutes searching runbooks,
            past incidents and Slack threads. I turn that knowledge into a Bedrock
            Knowledge Base so the right answer is one question away:{" "}
            <strong className="text-foreground">alerts &amp; runbooks → Knowledge Base → Flask → Docker → EC2 → public URL</strong>.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="#mvp"
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition"
            >
              Try the triage workflow <ArrowRight className="size-4" />
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
      title: "The problem",
      body:
        "Alerts fire 24/7. On-call engineers spend the first 5–15 minutes of every incident hunting for the right runbook, past ticket, or post-mortem — that's pure business impact.",
    },
    {
      icon: Lightbulb,
      title: "The idea",
      body:
        "Feed all runbooks, alert histories and post-mortems into a Bedrock Knowledge Base. When an alert hits, the engineer asks a question and gets a grounded, cited answer in seconds.",
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
      code: `aws s3 cp ./kb/ s3://incident-kb/ \\
  --recursive --exclude "*.DS_Store"`,
    },
    result: {
      title: "Upload report",
      lines: [
        "upload: kb/runbook_db_cpu.md       →  s3://incident-kb/runbook_db_cpu.md",
        "upload: kb/postmortem_2024_07.pdf  →  s3://incident-kb/postmortem_2024_07.pdf",
        "upload: kb/alerts_last_3mo.json    →  s3://incident-kb/alerts_last_3mo.json",
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
      code: `docker build -t incident-rag:1.0 .
docker run -p 5000:5000 \\
  -e AWS_REGION=us-east-1 \\
  -e KB_ID=KB-ABC123 \\
  incident-rag:1.0`,
    },
    result: {
      title: "Container status",
      lines: [
        "Successfully built sha256:9f3a…",
        "Successfully tagged incident-rag:1.0",
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
docker load -i incident-rag.tar
docker run -d -p 80:5000 \\
  --restart unless-stopped incident-rag:1.0`,
    },
    result: {
      title: "Host check",
      lines: [
        "CONTAINER ID   IMAGE             STATUS         PORTS",
        "a91c2f5e8b1d   incident-rag:1.0  Up 12 seconds  0.0.0.0:80->5000/tcp",
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
  const [active, setActive] = useState<BlockKey>("kb");
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
                  onClick={() => setActive(key)}
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
              <DetailPanel block={block} onClose={() => setActive("kb")} />
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
      <pre className="overflow-x-auto p-3 font-mono text-xs leading-relaxed text-foreground/90">
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
type WorkflowAlert = {
  id: string;
  severity: AlertSeverity;
  service: string;
  title: string;
  firedAt: string;
  source: string;
  question: string;
  matchedRunbook: string;
  actions: string[];
  decision: "auto-resolve" | "tier1-resolve" | "escalate";
  decisionReason: string;
  baselineMin: number; // typical MTTR without the assistant
  assistedMin: number; // MTTR with the assistant
  impactPerMin: number; // $ / min of business impact
};

const WORKFLOW_ALERTS: WorkflowAlert[] = [
  {
    id: "A-2041",
    severity: "P2",
    service: "postgres / prod-db-1",
    title: "Postgres CPU > 90% for 5m",
    firedAt: "14:02 UTC",
    source: "CloudWatch · prod-db-cpu",
    question: "Postgres CPU is 95% on prod-db-1 — what's the runbook?",
    matchedRunbook: "runbook_db_cpu.md",
    actions: [
      "Run pg_stat_activity to list long queries",
      "Cancel queries running > 5 minutes",
      "Check for missing indexes (seq_scan vs idx_scan)",
      "If load persists 15m, fail over to replica via Patroni",
    ],
    decision: "tier1-resolve",
    decisionReason:
      "Known runbook with deterministic steps. Tier-1 on-call can resolve without paging a DBA.",
    baselineMin: 22,
    assistedMin: 6,
    impactPerMin: 180,
  },
  {
    id: "A-2042",
    severity: "P1",
    service: "checkout-api",
    title: "API 5xx rate 12% for 4m",
    firedAt: "14:05 UTC",
    source: "Datadog · api_5xx_rate",
    question: "Checkout API 5xx spiked after a deploy — what do I do?",
    matchedRunbook: "runbook_api_5xx.md + postmortem_2024_07.md",
    actions: [
      "Check last deploy timestamp (<30m → likely cause)",
      "Tail /ecs/checkout logs for ERROR pattern",
      "Roll back: aws ecs update-service --task-definition <previous>",
      "Open #inc-checkout-<date> and page service owner",
    ],
    decision: "escalate",
    decisionReason:
      "Customer revenue at risk. Assistant prepared the rollback command + incident channel — engineer just confirms and pages.",
    baselineMin: 18,
    assistedMin: 4,
    impactPerMin: 920,
  },
  {
    id: "A-2043",
    severity: "P3",
    service: "email-worker",
    title: "Queue lag > 30s",
    firedAt: "14:11 UTC",
    source: "Prometheus · sqs_lag",
    question: "Email worker queue lag is 42s — is this actionable?",
    matchedRunbook: "alerts_last_3mo.json (similar A-1199)",
    actions: [
      "Compare against historical baseline (median 35s during EU peak)",
      "Confirm consumer healthy (no restarts, no errors)",
      "Mark as expected traffic spike, snooze alert for 30 min",
    ],
    decision: "auto-resolve",
    decisionReason:
      "Historical match: same pattern resolved itself in 8 minutes 3 months ago. Safe to silence without paging.",
    baselineMin: 9,
    assistedMin: 1,
    impactPerMin: 25,
  },
];

function severityColor(s: AlertSeverity): string {
  if (s === "P1") return "destructive";
  if (s === "P2") return "tools";
  return "rag";
}

function decisionMeta(d: WorkflowAlert["decision"]) {
  if (d === "auto-resolve")
    return { label: "Auto-resolve", color: "resolution", icon: ShieldCheck };
  if (d === "tier1-resolve")
    return { label: "Resolve at Tier-1", color: "interface", icon: CheckCircle2 };
  return { label: "Escalate (prepared)", color: "destructive", icon: ArrowUpRight };
}

function MvpWorkflow() {
  const [activeId, setActiveId] = useState<string>(WORKFLOW_ALERTS[0].id);
  const [resolved, setResolved] = useState<Set<string>>(new Set());
  const [stage, setStage] = useState<
    "idle" | "triage" | "suggest" | "decide" | "done"
  >("idle");

  const alert = WORKFLOW_ALERTS.find((a) => a.id === activeId)!;

  async function triage() {
    setStage("triage");
    await new Promise((r) => setTimeout(r, 500));
    setStage("suggest");
    await new Promise((r) => setTimeout(r, 600));
    setStage("decide");
    await new Promise((r) => setTimeout(r, 500));
    setStage("done");
  }

  function markResolved() {
    setResolved((prev) => new Set(prev).add(alert.id));
  }

  const totalSavedMin = WORKFLOW_ALERTS.filter((a) => resolved.has(a.id))
    .reduce((sum, a) => sum + (a.baselineMin - a.assistedMin), 0);
  const totalSavedImpact = WORKFLOW_ALERTS.filter((a) => resolved.has(a.id))
    .reduce((sum, a) => sum + (a.baselineMin - a.assistedMin) * a.impactPerMin, 0);

  const dMeta = decisionMeta(alert.decision);
  const DIcon = dMeta.icon;

  return (
    <section id="mvp" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--tools)]">
          <Activity className="size-3.5" />
          MVP workflow
        </div>
        <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
          From console alert → triage → resolve or escalate
        </h2>
        <p className="mt-2 text-muted-foreground max-w-3xl">
          The everyday on-call loop for DevOps, NOC and SRE teams. Pick an
          alert from the console, the assistant pulls the right runbook and
          past incidents from the Knowledge Base, suggests the next actions,
          and recommends whether Tier-1 can resolve it or it needs to be
          escalated — before business impact grows.
        </p>

        <div className="mt-8 grid gap-4 lg:grid-cols-[320px,1fr]">
          {/* Alert console */}
          <div className="rounded-xl border border-border bg-card/60 p-3">
            <div className="flex items-center justify-between px-2 py-1.5 text-xs uppercase tracking-wider text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Bell className="size-3.5" />
                Incoming alerts
              </span>
              <span>{WORKFLOW_ALERTS.length}</span>
            </div>
            <ul className="mt-1 space-y-2">
              {WORKFLOW_ALERTS.map((a) => {
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
                  ${totalSavedImpact.toLocaleString()}
                </span>
              </div>
              <div className="text-[11px] text-muted-foreground">
                {totalSavedMin} min of MTTR avoided this session
              </div>
            </div>
          </div>

          {/* Triage workspace */}
          <div className="rounded-xl border border-border bg-card/60 p-5">
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
                    <Play className="size-4" /> Run triage
                  </>
                )}
              </button>
            </div>

            <div className="mt-4">
              <WorkflowStages stage={stage} />
            </div>

            <AnimatePresence>
              {(stage === "suggest" ||
                stage === "decide" ||
                stage === "done") && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-5 rounded-lg border border-border bg-background/60 p-4"
                >
                  <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
                    <Database className="size-3.5 text-[var(--rag)]" />
                    KB match
                  </div>
                  <div className="mt-2 text-sm">
                    <span className="text-muted-foreground">Question sent: </span>
                    <span className="font-mono text-xs">"{alert.question}"</span>
                  </div>
                  <div className="mt-1 text-sm">
                    <span className="text-muted-foreground">Top runbook: </span>
                    <span className="font-medium">{alert.matchedRunbook}</span>
                  </div>

                  <div className="mt-4 text-xs uppercase tracking-wider text-muted-foreground">
                    Suggested actions
                  </div>
                  <ol className="mt-2 space-y-1.5">
                    {alert.actions.map((a, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-[color-mix(in_oklab,var(--interface)_25%,transparent)] text-[10px] font-semibold text-[var(--interface)]">
                          {i + 1}
                        </span>
                        <span>{a}</span>
                      </li>
                    ))}
                  </ol>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {(stage === "decide" || stage === "done") && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 rounded-lg border border-border bg-background/60 p-4"
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
                      Recommendation: {dMeta.label}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                    {alert.decisionReason}
                  </p>

                  <div className="mt-3 grid gap-2 sm:grid-cols-3 text-xs">
                    <div className="rounded border border-border bg-card/60 px-2.5 py-1.5">
                      <div className="text-muted-foreground">Baseline MTTR</div>
                      <div className="font-mono">{alert.baselineMin} min</div>
                    </div>
                    <div className="rounded border border-border bg-card/60 px-2.5 py-1.5">
                      <div className="text-muted-foreground">With assistant</div>
                      <div className="font-mono text-[var(--resolution)]">
                        {alert.assistedMin} min
                      </div>
                    </div>
                    <div className="rounded border border-border bg-card/60 px-2.5 py-1.5">
                      <div className="text-muted-foreground">Impact avoided</div>
                      <div className="font-mono text-[var(--resolution)]">
                        $
                        {(
                          (alert.baselineMin - alert.assistedMin) *
                          alert.impactPerMin
                        ).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {stage === "done" && !resolved.has(alert.id) && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                type="button"
                onClick={markResolved}
                className="mt-4 inline-flex items-center gap-2 rounded-md border border-border bg-card px-3.5 py-2 text-sm hover:bg-background transition"
              >
                <CheckCircle2 className="size-4 text-[var(--resolution)]" />
                Mark alert as resolved
              </motion.button>
            )}
            {resolved.has(alert.id) && (
              <div className="mt-4 text-xs text-[var(--resolution)] flex items-center gap-1.5">
                <CheckCircle2 className="size-3.5" />
                Logged · counted in business impact saved
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

function WorkflowStages({
  stage,
}: {
  stage: "idle" | "triage" | "suggest" | "decide" | "done";
}) {
  const steps: {
    key: typeof stage;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
  }[] = [
    { key: "triage", label: "Match KB", icon: Search, color: "rag" },
    { key: "suggest", label: "Suggest actions", icon: Sparkles, color: "interface" },
    { key: "decide", label: "Recommend", icon: ShieldCheck, color: "agent" },
    { key: "done", label: "Ready", icon: Clock, color: "resolution" },
  ];
  const order = ["idle", "triage", "suggest", "decide", "done"] as const;
  const currentIdx = order.indexOf(stage);

  return (
    <div className="flex items-center gap-2 overflow-x-auto">
      {steps.map((s, i) => {
        const stepIdx = order.indexOf(s.key);
        const done = currentIdx >= stepIdx && stage !== "idle";
        const active = stage === s.key;
        const Icon = s.icon;
        return (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className="flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs transition-all"
              style={{
                borderColor: done ? `var(--${s.color})` : "var(--border)",
                color: done ? `var(--${s.color})` : "var(--muted-foreground)",
                backgroundColor: active
                  ? `color-mix(in oklab, var(--${s.color}) 20%, transparent)`
                  : "transparent",
              }}
            >
              {active ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <Icon className="size-3.5" />
              )}
              {s.label}
            </div>
            {i < steps.length - 1 && (
              <ArrowRight className="size-3.5 text-muted-foreground/60" />
            )}
          </div>
        );
      })}
    </div>
  );
}


// ---------- Demo Mode ----------

const SAMPLE_DOCS = [
  {
    name: "runbook_db_cpu.md",
    text:
      "Runbook: Postgres CPU above 90% on prod-db-* hosts. Severity: P2. Step 1: Connect via bastion and run `SELECT pid, state, query_start, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY query_start;` to list long-running queries. Step 2: Identify queries running > 5 minutes; cancel with `SELECT pg_cancel_backend(pid);` or `pg_terminate_backend(pid)` if cancel fails. Step 3: Check for missing indexes via `pg_stat_user_tables` (seq_scan vs idx_scan). Step 4: If load persists, fail over to replica using Patroni: `patronictl failover --candidate prod-db-2`. Escalate to DBA on-call if CPU stays > 90% for 15 minutes.",
  },
  {
    name: "runbook_api_5xx.md",
    text:
      "Runbook: API 5xx rate above 2% for 5 minutes. Severity: P1. Step 1: Open Grafana dashboard `api-overview` and identify which service is failing (checkout, auth, search). Step 2: Tail logs in CloudWatch log group `/ecs/<service>` and grep for ERROR. Step 3: Common causes — upstream DB timeout, expired secret, bad deploy. Step 4: If a deploy went out in the last 30 min, roll back with `aws ecs update-service --force-new-deployment --task-definition <previous>`. Step 5: Open an incident channel #inc-<service>-<date> and page the service owner.",
  },
  {
    name: "postmortem_2024_07.md",
    text:
      "Postmortem 2024-07-14: Checkout service outage, 47 minutes, P1. Root cause: a deploy introduced an N+1 query against the orders table; Postgres CPU on prod-db-1 hit 100%, API 5xx rate spiked to 18%. Detection: PagerDuty alert from the api_5xx_rate monitor at 14:03 UTC. Resolution: rolled back the checkout deploy at 14:38, CPU recovered within 4 minutes. Action items: add query budget alert per endpoint, require EXPLAIN ANALYZE in code review for new SQL, add a pre-deploy load test for checkout.",
  },
  {
    name: "alerts_last_3mo.json",
    text:
      '[{"id":"A-1042","fired":"2024-07-14T14:03Z","severity":"P1","title":"api_5xx_rate > 2% on checkout","service":"checkout","resolved_after_min":47,"linked_postmortem":"postmortem_2024_07.md"},{"id":"A-1108","fired":"2024-08-02T09:11Z","severity":"P2","title":"prod-db-1 cpu > 90%","service":"postgres","resolved_after_min":12,"runbook":"runbook_db_cpu.md"},{"id":"A-1199","fired":"2024-09-21T22:40Z","severity":"P3","title":"queue lag > 30s on email-worker","service":"email-worker","resolved_after_min":8}]',
  },
];

type AskResult = Awaited<ReturnType<typeof askKb>>;

function DemoMode() {
  const ask = useServerFn(askKb);
  const [docsText, setDocsText] = useState(
    SAMPLE_DOCS.map((d) => `### ${d.name}\n${d.text}`).join("\n\n"),
  );
  const [question, setQuestion] = useState(
    "Postgres CPU is 95% on prod-db-1 — what's the runbook?",
  );
  const [result, setResult] = useState<AskResult | null>(null);
  const [stage, setStage] = useState<"idle" | "chunk" | "retrieve" | "generate" | "done">("idle");
  const [error, setError] = useState<string | null>(null);

  function parseDocs(raw: string) {
    const blocks = raw.split(/^###\s+/m).map((b) => b.trim()).filter(Boolean);
    if (blocks.length === 0) return [];
    return blocks.map((b, i) => {
      const lines = b.split("\n");
      const name = (lines[0] || `doc-${i + 1}`).trim();
      const text = lines.slice(1).join("\n").trim();
      return { name, text };
    });
  }

  async function run() {
    setError(null);
    setResult(null);
    const docs = parseDocs(docsText);
    setStage("chunk");
    await new Promise((r) => setTimeout(r, 350));
    setStage("retrieve");
    await new Promise((r) => setTimeout(r, 350));
    setStage("generate");
    try {
      const r = await ask({ data: { docs, question } });
      setResult(r);
      setStage("done");
      if (!r.ok) setError(r.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setStage("idle");
    }
  }

  return (
    <section id="demo" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--tools)]">
          <Sparkles className="size-3.5" />
          Live demo
        </div>
        <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
          Try the incident Knowledge Base in real time
        </h2>
        <p className="mt-2 text-muted-foreground max-w-2xl">
          Paste runbooks, past alerts, or a JSON export, ask an incident
          question, and watch the pipeline run: chunk → retrieve → generate →
          cited answer. Works with any dataset and handles common edge cases.
        </p>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-border bg-card/60 p-4">
            <label className="flex items-center justify-between text-xs uppercase tracking-wider text-muted-foreground">
              <span>Runbooks &amp; alerts · use `### filename` to split docs</span>
              <button
                type="button"
                onClick={() =>
                  setDocsText(
                    SAMPLE_DOCS.map((d) => `### ${d.name}\n${d.text}`).join("\n\n"),
                  )
                }
                className="text-[10px] underline hover:text-foreground"
              >
                Reset sample
              </button>
            </label>
            <textarea
              value={docsText}
              onChange={(e) => setDocsText(e.target.value)}
              className="mt-2 h-64 w-full resize-none rounded-md border border-border bg-background/80 p-3 font-mono text-xs leading-relaxed text-foreground/90 focus:outline-none focus:ring-2 focus:ring-ring"
              spellCheck={false}
            />
          </div>

          <div className="rounded-xl border border-border bg-card/60 p-4 flex flex-col">
            <label className="text-xs uppercase tracking-wider text-muted-foreground">
              Question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="mt-2 h-24 w-full resize-none rounded-md border border-border bg-background/80 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="mt-3 flex flex-wrap gap-2">
              {[
                "Postgres CPU is 95% on prod-db-1 — what's the runbook?",
                "What was the root cause of the July 2024 checkout outage?",
                "How do I deploy a new Kubernetes cluster?",
              ].map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => setQuestion(q)}
                  className="rounded-full border border-border bg-background/60 px-3 py-1 text-xs text-muted-foreground hover:bg-card hover:text-foreground transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={run}
              disabled={stage !== "idle" && stage !== "done"}
              className="mt-auto inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-60 transition"
            >
              {stage !== "idle" && stage !== "done" ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Running…
                </>
              ) : (
                <>
                  <Play className="size-4" />
                  Run the pipeline
                </>
              )}
            </button>
          </div>
        </div>

        <div className="mt-6">
          <PipelineStages stage={stage} />
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-4 flex items-start gap-2 rounded-lg border border-border bg-[color-mix(in_oklab,var(--destructive)_15%,transparent)] p-3 text-sm"
            >
              <AlertTriangle className="size-4 mt-0.5 text-[var(--destructive)]" />
              <div>
                <div className="font-medium">Edge case handled</div>
                <div className="text-muted-foreground text-xs">{error}</div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {result && result.ok && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-6 grid gap-4 md:grid-cols-3"
            >
              <Stat label="Docs" value={String(result.stats.docs)} color="ingest" />
              <Stat
                label="Chunks indexed"
                value={String(result.stats.chunks)}
                color="rag"
              />
              <Stat
                label="Total latency"
                value={`${result.stages.totalMs} ms`}
                color="resolution"
              />

              <div className="md:col-span-3 rounded-xl border border-border bg-background/60 p-5">
                <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
                  <Sparkles className="size-3.5 text-[var(--tools)]" />
                  Answer
                  {!result.grounded && (
                    <span className="ml-2 rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider bg-[color-mix(in_oklab,var(--destructive)_20%,transparent)] text-[var(--destructive)]">
                      Not in dataset
                    </span>
                  )}
                </div>
                <p className="mt-3 text-sm leading-relaxed text-foreground/95 whitespace-pre-wrap">
                  {result.answer}
                </p>
                {result.warning && (
                  <p className="mt-2 text-[11px] text-muted-foreground italic">
                    {result.warning}
                  </p>
                )}
                <div className="mt-3 text-[11px] text-muted-foreground">
                  Stages: chunk {result.stages.chunkMs}ms · retrieve{" "}
                  {result.stages.retrieveMs}ms · generate{" "}
                  {result.stages.generateMs}ms
                </div>
              </div>

              {result.citations.length > 0 && (
                <div className="md:col-span-3">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
                    Retrieved citations
                  </div>
                  <div className="grid gap-3 md:grid-cols-2">
                    {result.citations.map((c) => (
                      <div
                        key={`${c.doc}-${c.chunk}`}
                        className="rounded-lg border border-border bg-card/60 p-3"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-medium">
                            [{c.n}] {c.doc} · chunk {c.chunk}
                          </span>
                          <span className="text-muted-foreground">
                            score {c.score}
                          </span>
                        </div>
                        <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                          {c.preview}
                          {c.preview.length >= 220 ? "…" : ""}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-8 rounded-lg border border-border bg-card/40 p-4">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
            Edge cases this demo handles
          </div>
          <ul className="grid gap-2 sm:grid-cols-2 text-xs text-muted-foreground">
            {[
              "Empty dataset → friendly prompt",
              "Empty / too-short question",
              "Question is only stop-words",
              "No matching chunks → \"Not found\"",
              "Off-topic question → grounded refusal",
              "AI rate limit (429) / no credits (402)",
              "Very long docs → safe truncation",
              "Multiple sources → numbered citations",
            ].map((t) => (
              <li key={t} className="flex items-start gap-2">
                <CheckCircle2 className="size-3.5 mt-0.5 text-[var(--resolution)] shrink-0" />
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

function PipelineStages({
  stage,
}: {
  stage: "idle" | "chunk" | "retrieve" | "generate" | "done";
}) {
  const steps: { key: typeof stage; label: string; icon: React.ComponentType<{ className?: string }>; color: string }[] = [
    { key: "chunk", label: "Chunk", icon: Scissors, color: "ingest" },
    { key: "retrieve", label: "Retrieve", icon: Search, color: "rag" },
    { key: "generate", label: "Generate", icon: Sparkles, color: "agent" },
    { key: "done", label: "Answer", icon: CheckCircle2, color: "resolution" },
  ];
  const order = ["idle", "chunk", "retrieve", "generate", "done"] as const;
  const currentIdx = order.indexOf(stage);

  return (
    <div className="flex items-center gap-2 overflow-x-auto">
      {steps.map((s, i) => {
        const stepIdx = order.indexOf(s.key);
        const done = currentIdx >= stepIdx && stage !== "idle";
        const active = stage === s.key;
        const Icon = s.icon;
        return (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className="flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs transition-all"
              style={{
                borderColor: done ? `var(--${s.color})` : "var(--border)",
                color: done ? `var(--${s.color})` : "var(--muted-foreground)",
                backgroundColor: active
                  ? `color-mix(in oklab, var(--${s.color}) 20%, transparent)`
                  : "transparent",
              }}
            >
              {active ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <Icon className="size-3.5" />
              )}
              {s.label}
            </div>
            {i < steps.length - 1 && (
              <ArrowRight className="size-3.5 text-muted-foreground/60" />
            )}
          </div>
        );
      })}
    </div>
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
