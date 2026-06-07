// Parsing helpers that turn answer step text and citation snippets into a mix of
// prose and code segments, so the UI can render SQL/shell as proper code blocks.
// No external dependencies — keeps the bundle light.

export type CodeLang = "sql" | "bash" | "python" | "http" | "json" | "text";

export type Segment =
  | { kind: "prose"; text: string }
  | { kind: "code"; code: string; lang: CodeLang; destructive: boolean };

const SQL_START =
  /^(SELECT|INSERT|UPDATE|DELETE|WITH|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|VACUUM|ANALYZE|EXPLAIN|SET|BEGIN|COMMIT|ROLLBACK|COPY)\b/i;

const SHELL_START =
  /^(\$\s+)?(aws|docker|kubectl|psql|sudo|systemctl|service|curl|kill|pg_ctl|patronictl|helm|terraform|git|journalctl|top|htop|df|du|tail|cat|grep|export|ssh|scp|yum|apt|apt-get|pip|python|gunicorn|flask|nproc|free|vmstat|iostat)\b/i;

// Patterns considered destructive / "only if X fails".
const DESTRUCTIVE =
  /(pg_terminate_backend|\bDROP\s+(TABLE|DATABASE|INDEX)\b|\bTRUNCATE\b|\bDELETE\s+FROM\b|kill\s+-9|rm\s+-rf|\bSHUTDOWN\b|systemctl\s+stop|service\s+\w+\s+stop|reboot|shutdown\s+-)/i;

export function isDestructive(code: string): boolean {
  return DESTRUCTIVE.test(code);
}

