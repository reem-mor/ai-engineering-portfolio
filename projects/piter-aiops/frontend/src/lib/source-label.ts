export function sourceLabel(mode?: string, fallbackUsed?: boolean): string {
  if (fallbackUsed || mode === "local_fallback") {
    return "Source: Local project knowledge base fallback";
  }
  if (mode === "local") {
    return "Source: Local project knowledge base";
  }
  if (
    mode?.includes("bedrock") ||
    mode === "agent" ||
    mode === "bedrock_agent" ||
    mode === "retrieve_and_generate"
  ) {
    return "Source: Bedrock Agent + Knowledge Base";
  }
  return mode ? `Source: ${mode}` : "Source: unknown";
}
