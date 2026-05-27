import type { RagIndexSessionEntry } from "../../utils/ragIndexSession";
import { MetricCard } from "../ui/MetricCard";
import type { BadgeVariant } from "../ui/Badge";

export type OpsStatusStripProps = {
  health: string | null;
  sampleCount: number | null;
  uploadedCount: number | null;
  sessionIndex: RagIndexSessionEntry | null;
  isLoading: boolean;
};

function healthBadge(status: string | null): { label: string; variant: BadgeVariant } {
  if (status === "ok") return { label: "Online", variant: "success" };
  if (status) return { label: "Check API", variant: "warning" };
  return { label: "Unknown", variant: "neutral" };
}

export function OpsStatusStrip({ health, sampleCount, uploadedCount, sessionIndex, isLoading }: OpsStatusStripProps) {
  const hb = healthBadge(health);

  return (
    <section className="ops-status-strip" aria-label="Deployment status for this environment">
      <MetricCard
        label="Backend health"
        value={isLoading ? "…" : health ?? "—"}
        sub="Live probe · /api/health"
        badgeLabel={isLoading ? undefined : hb.label}
        badgeVariant={hb.variant}
      />
      <MetricCard
        label="Sample corpus"
        value={isLoading ? "…" : sampleCount ?? "—"}
        sub="Files available to index"
        badgeLabel="API list"
        badgeVariant="info"
      />
      <MetricCard
        label="Uploaded corpus"
        value={isLoading ? "…" : uploadedCount ?? "—"}
        sub="User uploads on backend"
        badgeLabel="API list"
        badgeVariant="info"
      />
      <MetricCard
        label="Last index"
        value={
          isLoading
            ? "…"
            : sessionIndex
              ? sessionIndex.indexedFileCount
              : "—"
        }
        sub={
          sessionIndex
            ? `${sessionIndex.kind} · ${new Date(sessionIndex.indexedAt).toLocaleString()}`
            : "Browser session only — not a live FAISS probe"
        }
        badgeLabel={sessionIndex ? "Indexed" : "Not run"}
        badgeVariant={sessionIndex ? "success" : "neutral"}
      />
    </section>
  );
}