export function detectLanguage(code: string): CodeLang {
  const trimmed = code.trim();
  if (!trimmed) return "text";
  if (/^(GET|POST|PUT|PATCH|DELETE)\s+\/?\S*\s+HTTP\//.test(trimmed)) return "http";
  if (
    /\b(boto3|import\s+\w+|def\s+\w+\s*\(|client\s*=|resp\s*=|print\()/.test(trimmed) &&
    !SQL_START.test(trimmed)
  )
    return "python";
  if (SQL_START.test(trimmed) || /\b(FROM|WHERE|pg_stat_activity|pg_terminate_backend)\b/i.test(trimmed))
    return "sql";
  if (SHELL_START.test(trimmed) || /^\$\s+/.test(trimmed)) return "bash";
  if (/^[[{][\s\S]*[\]}]$/.test(trimmed)) return "json";
  return "text";
}

function looksLikeCode(line: string): boolean {
  const t = line.trim();
  if (!t) return false;
  return SQL_START.test(t) || SHELL_START.test(t) || /^\$\s+/.test(t);
}

// Pull an inline SQL statement (keyword ... ;) out of a single prose line.
function extractInlineStatement(line: string): { before: string; code: string; after: string } | null {
  const sql = line.match(
    /\b(SELECT|INSERT|UPDATE|DELETE|WITH|CREATE|ALTER|DROP|TRUNCATE|GRANT|VACUUM|ANALYZE|EXPLAIN)\b[\s\S]*?;/i,
  );
  if (sql && sql.index != null) {
    return {
      before: line.slice(0, sql.index).trim(),
      code: sql[0].trim(),
      after: line.slice(sql.index + sql[0].length).trim(),
    };
  }
  // pg_terminate_backend(...) / pg_cancel_backend(...) calls without SELECT prefix
  const fn = line.match(/\b(pg_terminate_backend|pg_cancel_backend)\s*\([^)]*\)/i);
  if (fn && fn.index != null) {
    return {
      before: line.slice(0, fn.index).trim(),
      code: fn[0].trim(),
      after: line.slice(fn.index + fn[0].length).trim(),
    };
  }
  return null;
}

function pushProse(segments: Segment[], text: string) {
  const clean = text.replace(/\s+$/g, "").replace(/^\s+/g, "");
  if (clean) segments.push({ kind: "prose", text: clean });
}

function pushCode(segments: Segment[], code: string, lang?: CodeLang) {
  const trimmed = code.replace(/\n+$/g, "").replace(/^\n+/g, "");
  if (!trimmed.trim()) return;
  const detected = lang ?? detectLanguage(trimmed);
  segments.push({ kind: "code", code: trimmed, lang: detected, destructive: isDestructive(trimmed) });
}

/**
 * Split a block of text (a step string or a citation snippet) into ordered
 * prose / code segments. Handles fenced ```lang blocks, multi-line bare code
 * runs, and inline SQL statements embedded in a sentence.
 */
export function segmentText(input: string): Segment[] {
  const text = (input ?? "").trim();
  if (!text) return [];

  const segments: Segment[] = [];
  const fence = /```([\w+-]*)[ \t]*\r?\n?([\s\S]*?)```/g;
  let last = 0;
  let m: RegExpExecArray | null;

  while ((m = fence.exec(text)) !== null) {
    const prose = text.slice(last, m.index);
    segmentPlain(prose, segments);
    const lang = (m[1] || "").toLowerCase() as CodeLang;
    pushCode(segments, m[2], isKnownLang(lang) ? lang : undefined);
    last = m.index + m[0].length;
  }
  segmentPlain(text.slice(last), segments);

  return segments.length ? segments : [{ kind: "prose", text }];
}

function isKnownLang(lang: string): lang is CodeLang {
  return ["sql", "bash", "python", "http", "json", "text"].includes(lang);
}

// Handle a non-fenced chunk: group consecutive code-like lines, extract inline SQL.
function segmentPlain(chunk: string, segments: Segment[]) {
  const text = chunk.replace(/\s+$/g, "");
  if (!text.trim()) return;

  const lines = text.split(/\r?\n/);
  let proseBuf: string[] = [];
  let codeBuf: string[] = [];

  const flushProse = () => {
    if (proseBuf.length) {
      pushProse(segments, proseBuf.join("\n"));
      proseBuf = [];
    }
  };
  const flushCode = () => {
    if (codeBuf.length) {
      pushCode(segments, codeBuf.join("\n"));
      codeBuf = [];
    }
  };

  for (const line of lines) {
    if (looksLikeCode(line)) {
      flushProse();
      codeBuf.push(line);
      continue;
    }
    flushCode();
    // Single prose line that embeds an inline SQL statement.
    const inline = extractInlineStatement(line);
    if (inline) {
      if (inline.before) proseBuf.push(inline.before);
      flushProse();
      pushCode(segments, inline.code);
      if (inline.after) proseBuf.push(inline.after);
      continue;
    }
    proseBuf.push(line);
  }
  flushProse();
  flushCode();
}

/**
 * The backend emits "Recommended steps" line-by-line, so a numbered step that
 * contains a fenced SQL block arrives split across several array entries
 * ("```sql", the code, "```"). Re-join each fenced run onto its lead-in step so
 * one checklist item keeps its code with its text — and bare fence markers
 * ("```sql" / "```") never render as their own empty checkbox row.
 */
export function coalesceSteps(raw: string[]): string[] {
  const out: string[] = [];
  const fenceOpen = /^```([\w+-]*)\s*$/;
  const fenceClose = /^```\s*$/;
  for (let i = 0; i < raw.length; i++) {
    const line = raw[i] ?? "";
    const open = line.match(fenceOpen);
    if (open) {
      const lang = open[1] ?? "";
      const body: string[] = [];
      i++;
      while (i < raw.length && !fenceClose.test(raw[i] ?? "")) {
        body.push(raw[i] ?? "");
        i++;
      }
      // i is now on the closing fence (or past the end); the for-loop's i++ skips it.
      const block = "```" + lang + "\n" + body.join("\n") + "\n```";
      if (out.length) out[out.length - 1] = `${out[out.length - 1]}\n${block}`;
      else out.push(block);
      continue;
    }
    if (line.trim()) out.push(line);
  }
  return out;
}

/** True when a step's main action is a command an operator should run. */
export function isCommandStep(segments: Segment[], rawText: string): boolean {
  if (segments.some((s) => s.kind === "code")) return true;
  return /\b(run|execute|kill|cancel|terminate|restart|deploy|apply|sync|scale|vacuum|reindex)\b/i.test(
    rawText.split(/[.;]/)[0] ?? rawText,
  );
}

export const DESTRUCTIVE_LABEL = "destructive — use only if cancel fails";
