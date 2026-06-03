import { useState, type ReactNode } from "react";
import { Check, Copy, AlertTriangle } from "lucide-react";
import { type CodeLang, DESTRUCTIVE_LABEL } from "@/lib/answer-format";

// ---- Lightweight, dependency-free syntax highlighting (SQL + bash) ----

type Tok = { type: string; value: string };

const TOKEN_COLOR: Record<string, string> = {
  keyword: "var(--tools)", // cyan
  func: "var(--agent)", // purple
  string: "var(--resolution)", // green
  number: "var(--rag)", // teal
  comment: "color-mix(in oklab, var(--muted-foreground) 90%, transparent)",
  command: "var(--tools)",
  flag: "var(--ingest)",
};

function tokenize(code: string, re: RegExp): Tok[] {
  const out: Tok[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  re.lastIndex = 0;
  while ((m = re.exec(code)) !== null) {
    if (m.index > last) out.push({ type: "plain", value: code.slice(last, m.index) });
    const groups = m.slice(1);
    const idx = groups.findIndex((g) => g !== undefined);
    const types = re === SQL_RE
      ? ["comment", "string", "number", "func", "keyword"]
      : ["comment", "string", "command", "flag"];
    out.push({ type: types[idx] ?? "plain", value: m[0] });
    last = m.index + m[0].length;
    if (m.index === re.lastIndex) re.lastIndex++; // avoid zero-width loops
  }
  if (last < code.length) out.push({ type: "plain", value: code.slice(last) });
  return out;
}

const SQL_RE =
  /(--[^\n]*|\/\*[\s\S]*?\*\/)|('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|(\b\d+(?:\.\d+)?\b)|([a-zA-Z_][\w]*(?=\s*\())|\b(SELECT|FROM|WHERE|AND|OR|NOT|NULL|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|OFFSET|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|ON|AS|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|INDEX|VIEW|ALTER|DROP|TRUNCATE|WITH|DISTINCT|CASE|WHEN|THEN|ELSE|END|IS|IN|LIKE|ILIKE|BETWEEN|DESC|ASC|VACUUM|ANALYZE|EXPLAIN|BEGIN|COMMIT|ROLLBACK|GRANT|REVOKE|UNION|ALL|EXISTS|INTERVAL|NOW|COALESCE)\b/gi;

const BASH_RE =
  /(#[^\n]*)|('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|((?:^|\n)\s*[a-zA-Z][\w.\-]*|(?<=\|\s)[a-zA-Z][\w.\-]*)|(\s-{1,2}[A-Za-z][\w-]*)/g;

function highlight(code: string, lang: CodeLang): ReactNode {
  let toks: Tok[];
  if (lang === "sql") toks = tokenize(code, SQL_RE);
  else if (lang === "bash") toks = tokenize(code, BASH_RE);
  else return code;

  return toks.map((t, i) =>
    t.type === "plain" || !TOKEN_COLOR[t.type] ? (
      <span key={i}>{t.value}</span>
    ) : (
      <span key={i} style={{ color: TOKEN_COLOR[t.type] }}>
        {t.value}
      </span>
    ),
  );
}

const LANG_LABEL: Record<CodeLang, string> = {
  sql: "SQL",
  bash: "bash",
  python: "python",
  http: "HTTP",
  json: "JSON",
  text: "text",
};

// ---- Component ----

export function CodeBlock({
  code,
  lang,
  destructive = false,
}: {
  code: string;
  lang: CodeLang;
  destructive?: boolean;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard may be unavailable (insecure context) — fail quietly
    }
  }

  return (
    <div
      className="overflow-hidden rounded-lg border border-border bg-[oklch(0.13_0.02_265)]"
      style={
        destructive
          ? { borderLeft: "3px solid var(--ingest)" }
          : undefined
      }
    >
      <div className="flex items-center justify-between gap-2 border-b border-border px-3 py-1.5">
        <div className="flex items-center gap-2">
          <span
            className="rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
            style={{
              backgroundColor: "color-mix(in oklab, var(--tools) 18%, transparent)",
              color: "var(--tools)",
            }}
          >
            {LANG_LABEL[lang]}
          </span>
          {destructive && (
            <span
              className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold"
              style={{
                backgroundColor: "color-mix(in oklab, var(--ingest) 20%, transparent)",
                color: "var(--ingest)",
              }}
            >
              <AlertTriangle className="size-3" aria-hidden />
              {DESTRUCTIVE_LABEL}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[11px] text-muted-foreground transition-colors hover:bg-card hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={copied ? "Copied" : "Copy code"}
        >
          {copied ? (
            <>
              <Check className="size-3.5 text-[var(--resolution)]" aria-hidden /> Copied
            </>
          ) : (
            <>
              <Copy className="size-3.5" aria-hidden /> Copy
            </>
          )}
        </button>
      </div>
      <pre className="overflow-x-auto p-3 font-mono text-xs leading-relaxed text-foreground/90">
        <code>{highlight(code, lang)}</code>
      </pre>
    </div>
  );
}

/** A grouped set of statements that belong to one diagnostic session. */
export function CodeSession({
  blocks,
}: {
  blocks: { code: string; lang: CodeLang; destructive: boolean }[];
}) {
  const [copiedAll, setCopiedAll] = useState(false);
  if (blocks.length === 0) return null;

  async function copyAll() {
    try {
      await navigator.clipboard.writeText(blocks.map((b) => b.code).join("\n\n"));
      setCopiedAll(true);
      window.setTimeout(() => setCopiedAll(false), 1500);
    } catch {
      /* noop */
    }
  }

  return (
    <div className="mt-2 space-y-2">
      {blocks.map((b, i) => (
        <CodeBlock key={i} code={b.code} lang={b.lang} destructive={b.destructive} />
      ))}
      {blocks.length > 1 && (
        <button
          type="button"
          onClick={copyAll}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[11px] text-muted-foreground transition-colors hover:bg-card hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={copiedAll ? "All copied" : "Copy all statements in this session"}
        >
          {copiedAll ? (
            <>
              <Check className="size-3.5 text-[var(--resolution)]" aria-hidden /> All copied
            </>
          ) : (
            <>
              <Copy className="size-3.5" aria-hidden /> Copy all
            </>
          )}
        </button>
      )}
    </div>
  );
}
