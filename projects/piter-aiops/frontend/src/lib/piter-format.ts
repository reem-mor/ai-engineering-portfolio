/** Strip markdown symbols and split into clean bullet lines for UI rendering. */
export function parsePiterSection(text: string | undefined | null): string[] {
  if (!text?.trim()) return [];
  return text
    .split(/\n+/)
    .map((line) =>
      line
        .replace(/^#{1,6}\s+/, "")
        .replace(/^[-*•]\s+/, "")
        .replace(/^\d+\.\s+/, "")
        .replace(/\*\*/g, "")
        .replace(/\*/g, "")
        .trim(),
    )
    .filter((line) => line.length > 0);
}

export function formatCurrencyUsd(value: number | undefined | null): string | null {
  if (value == null || Number.isNaN(value)) return null;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number | undefined | null): string | null {
  if (value == null || Number.isNaN(value)) return null;
  return new Intl.NumberFormat("en-US").format(value);
}
