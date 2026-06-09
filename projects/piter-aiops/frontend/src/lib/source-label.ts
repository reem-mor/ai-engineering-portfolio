export function sourceLabel(mode?: string, fallbackUsed?: boolean): string {
  if (fallbackUsed || mode === "local_fallback") {
    return "Local fallback knowledge base";
  }
  if (mode === "local") {
    return "Local knowledge base";
  }
  if (mode?.includes("bedrock") || mode === "agent" || mode === "bedrock_agent") {
    return "Bedrock Agent + Knowledge Base";
  }
  if (mode === "retrieve_and_generate") {
    return "Bedrock Knowledge Base";
  }
  return mode ? `Source: ${mode}` : "Source: unknown";
}
