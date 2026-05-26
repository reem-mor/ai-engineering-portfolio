const STORAGE_KEY = "incidentiq_last_index";

export type RagIndexSessionEntry = {
  indexedAt: string;
  indexedFileCount: number;
  kind: "sample" | "uploaded";
  message: string;
};

export function readRagIndexSession(): RagIndexSessionEntry | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as unknown;
    if (typeof parsed !== "object" || parsed === null) return null;
    const o = parsed as Record<string, unknown>;
    if (typeof o.indexedAt !== "string" || typeof o.indexedFileCount !== "number") return null;
    if (o.kind !== "sample" && o.kind !== "uploaded") return null;
    if (typeof o.message !== "string") return null;
    return { indexedAt: o.indexedAt, indexedFileCount: o.indexedFileCount, kind: o.kind, message: o.message };
  } catch {
    return null;
  }
}

export function writeRagIndexSession(entry: RagIndexSessionEntry): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(entry));
  } catch {
    /* ignore quota / private mode */
  }
}
