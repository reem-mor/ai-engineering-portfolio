/** Shared P1 investigation progress labels (UI only — does not change storm timing). */
export const P1_ANALYZE_STEPS = [
  "Reading alert context",
  "Resolving service ownership",
  "Checking recent deployments",
  "Querying knowledge base",
  "Similar incidents lookup",
  "Action group enrichment",
  "Escalation recommendation",
  "Generating PITER response",
] as const;
