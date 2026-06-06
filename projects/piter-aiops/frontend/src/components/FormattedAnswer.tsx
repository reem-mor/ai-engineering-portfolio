import { useMemo, useState } from "react";
import { ChevronDown, Play, FileText } from "lucide-react";
import type { AnswerSections, Citation, PiterSections } from "@/types/rag";
import { segmentText, isCommandStep, coalesceSteps, type Segment } from "@/lib/answer-format";
import { CodeBlock, CodeSession } from "@/components/CodeBlock";

// Shared section wrapper: header + light divider for clear visual separation.
function Section({
  title,
  children,
  first = false,
}: {
  title: string;
  children: React.ReactNode;
  first?: boolean;
}) {
  return (
    <div className={first ? "" : "border-t border-border pt-4"}>
      <div className="text-xs uppercase tracking-wider text-muted-foreground">{title}</div>
      <div className="mt-2">{children}</div>
    </div>
  );
}

function StepNumberBadge({ n }: { n: number }) {
  return (
    <span
      data-step-badge
      className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold tabular-nums"
      style={{
        backgroundColor: "color-mix(in oklab, var(--resolution) 22%, transparent)",
        color: "var(--resolution)",
        border: "1px solid color-mix(in oklab, var(--resolution) 35%, transparent)",
      }}
      aria-hidden
    >
      {n}
    </span>
  );
}

function StepItem({ step, index }: { step: string; index: number }) {
  const segments = useMemo(() => segmentText(step), [step]);
  const command = useMemo(() => isCommandStep(segments, step), [segments, step]);
  const codeBlocks = segments.filter((s) => s.kind === "code") as Extract<Segment, { kind: "code" }>[];
  const proseText = segments
    .filter((s) => s.kind === "prose")
    .map((s) => (s.kind === "prose" ? s.text : ""))
    .join(" ")
    .trim();

  return (
    <li data-step-index={index} className="flex items-start gap-3">
      <StepNumberBadge n={index + 1} />
      <div className="min-w-0 flex-1 space-y-2">
        <div className="flex items-start gap-1.5 text-foreground/90">
          {command && (
            <Play className="mt-[3px] size-3.5 shrink-0 text-[var(--tools)]" aria-hidden />
          )}
          <span className={command ? "font-semibold" : ""}>
            {proseText || (codeBlocks.length ? "Run the command below" : step)}
          </span>
        </div>
        {codeBlocks.length > 0 && (
          <CodeSession
            blocks={codeBlocks.map((c) => ({ code: c.code, lang: c.lang, destructive: c.destructive }))}
          />
        )}
      </div>
    </li>
  );
}

