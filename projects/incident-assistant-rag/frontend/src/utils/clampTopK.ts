export function clampTopK(value: string): number {
  const parsed = Number(value);
  if (Number.isNaN(parsed)) return 5;
  return Math.min(10, Math.max(1, parsed));
}
