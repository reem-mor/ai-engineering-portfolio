import type { Citation } from "@/types/rag";
import { CheckCircle2, FileText } from "lucide-react";
import { classNames, toneClasses } from "@/lib/ui-utils";

export function Panel({
  title,
  icon: Icon,
  children,
  className,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={classNames(
        "rounded-xl border border-slate-700/60 bg-slate-900/50 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.03)]",
        className,
      )}
    >
      <div className="flex items-center gap-2 border-b border-slate-800/80 px-4 py-3">
        <Icon className="size-4 text-cyan-300" />
        <h3 className="text-sm font-semibold tracking-tight text-slate-100">{title}</h3>
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}

export function Pill({ children, tone = "cyan" }: { children: React.ReactNode; tone?: string }) {
  return (
    <span
      className={classNames(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium",
        toneClasses(tone),
      )}
    >
      {children}
    </span>
  );
}

export function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  sub: string;
  icon: React.ComponentType<{ className?: string }>;
  tone: string;
}) {
  return (
    <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-4 transition-colors hover:border-cyan-400/20">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
            {label}
          </div>
          <div className="mt-2 truncate text-2xl font-semibold tabular-nums text-white">
            {value}
          </div>
          <div className="mt-1 text-xs text-slate-500">{sub}</div>
        </div>
        <div className={classNames("shrink-0 rounded-lg border p-2.5", toneClasses(tone))}>
          <Icon className="size-4" />
        </div>
      </div>
    </div>
  );
}

export function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-700/80 bg-slate-950/50 p-3">
      <div className="text-[10px] font-medium uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-1 truncate text-sm font-semibold text-slate-100" title={value}>
        {value}
      </div>
    </div>
  );
}

export function SectionHeader({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return (
    <div>
      <div className="text-[11px] font-medium uppercase tracking-[0.22em] text-cyan-200/60">
        {eyebrow}
      </div>
      <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white">{title}</h2>
      <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-400">{body}</p>
    </div>
  );
}

export function ValueBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-slate-400">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

export function EvidenceCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-slate-700/80 bg-slate-950/40 p-3">
      <div className="text-sm font-semibold text-cyan-100">{title}</div>
      <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-slate-400">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-emerald-300" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[115px_minmax(0,1fr)] gap-2 border-b border-slate-800/80 pb-2 last:border-b-0 last:pb-0">
      <div className="text-[10px] font-medium uppercase tracking-wider text-slate-500">{label}</div>
      <div className="min-w-0 break-words text-sm text-slate-300">{value}</div>
    </div>
  );
}

export function CitationPreview({
  citations,
  compact = false,
}: {
  citations: Citation[];
  compact?: boolean;
}) {
  const visible = citations.length
    ? citations.slice(0, compact ? 2 : 4)
    : [
        {
          source_label: "runbook_bet_service_outage.md",
          snippet:
            "Check recent deployment, dependency health, and rollback availability before restarting services.",
          source_uri: "local://knowledge_base/runbooks/RB-011-bet-service-outage.md",
          index: 1,
        },
        {
          source_label: "severity-and-escalation-policy.md",
          snippet:
            "P1 incidents in regulated markets require immediate escalation preview and business impact assessment.",
          source_uri: "local://knowledge_base/policies/severity-and-escalation-policy.md",
          index: 2,
        },
      ];
  return (
    <div className="rounded-lg border border-slate-700/80 bg-slate-950/40 p-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-cyan-100">
        <FileText className="size-4" />
        RAG citations
      </div>
      <div className="mt-2 grid gap-2">
        {visible.map((citation) => (
          <div
            key={`${citation.index}-${citation.source_label}`}
            className="rounded-lg border border-slate-800 bg-slate-900/70 p-2.5 text-xs"
          >
            <div className="font-mono text-cyan-200">{citation.source_label}</div>
            <p className="mt-1 line-clamp-2 text-slate-400">
              {citation.snippet || citation.preview || citation.source_uri}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FilterBar({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-slate-700/70 bg-slate-900/40 p-2">
      {children}
    </div>
  );
}

export function FilterSelect({
  label,
  defaultValue,
}: {
  label: string;
  defaultValue: string;
}) {
  return (
    <label className="flex items-center gap-2 rounded-md border border-slate-700 bg-slate-950/60 px-2.5 py-1.5 text-xs text-slate-300">
      <span className="text-slate-500">{label}</span>
      <select
        defaultValue={defaultValue}
        className="cursor-pointer bg-transparent text-slate-200 outline-none"
        aria-label={label}
      >
        <option>{defaultValue}</option>
      </select>
    </label>
  );
}