export function FormattedAnswer({
  answer,
  sections,
  grounded = true,
}: {
  answer: string;
  sections?: AnswerSections;
  grounded?: boolean;
}) {
  const s = sections ?? {
    summary: answer.split("\n\n")[0] ?? answer,
    steps: [],
    escalation: [],
    why: "",
  };

  const steps = useMemo(() => coalesceSteps(s.steps), [s.steps]);
  const piter = s.piter_sections as PiterSections | undefined;
  const piterTriageSteps = useMemo(
    () => coalesceSteps(piter?.triage_plan ?? []),
    [piter?.triage_plan],
  );

  if (piter) {
    return (
      <div className="space-y-4 text-sm leading-relaxed">
        {piter.priority && (
          <Section title="Priority" first>
            <p className="text-foreground/95">{piter.priority}</p>
          </Section>
        )}
        {piter.investigation && (
          <Section title="Investigation findings">
            <p className="text-foreground/95">{piter.investigation}</p>
          </Section>
        )}
        {piterTriageSteps.length > 0 && (
          <Section title="Triage plan">
            <ul className="space-y-4">
              {piterTriageSteps.map((step, i) => (
                <StepItem key={i} step={step} index={i} />
              ))}
            </ul>
          </Section>
        )}
        {piter.escalation.length > 0 && (
          <Section title="Escalation recommendation">
            <ul className="list-disc space-y-1 pl-5 text-foreground/90">
              {piter.escalation.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </Section>
        )}
        {piter.resolution && (
          <Section title="Resolution plan">
            <p className="text-foreground/90">{piter.resolution}</p>
          </Section>
        )}
        {piter.business_impact && (
          <Section title="Business impact">
            <p className="text-foreground/90">{piter.business_impact}</p>
          </Section>
        )}
        {piter.sources && (
          <Section title="Sources">
            <p className="text-foreground/80">{piter.sources}</p>
          </Section>
        )}
        {piter.confidence && (
          <Section title="Confidence and uncertainty">
            <p className="text-foreground/80">{piter.confidence}</p>
          </Section>
        )}
      </div>
    );
  }

  if (!grounded) {
    return (
      <div className="space-y-4 text-sm leading-relaxed">
        <Section title="Answer" first>
          <p className="text-foreground/95">{s.summary || answer}</p>
        </Section>
      </div>
    );
  }

  return (
    <div className="space-y-4 text-sm leading-relaxed">
      <Section title="Answer" first>
        <p className="text-foreground/95">{s.summary || answer}</p>
      </Section>

      {steps.length > 0 && (
        <Section title="Recommended steps">
          <ul className="space-y-4">
            {steps.map((step, i) => (
              <StepItem key={i} step={step} index={i} />
            ))}
          </ul>
        </Section>
      )}

      {s.escalation.length > 0 && (
        <Section title="Escalation">
          <ul className="list-disc space-y-1 pl-5 text-foreground/90">
            {s.escalation.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </Section>
      )}

      {s.why && (
        <Section title="Why this answer">
          <p className="text-foreground/80">{s.why}</p>
        </Section>
      )}
    </div>
  );
}

function CitationScoreMeter({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(0, score <= 1 ? score * 100 : score));
  return (
    <div className="mt-2 flex items-center gap-2">
      <div
        className="h-1.5 min-w-0 flex-1 overflow-hidden rounded-full bg-border"
        role="meter"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Relevance ${pct.toFixed(0)} percent`}
      >
        <div
          className="h-full rounded-full transition-[width] duration-300"
          style={{
            width: `${pct}%`,
            backgroundColor: "var(--rag)",
          }}
        />
      </div>
      <span className="shrink-0 text-[10px] tabular-nums text-muted-foreground">
        {score.toFixed(2)}
      </span>
    </div>
  );
}

function CitationBody({ segments }: { segments: Segment[] }) {
  if (!segments.length) return null;
  return (
    <div className="mt-3 space-y-3 border-t border-border pt-3">
      {segments.map((seg, i) =>
        seg.kind === "code" ? (
          <CodeBlock key={i} code={seg.code} lang={seg.lang} destructive={seg.destructive} />
        ) : (
          <p
            key={i}
            className="border-l-2 pl-3 text-xs leading-relaxed text-foreground/80 whitespace-pre-line"
            style={{ borderColor: "color-mix(in oklab, var(--rag) 45%, transparent)" }}
          >
            {seg.text}
          </p>
        ),
      )}
    </div>
  );
}

export function CitationCard({ citation }: { citation: Citation }) {
  const [expanded, setExpanded] = useState(false);
  const chunk = citation.chunk_index != null ? `chunk ${citation.chunk_index}` : null;

  const fullSnippet = citation.snippet?.trim() ?? "";
  const preview = (citation.preview ?? citation.snippet ?? "").trim();
  const segments = useMemo(() => segmentText(fullSnippet), [fullSnippet]);
  const hasCode = segments.some((seg) => seg.kind === "code");
  const canExpand =
    fullSnippet.length > 0 &&
    (hasCode || segments.length > 1 || fullSnippet.length > (preview?.length ?? 0) + 40);

  const collapsedExcerpt =
    preview.length > 160 ? `${preview.slice(0, 157).trim()}…` : preview;

  return (
    <article
      className="overflow-hidden rounded-lg border border-border bg-card/50 shadow-sm"
      data-citation-index={citation.index}
    >
      <button
        type="button"
        className="flex w-full items-start gap-3 p-3 text-left transition-colors hover:bg-card/80 disabled:cursor-default disabled:hover:bg-card/50"
        onClick={() => canExpand && setExpanded((v) => !v)}
        aria-expanded={expanded}
        disabled={!canExpand}
      >
        <span
          className="flex size-7 shrink-0 items-center justify-center rounded-md text-[11px] font-bold tabular-nums"
          style={{
            backgroundColor: "color-mix(in oklab, var(--rag) 18%, transparent)",
            color: "var(--rag)",
          }}
        >
          {citation.index}
        </span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-xs font-semibold text-foreground">{citation.source_label}</div>
          {chunk && (
            <div className="mt-0.5 text-[10px] uppercase tracking-wide text-muted-foreground">{chunk}</div>
          )}
          {citation.score != null && <CitationScoreMeter score={citation.score} />}
          {!expanded && collapsedExcerpt && (
            <p className="mt-2 line-clamp-2 text-[11px] leading-snug text-muted-foreground">
              {collapsedExcerpt}
            </p>
          )}
        </div>
        {canExpand && (
          <ChevronDown
            className={`mt-1 size-4 shrink-0 text-muted-foreground transition-transform ${expanded ? "rotate-180" : ""}`}
            aria-hidden
          />
        )}
      </button>

      {expanded && <div className="px-3 pb-3"><CitationBody segments={segments} /></div>}
    </article>
  );
}

export function CitationList({
  citations,
  title = "Retrieved citations",
  collapsible = true,
  defaultOpen = false,
}: {
  citations: Citation[];
  title?: string;
  collapsible?: boolean;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  if (!citations.length) return null;

  const grid = (
    <div className="grid gap-3 sm:grid-cols-2">
      {citations.map((c) => (
        <CitationCard key={c.index} citation={c} />
      ))}
    </div>
  );

  if (!collapsible) {
    return (
      <div className="border-t border-border pt-4">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">{title}</div>
        {grid}
      </div>
    );
  }

  return (
    <div className="border-t border-border pt-4">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-2 text-left"
      >
        <span className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
          <FileText className="size-3.5" aria-hidden />
          {title}
          <span className="rounded-full bg-card px-1.5 py-0.5 text-[10px] normal-case tracking-normal text-foreground/70">
            {citations.length}
          </span>
        </span>
        <ChevronDown
          className={`size-4 shrink-0 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`}
          aria-hidden
        />
      </button>
      {open && <div className="mt-3">{grid}</div>}
    </div>
  );
}
