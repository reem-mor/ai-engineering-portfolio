import type { SearchResult } from "./common";
export type ChatRequest = { question: string; top_k: number; };
export type ChatResponse = { answer: string; sources: string[]; retrieved_chunks: SearchResult[]; confidence: "high" | "medium" | "low" | "none"; used_context: boolean; };
