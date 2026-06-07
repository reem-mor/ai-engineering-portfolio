import { createServerFn } from "@tanstack/react-start";

type Doc = { name: string; text: string };
type Chunk = { docName: string; chunkIdx: number; text: string; score: number };

const STOP = new Set([
  "the","a","an","and","or","but","of","to","in","on","for","with","is","are",
  "was","were","be","been","being","it","this","that","these","those","as","by",
  "at","from","i","you","he","she","they","we","do","does","did","not","no","yes",
  "if","then","than","so","what","who","when","where","why","how","which","about",
]);

function tokenize(s: string): string[] {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 1 && !STOP.has(t));
}

function chunkText(text: string, size = 400, overlap = 60): string[] {
  const clean = text.replace(/\r\n/g, "\n").trim();
  if (clean.length <= size) return [clean];
  const out: string[] = [];
  let i = 0;
  while (i < clean.length) {
    out.push(clean.slice(i, i + size));
    i += size - overlap;
  }
  return out;
}

export const askKb = createServerFn({ method: "POST" })
  .inputValidator(
    (d: { docs: Doc[]; question: string }) => {
      if (!d || !Array.isArray(d.docs)) throw new Error("Invalid payload");
      return {
        docs: d.docs
          .filter((x) => x && typeof x.text === "string")
          .slice(0, 50)
          .map((x) => ({
            name: String(x.name || "untitled").slice(0, 80),
            text: String(x.text).slice(0, 20000),
          })),
        question: String(d.question || "").slice(0, 500).trim(),
      };
    },
  )
  .handler(async ({ data }) => {
    const t0 = Date.now();

    // Edge case: no docs
    if (data.docs.length === 0) {
      return {
        ok: false as const,
        reason: "empty_dataset",
        message: "Add at least one document to your dataset before asking.",
      };
    }
    // Edge case: empty / too short question
    if (data.question.length < 3) {
      return {
        ok: false as const,
        reason: "empty_question",
        message: "Type a question with at least 3 characters.",
      };
    }

    // 1) CHUNK
    const tChunk = Date.now();
    const chunks: Chunk[] = [];
    for (const d of data.docs) {
      const parts = chunkText(d.text);
      parts.forEach((p, idx) =>
        chunks.push({ docName: d.name, chunkIdx: idx, text: p, score: 0 }),
      );
    }
    const chunkMs = Date.now() - tChunk;

    // 2) RETRIEVE (keyword overlap, lightweight stand-in for vector search)
    const tRet = Date.now();
    const qTokens = new Set(tokenize(data.question));
    if (qTokens.size === 0) {
      return {
        ok: false as const,
        reason: "stopwords_only",
        message: "Your question has no searchable keywords. Try rephrasing.",
      };
    }
    for (const c of chunks) {
      const ct = tokenize(c.text);
      let hits = 0;
      for (const tok of ct) if (qTokens.has(tok)) hits++;
      c.score = ct.length ? hits / Math.sqrt(ct.length) : 0;
    }
    const top = chunks
      .filter((c) => c.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 4);
    const retrieveMs = Date.now() - tRet;

    const totalChunks = chunks.length;

    // Edge case: nothing relevant
    if (top.length === 0) {
      return {
        ok: true as const,
        stages: {
          chunkMs,
          retrieveMs,
          generateMs: 0,
          totalMs: Date.now() - t0,
        },
        stats: { docs: data.docs.length, chunks: totalChunks, retrieved: 0 },
        citations: [],
        answer:
          "I couldn't find anything in your dataset that matches this question. Try rephrasing or adding more documents.",
        grounded: false,
      };
    }

    // 3) GENERATE via Lovable AI Gateway
    const tGen = Date.now();
    const apiKey = process.env.LOVABLE_API_KEY;
    let answer = "";
    let grounded = true;
    let warning: string | undefined;

    const context = top
      .map(
        (c, i) =>
          `[${i + 1}] (${c.docName} · chunk ${c.chunkIdx})\n${c.text}`,
      )
      .join("\n\n");

    const systemPrompt =
      "You are a strict RAG assistant. Answer ONLY using the provided CONTEXT. " +
      "If the answer isn't in the context, reply exactly: \"Not found in the dataset.\" " +
      "Cite sources inline as [1], [2], etc. Keep answers concise (2-4 sentences).";
    const userPrompt = `CONTEXT:\n${context}\n\nQUESTION: ${data.question}`;

    if (!apiKey) {
      // Graceful fallback if AI is not configured
      answer =
        "AI is not enabled. Top matching chunk: \n\n" +
        `"${top[0].text.slice(0, 280)}..." [1]`;
      grounded = true;
      warning = "LOVABLE_API_KEY missing — showing raw retrieval only.";
    } else {
      try {
        const res = await fetch(
          "https://ai.gateway.lovable.dev/v1/chat/completions",
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${apiKey}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              model: "google/gemini-2.5-flash",
              messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPrompt },
              ],
            }),
          },
        );
        if (res.status === 429) {
          return {
            ok: false as const,
            reason: "rate_limited",
            message: "AI gateway rate limit hit. Try again in a moment.",
          };
        }
        if (res.status === 402) {
          return {
            ok: false as const,
            reason: "payment_required",
            message:
              "AI credits exhausted. Add credits in Lovable Cloud settings.",
          };
        }
        if (!res.ok) {
          const txt = await res.text();
          throw new Error(`AI gateway ${res.status}: ${txt.slice(0, 200)}`);
        }
        const json = (await res.json()) as {
          choices?: { message?: { content?: string } }[];
        };
        answer = json.choices?.[0]?.message?.content?.trim() ?? "";
        if (!answer) answer = "Not found in the dataset.";
        if (/^not found in the dataset\.?$/i.test(answer)) grounded = false;
      } catch (e) {
        return {
          ok: false as const,
          reason: "ai_error",
          message: e instanceof Error ? e.message : "AI call failed.",
        };
      }
    }
    const generateMs = Date.now() - tGen;

    return {
      ok: true as const,
      stages: {
        chunkMs,
        retrieveMs,
        generateMs,
        totalMs: Date.now() - t0,
      },
      stats: { docs: data.docs.length, chunks: totalChunks, retrieved: top.length },
      citations: top.map((c, i) => ({
        n: i + 1,
        doc: c.docName,
        chunk: c.chunkIdx,
        score: Number(c.score.toFixed(3)),
        preview: c.text.slice(0, 220),
      })),
      answer,
      grounded,
      warning,
    };
  });
